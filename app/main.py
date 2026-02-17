"""FastAPI startup - KB Service API"""

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from llm.gateway import AIGateway
from core.database import init_pool, close_pool
from .dependencies import verify_api_key
from .routes import health, llm, query, ingest, config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _configure_logging() -> None:
    config = get_config()
    level = logging.DEBUG if config.debug else logging.INFO
    logging.getLogger().setLevel(level)
    # Keep uvicorn access logs at WARNING so they don't flood debug output
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    if config.debug:
        logger.debug("DEBUG logging enabled — full pipeline output active")

gateway: AIGateway = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI application lifecycle."""
    global gateway

    _configure_logging()
    logger.info("Starting KB Service API")

    # PostgreSQL pool + schema
    try:
        await init_pool()
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")

    # AI Gateway
    gateway = AIGateway()
    logger.info("AI Gateway initialized")

    yield

    logger.info("Shutting down KB Service API")
    await close_pool()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="KB Service API",
        description="Knowledge base service with hybrid retrieval",
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

    _auth = [Depends(verify_api_key)]
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(llm.router, prefix="/v1", tags=["llm"], dependencies=_auth)
    app.include_router(query.router, prefix="/v1", tags=["kb"], dependencies=_auth)
    app.include_router(ingest.router, prefix="/v1", tags=["kb"], dependencies=_auth)
    app.include_router(config.router, prefix="/v1", tags=["config"], dependencies=_auth)

    return app


app = create_app()
