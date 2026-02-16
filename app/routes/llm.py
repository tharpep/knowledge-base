"""LLM routes — OpenAI-compatible chat completions."""

import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from core.config import get_config
from core.profile_manager import get_profile_manager
from core.prompt_manager import get_prompt_manager

logger = logging.getLogger(__name__)

router = APIRouter()


# ===== Request / Response Models =====

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[ChatMessage] = Field(..., min_length=1)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, gt=0)
    use_kb: Optional[bool] = Field(None, description="Inject KB context into the last user message")
    system_prompt: Optional[str] = Field(None, description="Override the default system prompt")


# ===== Helpers =====

def _build_system_content(system_prompt_override: Optional[str]) -> str:
    """Compose system prompt from prompt manager + user profile."""
    prompt_mgr = get_prompt_manager()
    profile_mgr = get_profile_manager()

    system = system_prompt_override or prompt_mgr.get_system_prompt()
    profile_ctx = profile_mgr.get_context_string()
    if profile_ctx:
        system = f"{system}\n\n{profile_ctx}"
    return system


async def _inject_kb_context(messages: List[Dict], query: str) -> list:
    """Retrieve KB chunks and prepend them to the last user message. Returns chunks used."""
    try:
        from rag.retriever import retrieve
        chunks = await retrieve(query=query)
        if not chunks:
            return []

        context_text = "\n\n".join(c.content for c in chunks)
        context_block = (
            "<CONTEXT_FOR_REFERENCE>\n"
            "The following information is from your knowledge base and may be relevant.\n\n"
            f"{context_text}\n"
            "</CONTEXT_FOR_REFERENCE>\n\n"
        )

        # Prepend to the last user message
        for i in range(len(messages) - 1, -1, -1):
            if messages[i]["role"] == "user":
                messages[i]["content"] = context_block + messages[i]["content"]
                break

        return chunks
    except Exception as e:
        logger.warning(f"KB context injection failed, continuing without context: {e}")
        return []


# ===== Endpoints =====

@router.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest) -> Dict[str, Any]:
    """OpenAI-compatible chat completions with optional KB context injection."""
    from ..main import gateway

    config = get_config()

    # Build messages list with system prompt injected at position 0
    messages: List[Dict] = [{"role": m.role, "content": m.content} for m in request.messages]
    if not messages or messages[0]["role"] != "system":
        messages.insert(0, {"role": "system", "content": _build_system_content(request.system_prompt)})

    # KB context injection
    kb_chunks = []
    use_kb = request.use_kb if request.use_kb is not None else config.chat_kb_enabled
    if use_kb and config.chat_context_enabled:
        user_query = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), None
        )
        if user_query:
            kb_chunks = await _inject_kb_context(messages, user_query)

    # Call the gateway
    try:
        response_text = gateway.chat(messages=messages, model=request.model)
    except Exception as e:
        logger.error(f"Gateway call failed: {e}")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=f"Gateway error: {e}")

    # Token estimation (word count × 1.3)
    prompt_tokens = int(sum(len(m["content"].split()) for m in messages) * 1.3)
    completion_tokens = int(len(response_text.split()) * 1.3)

    result: Dict[str, Any] = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model or config.default_model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": response_text},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }

    if kb_chunks:
        result["kb_context"] = {
            "chunks_used": len(kb_chunks),
            "sources": sorted({c.filename for c in kb_chunks}),
        }

    return result


@router.get("/models")
async def list_models() -> Dict[str, Any]:
    """List available models (returns the configured default)."""
    config = get_config()
    return {
        "object": "list",
        "data": [
            {
                "id": config.default_model,
                "object": "model",
                "owned_by": "gateway",
                "permission": [],
            }
        ],
    }
