"""FastAPI startup - KB Service API"""

import logging
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from core.config import get_config
from core.database import close_pool, init_pool
from llm.gateway import AIGateway

from .dependencies import verify_api_key
from .routes import config, health, ingest, llm, query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# httpx logs every request URL at INFO, including API keys that some providers take as query
# parameters (GNews, Google Maps, fact checks). Keep it at WARNING so keys never reach the logs.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

def _configure_logging() -> None:
    config = get_config()
    level = logging.DEBUG if config.debug else logging.INFO
    logging.getLogger().setLevel(level)
    # Keep uvicorn access logs at WARNING so they don't flood debug output
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    if config.debug:
        logger.debug("DEBUG logging enabled — full pipeline output active")


def _configure_sentry() -> None:
    """No-op unless SENTRY_DSN is set — nothing to configure until a Sentry
    project exists. logger.error/exception calls are captured automatically
    via the logging integration once it is."""
    config = get_config()
    if not config.sentry_dsn:
        return
    sentry_sdk.init(
        dsn=config.sentry_dsn,
        integrations=[
            FastApiIntegration(),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
        traces_sample_rate=config.sentry_traces_sample_rate,
        send_default_pii=False,
    )
    logger.info("Sentry error tracking enabled")

gateway: AIGateway = None


def _require_api_key() -> None:
    """Refuse to start without API_KEY unless ALLOW_NO_AUTH says this is local dev."""
    config = get_config()
    if config.api_key:
        return
    if config.allow_no_auth:
        logger.warning("API_KEY is empty and ALLOW_NO_AUTH=true: every route is open (dev only)")
        return
    msg = "API_KEY is not set. Set it, or set ALLOW_NO_AUTH=true for local development."
    raise RuntimeError(msg)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI application lifecycle."""
    global gateway

    _configure_logging()
    _require_api_key()
    _configure_sentry()
    logger.info("Starting KB Service API")

    # PostgreSQL pool + schema. init_pool() itself no-ops gracefully when
    # DATABASE_URL isn't set (local dev) — a real failure here (bad DSN,
    # unreachable Postgres, broken schema SQL) must crash startup instead of
    # deploying a revision that looks healthy but 500s on every DB-touching
    # request, since get_pool() raises once _pool is never set.
    await init_pool()

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
        allow_origins=get_config().allowed_origins,
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
