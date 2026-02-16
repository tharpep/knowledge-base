"""FastAPI startup - Personal AI Assistant API"""

import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from llm.gateway import AIGateway
from core.database import init_pool, close_pool
from .db import init_database, log_request
from .routes import health, llm, query, ingest, config, memory, logs, profile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

gateway: AIGateway = None


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all API requests to the SQLite request log."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/health"):
            return await call_next(request)

        request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"
        start_time = time.time()
        status_code = 500
        error_type = None
        error_message = None
        response = None

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            raise
        finally:
            response_time_ms = (time.time() - start_time) * 1000
            try:
                log_request(
                    request_id=request_id,
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=status_code,
                    response_time_ms=response_time_ms,
                    error_type=error_type,
                    error_message=error_message,
                )
            except Exception as e:
                logger.error(f"Failed to log request: {e}")

        if response:
            response.headers["X-Request-ID"] = request_id
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI application lifecycle."""
    global gateway

    logger.info("Starting Personal AI Assistant API")

    # SQLite request logging (non-critical)
    try:
        init_database()
        logger.info("Request logging database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize logging database: {e}")

    # PostgreSQL pool + schema
    try:
        await init_pool()
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")

    # AI Gateway
    gateway = AIGateway()
    logger.info("AI Gateway initialized")

    yield

    # Shutdown
    logger.info("Shutting down Personal AI Assistant API")
    await close_pool()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Personal AI Assistant API",
        description="OpenAI-compatible API for personal AI assistant",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestLoggingMiddleware)

    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(llm.router, prefix="/v1", tags=["llm"])
    app.include_router(query.router, prefix="/v1", tags=["kb"])
    app.include_router(ingest.router, prefix="/v1", tags=["kb"])
    app.include_router(config.router, prefix="/v1", tags=["config"])
    app.include_router(memory.router, prefix="/v1", tags=["memory"])
    app.include_router(logs.router, prefix="/v1", tags=["logs"])
    app.include_router(profile.router, prefix="/v1", tags=["profile"])

    return app


app = create_app()
