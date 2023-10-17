from uuid import UUID

import redis
import redis.asyncio as async_redis
from django.conf import settings

from voxpop.models import Message


def get_notify_channel_name(*, voxpop_id: UUID, channel_prefix: str = "") -> str:
    if isinstance(voxpop_id, str):
        voxpop_id = UUID(voxpop_id)

    return f"{channel_prefix}questions_{voxpop_id.hex}"


def notify(*, channel_name: str, payload: Message) -> None:
    r = redis.from_url(url=settings.REDIS_URL)
    r.publish(channel=channel_name, message=str(payload))


class RedisPool:
    _pool = None

    @classmethod
    def get_pool(cls):
        """Return a connection pool for Redis."""
        if not cls._pool:
            cls._pool = async_redis.ConnectionPool.from_url(url=settings.REDIS_URL)
        return cls._pool


def get_async_redis_connection() -> async_redis.Redis:
    """Return an async Redis connection."""
    pool = RedisPool.get_pool()
    return async_redis.Redis(connection_pool=pool)
