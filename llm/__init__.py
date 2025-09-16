"""LLM Gateway package initialization

This package provides LLM gateway functionality and adapters for Personal AI.
"""

__version__ = "0.1.0"

from .external import *
from .gateway import LLMSimpleGateway
from .local import OllamaClient, OllamaConfig

__all__ = [
    "LLMSimpleGateway",
    "OllamaClient", 
    "OllamaConfig",
]
