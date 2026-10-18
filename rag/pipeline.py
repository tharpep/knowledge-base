"""Ingest pipeline: summarize, chunk, embed, and upsert one document into kb_chunks + kb_sources.

Every way content enters the KB (upload, pasted text, URL) goes through ingest_document(), so a
document looks the same downstream whatever its origin. A file_id identifies one source; ingesting
the same file_id again replaces its chunks instead of adding a second copy.
"""

import asyncio
import json
import logging

from core.config import get_config
from core.database import get_pool
from llm.gateway import AIGateway
from rag.chunking import chunk_markdown, chunk_text
from rag.embedder import embed_documents

logger = logging.getLogger(__name__)

SUMMARY_UNAVAILABLE = "[unavailable]"

# Stay well under Voyage's 128-input / 320K-token per-request limit
EMBED_BATCH = 96


class EmptyContentError(ValueError):
    """The document had no text, or chunking produced nothing to embed."""


def generate_summary(text: str, gw: AIGateway) -> str:
    """Call the AI gateway for a 1-2 sentence document summary."""
    try:
        return gw.chat(
            f"In 1-2 sentences, describe what this document is about and what kind of "
            f"information it contains. Be specific about names, projects, or topics if evident. "
            f"Reply with only the description, no preamble.\n\n{text[:2000]}"
        )
    except Exception as exc:
        logger.warning(f"Summary generation failed: {exc}")
        return SUMMARY_UNAVAILABLE


def contextualize_chunk(chunk: str, filename: str, summary: str, section_title: str = "") -> str:
    """Prepend a short doc-aware (and section-aware, if known) context blurb before embedding.

    Implements Anthropic's Contextual Retrieval. The contextualized text is what
    gets embedded AND stored in `content` — so the generated `fts` tsvector also
    benefits — the deliberate tradeoff (per issue #102's "simplest first cut") is
    that retrieved chunks show this prefix.
    """
    context_bits = [f"From '{filename}'"]
    if summary and summary != SUMMARY_UNAVAILABLE:
        context_bits.append(f"({summary})")
    if section_title:
        context_bits.append(f"[{section_title}]")
    prefix = " ".join(context_bits) + ": "
    return prefix + chunk


async def upsert_kb_source(
    conn,
    file_id: str,
    filename: str,
    category: str,
    chunk_count: int,
    summary: str,
    raw_content: str,
    origin: str,
) -> None:
    """Insert or update a kb_sources record, stamping modified_time and last_synced with now."""
    await conn.execute(
        """
        INSERT INTO kb_sources
            (file_id, filename, category, modified_time, last_synced, chunk_count, summary,
             status, raw_content, origin)
        VALUES ($1, $2, $3, NOW(), NOW(), $4, $5, 'active', $6, $7)
        ON CONFLICT (file_id) DO UPDATE SET
            filename      = EXCLUDED.filename,
            category      = EXCLUDED.category,
            modified_time = NOW(),
            last_synced   = NOW(),
            chunk_count   = EXCLUDED.chunk_count,
            summary       = EXCLUDED.summary,
            status        = 'active',
            raw_content   = EXCLUDED.raw_content,
            origin        = EXCLUDED.origin
        """,
        file_id,
        filename,
        category,
        chunk_count,
        summary,
        raw_content,
        origin,
    )


async def upsert_file_chunks(
    pool,
    file_id: str,
    filename: str,
    source_category: str,
    chunks: list[str],
    embeddings: list[list[float]],
    section_titles: list[str] | None = None,
) -> int:
    """Delete existing chunks for this source and insert new ones atomically.

    The column is still named drive_file_id from the Drive-sync days; it now holds any file_id.
    Returns the number of chunks inserted.
    """
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("DELETE FROM kb_chunks WHERE drive_file_id = $1", file_id)
            if not chunks:
                return 0
            await conn.executemany(
                """
                INSERT INTO kb_chunks
                    (content, embedding, source_category, drive_file_id, filename, chunk_index, metadata)
                VALUES ($1, $2::vector, $3, $4, $5, $6, $7::jsonb)
                """,
                [
                    (
                        chunk,
                        f"[{','.join(str(x) for x in emb)}]",
                        source_category,
                        file_id,
                        filename,
                        idx,
                        json.dumps(
                            {"section_title": section_titles[idx]}
                            if section_titles and section_titles[idx]
                            else {}
                        ),
                    )
                    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings))
                ],
            )
    return len(chunks)


async def ingest_document(
    file_id: str, filename: str, category: str | None, content: str, origin: str
) -> dict:
    """Summarize, chunk (markdown-aware by filename), embed, and store one document.

    Raises EmptyContentError when there is nothing to index.
    """
    if not content.strip():
        raise EmptyContentError("No content to ingest")

    config = get_config()
    summary = await asyncio.to_thread(generate_summary, content, AIGateway())

    section_titles: list[str] | None = None
    if filename.lower().endswith((".md", ".markdown")):
        raw_chunks = chunk_markdown(
            content, chunk_size=config.kb_chunk_size, overlap=config.kb_chunk_overlap
        )
        chunks = [
            contextualize_chunk(chunk, filename, summary, section_title)
            for chunk, section_title in raw_chunks
        ]
        # Stored in kb_chunks.metadata so a caller can cite "section X" instead
        # of only ever pointing at the whole document.
        section_titles = [section_title for _, section_title in raw_chunks]
    else:
        raw_chunks = chunk_text(
            content, chunk_size=config.kb_chunk_size, overlap=config.kb_chunk_overlap
        )
        chunks = [contextualize_chunk(chunk, filename, summary) for chunk in raw_chunks]
    if not chunks:
        raise EmptyContentError("Content produced no chunks")

    embeddings: list[list[float]] = []
    for i in range(0, len(chunks), EMBED_BATCH):
        embeddings.extend(await embed_documents(chunks[i : i + EMBED_BATCH]))

    pool = get_pool()
    inserted = await upsert_file_chunks(
        pool,
        file_id=file_id,
        filename=filename,
        source_category=category or "",
        chunks=chunks,
        embeddings=embeddings,
        section_titles=section_titles,
    )
    async with pool.acquire() as conn:
        await upsert_kb_source(
            conn,
            file_id,
            filename,
            category or "",
            inserted,
            summary,
            raw_content=content,
            origin=origin,
        )

    logger.info(f"Ingested '{filename}' ({origin}): {inserted} chunk(s)")
    return {
        "file_id": file_id,
        "filename": filename,
        "category": category,
        "origin": origin,
        "chunk_count": inserted,
        "summary": summary,
    }
