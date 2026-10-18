"""KB content routes: ingest (upload, text, URL), list sources, read, and delete."""

import asyncio
import hashlib
import logging
import uuid
from pathlib import PurePath

import httpx
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from core.database import get_pool
from rag.loader import _gateway_headers, _gateway_url, parse_content
from rag.pipeline import EmptyContentError, ingest_document

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_EXTENSIONS = (".pdf", ".docx", ".md", ".markdown", ".txt", ".csv")
MAX_UPLOAD_BYTES = 15 * 1024 * 1024


@router.get("/kb/sources")
async def list_kb_sources():
    """List every source in the KB, newest first."""
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT file_id, filename, category, origin, summary, modified_time, last_synced,
                       chunk_count, status, length(raw_content) AS content_chars
                FROM kb_sources
                ORDER BY last_synced DESC NULLS LAST, filename
                """
            )
        return {
            "sources": [
                {
                    "file_id": r["file_id"],
                    "filename": r["filename"],
                    "category": r["category"],
                    "origin": r["origin"],
                    "summary": r["summary"],
                    "modified_time": r["modified_time"].isoformat() if r["modified_time"] else None,
                    "last_synced": r["last_synced"].isoformat() if r["last_synced"] else None,
                    "chunk_count": r["chunk_count"],
                    "content_chars": r["content_chars"] or 0,
                    "status": r["status"],
                }
                for r in rows
            ],
            "count": len(rows),
        }
    except Exception as e:
        logger.exception("Failed to list KB sources")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/kb/files")
async def list_kb_files():
    """List all files currently indexed in kb_chunks, with chunk counts and category."""
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT drive_file_id, filename, source_category, COUNT(*) AS chunk_count
                FROM kb_chunks
                GROUP BY drive_file_id, filename, source_category
                ORDER BY filename
                """
            )
        return {
            "files": [
                {
                    "drive_file_id": r["drive_file_id"],
                    "filename": r["filename"],
                    "source_category": r["source_category"],
                    "chunk_count": r["chunk_count"],
                }
                for r in rows
            ],
            "count": len(rows),
        }
    except Exception as e:
        logger.exception("Failed to list KB files")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/kb", status_code=204)
async def clear_kb():
    """Truncate kb_chunks and kb_sources — removes all indexed content."""
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.execute("TRUNCATE TABLE kb_chunks")
            await conn.execute("TRUNCATE TABLE kb_sources")
    except Exception as e:
        logger.exception("Failed to clear KB")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/kb/files/{file_id}", status_code=204)
async def delete_kb_file(file_id: str):
    """Remove a source entirely: its chunks and its kb_sources row (including the stored text)."""
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                chunks = await conn.execute("DELETE FROM kb_chunks WHERE drive_file_id = $1", file_id)
                sources = await conn.execute("DELETE FROM kb_sources WHERE file_id = $1", file_id)
        if int(chunks.split()[-1]) == 0 and int(sources.split()[-1]) == 0:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Source not found: {file_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete KB source {file_id}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


class IngestTextRequest(BaseModel):
    title: str
    content: str
    category: str | None = None
    # A caller-chosen stable id (e.g. 'journal-career-2026-10'). Re-ingesting with the same
    # source_id replaces that source instead of adding a duplicate. No slashes: ids go in URL paths.
    source_id: str | None = Field(None, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$")


class IngestUrlRequest(BaseModel):
    url: str
    category: str | None = None


class IngestResponse(BaseModel):
    file_id: str
    filename: str
    category: str | None
    origin: str
    chunk_count: int
    summary: str


async def _ingest(file_id: str, filename: str, category: str | None, content: str, origin: str) -> IngestResponse:
    try:
        return IngestResponse(**await ingest_document(file_id, filename, category, content, origin))
    except EmptyContentError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.exception(f"{origin} ingest failed for '{filename}'")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/kb/ingest/file", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_file(
    file: UploadFile = File(...),  # noqa: B008
    category: str | None = Form(None),
):
    """Upload a document (PDF, DOCX, Markdown, text, CSV) and index it.

    Keyed by filename, so uploading a new version of 'resume.pdf' replaces the old one.
    """
    filename = PurePath(file.filename or "").name
    if not filename.lower().endswith(UPLOAD_EXTENSIONS):
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed: {', '.join(UPLOAD_EXTENSIONS)}",
        )

    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File is over {MAX_UPLOAD_BYTES // (1024 * 1024)} MB",
        )

    try:
        text = await asyncio.to_thread(parse_content, data, file.content_type or "", filename)
    except Exception as e:
        logger.warning(f"Could not parse upload '{filename}': {e}")
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Could not read {filename}: {e}")

    file_id = f"upload:{hashlib.sha256(filename.lower().encode()).hexdigest()[:32]}"
    return await _ingest(file_id, filename, category, text, origin="upload")


@router.post("/kb/ingest/text", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_text(body: IngestTextRequest):
    """Directly ingest arbitrary text content."""
    file_id = f"text:{body.source_id or uuid.uuid4()}"
    return await _ingest(file_id, body.title, body.category, body.content, origin="text")


@router.post("/kb/ingest/url", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_url(body: IngestUrlRequest):
    """Fetch a URL via the gateway's web-fetch (Tavily extract) and ingest its text."""
    file_id = f"url:{hashlib.sha256(body.url.encode()).hexdigest()}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            _gateway_url("search/web/fetch"),
            json={"url": body.url},
            headers=_gateway_headers(),
        )
    if resp.status_code != 200:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=f"URL fetch failed: {resp.text}")

    data = resp.json()
    results = data.get("results") or []
    if not results or not results[0].get("raw_content"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"No content extracted from {body.url}")

    return await _ingest(file_id, body.url, body.category, results[0]["raw_content"], origin="url")


@router.get("/kb/sources/{file_id}/content")
async def get_source_content(file_id: str):
    """Return a source's full original text plus metadata — backs full-document reads."""
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT file_id, filename, category, origin, raw_content "
            "FROM kb_sources WHERE file_id = $1 AND status = 'active'",
            file_id,
        )
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Source not found: {file_id}")
    return {
        "file_id": row["file_id"],
        "filename": row["filename"],
        "category": row["category"],
        "origin": row["origin"],
        "content": row["raw_content"] or "",
    }
