"""Model registry for embedding and LLM models."""

from pydantic import BaseModel, Field
from typing import Literal, Optional
from enum import Enum


class ModelType(str, Enum):
    """Type of model in the registry."""
    EMBEDDING = "embedding"
    LLM = "llm"


class ModelMetadata(BaseModel):
    """Metadata schema for a registered model."""
    name: str
    type: ModelType
    tags: list[str] = Field(default_factory=list)
    dimension: Optional[int] = None
    provider: Optional[str] = None
    description: Optional[str] = None


MODELS: dict[str, ModelMetadata] = {
    # Embedding Models
    "bge-m3": ModelMetadata(
        name="BAAI/bge-m3",
        type=ModelType.EMBEDDING,
        tags=["library", "journal", "multilingual", "long-context", "gpu-preferred"],
        dimension=1024,
        provider="sentence-transformers",
        description="Top-tier multilingual embedding. 8K context, best all-rounder on MTEB."
    ),
    "bge-small-en-v1.5": ModelMetadata(
        name="BAAI/bge-small-en-v1.5",
        type=ModelType.EMBEDDING,
        tags=["fast", "cpu-friendly"],
        dimension=384,
        provider="sentence-transformers",
        description="Lightweight English embedding for resource-constrained environments."
    ),
    
    # LLM Models
    "llama3.2:1b": ModelMetadata(
        name="llama3.2:1b",
        type=ModelType.LLM,
        tags=["chat", "fast", "cpu-friendly"],
        provider="ollama",
        description="Lightweight Llama model for quick responses."
    ),
    "llama3.2:3b": ModelMetadata(
        name="llama3.2:3b",
        type=ModelType.LLM,
        tags=["chat", "balanced"],
        provider="ollama",
        description="Balanced Llama model for general use."
    ),
    "qwen3:1.7b": ModelMetadata(
        name="qwen3:1.7b",
        type=ModelType.LLM,
        tags=["chat", "fast", "reasoning"],
        provider="ollama",
        description="Qwen model with strong reasoning capabilities."
    ),
    "qwen3:8b": ModelMetadata(
        name="qwen3:8b",
        type=ModelType.LLM,
        tags=["chat", "quality", "gpu-preferred"],
        provider="ollama",
        description="Larger Qwen model for high-quality responses."
    ),
}


def get_models_by_tag(tag: str) -> list[ModelMetadata]:
    """Get all models that have a specific tag."""
    return [model for model in MODELS.values() if tag in model.tags]


def get_models_by_type(model_type: ModelType) -> list[ModelMetadata]:
    """Get all models of a specific type."""
    return [model for model in MODELS.values() if model.type == model_type]


def get_model_for_task(task: Literal["library", "journal"]) -> ModelMetadata:
    """Get the default model for a specific task."""
    models = get_models_by_tag(task)
    if not models:
        raise ValueError(f"No model found for task: {task}")
    return models[0]


def get_model(name: str) -> Optional[ModelMetadata]:
    """Get a model by its registry key."""
    return MODELS.get(name)


def list_models() -> list[str]:
    """List all registered model names."""
    return list(MODELS.keys())


def get_configured_model(task: Literal["library", "journal"]) -> ModelMetadata:
    """Get the model for a task, respecting config overrides."""
    from core.config import get_config
    
    config = get_config()
    model_name = config.embedding_model
    
    model = get_model(model_name)
    if model is None:
        for m in MODELS.values():
            if m.name == model_name:
                return m
        raise ValueError(f"Model '{model_name}' not found in registry")
    
    return model
