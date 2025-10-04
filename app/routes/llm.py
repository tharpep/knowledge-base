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
        
        # Call gateway (AIGateway.chat is synchronous)
        response = gateway.chat(
            message=messages[-1]["content"] if messages else "",
            provider=None,  # Auto-select based on config
            model=request.model
        )
        
        # Convert AIGateway response to OpenAI format
        return {
            "id": f"chatcmpl-{hash(str(messages))}", 
            "object": "chat.completion",
            "model": request.model or gateway.rag_config.model_name,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": response},
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(str(messages).split()),
                "completion_tokens": len(response.split()),
                "total_tokens": len(str(messages).split()) + len(response.split())
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
            "model": request.model or gateway.rag_config.model_name,
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
        # Get available providers and their models
        providers = gateway.get_available_providers()
        models = []
        
        for provider in providers:
            if provider == "ollama":
                # Get Ollama models
                ollama_client = gateway.providers["ollama"]
                ollama_models = ollama_client.get_available_models()
                models.extend([{"id": model, "provider": "ollama"} for model in ollama_models])
            elif provider == "purdue":
                # Get Purdue models
                purdue_client = gateway.providers["purdue"]
                purdue_models = purdue_client.get_available_models()
                models.extend([{"id": model, "provider": "purdue"} for model in purdue_models])
        
        return {
            "object": "list",
            "data": [
                {
                    "id": model["id"],
                    "object": "model",
                    "owned_by": model["provider"],
                    "permission": []
                }
                for model in models
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")
