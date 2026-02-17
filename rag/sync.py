"""KB sync engine — Drive → kb_chunks with kb_sources change tracking."""

import logging
from datetime import datetime, timezone
from typing import Optional

from core.config import get_config
from core.database import get_pool
from rag.chunking import chunk_text
from rag.embedder import embed_documents
from rag.loader import DriveFileRecord, download_file, list_drive_files, parse_content

logger = logging.getLogger(__name__)

# Stay well under Voyage's 128-input / 320K-token per-request limit
_EMBED_BATCH = 96


async def _get_all_kb_sources(pool) -> dict[str, dict]:
    """Fetch all kb_sources rows keyed by file_id."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT file_id, filename, category, modified_time, last_synced, chunk_count, status "
            "FROM kb_sources"
        )
    return {r["file_id"]: dict(r) for r in rows}


async def _upsert_kb_source(
    conn,
    file_id: str,
    filename: str,
    category: str,
    modified_time: str,
    chunk_count: int,
) -> None:
    """Insert or update a kb_sources record, setting last_synced to now."""
    await conn.execute(
        """
        INSERT INTO kb_sources (file_id, filename, category, modified_time, last_synced, chunk_count, status)
        VALUES ($1, $2, $3, $4::timestamptz, NOW(), $5, 'active')
        ON CONFLICT (file_id) DO UPDATE SET
            filename      = EXCLUDED.filename,
            category      = EXCLUDED.category,
            modified_time = EXCLUDED.modified_time,
            last_synced   = NOW(),
            chunk_count   = EXCLUDED.chunk_count,
            status        = 'active'
        """,
        file_id,
        filename,
        category,
        modified_time,
        chunk_count,
    )


async def _upsert_file_chunks(
    pool,
    drive_file_id: str,
    filename: str,
    source_category: str,
    chunks: list[str],
    embeddings: list[list[float]],
) -> int:
    """Delete existing chunks for this file and insert new ones atomically.

    Returns the number of chunks inserted.
    """
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "DELETE FROM kb_chunks WHERE drive_file_id = $1", drive_file_id
            )
            if not chunks:
                return 0
            await conn.executemany(
                """
                INSERT INTO kb_chunks
                    (content, embedding, source_category, drive_file_id, filename, chunk_index)
                VALUES ($1, $2::vector, $3, $4, $5, $6)
                """,
                [
                    (
                        chunk,
                        f"[{','.join(str(x) for x in emb)}]",
                        source_category,
                        drive_file_id,
                        filename,
                        idx,
                    )
                    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings))
                ],
            )
    return len(chunks)


async def _remove_deleted_files(pool, file_ids: list[str]) -> None:
    """Delete chunks and mark kb_sources as deleted for files no longer in Drive."""
    async with pool.acquire() as conn:
        async with conn.transaction():
            for fid in file_ids:
                await conn.execute(
                    "DELETE FROM kb_chunks WHERE drive_file_id = $1", fid
                )
                await conn.execute(
                    "UPDATE kb_sources SET status = 'deleted', last_synced = NOW() "
                    "WHERE file_id = $1",
                    fid,
                )


def _needs_sync(file: DriveFileRecord, source: Optional[dict]) -> bool:
    """Return True if the file is new or has been modified since last sync."""
    if source is None:
        return True
    last_synced: Optional[datetime] = source.get("last_synced")
    if last_synced is None:
        return True
    file_modified = datetime.fromisoformat(file.modified_time.replace("Z", "+00:00"))
    # last_synced from asyncpg is already timezone-aware
    if last_synced.tzinfo is None:
        last_synced = last_synced.replace(tzinfo=timezone.utc)
    return file_modified > last_synced


async def sync_drive(force: bool = False) -> dict:
    """Sync all KB Drive subfolders into kb_chunks, using kb_sources for change detection.

    Args:
        force: If True, re-sync every file regardless of modification time.

    Returns:
        dict with keys: files_synced, files_skipped, files_deleted, chunks_inserted,
                        errors, synced_at
    """
    config = get_config()
    pool = get_pool()

    # All files across all KB subfolders (category comes from each file's DriveFileRecord)
    drive_files = await list_drive_files()
    logger.info(f"Drive sync: {len(drive_files)} file(s) found across all KB subfolders")

    # Existing kb_sources state for change detection and deletion tracking
    existing_sources = await _get_all_kb_sources(pool)
    drive_ids = {f.id for f in drive_files}

    # Files that no longer exist in Drive but are still active in kb_sources
    deleted_ids = [
        fid
        for fid, src in existing_sources.items()
        if src.get("status") == "active" and fid not in drive_ids
    ]

    # Remove deleted files first
    if deleted_ids:
        await _remove_deleted_files(pool, deleted_ids)
        logger.info(f"Removed {len(deleted_ids)} deleted file(s) from KB")

    files_synced = 0
    files_skipped = 0
    chunks_inserted = 0
    errors: list[str] = []

    for file in drive_files:
        source = existing_sources.get(file.id)

        if not force and not _needs_sync(file, source):
            files_skipped += 1
            logger.debug(f"Skipping '{file.name}' — not modified since last sync")
            continue

        try:
            data, content_type, _ = await download_file(file.id)
            logger.debug(f"  downloaded '{file.name}': {len(data):,} bytes, type={content_type}")

            text = parse_content(data, content_type, file.name)
            logger.debug(f"  parsed '{file.name}': {len(text):,} chars")

            if not text.strip():
                logger.warning(f"No text extracted from '{file.name}', skipping")
                continue

            chunks = chunk_text(
                text,
                chunk_size=config.kb_chunk_size,
                overlap=config.kb_chunk_overlap,
            )
            if not chunks:
                continue

            n_batches = (len(chunks) + _EMBED_BATCH - 1) // _EMBED_BATCH
            logger.debug(
                f"  embedding '{file.name}': {len(chunks)} chunk(s) in {n_batches} batch(es)"
            )
            all_embeddings: list[list[float]] = []
            for i in range(0, len(chunks), _EMBED_BATCH):
                batch = chunks[i : i + _EMBED_BATCH]
                embs = await embed_documents(batch)
                all_embeddings.extend(embs)

            inserted = await _upsert_file_chunks(
                pool,
                drive_file_id=file.id,
                filename=file.name,
                source_category=file.category,
                chunks=chunks,
                embeddings=all_embeddings,
            )

            # Update kb_sources within its own connection (outside chunk transaction)
            async with pool.acquire() as conn:
                await _upsert_kb_source(
                    conn, file.id, file.name, file.category, file.modified_time, inserted
                )

            files_synced += 1
            chunks_inserted += inserted
            logger.info(f"Synced '{file.name}': {inserted} chunk(s)")

        except Exception as e:
            logger.error(f"Error syncing '{file.name}': {e}")
            errors.append(f"{file.name}: {e}")

    return {
        "files_synced": files_synced,
        "files_skipped": files_skipped,
        "files_deleted": len(deleted_ids),
        "chunks_inserted": chunks_inserted,
        "errors": errors,
        "synced_at": datetime.now(timezone.utc).isoformat(),
    }
