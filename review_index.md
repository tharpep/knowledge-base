# AI Slop Index

## Category 1: Verbose Docstrings on Simple Methods ✅ COMPLETED

**Status:** All Category 1 files have been cleaned up. Docstrings now follow:
- Public methods: One-line docstrings
- Private methods: Docstrings removed entirely
- Class docstrings: Brief and concise

### `core/services/chat_service.py`
- Line 23: `ChatMessageResult` - verbose class docstring for simple dataclass
- Line 48-55: `__init__` - verbose docstring with Args/Returns for simple initializer
- Line 61-95: `prepare_chat_message` - overly detailed docstring with numbered steps
- Line 199-213: `_retrieve_library_context` - verbose docstring with "Strategies:" section
- Line 252-262: `_retrieve_library_direct` - verbose docstring for simple wrapper
- Line 289-298: `_get_cached_context` - verbose docstring for simple cache lookup
- Line 329-336: `_cache_context` - verbose docstring for simple cache set
- Line 351-360: `_format_context_text` - verbose docstring for simple join
- Line 370-382: `_format_user_message` - verbose docstring with unused parameter note
- Line 408-427: `_retrieve_journal_context` - verbose docstring with "Now uses..." note
- Line 461-475: `_merge_context` - verbose docstring for simple string merge

### `rag/retriever.py`
- Line 16-21: `__init__` - verbose docstring for simple initializer
- Line 41-50: `encode_documents` - verbose docstring for simple encode call
- Line 54-63: `encode_query` - verbose docstring for simple encode call
- Line 67-80: `create_points` - verbose docstring with detailed parameter descriptions
- Line 100-107: `get_embedding_dimension` - verbose docstring for property access
- Line 109-115: `get_model_info` - verbose docstring for simple dict return

### `rag/document_ingester.py`
- Line 16-22: `__init__` - verbose docstring for simple initializer
- Line 26-35: `ingest_file` - verbose docstring with Returns dict structure
- Line 74-83: `ingest_folder` - verbose docstring with Returns dict structure
- Line 118-127: `_preprocess_text` - verbose docstring for simple text clean
- Line 136-147: `_chunk_text` - verbose docstring for simple chunking function
- Line 175-184: `get_supported_files` - verbose docstring for simple glob

### `llm/gateway.py`
- Line 15-24: `load_env_file` - verbose docstring for simple env loader
- Line 32-39: `__init__` - verbose docstring with detailed config description
- Line 78-91: `chat` - verbose docstring with detailed Args/Returns
- Line 141-151: `embeddings` - verbose docstring for simple async call

### `agents/router.py`
- Line 14-22: `ToolRouter` - verbose class docstring with bullet points
- Line 24-30: `__init__` - verbose docstring for simple initializer
- Line 41-61: `route` - verbose docstring with detailed Returns dict structure
- Line 91-105: `validate_tool_plan` - verbose docstring for simple validation

### `agents/base_tool.py`
- Line 45-54: `BaseTool` - verbose class docstring with implementation checklist
- Line 78-89: `execute` - verbose docstring for abstract method
- Line 91-99: `get_schema` - verbose docstring for abstract method
- Line 101-110: `validate_parameters` - verbose docstring for simple validation

### `agents/tool_registry.py`
- Line 14-23: `ToolRegistry` - verbose class docstring with bullet points
- Line 30-39: `register` - verbose docstring with Raises section
- Line 46-56: `get_tool` - verbose docstring for simple dict.get
- Line 58-64: `get_available_tools` - verbose docstring for simple filter
- Line 70-76: `set_allowlist` - verbose docstring for simple setter
- Line 86-95: `is_allowed` - verbose docstring for simple check
- Line 102-121: `execute_tool` - verbose docstring with Raises section

### `core/file_storage.py`
- Line 35-41: `BlobStorage` - verbose class docstring with implementation details
- Line 43-49: `__init__` - verbose docstring for simple initializer
- Line 53-55: `_ensure_storage_exists` - verbose docstring for mkdir
- Line 57-59: `_generate_blob_id` - verbose docstring for uuid generation
- Line 61-63: `_get_manifest_path` - verbose docstring for Path construction
- Line 65-67: `_load_manifest` - verbose docstring for json.load
- Line 76-78: `_save_manifest` - verbose docstring for json.dump
- Line 82-92: `save` - verbose docstring with detailed Returns
- Line 121-130: `get` - verbose docstring for simple path lookup
- Line 141-150: `get_info` - verbose docstring for simple dict lookup
- Line 158-164: `list` - verbose docstring for simple list comprehension
- Line 168-177: `delete` - verbose docstring for simple delete
- Line 214-233: `JournalBlobStorage` - verbose class docstring with implementation details
- Line 235-241: `__init__` - verbose docstring for simple initializer
- Line 245-247: `_ensure_storage_exists` - verbose docstring for mkdir
- Line 249-251: `_get_session_path` - verbose docstring for Path construction
- Line 253-266: `export_session` - verbose docstring with detailed Args structure
- Line 283-292: `get_session` - verbose docstring for simple json.load
- Line 304-313: `exists` - verbose docstring for simple path.exists
- Line 316-325: `delete_session` - verbose docstring for simple unlink
- Line 334-340: `list_sessions` - verbose docstring for simple glob
- Line 365-378: `get_session_text` - verbose docstring with formatting details

