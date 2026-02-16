"""KB sync routes — Drive → kb_chunks sync management."""

import logging

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from core.database import get_pool
from rag.sync import sync_drive

logger = logging.getLogger(__name__)

router = APIRouter()


class SyncResponse(BaseModel):
    files_synced: int
    files_skipped: int
    files_deleted: int
    chunks_inserted: int
    errors: list[str]
    synced_at: str


@router.post("/kb/sync", response_model=SyncResponse)
async def run_sync(
    force: bool = Query(
        default=False,
        description="Re-sync all files regardless of modification time",
    ),
):
    """Sync KB Drive folder into kb_chunks.

    By default only processes new or modified files (smart incremental sync
    using kb_sources change tracking). Pass force=true to re-sync everything.
    """
    try:
        result = await sync_drive(force=force)
        return SyncResponse(**result)
    except Exception as e:
        logger.error(f"KB sync failed: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/kb/sources")
async def list_kb_sources():
    """List all files tracked in kb_sources with their sync status."""
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT file_id, filename, category, modified_time, last_synced,
                       chunk_count, status
                FROM kb_sources
                ORDER BY filename
                """
            )
        return {
            "sources": [
                {
                    "file_id": r["file_id"],
                    "filename": r["filename"],
                    "category": r["category"],
                    "modified_time": r["modified_time"].isoformat() if r["modified_time"] else None,
                    "last_synced": r["last_synced"].isoformat() if r["last_synced"] else None,
                    "chunk_count": r["chunk_count"],
                    "status": r["status"],
                }
                for r in rows
            ],
            "count": len(rows),
        }
    except Exception as e:
        logger.error(f"Failed to list KB sources: {e}")
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
        logger.error(f"Failed to list KB files: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/kb", status_code=204)
async def clear_kb():
    """Truncate kb_chunks and kb_sources — removes all indexed content and sync state."""
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.execute("TRUNCATE TABLE kb_chunks")
            await conn.execute("TRUNCATE TABLE kb_sources")
    except Exception as e:
        logger.error(f"Failed to clear KB: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/kb/files/{drive_file_id}", status_code=204)
async def delete_kb_file(drive_file_id: str):
    """Remove a file's chunks from kb_chunks and mark it deleted in kb_sources."""
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM kb_chunks WHERE drive_file_id = $1", drive_file_id
            )
            deleted_count = int(result.split()[-1])
            if deleted_count == 0:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    detail=f"No chunks found for drive_file_id={drive_file_id}",
                )
            await conn.execute(
                "UPDATE kb_sources SET status = 'deleted', last_synced = NOW() "
                "WHERE file_id = $1",
                drive_file_id,
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete KB file {drive_file_id}: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
