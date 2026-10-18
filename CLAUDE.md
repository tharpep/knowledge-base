# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Knowledge base service** built with **FastAPI** (Python 3.11+). Ingests uploaded files, pasted text and URLs, stores vectors in PostgreSQL + pgvector (homelab CT 103), and exposes a hybrid retrieval API. Google Drive sync was removed on 2026-10-18; content is added from the Sazed console's Knowledge page or by Sazed itself. Part of a larger personal AI ecosystem — see `../api-gateway/developmentplan.md` for the full architecture.

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

**Entry point:** `app/main.py` — creates FastAPI app with lifespan that initialises the asyncpg pool + schema and the `AIGateway` singleton. Mounts all routers under `/v1` (and health under `/health`).

**Configuration:** `core/config.py` — `AppConfig` via pydantic-settings, loaded from `.env`. Singleton via `get_config()`. Key env vars: `DATABASE_URL`, `VOYAGE_API_KEY`, `API_GATEWAY_URL`, `API_GATEWAY_KEY`.

### Module Layout

```
app/
  main.py            — FastAPI app + lifespan, CORS, router mounts
  routes/
    health.py        — GET /health, GET /health/detailed
    llm.py           — POST /v1/chat/completions (OpenAI-compat, optional KB injection)
                       GET  /v1/models
    query.py         — POST /v1/kb/search (hybrid retrieval), GET /v1/kb/stats
    ingest.py        — POST /v1/kb/ingest/file (multipart upload: pdf/docx/md/txt/csv, 15 MB)
                       POST /v1/kb/ingest/text (optional source_id = stable, replaceable)
                       POST /v1/kb/ingest/url
                       GET  /v1/kb/sources, GET /v1/kb/sources/{file_id}/content, GET /v1/kb/files
                       DELETE /v1/kb, DELETE /v1/kb/files/{file_id}
    config.py        — GET /v1/config, PATCH /v1/config

core/
  config.py          — AppConfig (pydantic-settings singleton)
  database.py        — asyncpg pool + schema init (kb_chunks, kb_sources, pgvector)

llm/
  gateway.py         — AIGateway: routes LLM calls to api-gateway /ai/v1/chat/completions
  base_client.py     — provider interface
  local.py           — Ollama provider (local dev only, never deployed)
  providers/
    anthropic.py     — direct Anthropic client (unused; routing goes through gateway)

rag/
  embedder.py        — Voyage AI embed_documents() / embed_query() (async, batched at 96)
  loader.py          — parse_content(): PDF (PyPDF2), DOCX (python-docx), XLSX, text/CSV/markdown
  chunking.py        — text chunking (langchain-text-splitters)
  pipeline.py        — ingest_document(): summarize, chunk, embed, upsert (every ingest path)
  retriever.py       — hybrid search: dense (pgvector) + FTS → RRF → Voyage rerank
  reranker.py        — Voyage rerank-2.5 via voyageai SDK
  query_processor.py — LLM query expansion via gateway (optional, per-request flag)
```

### Database Schema (`core/database.py`)

Tables auto-created on startup:

- **kb_chunks** — content, embedding (vector 1024), fts (tsvector), source_category, drive_file_id, filename, chunk_index, metadata. Indexes: HNSW (embedding), GIN (fts), btree (drive_file_id, source_category).
- **kb_sources** — file_id (PK), filename, category, origin (upload | text | url), summary, raw_content, modified_time, last_synced, chunk_count, status. One row per source. file_id prefixes: `upload:` (hash of the filename, so re-uploading replaces), `text:` (source_id or a uuid), `url:` (hash of the URL). `kb_chunks.drive_file_id` holds the file_id (old column name).

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

### Ingest Pipeline (`rag/pipeline.py`)

```
upload -> parse_content()  |  text  |  url -> gateway /search/web/fetch
    -> ingest_document(file_id, filename, category, content, origin)
    -> generate_summary() (gateway) -> chunk_markdown()/chunk_text() -> contextualize_chunk()
    -> embed_documents() in batches of 96
    -> atomic transaction: DELETE old chunks for file_id + INSERT new ones
    -> upsert kb_sources (summary, raw_content, origin, chunk_count)
```

### LLM Calls (`llm/gateway.py`)

All generation goes through `AIGateway.chat()` → api-gateway `/ai/v1/chat/completions`. The knowledge-base never calls Anthropic directly. `AIGateway` is a synchronous client (httpx); it is initialised once in `app/main.py` and accessed via a module-level global.

## Key Conventions

- **Ruff** for linting: line length 120, target Python 3.11
- **black** for formatting: line length 120
- All DB access via `asyncpg` pool from `core/database.py`; get with `get_pool()`
- Outbound calls (LLM, web fetch) go through the api-gateway, never directly to providers
- Voyage AI client is synchronous; wrapped in `asyncio.to_thread` in `embedder.py` and `reranker.py`
- Config singleton: `from core.config import get_config; config = get_config()`