### `core/session_store.py`
- Line 22-31: `SessionStore` - verbose class docstring with implementation details
- Line 39-40: `_init_db` - verbose docstring for table creation
- Line 90-92: `_get_connection` - verbose docstring for context manager
- Line 107-114: `upsert_session` - verbose docstring for simple upsert
- Line 142-143: `increment_message_count` - verbose docstring for simple increment
- Line 152-153: `set_session_name` - verbose docstring for simple update
- Line 161-162: `get_session` - verbose docstring for simple select
- Line 169-170: `list_sessions` - verbose docstring for simple query
- Line 180-181: `delete_session` - verbose docstring for simple delete
- Line 195-213: `add_message` - verbose docstring with detailed Returns
- Line 231-240: `get_messages` - verbose docstring for simple query
- Line 254-263: `get_session_with_messages` - verbose docstring for simple join
- Line 271-282: `get_first_user_message` - verbose docstring with "Used for..." note
- Line 297-306: `delete_messages` - verbose docstring for simple delete
- Line 320-327: `set_ingested_at` - verbose docstring for simple update
- Line 339-345: `clear_ingested_at` - verbose docstring for simple update
- Line 354-367: `has_new_messages_since_ingest` - verbose docstring with "Returns True if:" list
- Line 389-400: `get_sessions_needing_ingest` - verbose docstring with "Useful for..." note

### `core/profile_manager.py`
- Line 38-42: `ProfileManager` - verbose class docstring with file path details
- Line 49-50: `_ensure_data_dir` - verbose docstring for mkdir
- Line 54-58: `get_profile` - verbose docstring with "Returns default..." note
- Line 69-73: `update_profile` - verbose docstring with merge details

### `rag/vector_store.py`
- Line 17-25: `__init__` - verbose docstring with detailed parameter descriptions
- Line 53-63: `setup_collection` - verbose docstring for simple create
- Line 83-93: `add_points` - verbose docstring for simple upsert
- Line 101-112: `search` - verbose docstring for simple query
- Line 125-134: `get_collection_stats` - verbose docstring for simple info call
- Line 146-155: `delete_collection` - verbose docstring for simple delete
- Line 163-169: `list_collections` - verbose docstring for simple list
- Line 177-187: `clear_collection` - verbose docstring with dimension note
- Line 208-214: `cleanup_old_collections` - verbose docstring for simple cleanup

### `llm/providers/anthropic.py`
- Line 14-24: `load_env_file` - verbose docstring for simple env loader
- Line 31-37: `__init__` - verbose docstring with detailed API key description
- Line 57-67: `chat` - verbose docstring with detailed model note
- Line 146-152: `get_available_models` - verbose docstring for hardcoded list

### `llm/providers/purdue.py`
- Line 14-24: `load_env_file` - verbose docstring for simple env loader
- Line 31-37: `__init__` - verbose docstring with detailed API key description
- Line 55-65: `chat` - verbose docstring for simple API call

### `llm/local.py`
- Line 1-21: Module docstring - overly detailed architecture explanation
- Line 45-51: `OllamaClient` - verbose class docstring with usage example
- Line 79-81: `_ensure_sync_client` - verbose docstring for client init
- Line 93-94: `_ensure_client` - verbose docstring with "(for future async usage)" note
- Line 107-115: `chat` - verbose docstring for simple API call
- Line 151-152: `health_check` - verbose docstring with "(synchronous)" note
- Line 161-167: `_check_ollama_health` - verbose docstring with detailed Returns
- Line 182-183: `get_available_models` - verbose docstring with "(synchronous, required by...)" note

