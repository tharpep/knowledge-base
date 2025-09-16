"""LLM API routes - OpenAI-compatible endpoints"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class ChatMessage(BaseModel):
    """OpenAI-style chat message."""
    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request."""
    model: Optional[str] = Field(None, description="Model to use for completion")
    messages: List[ChatMessage] = Field(..., description="List of messages")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Top-p sampling")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens to generate")


class EmbeddingRequest(BaseModel):
    """OpenAI-compatible embedding request."""
    input: str = Field(..., description="Text to embed")
    model: Optional[str] = Field(None, description="Model to use for embeddings")


@router.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest) -> Dict[str, Any]:
    """OpenAI-compatible chat completions endpoint."""
    from ..main import gateway
    
    try:
        # Convert Pydantic messages to dicts
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Prepare kwargs for optional parameters
        kwargs = {}
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.top_p is not None:
            kwargs["top_p"] = request.top_p
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        
        # Call gateway
        response = await gateway.chat(
            messages=messages,
            model=request.model,
            **kwargs
        )
        
        # Convert Ollama response to OpenAI format
        return {
            "id": f"chatcmpl-{hash(str(messages))}", 
            "object": "chat.completion",
            "model": request.model or gateway.config.default_model,
            "choices": [{
                "index": 0,
                "message": response.get("message", {}),
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": response.get("prompt_eval_count", 0),
                "completion_tokens": response.get("eval_count", 0), 
                "total_tokens": response.get("prompt_eval_count", 0) + response.get("eval_count", 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {str(e)}")


@router.post("/embeddings")
async def create_embeddings(request: EmbeddingRequest) -> Dict[str, Any]:
    """OpenAI-compatible embeddings endpoint."""
    from ..main import gateway
    
    try:
        response = await gateway.embeddings(
            prompt=request.input,
            model=request.model
        )
        
        # Convert Ollama response to OpenAI format
        embedding = response.get("embedding", [])
        
        return {
            "object": "list",
            "data": [{
                "object": "embedding",
                "index": 0,
                "embedding": embedding
            }],
            "model": request.model or gateway.config.default_model,
            "usage": {
                "prompt_tokens": len(request.input.split()),  # Rough estimate
                "total_tokens": len(request.input.split())
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")


@router.get("/models")
async def list_models() -> Dict[str, Any]:
    """List available models."""
    from ..main import gateway
    
    try:
        models = await gateway._client.list_models()
        
        return {
            "object": "list",
            "data": [
                {
                    "id": model,
                    "object": "model",
                    "owned_by": "local",
                    "permission": []
                }
                for model in models
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")
