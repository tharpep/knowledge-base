"""LLM Gateway package initialization

This package provides LLM gateway functionality and adapters for Personal AI.
"""

__version__ = "0.1.0"

from .providers import PurdueGenAI, AnthropicClient
from .gateway import AIGateway
from .local import OllamaClient, OllamaConfig

__all__ = [
    "AIGateway",
    "OllamaClient", 
    "OllamaConfig",
    "PurdueGenAI",
    "AnthropicClient",
]
