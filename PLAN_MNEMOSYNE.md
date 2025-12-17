# Project Mnemosyne: Advanced Memory & RAG Sytem

**Goal**: Transform the current basic RAG into an "Infinite Memory" system with dual-tier storage (Library vs. Journal), static user context (Profile), and advanced dynamic prompting.

## User Review Required
> [!IMPORTANT]
> **Model Selection (Locked In)**: 
> 1. **Library**: `nomic-embed-text-v1.5` (Deep knowledge, long context)
> 2. **Journal**: `BAAI/bge-small-en-v1.5` (Fast chat recall)

> [!NOTE]
> **Naming**: "Mnemosyne" was just a project codename (Greek goddess of memory). For the actual code/collections, we will use clear, boring names: `myai_library` and `myai_journal`.

## Architecture

### 1. The Model Registry
We will implement a unified `model_registry.json` (or config class) to manage all models with capability tags.
**Example Structure:**
```json
{
  "nomic-embed-text-v1.5": {
    "type": "embedding",
    "tags": ["library", "long-context", "gpu-preferred"],
    "dimension": 768
  },
  "bge-small-en-v1.5": {
    "type": "embedding",
    "tags": ["journal", "fast", "cpu-friendly"],
    "dimension": 384
  },
  "llama3.2": {
    "type": "llm",
    "tags": ["chat", "fast"],
    "provider": "ollama"
  }
}
```

### 2. Dual-Tier Memory & Payload Strategy

#### Tier 1: The Library (Documents)
*   **Storage**: `myai_library`
*   **Payload**: Stores `{ "text": "chunk content", "blob_id": "...", "page": 1 }`
*   **Linkage**: Linked to `library_blob` (renamed from `preindex_blob`) via `blob_id`.

#### Tier 2: The Journal (Chat History)
*   **Storage**: `myai_journal`
*   **Payload Strategy**: Full text stored in Qdrant payload.
    *   **Schema**:
        ```json
        {
          "role": "user",
          "content": "I prefer using PyTorch.",
          "session_id": "chat-123",
          "timestamp": "2024-10-10T10:00:00"
        }
        ```
    *   **Naming**: Sessions auto-named by LLM call, stored in SQL `sessions` table.

### 3. Context Injection Pipeline (Performance)
The pipeline adds ~20-50ms overhead (very fast):
1.  **System Prompt** (0ms)
2.  **User Profile** (0ms - Memory load)
3.  **The Library** (Query `myai_library`: ~20ms)
4.  **The Journal** (Query `myai_journal`: ~10ms)
5.  **Sliding Window** (0ms - Memory load)
**Total Overhead**: ~30-50ms. Negligible compared to LLM generation (1000ms+).

### 4. Stateless Mode (API Pass-through)
We will rename `use_rag` to `use_context` (keeping `use_rag` as an alias for backward compatibility).
*   **`use_context=True` (Default)**: Activates the full Mnemosyne pipeline (Profile + Library + Journal).
*   **`use_context=False`**: Bypasses everything. Returns a raw LLM response. Useful for generic API usage.

## Missing / Future Considerations
*   **Authentication**: Single User mode (You). `user_id` is simplified to "owner" or similar constant.
*   **Deployment**: This stack works perfectly on Proxmox (Docker VM/LXC) + Cloudflare Tunnel.
*   **Re-Ingest**: Script `scripts/ingest_library.py` needed to iterate `library_blob` and re-ingest entire library.
*   **Backup**: Qdrant snapshots should be automated.
*   **Safety**: `DELETE` endpoints for memory must require a confirmation flag (e.g., `?confirm=true`) to prevent accidental wiping.

## Proposed Changes

### Core Infrastructure
#### [NEW] [core/model_registry.py](file:///c:/Users/aatha/Desktop/Local%20Git%20Repositories/MY-AI/MY-AI/core/model_registry.py)
*   Class to manage models and their capability tags.
*   Helper methods: `get_model_for_task("library")`, `get_model_for_task("journal")`.

#### [MODIFY] [core/file_storage.py](file:///c:/Users/aatha/Desktop/Local%20Git%20Repositories/MY-AI/MY-AI/core/file_storage.py)
*   Rename `preindex_blob` -> `library_blob` (folder and config variables).

#### [MODIFY] [core/config.py](file:///c:/Users/aatha/Desktop/Local%20Git%20Repositories/MY-AI/MY-AI/core/config.py)
*   Add `hardware_mode` config (`gpu` vs `cpu`).
*   Integrate model registry settings.
*   Rename RAG settings to Context settings (with aliases).
*   Rename `blob_storage_path` default to `./data/library_blob`.

### Data & Memory
#### [NEW] [rag/journal.py](file:///c:/Users/aatha/Desktop/Local%20Git%20Repositories/MY-AI/MY-AI/rag/journal.py)
*   `JournalManager`: Handles embedding and storing chat turns.
*   `generate_session_name(messages)`: LLM helper to name sessions.

#### [MODIFY] [rag/rag_setup.py](file:///c:/Users/aatha/Desktop/Local%20Git%20Repositories/MY-AI/MY-AI/rag/rag_setup.py)
*   Refactor `BasicRAG` to `ContextEngine`.
*   Support multiple retrievers.

#### [MODIFY] [app/routes/llm.py](file:///c:/Users/aatha/Desktop/Local%20Git%20Repositories/MY-AI/MY-AI/app/routes/llm.py)
*   Accept `use_context` parameter.

### Endpoints
#### [NEW] [app/routes/profile.py](file:///c:/Users/aatha/Desktop/Local%20Git%20Repositories/MY-AI/MY-AI/app/routes/profile.py)
*   `GET /v1/profile`: Get user profile data.
*   `PATCH /v1/profile`: Update user profile data.

#### [NEW] [app/routes/memory.py](file:///c:/Users/aatha/Desktop/Local%20Git%20Repositories/MY-AI/MY-AI/app/routes/memory.py)
*   `GET /v1/memory/sessions`: List all named sessions.
*   `DELETE /v1/memory/sessions/{id}`: Delete a session memory (Protected).
*   `DELETE /v1/memory`: Clear all journal memory (Protected).

#### [MODIFY] [app/routes/ingest.py](file:///c:/Users/aatha/Desktop/Local%20Git%20Repositories/MY-AI/MY-AI/app/routes/ingest.py)
*   `POST /v1/ingest/file/{filename}`: Manually trigger ingestion for a file already in `preindex_blob`.
*   *Use Case*: User uploads file via SCP/FTP/Blobs UI, then clicks "Ingest" in frontend.
*   `GET /v1/profile`: Get user profile data.
*   `PATCH /v1/profile`: Update user profile data.

#### [NEW] [app/routes/memory.py](file:///c:/Users/aatha/Desktop/Local%20Git%20Repositories/MY-AI/MY-AI/app/routes/memory.py)
*   `GET /v1/memory/sessions`: List all named sessions.
*   `DELETE /v1/memory/sessions/{id}`: Delete a session memory.
*   `DELETE /v1/memory`: Clear all journal memory.
