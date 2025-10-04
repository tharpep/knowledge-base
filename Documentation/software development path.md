# Personal AI — Software Development Path (Tier‑2, Local‑First)

> **Scope:** Software only. Local-first models via LLM Gateway; no hardware here. Keep it conceptual and implementation-agnostic.

---

## Step 0 — Planning (Contracts & Guardrails)

* Define **unified API surface** (Personal AI Assistant API).
* Fix I/O shapes: OpenAI-compatible endpoints (`/v1/chat/completions`, `/v1/embeddings`, `/v1/models`) + RAG endpoints (`/v1/query`, `/v1/ingest`, `/v1/stats`).
* Tier‑2 routing policy: internal LLM Gateway class calls → `{tool, args}` JSON; validate schema; fallback to `rag_answer` after one clarifying question.
* Allowlist staged: v0 = `rag_answer`, `drive_search`, `web_search`; v1 = `calendar_lookup`; v2 = `spotify_lookup`, `banking_readonly`.
* Guardrails: no loops; summarization toggleable per request; short‑term memory only at first.

**Outcome:** Contracts and policies locked before scaffolding.

---

## Step 1 — Scaffolding (Unified API Skeleton)

* Repo layout: `app/`, `llm/`, `rag/`, `core/`, `agents/`, `connectors/`.
* `/v1/query` returns placeholder `answer|data`, empty `citations`, empty `transcript`.
* Add health check endpoint.
* Stubs for RAG, tools, router.

**Outcome:** Running unified API scaffold with fixed response envelope.

---

## Step 2 — LLM Gateway Integration

* Integrate LLM Gateway class (AIGateway) into unified API.
* Support local models (Ollama) and cloud fallback (Purdue GenAI Studio).
* OpenAI-compatible endpoints (`/v1/chat/completions`, `/v1/embeddings`, `/v1/models`).
* No business logic in Gateway - pure AI functionality.

**Outcome:** Unified API can generate text/embeddings via integrated Gateway.

---

## Step 3 — RAG MVP (Read‑Only Corpus)

* **Ingest:** loaders → chunk → embed (via integrated Gateway) → store (Qdrant vector database).
* **Query:** embed query → retrieve (similarity search) → generate answer with citations.
* **Document ingestion:** Documents become searchable knowledge base for RAG queries.
* Optional summarization if `summarize=true`.

**Outcome:** `/v1/query` returns cited answers from ingested document corpus. No tools yet.

---

## Step 4 — Smart Chatbot Integration (AI‑Assisted)

* **Intent analysis** - Analyze user messages to determine if RAG context is needed
* **Smart routing** - Chatbot automatically uses RAG when appropriate
* **Seamless experience** - User doesn't need to choose between RAG and pure AI
* Internal Gateway call: map user text → `{tool, args}` or `rag_answer`.
* Validate plan; invalid → one clarifying question → fallback to `rag_answer`.
* Optional summarization if flag set.

**Outcome:** Intelligent chatbot that automatically uses document context when relevant; bounded to 1–2 internal Gateway calls.

---

## Step 5 — First Tools (Read‑Only)

* Implement `drive_search`, `web_search`, then `calendar_lookup`.
* All read‑only; return normalized outputs.
* Log transcripts of tool calls (inputs/outputs, duration).

**Outcome:** Tools execute end‑to‑end with transcripts; still bounded call counts.

---

## Step 6 — Hybrid Memory System (RAG + Persistent + Context)

* **RAG Layer**: Document-based knowledge (already implemented)
* **Persistent Memory**: Personal facts, preferences, conversation history
* **Context Awareness**: Current session state and conversation flow
* **Smart Integration**: Intent analysis determines which memory layer(s) to use
* Store locally (SQLite/disk); purgeable and configurable.

**Outcome:** Three-layer memory system active - RAG for documents, persistent for personal facts, context for session flow.

---

## Step 7 — Mutable Corpus (AI‑Proposed, Human‑Approved)

* Allow ingest updates via diff proposals: add/update/delete docs/chunks.
* AI/tools propose diffs; human approves before commit.
* Approved diffs → (re)chunk → (re)embed via Gateway → upsert store.

**Outcome:** Knowledge base can be maintained dynamically with provenance and human approval.

---

## Step 8 — Cloud Deployment (Your Own Cloud)

* **Docker deployment** - Build and deploy to your chosen cloud platform
* **Environment configuration** - Switch between local and cloud settings
* **Persistent storage** - Document corpus and vector database in cloud
* **Access anywhere** - Phone, laptop, work computer access
* **Hybrid workflow** - Local development, cloud production

**Outcome:** Personal AI assistant accessible anywhere while maintaining privacy and control.

---

## Observability & Safeguards (continuous)

* Metrics: latency, tokens, Gateway calls, retrieval hit rate.
* Evals: small golden Q/A set for RAG correctness and citation accuracy.
* Policies: allowlists, schema enforcement, per‑tool budgets, feature flags for deferred tools.

---