### `rag/rag_setup.py`
- Line 1-5: Module docstring - verbose with "formerly RAG System Orchestrator" note
- Line 14-20: `ContextEngine` - verbose class docstring with dual-tier explanation
- Line 22-30: `__init__` - verbose docstring with detailed parameter descriptions
- Line 79-89: `add_documents` - verbose docstring with metadata example
- Line 99-109: `search` - verbose docstring for simple search
- Line 120-138: `get_context_for_chat` - verbose docstring with detailed filtering explanation

### `rag/journal.py` (Additional findings)
- Line 1-9: Module docstring - overly detailed architecture explanation
- Line 25-30: `JournalEntry` - verbose class docstring for simple schema
- Line 37-42: `JournalChunkPayload` - verbose class docstring for simple schema
- Line 52-58: `JournalManager` - verbose class docstring with implementation details
- Line 60-67: `__init__` - verbose docstring with Args section
- Line 112-129: `ingest_session` - verbose docstring with numbered pipeline steps and detailed Args/Returns

### `rag/workers.py` (Additional findings)
- Line 1-4: Module docstring - brief but could be simpler
- Line 12-25: `process_document` - verbose docstring with pipeline explanation and Args/Returns
- Line 103-104: `_get_worker_settings` - verbose docstring for simple function
- Line 114: `WorkerSettings` - verbose class docstring

## Category 2: Unnecessary Comments and Notes ✅ COMPLETED

### `core/services/chat_service.py`
- Line 43: `# Class-level cache shared across all instances (for API multi-request scenarios)` - implementation detail comment
- Line 45: `# Keep last 20 queries` - obvious comment
- Line 57: `# Support both old (rag_instance) and new (context_engine) parameter names` - migration note
- Line 59: `# Lazy-loaded from context_engine` - obvious comment
- Line 96: `# Master switch check` - obvious comment
- Line 98: `# Context disabled - return un-augmented message` - obvious comment
- Line 113: `# Use provided values or fall back to config` - obvious comment
- Line 129: `# Timing for Library retrieval` - obvious comment
- Line 132: `# Retrieve Library context if enabled` - obvious comment
- Line 142: `# Timing for Journal retrieval` - obvious comment
- Line 145: `# Retrieve Journal context if enabled` - obvious comment
- Line 155: `# Timing for prompt formatting` - obvious comment
- Line 158: `# Merge context from both sources` - obvious comment
- Line 164: `# Format the user message with merged context if available` - obvious comment
- Line 214: `# Strategy 1: Check context cache` - obvious comment
- Line 224: `# Strategy 2: Direct query retrieval` - obvious comment
- Line 231: `# Cache results for future use` - obvious comment
- Line 235: `# Format context text` - obvious comment
- Line 264: `# Use pre-initialized context engine if available` - obvious comment
- Line 272: `# Retrieve Library context` - obvious comment
- Line 302: `# Normalize query for matching (lowercase, strip)` - obvious comment
- Line 306: `# Check recent cache entries first (most likely to match)` - obvious comment
- Line 307: `# Limit to last 5 entries for performance` - obvious comment
- Line 313: `# Calculate Jaccard similarity (intersection over union)` - obvious comment
- Line 319: `# If >50% keyword overlap, reuse cached context` - obvious comment
- Line 323: `# Move to end (most recently used)` - obvious comment
- Line 337: `# Normalize query for consistent caching` - obvious comment
- Line 340: `# Keep cache size manageable` - obvious comment
- Line 342: `# Remove oldest entry (FIFO)` - obvious comment
- Line 345: `# Store results` - obvious comment
- Line 348: `# Move to end (most recently used)` - obvious comment
- Line 383: `# Format with context clearly separated` - obvious comment
- Line 385: `# Use custom template` - obvious comment
- Line 393: `# Use default: make user question prominent, context as reference` - obvious comment
- Line 405: `# No RAG context - return plain user message` - obvious comment
- Line 429: `# Get Journal from ContextEngine` - obvious comment
- Line 438: `# Use unified interface (same as Library)` - obvious comment
- Line 439: `# Uses config default similarity threshold` - obvious comment
- Line 446: `# Always search all sessions, not just current` - obvious comment
- Line 452: `# Format context text (same pattern as Library)` - obvious comment
- Line 478: `# Add session context header` - obvious comment
- Line 390: `# Format messages` - obvious comment

### `rag/document_ingester.py`
- Line 44: `# Read file content` - obvious comment
- Line 49: `# Basic preprocessing` - obvious comment
- Line 52: `# Chunk long documents using config values` - obvious comment
- Line 61: `# Index chunks` - obvious comment
- Line 97: `# Find all supported files` - obvious comment
- Line 128: `# Remove extra whitespace` - obvious comment
- Line 131: `# Remove empty lines` - obvious comment
- Line 157: `# Try to break at sentence boundary` - obvious comment
- Line 159: `# Look for sentence endings` - obvious comment

