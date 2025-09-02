# Personal AI — Software Development Path (Tier‑2, Local‑First)

> **Scope:** Software only. Local-first models via LLM Gateway; no hardware here. Keep it conceptual and implementation-agnostic.

---

## Step 0 — Planning (Contracts & Guardrails)

* Define **surfaces** (LLM Gateway, Personal API).
* Fix I/O shapes: Gateway = `/v1/chat`, `/v1/embeddings`; Personal API = `/v1/query`, `/v1/ingest`, `/v1/tools/run` (internal).
* Tier‑2 routing policy: one Gateway call → `{tool, args}` JSON; validate schema; fallback to `rag_answer` after one clarifying question.
* Allowlist staged: v0 = `rag_answer`, `drive_search`, `web_search`; v1 = `calendar_lookup`; v2 = `spotify_lookup`, `banking_readonly`.
* Guardrails: no loops; summarization toggleable per request; short‑term memory only at first.

**Outcome:** Contracts and policies locked before scaffolding.

---

## Step 1 — Scaffolding (Personal API Skeleton)

* Repo layout: `apps/api`, `packages/core`, `packages/rag`, `packages/llms`, `packages/agents`, `packages/connectors`.
* `/v1/query` returns placeholder `answer|data`, empty `citations`, empty `transcript`.
* Add health check endpoint.
* Stubs for RAG, tools, router.

**Outcome:** Running API scaffold with fixed response envelope.

---

## Step 2 — Local LLM Gateway

* Stand up local model service (e.g., Ollama/vLLM) behind Gateway with `/v1/chat` and `/v1/embeddings`.
* Config flag to swap between local and cloud.
* No business logic.

**Outcome:** Personal API can call Gateway and get text/embeddings back.

---

## Step 3 — RAG MVP (Read‑Only Corpus)

* **Ingest:** loaders → chunk → embed (via Gateway) → store (SQLite + FAISS/sqlite‑vec).
* **Query:** embed query → retrieve (BM25 + vectors) → extractive compose with citations.
* Optional summarization if `summarize=true`.

**Outcome:** `/v1/query` returns cited answers from seed corpus. No tools yet.

---

## Step 4 — Tier‑2 Router (AI‑Assisted)

* Gateway call: map user text → `{tool, args}` or `rag_answer`.
* Validate plan; invalid → one clarifying question → fallback to `rag_answer`.
* Optional summarization if flag set.

**Outcome:** Natural queries route correctly; bounded to 1–2 Gateway calls.

---

## Step 5 — First Tools (Read‑Only)

* Implement `drive_search`, `web_search`, then `calendar_lookup`.
* All read‑only; return normalized outputs.
* Log transcripts of tool calls (inputs/outputs, duration).

**Outcome:** Tools execute end‑to‑end with transcripts; still bounded call counts.

---

## Step 6 — Memory (Short‑Term First)

* Add **session memory**: rolling window of recent turns.
* Store locally (SQLite/disk); purgeable.
* Use memory as extra context to RAG or router; always cite source.
* Plan for later long‑term memory (condensed notes/embeddings).

**Outcome:** Short‑term memory active across a session; design ready for future long‑term condensation.

---

## Step 7 — Mutable Corpus (AI‑Proposed, Human‑Approved)

* Allow ingest updates via diff proposals: add/update/delete docs/chunks.
* AI/tools propose diffs; human approves before commit.
* Approved diffs → (re)chunk → (re)embed via Gateway → upsert store.

**Outcome:** Knowledge base can be maintained dynamically with provenance and human approval.

---

## Observability & Safeguards (continuous)

* Metrics: latency, tokens, Gateway calls, retrieval hit rate.
* Evals: small golden Q/A set for RAG correctness and citation accuracy.
* Policies: allowlists, schema enforcement, per‑tool budgets, feature flags for deferred tools.

---
