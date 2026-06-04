from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, health, ingest, workflows
from app.config import settings
from app.services.cache import cache_service
from app.utils.logging import get_logger, setup_logging

setup_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("application_startup", version=settings.app_version, demo_mode=settings.is_demo_mode)

    await cache_service.connect()

    yield

    await cache_service.disconnect()
    logger.info("application_shutdown")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Native Automation Platform for Humanitarian Operations",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(ingest.router, prefix="/api", tags=["ingestion"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(workflows.router, prefix="/api", tags=["workflows"])


@app.get("/")
async def root() -> dict:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "demo_mode": settings.is_demo_mode,
        "message": "AidOps AI - AI-Native Automation Platform for Humanitarian Operations",
    }