### `llm/gateway.py`
- Line 14: `# Load environment variables from .env file` - obvious comment
- Line 44: `# Setup Anthropic/Claude provider` - obvious comment
- Line 55: `# Setup Purdue provider` - obvious comment
- Line 64: `# Setup Local Ollama provider` - obvious comment
- Line 92: `# Auto-select provider based on availability (prioritize Anthropic)` - obvious comment
- Line 94: `# Prioritize Anthropic if available (preferred default)` - obvious comment
- Line 97: `# Fallback to config default` - obvious comment
- Line 100: `# Additional fallback logic` - obvious comment
- Line 116: `# Handle different provider types` - obvious comment
- Line 120: `# Use provider-specific default model if no model specified` - obvious comment
- Line 123: `# For non-Ollama providers, use messages array if provided, otherwise use message string` - obvious comment
- Line 130: `# Helper to handle Ollama calls` - obvious comment
- Line 131: `# If messages array provided, use it; otherwise use single message string` - obvious comment
- Line 152: `# Use Ollama for embeddings if available` - obvious comment

### `agents/router.py`
- Line 62: `# For now, return simple routing logic` - TODO-style comment
- Line 68: `# Simple heuristic: if message contains question words, use RAG` - obvious comment
- Line 74: `# Default to RAG answer if it's available and looks like a question` - obvious comment
- Line 83: `# Otherwise, direct AI response` - obvious comment
- Line 122: `# Check if tool exists` - obvious comment
- Line 130: `# Check if tool is allowed` - obvious comment
- Line 137: `# Validate parameters if requested` - obvious comment
- Line 146: `# Execute tool` - obvious comment
- Line 153: `# Add execution time if not already set` - obvious comment

### `core/file_storage.py`
- Line 19: `# Default blob storage directories` - obvious comment
- Line 88: `# Add any extra metadata (like blob_id)` - obvious comment
- Line 96: `# Create blob info` - obvious comment
- Line 104: `# Update manifest` - obvious comment
- Line 183: `# Delete file` - obvious comment
- Line 187: `# Remove from manifest` - obvious comment
- Line 195: `# Singleton instance for convenience` - obvious comment
- Line 209: `# =============================================================================` - separator comment
- Line 210: `# Journal Blob Storage - For exported chat sessions` - obvious comment
- Line 211: `# =============================================================================` - separator comment
- Line 343: `# Skip manifest files` - obvious comment
- Line 361: `# Sort by exported_at descending` - obvious comment
- Line 385: `# Add session context header` - obvious comment
- Line 390: `# Format messages` - obvious comment
- Line 399: `# Singleton instance for journal blob storage` - obvious comment

### `core/session_store.py`
- Line 18: `# Database file path` - obvious comment
- Line 44: `# Sessions table` - obvious comment
- Line 67: `# Messages table` - obvious comment
- Line 60: `# Migration: Add ingested_at column if it doesn't exist` - migration note
- Line 120: `# Check if session exists` - obvious comment
- Line 125: `# Update last_activity` - obvious comment
- Line 134: `# Insert new session` - obvious comment
- Line 184: `# Delete messages first (foreign key)` - obvious comment
- Line 186: `# Delete session` - obvious comment
- Line 191: `# =========================================================================` - separator comment
- Line 192: `# Message Methods` - obvious comment
- Line 193: `# =========================================================================` - separator comment
- Line 316: `# =========================================================================` - separator comment
- Line 317: `# Ingestion Tracking Methods` - obvious comment
- Line 318: `# =========================================================================` - separator comment
- Line 372: `# No messages = nothing to ingest` - obvious comment
- Line 378: `# Never ingested but has messages` - obvious comment
- Line 382: `# Compare timestamps` - obvious comment

### `rag/vector_store.py`
- Line 32: `# Connect to Qdrant server (supports multi-process access)` - implementation detail
- Line 34: `# Test connection` - obvious comment
- Line 189: `# Delete the entire collection` - obvious comment
- Line 193: `# Recreate the collection immediately` - obvious comment

