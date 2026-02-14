"""LLM Gateway — routes all chat requests through the api-gateway."""

from typing import Any

import httpx

from core.config import get_config


class AIGateway:
    """Routes LLM requests to the api-gateway's /ai/v1/chat/completions endpoint."""

    def __init__(self) -> None:
        self.config = get_config()

    def chat(
        self,
        message: str | None = None,
        messages: list[dict[str, str]] | None = None,
        model: str | None = None,
    ) -> str:
        """Send a chat request and return the response text."""
        if messages is None:
            if message is None:
                raise ValueError("Either message or messages must be provided")
            messages = [{"role": "user", "content": message}]

        url = f"{self.config.api_gateway_url.rstrip('/')}/ai/v1/chat/completions"
        payload: dict[str, Any] = {
            "messages": messages,
            "model": model or self.config.default_model,
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                url,
                json=payload,
                headers={"X-API-Key": self.config.api_gateway_key},
            )

        response.raise_for_status()
        data = response.json()

        # OpenAI-compatible response shape
        return data["choices"][0]["message"]["content"]

    def get_available_providers(self) -> list[str]:
        return ["gateway"]
