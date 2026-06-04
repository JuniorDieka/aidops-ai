from fastapi import APIRouter, Depends

from app.api.dependencies import get_vector_store
from app.config import settings
from app.core.models import HealthCheck
from app.core.providers.vectorstore import VectorStoreProvider
from app.services.cache import cache_service

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check(vector_store: VectorStoreProvider = Depends(get_vector_store)) -> HealthCheck:
    services = {
        "redis": cache_service.redis_client is not None,
        "vector_db": True,
        "demo_mode": settings.is_demo_mode,
    }

    try:
        await vector_store.count()
        services["vector_db"] = True
    except Exception:
        services["vector_db"] = False

    return HealthCheck(
        status="healthy" if all(services.values()) else "degraded",
        version=settings.app_version,
        demo_mode=settings.is_demo_mode,
        services=services,
    )