### `llm/providers/anthropic.py`
- Line 13: `# Load environment variables from .env file` - obvious comment
- Line 41: `# Try multiple environment variable names for flexibility` - obvious comment
- Line 52: `# Get default model from config` - obvious comment
- Line 68: `# Handle both string and list formats` - obvious comment
- Line 70: `# Convert single string to messages format` - obvious comment
- Line 72: `# Ensure all messages have the right format` - obvious comment
- Line 76: `# Anthropic uses 'user' and 'assistant' roles` - obvious comment
- Line 79: `# Anthropic handles system messages differently` - obvious comment
- Line 80: `# Skip system messages for now` - obvious comment
- Line 93: `# Extract system message if present (Anthropic handles it separately)` - obvious comment
- Line 97: `# Filter out system messages from conversation (Anthropic handles them separately)` - obvious comment
- Line 105: `# Prepare request with full conversation history` - obvious comment
- Line 112: `# Add system message if provided` - obvious comment
- Line 116: `# Make API request` - obvious comment
- Line 130: `# Extract text from response` - obvious comment
- Line 147: `# Get list of available Anthropic models (latest versions only)` - obvious comment

### `llm/providers/purdue.py`
- Line 13: `# Load environment variables from .env file` - obvious comment
- Line 41: `# Try multiple environment variable names for flexibility` - obvious comment
- Line 51: `# Get default model from config` - obvious comment
- Line 66: `# Use default model if none specified` - obvious comment
- Line 70: `# Handle both string and message list formats` - obvious comment
- Line 90: `# Make request` - obvious comment
- Line 108: `# Get list of available models (hardcoded for Purdue)` - obvious comment

### `llm/local.py`
- Line 40: `# Increased timeout for complex queries` - obvious comment
- Line 57: `# Separate clients for sync and async usage` - obvious comment
- Line 61: `# Check if Ollama is running during initialization` - obvious comment
- Line 75: `# Cleanup sync client on destruction` - obvious comment

## Category 3: AI-Generated Patterns and Weird Notes ✅ COMPLETED

### `core/services/chat_service.py`
- Line 27: `# Journal (chat history) results - now matches Library format` - migration note
- Line 377: `# Format user message with optional RAG context.` - trailing period in docstring
- Line 377: Empty line in docstring

### `llm/local.py`
- Line 1-21: Entire module docstring is overly detailed architecture explanation
- Line 40: `# Increased timeout for complex queries` - comment explaining a default value

### `rag/rag_setup.py`
- Line 1: `# Context Engine (formerly RAG System Orchestrator)` - migration note in docstring

### `core/file_storage.py`
- Line 209-211: Separator comments with equals signs (AI pattern)

### `core/session_store.py`
- Line 191-193, 316-318: Separator comments with equals signs (AI pattern)

## Category 4: Missing TODOs

### `agents/router.py`
- Line 63: `# TODO: Implement LLM-based intent analysis in future phase` - only TODO found

## Category 5: Weird Notes and AI Patterns ✅ COMPLETED

### `core/config.py`
- Line 44-47: Commented-out model list with "Previously tested Ollama models (commented for reference):" - reference note
- Line 227: Duplicate section header `# ===== Document Source Configuration =====`

### `llm/gateway.py`
- Line 15-24: `load_env_file()` function with verbose docstring - should use python-dotenv

### `llm/providers/anthropic.py`
- Line 14-24: `load_env_file()` function with verbose docstring - should use python-dotenv

### `llm/providers/purdue.py`
- Line 14-24: `load_env_file()` function with verbose docstring - should use python-dotenv

### `core/services/chat_service.py`
- Line 377: Empty line in middle of docstring (formatting issue)

---

## Summary Statistics

- Total files reviewed: 35+
- **Category 1 (Verbose Docstrings):** ✅ COMPLETED - All 17 files cleaned (15 original + 2 additional)
- **Category 2 (Unnecessary Comments):** ✅ COMPLETED - All obvious comments removed from listed files
- **Category 3 (AI-Generated Patterns):** ✅ COMPLETED - Separator comments removed, migration notes cleaned
- **Category 5 (Weird Notes):** ✅ COMPLETED - Commented-out code removed, duplicate headers fixed, load_env_file replaced with python-dotenv
- **Additional Findings:** ✅ COMPLETED - All 6 additional files cleaned (~55+ issues total)
- Unnecessary comments: ~100+ (cleaned)
- AI-generated patterns: ~15 (cleaned)
- Missing TODOs: 1 (router.py - deferred)
- Weird notes: ~10 (cleaned)

**Additional Findings:**
- ✅ `rag/document_parser.py` - ~10+ issues → ✅ CLEANED
- ✅ `core/model_registry.py` - ~5+ issues → ✅ CLEANED
- ✅ `llm/base_client.py` - ~5+ issues → ✅ CLEANED
- ✅ `core/queue.py` - ~10+ issues → ✅ CLEANED
- ✅ `core/utils/logging_config.py` - ~10+ issues → ✅ CLEANED
- ✅ `agents/tools/rag_answer.py` - ~15+ issues → ✅ CLEANED

