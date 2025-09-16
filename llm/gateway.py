"""LLM Gateway - routes OpenAI-style requests to underlying providers.

This minimal gateway supports a single local provider (Ollama) and exposes
async methods that the Personal API can call. The gateway is intentionally
small: it performs routing, structured logging, and simple health checks.
"""

from typing import Any, Dict, List, Optional
import logging

from .local import OllamaClient, OllamaConfig


logger = logging.getLogger(__name__)


class LLMSimpleGateway:
    """Simple gateway that forwards chat/embeddings to local Ollama.

    Usage:
        gateway = LLMSimpleGateway()
        resp = await gateway.chat(messages)
    """

    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self._client = OllamaClient(self.config)

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._client.__aexit__(exc_type, exc, tb)

    async def chat(self, messages: List[Dict[str, Any]], model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Forward a chat request to the configured provider.

        Accepts OpenAI-style messages and returns provider JSON.
        """
        logger.info("gateway.chat", extra={"model": model or self.config.default_model, "msg_count": len(messages)})
        return await self._client.chat(messages=messages, model=model, **kwargs)

    async def embeddings(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        logger.info("gateway.embeddings", extra={"model": model or self.config.default_model})
        return await self._client.embeddings(prompt=prompt, model=model)

    async def health_check(self) -> Dict[str, Any]:
        """Return combined health of gateway and provider(s)."""
        ok = False
        details = {}
        try:
            ok = await self._client.health_check()
            details["local"] = {"ok": ok}
        except Exception as e:
            details["local"] = {"ok": False, "error": str(e)}

        status = {"ok": ok, "details": details}
        logger.info("gateway.health", extra=status)
        return status

