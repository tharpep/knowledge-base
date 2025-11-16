"""LLM API routes - OpenAI-compatible endpoints"""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
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
    
    # Generate request ID for tracing
    request_id = f"req_{uuid.uuid4().hex[:12]}"
    
    try:
        # Validate messages
        if not request.messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "message": "Messages array cannot be empty",
                        "type": "invalid_request_error",
                        "code": "empty_messages"
                    },
                    "request_id": request_id
                }
            )
        
        # Validate message roles and content
        valid_roles = {"system", "user", "assistant"}
        for i, msg in enumerate(request.messages):
            if msg.role not in valid_roles:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "error": {
                            "message": f"Invalid role '{msg.role}' in message {i}. Must be one of: {', '.join(valid_roles)}",
                            "type": "validation_error",
                            "code": "invalid_role"
                        },
                        "request_id": request_id
                    }
                )
            if not msg.content or not msg.content.strip():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "error": {
                            "message": f"Message {i} content cannot be empty",
                            "type": "validation_error",
                            "code": "empty_content"
                        },
                        "request_id": request_id
                    }
                )
        
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
        
        # Call gateway with full message history
        # For now, use single turn (last message) as per Phase 1 requirements
        # Message array support is ready in gateway, but keeping single turn for now
        response = gateway.chat(
            message=messages[-1]["content"],
            provider=None,  # Auto-select based on config
            model=request.model,
            messages=messages  # Pass full history for future use
        )
        
        # Rough token estimation (word count * 1.3)
        prompt_text = " ".join([msg["content"] for msg in messages])
        prompt_tokens = int(len(prompt_text.split()) * 1.3)
        completion_tokens = int(len(response.split()) * 1.3)
        total_tokens = prompt_tokens + completion_tokens
        
        # Convert AIGateway response to OpenAI format
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(__import__("time").time()),
            "model": request.model or gateway.config.model_name,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": response},
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            },
            "request_id": request_id
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (already properly formatted)
        raise
    except ValueError as e:
        # Validation errors
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "message": str(e),
                    "type": "validation_error",
                    "code": "invalid_parameter"
                },
                "request_id": request_id
            }
        )
    except ConnectionError as e:
        # Connection errors (provider unavailable)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": {
                    "message": f"AI provider unavailable: {str(e)}",
                    "type": "service_unavailable",
                    "code": "provider_unavailable"
                },
                "request_id": request_id
            }
        )
    except TimeoutError as e:
        # Timeout errors
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "error": {
                    "message": f"Request timed out: {str(e)}",
                    "type": "timeout_error",
                    "code": "request_timeout"
                },
                "request_id": request_id
            }
        )
    except Exception as e:
        # Generic server errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "message": f"Chat completion failed: {str(e)}",
                    "type": "internal_error",
                    "code": "server_error"
                },
                "request_id": request_id
            }
        )


@router.post("/embeddings")
async def create_embeddings(request: EmbeddingRequest) -> Dict[str, Any]:
    """OpenAI-compatible embeddings endpoint."""
    from ..main import gateway
    
    # Generate request ID for tracing
    request_id = f"req_{uuid.uuid4().hex[:12]}"
    
    try:
        # Validate input
        if not request.input or not request.input.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "message": "Input text cannot be empty",
                        "type": "invalid_request_error",
                        "code": "empty_input"
                    },
                    "request_id": request_id
                }
            )
        
        response = await gateway.embeddings(
            prompt=request.input,
            model=request.model
        )
        
        # Convert Ollama response to OpenAI format
        embedding = response.get("embedding", [])
        
        if not embedding:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "error": {
                        "message": "Embedding provider returned empty response",
                        "type": "bad_gateway",
                        "code": "empty_embedding"
                    },
                    "request_id": request_id
                }
            )
        
        # Rough token estimation (word count * 1.3)
        prompt_tokens = int(len(request.input.split()) * 1.3)
        
        return {
            "object": "list",
            "data": [{
                "object": "embedding",
                "index": 0,
                "embedding": embedding
            }],
            "model": request.model or gateway.config.model_name,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "total_tokens": prompt_tokens
            },
            "request_id": request_id
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (already properly formatted)
        raise
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": {
                    "message": f"Embedding provider unavailable: {str(e)}",
                    "type": "service_unavailable",
                    "code": "provider_unavailable"
                },
                "request_id": request_id
            }
        )
    except TimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "error": {
                    "message": f"Request timed out: {str(e)}",
                    "type": "timeout_error",
                    "code": "request_timeout"
                },
                "request_id": request_id
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "message": f"Embedding generation failed: {str(e)}",
                    "type": "internal_error",
                    "code": "server_error"
                },
                "request_id": request_id
            }
        )


@router.get("/models")
async def list_models() -> Dict[str, Any]:
    """List available models."""
    from ..main import gateway
    
    # Generate request ID for tracing
    request_id = f"req_{uuid.uuid4().hex[:12]}"
    
    try:
        # Get available providers and their models
        providers = gateway.get_available_providers()
        models = []
        
        if not providers:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": {
                        "message": "No AI providers available. Please configure at least one provider.",
                        "type": "service_unavailable",
                        "code": "no_providers"
                    },
                    "request_id": request_id
                }
            )
        
        for provider in providers:
            try:
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
            except Exception as e:
                # Log provider error but continue with other providers
                import logging
                logging.warning(f"Failed to get models from provider {provider}: {e}")
                continue
        
        if not models:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": {
                        "message": "No models available from any provider",
                        "type": "service_unavailable",
                        "code": "no_models"
                    },
                    "request_id": request_id
                }
            )
        
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
            ],
            "request_id": request_id
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (already properly formatted)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "message": f"Failed to list models: {str(e)}",
                    "type": "internal_error",
                    "code": "server_error"
                },
                "request_id": request_id
            }
        )
