"""KB sync engine — Drive → kb_chunks (fetch → parse → chunk → embed → upsert)."""

import logging
from datetime import datetime, timezone
from typing import Optional

from core.config import get_config
from core.database import get_pool
from rag.chunking import chunk_text
from rag.embedder import embed_documents
from rag.loader import download_file, list_drive_files, parse_content

logger = logging.getLogger(__name__)

# Stay well under Voyage's 128-input / 320K-token per-request limit
_EMBED_BATCH = 96


async def _upsert_file_chunks(
    pool,
    drive_file_id: str,
    filename: str,
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
                INSERT INTO kb_chunks (content, embedding, drive_file_id, filename, chunk_index)
                VALUES ($1, $2::vector, $3, $4, $5)
                """,
                [
                    (
                        chunk,
                        f"[{','.join(str(x) for x in emb)}]",
                        drive_file_id,
                        filename,
                        idx,
                    )
                    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings))
                ],
            )
    return len(chunks)


async def sync_drive(modified_after: Optional[str] = None) -> dict:
    """Sync the KB/General Drive folder into kb_chunks.

    Args:
        modified_after: ISO 8601 timestamp. When set, only files modified after
                        this time are processed (incremental). When None, all
                        files are processed (full sync).

    Returns:
        dict with keys: files_synced, chunks_inserted, errors, synced_at
    """
    config = get_config()
    pool = get_pool()

    files = await list_drive_files(modified_after=modified_after)
    logger.info(f"Drive sync: {len(files)} file(s) to process")

    files_synced = 0
    chunks_inserted = 0
    errors: list[str] = []

    for file in files:
        try:
            data, content_type, _ = await download_file(file.id)
            text = parse_content(data, content_type, file.name)

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

            # Embed in batches to stay within Voyage rate/size limits
            all_embeddings: list[list[float]] = []
            for i in range(0, len(chunks), _EMBED_BATCH):
                batch = chunks[i : i + _EMBED_BATCH]
                embs = await embed_documents(batch)
                all_embeddings.extend(embs)

            inserted = await _upsert_file_chunks(
                pool,
                drive_file_id=file.id,
                filename=file.name,
                chunks=chunks,
                embeddings=all_embeddings,
            )

            files_synced += 1
            chunks_inserted += inserted
            logger.info(f"Synced '{file.name}': {inserted} chunk(s)")

        except Exception as e:
            logger.error(f"Error syncing '{file.name}': {e}")
            errors.append(f"{file.name}: {e}")

    return {
        "files_synced": files_synced,
        "chunks_inserted": chunks_inserted,
        "errors": errors,
        "synced_at": datetime.now(timezone.utc).isoformat(),
    }
