import json
from datetime import datetime
from typing import Any

import redis.asyncio as redis

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class CacheService:
    def __init__(self) -> None:
        self.redis_client: redis.Redis | None = None
        self.ttl = settings.redis_cache_ttl

    async def connect(self) -> None:
        try:
            self.redis_client = redis.from_url(
                settings.redis_url, encoding="utf-8", decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("redis_connected", url=settings.redis_url)
        except Exception as e:
            logger.warning("redis_connection_failed", error=str(e))
            self.redis_client = None

    async def disconnect(self) -> None:
        if self.redis_client:
            await self.redis_client.close()
            logger.info("redis_disconnected")

    async def get(self, key: str) -> Any | None:
        if not self.redis_client:
            return None

        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error("cache_get_failed", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        if not self.redis_client:
            return False

        try:
            serialized = json.dumps(value, cls=DateTimeEncoder)
            await self.redis_client.setex(key, ttl or self.ttl, serialized)
            return True
        except Exception as e:
            logger.error("cache_set_failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        if not self.redis_client:
            return False

        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error("cache_delete_failed", key=key, error=str(e))
            return False

    async def publish(self, channel: str, message: dict[str, Any]) -> bool:
        if not self.redis_client:
            return False

        try:
            serialized = json.dumps(message, cls=DateTimeEncoder)
            await self.redis_client.publish(channel, serialized)
            return True
        except Exception as e:
            logger.error("pubsub_publish_failed", channel=channel, error=str(e))
            return False

    async def subscribe(self, channel: str) -> Any:
        if not self.redis_client:
            return None

        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(channel)
            return pubsub
        except Exception as e:
            logger.error("pubsub_subscribe_failed", channel=channel, error=str(e))
            return None


cache_service = CacheService()