**Excluded Files (per user instructions):**
- `app/routes/*.py` files: ~80+ verbose docstrings and obvious comments (excluded)
- `app/main.py`: ~20+ verbose docstrings and obvious comments (excluded)
- `app/db.py`: ~15+ verbose docstrings and obvious comments (excluded)

**Most common issues:**
1. ✅ Verbose docstrings on simple getters/setters/initializers - **FIXED**
2. Obvious comments explaining what the code does
3. Implementation detail comments that don't add value
4. Separator comments with equals signs
5. Migration/backward compatibility notes in docstrings

**Files with most issues (before cleanup):**
1. `core/services/chat_service.py` - 50+ issues → ✅ Cleaned
2. `core/file_storage.py` - 30+ issues → ✅ Cleaned
3. `core/session_store.py` - 25+ issues → ✅ Cleaned
4. `rag/document_ingester.py` - 20+ issues → ✅ Cleaned
5. `agents/tool_registry.py` - 15+ issues → ✅ Cleaned

**Additional files cleaned up:**
- `rag/journal.py` - ✅ Cleaned (6+ verbose docstrings removed)
- `rag/workers.py` - ✅ Cleaned (3+ verbose docstrings removed)
- `rag/document_parser.py` - ✅ Cleaned (10+ issues)
- `core/model_registry.py` - ✅ Cleaned (5+ issues)
- `llm/base_client.py` - ✅ Cleaned (5+ issues)
- `core/queue.py` - ✅ Cleaned (10+ issues)
- `core/utils/logging_config.py` - ✅ Cleaned (10+ issues)
- `agents/tools/rag_answer.py` - ✅ Cleaned (15+ issues)

**Note:** Endpoint routes (`app/routes/*.py`), `main.py`, `db.py`, and `config.py` were excluded from Category 1 cleanup per user instructions, though they contain many verbose docstrings. These are documented in the "Additional Findings" section above.

---

## Additional Findings (Not Yet Cleaned - Excluded Files)

### `app/routes/llm.py`
- Line 1-19: Very verbose module docstring with detailed endpoint descriptions
- Line 37: Separator comment `# ===== Request/Response Models =====`
- Line 69: Separator comment `# ===== Session Management Helpers =====`
- Line 78-94: `_handle_session_management` - verbose docstring with numbered steps and detailed Args/Returns
- Line 128-136: `_maybe_auto_ingest_session` - verbose docstring with detailed Args
- Line 158-168: `_maybe_auto_name_session` - verbose docstring with detailed Args
- Line 191: Separator comment `# ===== Chat Completions Endpoint =====`
- Line 347-349: Separator comment block `# =========================================================================`
- Line 364: Comment `# Note: If provider_used is None, gateway auto-selected based on config/fallback`
- Line 613: Separator comment `# ===== Embeddings Endpoint =====`
- Line 718: Separator comment `# ===== Models Endpoint =====`

### `app/routes/ingest.py`
- Line 1: Verbose module docstring
- Line 17-32: `ingest_documents` - verbose docstring with detailed Args/Returns structure
- Line 111-125: `upload_document` - verbose docstring with detailed Args/Returns
- Line 207-220: `ingest_manual_file` - verbose docstring with numbered list of capabilities
- Line 231, 236, 251: Strategy comments `# Strategy 1:`, `# Strategy 2:`, `# Strategy 3:`
- Line 322-330: `get_job_status` - verbose docstring with detailed Args/Returns
- Line 378-384: `list_blobs` - verbose docstring
- Line 424-432: `delete_blob` - verbose docstring with detailed Args/Returns
- Line 478-483: `get_indexed_stats` - verbose docstring
- Line 519-526: `clear_all_indexed` - verbose docstring with detailed Args/Returns
- Line 586-591: `list_indexed_files` - verbose docstring
- Line 623-631: `delete_indexed_file` - verbose docstring with detailed Args/Returns

### `app/routes/query.py`
- Line 1-6: Verbose module docstring
- Line 15: Separator comment `# ===== Library Statistics Endpoint =====`

