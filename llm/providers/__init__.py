"""
External AI Provider Clients

This package contains clients for external AI providers:
- Purdue GenAI Studio
- Anthropic Claude
- (Future: OpenAI, etc.)
"""

from .purdue import PurdueGenAI
from .anthropic import AnthropicClient

__all__ = ["PurdueGenAI", "AnthropicClient"]

