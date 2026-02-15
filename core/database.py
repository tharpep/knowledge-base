"""PostgreSQL connection pool and schema initialization."""

import logging
from typing import Optional

import asyncpg

from core.config import get_config

logger = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None

_SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS kb_chunks (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content       TEXT NOT NULL,
    embedding     vector(1024),
    fts           TSVECTOR GENERATED ALWAYS AS
                    (to_tsvector('english', content)) STORED,
    drive_file_id TEXT,
    filename      TEXT,
    folder        TEXT,
    chunk_index   INTEGER,
    metadata      JSONB DEFAULT '{}',
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS kb_chunks_embedding_idx
    ON kb_chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS kb_chunks_fts_idx
    ON kb_chunks USING gin (fts);

CREATE INDEX IF NOT EXISTS kb_chunks_drive_file_id_idx
    ON kb_chunks (drive_file_id);
"""


async def init_pool() -> None:
    """Create the asyncpg pool and initialize the schema."""
    global _pool

    config = get_config()
    if not config.database_url:
        logger.warning("DATABASE_URL not set — skipping database init")
        return

    # asyncpg expects postgresql://, not postgresql+asyncpg://
    dsn = config.database_url.replace("postgresql+asyncpg://", "postgresql://")

    logger.info("Connecting to PostgreSQL...")
    _pool = await asyncpg.create_pool(dsn=dsn, min_size=2, max_size=10)

    async with _pool.acquire() as conn:
        await conn.execute(_SCHEMA_SQL)

    logger.info("Database pool ready and schema initialized")


def get_pool() -> asyncpg.Pool:
    """Return the active pool. Raises if not initialized."""
    if _pool is None:
        raise RuntimeError("Database pool not initialized — call init_pool() first")
    return _pool


async def close_pool() -> None:
    """Close the pool on shutdown."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("Database pool closed")
