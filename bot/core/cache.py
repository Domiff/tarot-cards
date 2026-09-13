from datetime import timedelta
from functools import lru_cache
from typing import Any, Callable, Awaitable

from redis.asyncio import Redis
from redis.exceptions import (
    ConnectionError as RedisConnectionError,
    TimeoutError as RedisTimeoutError,
)

from bot.core.config import settings
from bot.core.logging import get_logger


@lru_cache
def _get_redis() -> Redis:
    return Redis.from_url(
        url=settings.redis.REDIS_URL,
        max_connections=settings.redis.CONNECTION_POOL_MAXSIZE,
        decode_responses=False,
    )


class BaseRedis:
    def __init__(self, redis) -> None:
        self.redis: Redis = redis
        self.logger = get_logger(self.__class__.__name__)

    @staticmethod
    def key_builder(prefix: str, key: str) -> str:
        return f"{prefix}:{key}"

    async def _do(
            self, func: Callable[..., Awaitable[Any]], *args, **kwargs
    ) -> Any:
        operation = getattr(func, "__name__", repr(func))
        try:
            return await func(*args, **kwargs)
        except (RedisConnectionError, RedisTimeoutError) as e:
            self.logger.error(
                "Redis connection error", operation=operation, error=str(e)
            )
            raise
        except Exception as e:
            self.logger.error(
                "Redis operation failed", operation=operation, error=str(e)
            )
            raise


class RedisCache(BaseRedis):
    async def set(
            self, key: str, value, expire: int | timedelta = settings.redis.EXPIRE
    ) -> None:
        await self._do(self.redis.set, key, value, ex=expire)
        self.logger.info("redis_set", redis_key=key)

    async def get(self, key: str) -> str | bytes | None:
        value = await self._do(self.redis.get, key)
        if value:
            self.logger.info("redis_get", redis_key=key)
            return value
        return None

    async def delete(self, key: str) -> None:
        await self._do(self.redis.delete, key)
        self.logger.info("redis_delete", redis_key=key)


@lru_cache
def get_redis() -> Redis:
    return Redis.from_url(
        settings.redis.REDIS_URL,
        max_connections=settings.redis.CONNECTION_POOL_MAXSIZE,
        decode_responses=True,
    )


def get_cache() -> RedisCache:
    return RedisCache(get_redis())