### `app/routes/memory.py`
- Line 1: Verbose module docstring
- Line 15-16: `_generate_request_id` - verbose docstring for simple function
- Line 23-31: `list_sessions` - verbose docstring with detailed Returns structure
- Line 63-73: `get_session_messages` - verbose docstring with "Used by frontend..." note and detailed Args/Returns
- Line 136-150: `ingest_session` - verbose docstring with numbered pipeline steps and detailed Args/Returns
- Line 248-261: `delete_session` - verbose docstring with numbered deletion targets and detailed Args/Returns
- Line 321-328: `get_memory_stats` - verbose docstring with detailed Returns structure
- Line 383-391: `get_session_status` - verbose docstring with detailed Args/Returns

### `app/routes/profile.py`
- Line 1: Verbose module docstring
- Line 17-22: `get_profile` - verbose docstring with Returns description
- Line 35-43: `update_profile` - verbose docstring with detailed Args/Returns

### `app/routes/config.py`
- Line 1-7: Verbose module docstring
- Line 20: Separator comment `# ===== Request/Response Models =====`
- Line 55: Separator comment `# ===== Config Endpoints =====`
- Line 59-64: `get_config` - verbose docstring with detailed Returns description
- Line 144-152: `update_config` - verbose docstring with Note about persistence
- Line 201-205: `get_config_schema` - verbose docstring with "Useful for..." note

### `app/routes/health.py`
- Line 11: `health_check` - verbose docstring
- Line 21: `detailed_health_check` - verbose docstring

### `app/routes/logs.py`
- Line 1-6: Verbose module docstring
- Line 25-30: `get_logs` - verbose docstring with detailed Returns description
- Line 63-65: `get_log_detail` - verbose docstring

### `app/main.py`
- Line 1: Verbose module docstring
- Line 27: `RequestLoggingMiddleware` - verbose class docstring
- Line 84: `lifespan` - verbose docstring
- Line 149: `create_app` - verbose docstring
- Line 31: Comment `# Skip logging for health checks`
- Line 34: Comment `# Get request ID from header or generate one`
- Line 37: Comment `# Generate request ID if not provided`
- Line 41: Comment `# Start timing`
- Line 44: Comment `# Process request`
- Line 59: Comment `# Calculate response time`
- Line 62: Comment `# Log request (non-blocking)`
- Line 76: Comment `# Add request ID to response header`
- Line 87: Comment `# Startup`
- Line 90: Comment `# Initialize database`
- Line 98: Comment `# Initialize gateway`
- Line 102: Comment `# Initialize RAG if enabled (do this at startup to avoid delays during requests)`
- Line 118: Comment `# Initialize tool registry and register default tools`
- Line 125: Comment `# Register RAG answer tool (default tool)`
- Line 129: Comment `# Set initial allowlist (v0 tools: rag_answer)`
- Line 139: Comment `# Shutdown`
- Line 157: Comment `# Add CORS middleware`
- Line 166: Comment `# Add request logging middleware`
- Line 169: Comment `# Include routes`

### `app/db.py`
- Line 1-5: Verbose module docstring
- Line 16: Comment `# Database file path`
- Line 22: `init_database` - verbose docstring
- Line 27: Comment `# Create requests table`
- Line 48: Comment `# Create index on request_id for fast lookups`
- Line 53: Comment `# Create index on timestamp for time-based queries`
- Line 58: Comment `# Create index on endpoint for endpoint-based queries`
- Line 73: `get_db_connection` - verbose docstring
- Line 89-119: `log_request` - verbose docstring with detailed Args section
- Line 141: Comment `# Request ID already exists (shouldn't happen, but handle gracefully)`
- Line 144: Comment `# Don't fail the request if logging fails`
- Line 148-157: `get_request_by_id` - verbose docstring with detailed Args/Returns
- Line 175-185: `get_recent_requests` - verbose docstring with detailed Args/Returns

### `rag/document_parser.py` ✅ CLEANED
- Line 1-4: Verbose module docstring → ✅ Cleaned
- Line 16: `ParsedDocument` - verbose class docstring → ✅ Cleaned
- Line 24-28: `DocumentParser` - verbose class docstring → ✅ Cleaned
- Line 33: `supports` - verbose docstring → ✅ Cleaned
- Line 36-45: `parse` - verbose docstring with detailed Args/Returns → ✅ Cleaned
- Line 62: `_parse_text` - verbose docstring → ✅ Cleaned (removed)
- Line 74: `_parse_pdf` - verbose docstring → ✅ Cleaned (removed)
- Line 91: `_parse_docx` - verbose docstring → ✅ Cleaned (removed)
- Line 103: Comment `# Singleton instance` → ✅ Cleaned
- Line 108: `get_document_parser` - verbose docstring → ✅ Cleaned

