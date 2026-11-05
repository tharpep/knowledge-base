# KB Service

Personal knowledge base. Ingests uploaded files, pasted text and URLs, chunks and embeds them with Voyage AI, stores vectors in PostgreSQL + pgvector, and exposes a hybrid retrieval API (dense + FTS → RRF → rerank).

Deployed to GCP Cloud Run. All external access goes through the [api-gateway](https://github.com/tharpep/api-gateway) `/kb/*` proxy — this service is internal.

## Ecosystem

Part of a personal AI ecosystem — see [sazed](https://github.com/tharpep/sazed) for the full picture.

## Architecture

```
Uploads / text / URLs (Sazed console Knowledge page, Sazed tools)
    ↓  api-gateway /kb/ingest/*
KB Service (this repo)
    ↓  chunk → embed (Voyage AI) → pgvector (homelab Postgres)
api-gateway /kb/* proxy
    ↓
Agent / local-mcp / any consumer
```

## API

All routes require the `X-API-Key` header. The service refuses to start with an empty `API_KEY` unless `ALLOW_NO_AUTH=true` (local dev only; it opens every route).

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/kb/search` | Hybrid search (dense + FTS → RRF → rerank) |
| `POST` | `/v1/kb/ingest/file` | Upload a PDF/DOCX/MD/TXT/CSV (15 MB max; same filename replaces) |
| `POST` | `/v1/kb/ingest/text` | Ingest text (optional `source_id` to replace on re-ingest) |
| `POST` | `/v1/kb/ingest/url` | Fetch a URL and ingest its text |
| `GET` | `/v1/kb/sources` | List sources, newest first |
| `GET` | `/v1/kb/sources/{id}/content` | A source's full text |
| `GET` | `/v1/kb/files` | List indexed files with chunk counts |
| `GET` | `/v1/kb/stats` | Total chunk and file counts |
| `DELETE` | `/v1/kb` | Clear all indexed content |
| `DELETE` | `/v1/kb/files/{id}` | Remove a specific file |
| `POST` | `/v1/chat/completions` | OpenAI-compatible proxy with RAG injection |
| `GET` | `/health` | Health check (no auth) |

### Search request

```json
{
  "query": "how does auth refresh work?",
  "top_k": 5,
  "categories": ["projects", "general"],
  "threshold": 0.15,
  "expand_query": false
}
```

`categories` filters to specific categories. Omit to search all.

## Setup

### Prerequisites

- Python 3.11+
- Poetry
- PostgreSQL with pgvector (local: Docker; prod: GCP Cloud SQL)
- Voyage AI API key
- api-gateway running and accessible

### Local dev

```bash
# Install dependencies
poetry install

# Copy and fill in env vars
cp .env.example .env

# Start (with an empty API_KEY, set ALLOW_NO_AUTH=true first)
poetry run uvicorn app.main:app --reload
```

### Environment variables

| Variable | Description |
|----------|-------------|
| `API_KEY` | Key callers must send. Required: startup refuses an empty one. |
| `ALLOW_NO_AUTH` | Local dev only: `true` lets an empty `API_KEY` start, with every route open. |
| `DATABASE_URL` | PostgreSQL connection string (`postgresql+asyncpg://...`) |
| `VOYAGE_API_KEY` | Voyage AI key for embeddings and reranking |
| `API_GATEWAY_URL` | api-gateway base URL |
| `API_GATEWAY_KEY` | api-gateway API key (for outbound LLM calls) |

See `.env.example` for all available settings.

## Project structure

```
app/
  main.py          — FastAPI app, lifespan, router registration
  dependencies.py  — API key auth
  routes/
    health.py      — /health
    query.py       — /v1/kb/search, /v1/kb/stats
    ingest.py      — /v1/kb/ingest/*, /v1/kb/sources, /v1/kb/files
    llm.py         — /v1/chat/completions (RAG-injected)
    config.py      — /v1/config
core/
  config.py        — AppConfig (pydantic-settings)
  database.py      — asyncpg pool, schema init (kb_chunks + kb_sources)
rag/
  loader.py        — parse_content() for PDF/DOCX/XLSX/text
  pipeline.py      — ingest_document(): summarize, chunk, embed, upsert
  chunking.py      — Text chunking (langchain-text-splitters)
  embedder.py      — Voyage AI embeddings
  reranker.py      — Voyage AI reranking
  retriever.py     — Hybrid retrieval (dense + FTS → RRF → rerank)
llm/
  gateway.py       — LLM client (proxies to api-gateway /ai)
```

## Deployment

Deploys to GCP Cloud Run via GitHub Actions on push to `main` (`.github/workflows/deploy.yml`).

One-time GCP setup:
```bash
gcloud artifacts repositories create kb-service \
  --repository-format=docker \
  --location=us-central1
```

Add `GCP_PROJECT_ID` and `GCP_SA_KEY` secrets to the GitHub repo. Set env vars on the Cloud Run service in the GCP console.
