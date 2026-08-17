"""Async Redis-клиент: кэш справочников, распределённые локи, очереди уведомлений."""

from redis.asyncio import Redis

from app.core.config import settings

redis_client: Redis = Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)


async def get_redis() -> Redis:
    """FastAPI-зависимость для доступа к Redis."""
    return redis_client
