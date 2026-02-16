"""Google Drive KB loader — fetches files via the api-gateway /storage endpoints."""

import io
import logging
from dataclasses import dataclass
from typing import Optional

import httpx
from PyPDF2 import PdfReader
from docx import Document

from core.config import get_config

logger = logging.getLogger(__name__)

_TEXT_MIMES = {"text/plain", "text/csv", "text/markdown"}


@dataclass
class DriveFileRecord:
    id: str
    name: str
    mime_type: str
    modified_time: str
    category: str           # KB subfolder name (e.g. "general", "projects")
    size: Optional[int] = None


def _gateway_url(path: str) -> str:
    config = get_config()
    return f"{config.api_gateway_url.rstrip('/')}/{path.lstrip('/')}"


def _gateway_headers() -> dict:
    config = get_config()
    return {"X-API-Key": config.api_gateway_key} if config.api_gateway_key else {}


async def list_drive_files() -> list[DriveFileRecord]:
    """List files across all KB subfolders via the api-gateway.

    Returns files from all configured subfolders (General, Projects, Purdue,
    Career, Reference). Each record includes its source category.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(
            _gateway_url("/storage/files"),
            headers=_gateway_headers(),
        )
        r.raise_for_status()
        data = r.json()

    return [
        DriveFileRecord(
            id=f["id"],
            name=f["name"],
            mime_type=f["mime_type"],
            modified_time=f["modified_time"],
            category=f["category"],
            size=f.get("size"),
        )
        for f in data.get("files", [])
    ]


async def download_file(file_id: str) -> tuple[bytes, str, str]:
    """Download a file's content via the api-gateway.

    Returns:
        (content_bytes, content_type, filename)
    """
    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        r = await client.get(
            _gateway_url(f"/storage/files/{file_id}/content"),
            headers=_gateway_headers(),
        )
        r.raise_for_status()

    content_type = r.headers.get("content-type", "application/octet-stream").split(";")[0].strip()
    filename = r.headers.get("x-file-name", file_id)
    return r.content, content_type, filename


def parse_content(data: bytes, content_type: str, filename: str) -> str:
    """Parse raw bytes into plain text based on content type or filename extension."""
    # Plain text (includes Google Docs exported as text/plain, CSVs, markdown)
    if content_type in _TEXT_MIMES or filename.endswith((".txt", ".md", ".csv")):
        return data.decode("utf-8", errors="replace")

    # PDF
    if content_type == "application/pdf" or filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(p for p in pages if p.strip())

    # DOCX
    if (
        content_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        or filename.endswith(".docx")
    ):
        doc = Document(io.BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)

    # Fallback: try UTF-8
    logger.warning(f"Unknown content type '{content_type}' for '{filename}', attempting UTF-8 decode")
    return data.decode("utf-8", errors="replace")
