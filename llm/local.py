"""Minimal Ollama client wrapper for local development.

This file provides a small, easy-to-understand Async client for Ollama.
It focuses on a single default model (qwen3:1.7b) with clear methods:
- chat(model, messages, **kwargs)
- embeddings(prompt, model=None)
- health_check()
- list_models()

Keep it intentionally small so it's easy to test and extend later.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx


DEFAULT_MODEL = "qwen3:1.7b"


@dataclass
class OllamaConfig:
    base_url: str = "http://localhost:11434"
    default_model: str = DEFAULT_MODEL
    chat_timeout: float = 15.0
    embeddings_timeout: float = 30.0
    connection_timeout: float = 5.0


class OllamaClient:
    """Very small Ollama HTTP client.

    Usage:
        async with OllamaClient() as client:
            resp = await client.chat([{"role":"user","content":"Hello"}])
    """

    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self.logger = logging.getLogger(__name__)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=httpx.Timeout(
                    connect=self.config.connection_timeout,
                    read=max(self.config.chat_timeout, self.config.embeddings_timeout),
                ),
            )
        return self._client

    async def chat(self, messages: List[Dict[str, Any]], model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Send messages to Ollama chat endpoint.

        Args:
            messages: List of {role, content} messages (OpenAI style)
            model: Optional model name; defaults to configured default
        Returns:
            Parsed JSON response from Ollama
        """
        client = await self._ensure_client()
        model = model or self.config.default_model

        payload = {"model": model, "messages": messages, **kwargs}
        self.logger.debug("ollama chat payload", extra={"model": model, "msg_count": len(messages)})

        resp = await client.post("/api/chat", json=payload, timeout=self.config.chat_timeout)
        resp.raise_for_status()
        return resp.json()

    async def embeddings(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        client = await self._ensure_client()
        model = model or self.config.default_model
        payload = {"model": model, "prompt": prompt}
        resp = await client.post("/api/embeddings", json=payload, timeout=self.config.embeddings_timeout)
        resp.raise_for_status()
        return resp.json()

    async def health_check(self) -> bool:
        try:
            client = await self._ensure_client()
            resp = await client.get("/api/tags", timeout=self.config.connection_timeout)
            return resp.status_code == 200
        except Exception:
            self.logger.exception("health_check failed")
            return False

    async def list_models(self) -> List[str]:
        client = await self._ensure_client()
        resp = await client.get("/api/tags", timeout=self.config.connection_timeout)
        resp.raise_for_status()
        data = resp.json()
        return [m.get("name") for m in data.get("models", []) if m.get("name")]
