"""Shared FastAPI dependencies."""

from fastapi import HTTPException, Request

from core.config import get_config


def verify_api_key(request: Request) -> None:
    """
    Require a valid API key when config.api_key is set.
    Accepts X-API-Key or Authorization: Bearer <key>.
    When API_KEY env var is empty, auth is disabled (local dev).
    """
    config = get_config()
    if not config.api_key:
        return

    key: str | None = request.headers.get("X-API-Key")
    if not key:
        auth = request.headers.get("Authorization") or ""
        if auth.lower().startswith("bearer "):
            key = auth[7:].strip()

    if not key or key != config.api_key:
        raise HTTPException(401, "Invalid or missing API key")
