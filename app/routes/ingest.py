"""KB sync routes — trigger Drive → kb_chunks sync."""

import logging

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from core.database import get_pool
from rag.sync import sync_drive

logger = logging.getLogger(__name__)

router = APIRouter()


class SyncResponse(BaseModel):
    files_synced: int
    chunks_inserted: int
    errors: list[str]
    synced_at: str


@router.post("/kb/sync", response_model=SyncResponse)
async def full_sync():
    """Full sync: pull all files from the KB/General Drive folder into kb_chunks."""
    try:
        result = await sync_drive()
        return SyncResponse(**result)
    except Exception as e:
        logger.error(f"KB full sync failed: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/kb/sync/incremental", response_model=SyncResponse)
async def incremental_sync(
    modified_after: str = Query(
        ..., description="ISO 8601 timestamp — only sync files modified after this time"
    ),
):
    """Incremental sync: only process Drive files modified after the given timestamp."""
    try:
        result = await sync_drive(modified_after=modified_after)
        return SyncResponse(**result)
    except Exception as e:
        logger.error(f"KB incremental sync failed: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/kb/files")
async def list_kb_files():
    """List all files currently indexed in kb_chunks, with chunk counts."""
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT drive_file_id, filename, COUNT(*) AS chunk_count
                FROM kb_chunks
                GROUP BY drive_file_id, filename
                ORDER BY filename
                """
            )
        return {
            "files": [
                {
                    "drive_file_id": r["drive_file_id"],
                    "filename": r["filename"],
                    "chunk_count": r["chunk_count"],
                }
                for r in rows
            ],
            "count": len(rows),
        }
    except Exception as e:
        logger.error(f"Failed to list KB files: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/kb/files/{drive_file_id}", status_code=204)
async def delete_kb_file(drive_file_id: str):
    """Remove all chunks for a specific Drive file from kb_chunks."""
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM kb_chunks WHERE drive_file_id = $1", drive_file_id
            )
        # asyncpg returns "DELETE N" — check the count
        deleted_count = int(result.split()[-1])
        if deleted_count == 0:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=f"No chunks found for drive_file_id={drive_file_id}",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete KB file {drive_file_id}: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
