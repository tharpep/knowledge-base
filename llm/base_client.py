"""Base class for LLM clients."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    def chat(self, messages: Any, model: Optional[str] = None, **kwargs) -> str:
        """Send chat messages and get response."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider."""
        pass
    
    def health_check(self) -> bool:
        """Check if provider is available/healthy."""
        try:
            return True
        except:
            return False

