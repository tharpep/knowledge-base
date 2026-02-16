# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cloud-first **knowledge base service** built with **FastAPI** (Python 3.11+). Ingests documents from Google Drive (via the api-gateway), stores vectors in PostgreSQL + pgvector (GCP Cloud SQL), and exposes a hybrid retrieval API. Part of a larger personal AI ecosystem — see `../api-gateway/developmentplan.md` for the full architecture.

Managed with **Poetry**. Deployed to **GCP Cloud Run**.

## Commands

```bash
# Install dependencies
poetry install

# Run dev server (hot reload)
poetry run uvicorn app.main:app --reload

# Lint
ruff check .

# Format
ruff format .
# or: black .
```

No test suite exists yet.

## Architecture

**Entry point:** `app/main.py` — creates FastAPI app with lifespan that initialises the asyncpg pool + schema, and the `AIGateway` singleton. Includes SQLite request logging middleware (non-critical). Mounts all routers under `/v1`.

**Configuration:** `core/config.py` — `AppConfig` via pydantic-settings, loaded from `.env`. Singleton via `get_config()`. Key env vars: `DATABASE_URL`, `VOYAGE_API_KEY`, `API_GATEWAY_URL`, `API_GATEWAY_KEY`.

### Module Layout

```
app/
  main.py            — FastAPI app + lifespan
  db.py              — SQLite request logging (non-critical)
  routes/
    health.py        — GET /health
    llm.py           — POST /v1/chat/completions (OpenAI-compat, optional KB injection)
                       GET  /v1/models
    query.py         — POST /v1/kb/query (hybrid retrieval)
                       GET  /v1/kb/stats
    ingest.py        — POST /v1/kb/sync (full sync from Drive)
                       POST /v1/kb/sync/incremental (modified_after param)
                       GET  /v1/kb/files (indexed files + chunk counts)
                       DELETE /v1/kb (truncate all chunks)
                       DELETE /v1/kb/files/{drive_file_id}
    config.py        — GET /v1/config (current AppConfig values)
    logs.py          — request log access
    profile.py       — user profile for system prompt injection

core/
  config.py          — AppConfig (pydantic-settings singleton)
  database.py        — asyncpg pool + schema init (kb_chunks table, pgvector extension)
  profile_manager.py — user profile context injected into LLM system prompts
  prompt_manager.py  — system prompt templates

llm/
  gateway.py         — AIGateway: routes LLM calls to api-gateway /ai/v1/chat/completions
  base_client.py     — provider interface
  local.py           — Ollama provider (local dev only, never deployed)
  providers/
    anthropic.py     — direct Anthropic client (unused in current routing)

rag/
  embedder.py        — Voyage AI embed_documents() / embed_query() (async, batched at 96)
  loader.py          — lists + downloads files from api-gateway /storage endpoints;
                       parses PDF (PyPDF2), DOCX (python-docx), plain text/CSV/markdown
  chunking.py        — text chunking (langchain-text-splitters)
  sync.py            — sync_drive(): full/incremental Drive → kb_chunks pipeline
  retriever.py       — hybrid search: dense (pgvector) + FTS → RRF → Voyage rerank
  reranker.py        — Voyage rerank-2.5 via voyageai SDK
  query_processor.py — LLM query expansion via gateway (optional, per-request flag)
```

### Database Schema (`core/database.py`)

Single table auto-created on startup:

```sql
CREATE TABLE kb_chunks (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content       TEXT NOT NULL,
    embedding     vector(1024),             -- Voyage AI voyage-4 (1024d)
    fts           TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    drive_file_id TEXT,
    filename      TEXT,
    folder        TEXT,
    chunk_index   INTEGER,
    metadata      JSONB DEFAULT '{}',
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes: HNSW cosine (embedding), GIN (fts), btree (drive_file_id)
```

**Note:** `source_category` column and `kb_sources` tracking table from the dev plan are not yet implemented. Incremental sync relies on the caller passing `modified_after`.

### Retrieval Pipeline (`rag/retriever.py`)

```
embed_query(query)
    → dense_search (pgvector HNSW cosine, top candidates)
    → fts_search (PostgreSQL plainto_tsquery, top candidates)  [skipped if sparse_weight=0]
    → RRF fusion
    → Voyage rerank-2.5 (top_k)
    → similarity threshold filter
```

Config knobs (all in `core/config.py`): `hybrid_sparse_weight`, `rerank_enabled`, `rerank_candidates`, `rerank_model`, `chat_kb_top_k`, `chat_kb_similarity_threshold`.

### Sync Pipeline (`rag/sync.py`)

```
list_drive_files() → GET api-gateway/storage/files
    → download_file() → GET api-gateway/storage/files/{id}/content
    → parse_content() (PDF/DOCX/text)
    → chunk_text()
    → embed_documents() in batches of 96
    → atomic transaction: DELETE old chunks + INSERT new chunks per file
```

Source is currently scoped to `Knowledge Base → General` Drive folder (gateway limitation). Multi-category support is pending.

### LLM Calls (`llm/gateway.py`)

All generation goes through `AIGateway.chat()` → api-gateway `/ai/v1/chat/completions`. The knowledge-base never calls Anthropic directly. `AIGateway` is a synchronous client (httpx); it is initialised once in `app/main.py` and accessed via a module-level global.

## Key Conventions

- **Ruff** for linting: line length 120, target Python 3.11
- **black** for formatting: line length 120
- All DB access via `asyncpg` pool from `core/database.py`; get with `get_pool()`
- All Drive access via httpx to the api-gateway (never directly to Google APIs)
- Voyage AI client is synchronous; wrapped in `asyncio.to_thread` in `embedder.py` and `reranker.py`
- Config singleton: `from core.config import get_config; config = get_config()`
