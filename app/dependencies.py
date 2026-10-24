"""Shared FastAPI dependencies."""

import hmac

from fastapi import HTTPException, Request

from core.config import get_config


def verify_api_key(request: Request) -> None:
    """
    Require a valid API key. Accepts X-API-Key or Authorization: Bearer <key>.
    Auth is off only when API_KEY is empty and ALLOW_NO_AUTH=true (local dev). An empty key
    without that flag refuses every request; startup refuses it too (main.py), this is the
    second line.
    """
    config = get_config()
    if not config.api_key:
        if config.allow_no_auth:
            return
        raise HTTPException(503, "API_KEY is not configured")

    key: str | None = request.headers.get("X-API-Key")
    if not key:
        auth = request.headers.get("Authorization") or ""
        if auth.lower().startswith("bearer "):
            key = auth[7:].strip()

    if not key or not hmac.compare_digest(key.encode(), config.api_key.encode()):
        raise HTTPException(401, "Invalid or missing API key")