### `core/model_registry.py` ✅ CLEANED
- Line 1-4: Verbose module docstring → ✅ Cleaned
- Line 18-28: `ModelMetadata` - verbose class docstring with detailed Attributes section → ✅ Cleaned
- Line 37-39: Separator comments `# =============================================================================` → ✅ Cleaned
- Line 92-94: Separator comments `# =============================================================================` → ✅ Cleaned
- Line 97-100: `get_models_by_tag` - verbose docstring with detailed Args/Returns → ✅ Cleaned

### `llm/base_client.py` ✅ CLEANED
- Line 1-4: Verbose module docstring → ✅ Cleaned
- Line 14-26: `chat` - verbose docstring with detailed Args/Returns → ✅ Cleaned
- Line 29-36: `get_available_models` - verbose docstring with detailed Returns → ✅ Cleaned
- Line 38-45: `health_check` - verbose docstring with detailed Returns → ✅ Cleaned
- Line 46: Comment `# Default implementation - can be overridden` → ✅ Cleaned

### `core/queue.py` ✅ CLEANED
- Line 1-4: Verbose module docstring → ✅ Cleaned
- Line 19: `JobStatus` - verbose class docstring → ✅ Cleaned
- Line 28-32: `RedisQueue` - verbose class docstring → ✅ Cleaned
- Line 35-40: `__init__` - verbose docstring with detailed Args → ✅ Cleaned
- Line 45: `get_pool` - verbose docstring → ✅ Cleaned
- Line 50-61: `enqueue` - verbose docstring with detailed Args/Returns → ✅ Cleaned
- Line 67-76: `get_job_status` - verbose docstring with detailed Args/Returns → ✅ Cleaned
- Line 87: Comment `# Map arq JobStatus enum to our status strings` → ✅ Cleaned
- Line 97: Comment `# Safely get attributes from JobDef (different versions may have different attrs)` → ✅ Cleaned
- Line 101: Comment `# Check if job failed (result is exception)` → ✅ Cleaned
- Line 125: Comment `# Singleton instance` → ✅ Cleaned
- Line 130: `get_redis_queue` - verbose docstring with parenthetical note → ✅ Cleaned

### `core/utils/logging_config.py` ✅ CLEANED
- Line 1-4: Verbose module docstring → ✅ Cleaned
- Line 20-28: `setup_logging` - verbose docstring with detailed Args section → ✅ Cleaned
- Line 60: Comment `# RAG demo log (with simple rotation)` → ✅ Cleaned
- Line 75: Comment `# Tuning demo log (with simple rotation)` → ✅ Cleaned
- Line 91-101: `get_logger` - verbose docstring with detailed Args/Returns → ✅ Cleaned
- Line 105: `get_rag_logger` - verbose docstring → ✅ Cleaned
- Line 109: `get_tuning_logger` - verbose docstring → ✅ Cleaned
- Line 124-138: `log_rag_result` - verbose docstring with detailed Args section → ✅ Cleaned
- Line 141: Comment `# Simple log format with wrapped answers` → ✅ Cleaned
- Line 147: Comment `# Log retrieved context details (show what was found, not full content)` → ✅ Cleaned
- Line 151: Comment `# Show first 100 chars to see what type of content was retrieved` → ✅ Cleaned
- Line 161-187: `log_tuning_result` - verbose docstring with detailed Args section → ✅ Cleaned
- Line 190: Comment `# Simple log format` → ✅ Cleaned
- Line 197: Comment `# Initialize logging when module is imported` → ✅ Cleaned

### `agents/tools/rag_answer.py` ✅ CLEANED
- Line 1-5: Verbose module docstring → ✅ Cleaned
- Line 16-20: `RAGAnswerTool` - verbose class docstring → ✅ Cleaned
- Line 23: `__init__` - verbose docstring → ✅ Cleaned
- Line 27: `_get_rag` - verbose docstring → ✅ Cleaned (removed)
- Line 35: `name` - verbose docstring → ✅ Cleaned
- Line 39: `description` - verbose docstring → ✅ Cleaned
- Line 44: `read_only` - verbose docstring → ✅ Cleaned
- Line 49: `idempotent` - verbose docstring → ✅ Cleaned
- Line 54: `get_schema` - verbose docstring → ✅ Cleaned
- Line 111-127: `execute` - verbose docstring with detailed Args/Returns → ✅ Cleaned
- Line 131: Comment `# Validate query` → ✅ Cleaned
- Line 138: Comment `# Get RAG system` → ✅ Cleaned
- Line 141: Comment `# Execute RAG query` → ✅ Cleaned
- Line 147: Comment `# Build answer snippets` → ✅ Cleaned
