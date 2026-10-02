from datetime import timedelta
from functools import lru_cache
from typing import Any, Awaitable, Callable

from redis.asyncio import Redis
from redis.exceptions import (
    ConnectionError as RedisConnectionError,
    TimeoutError as RedisTimeoutError,
)

from bot.core.config import settings
from bot.core.logging import get_logger


class BaseRedis:
    def __init__(self, redis) -> None:
        self.redis: Redis = redis
        self.logger = get_logger(self.__class__.__name__)

    async def _do(
        self, func: Callable[..., Awaitable[Any] | Any], *args, **kwargs
    ) -> Any:
        operation = getattr(func, "__name__", repr(func))
        try:
            return await func(*args, **kwargs)
        except (RedisConnectionError, RedisTimeoutError) as e:
            self.logger.error(
                "Redis connection error",
                extra={"operation": operation, "error": str(e)},
            )
        except Exception as e:
            self.logger.error(
                "Redis operation failed",
                extra={"operation": operation, "error": str(e)},
            )
            raise


class RedisCache(BaseRedis):
    async def set(
        self, key: str, value, expire: int | timedelta = settings.redis.EXPIRE
    ) -> None:
        await self._do(self.redis.set, key, value, ex=expire)
        self.logger.info("redis_set", extra={"redis_key": key})

    async def get(self, key: str) -> str | None:
        value = await self._do(self.redis.get, key)
        if value is None:
            return None
        self.logger.info("redis_get", extra={"redis_key": key})
        return value

    async def expire(self, key: str) -> None:
        await self._do(self.redis.expire, key, settings.redis.EXPIRE)
        self.logger.info("redis_expire", extra={"redis_key": key})

    async def delete(self, key: str) -> None:
        await self._do(self.redis.delete, key)
        self.logger.info("redis_delete", extra={"redis_key": key})

    async def delete_by_pattern(self, pattern: str) -> None:
        async for key in self.redis.scan_iter(match=pattern, count=100):
            await self._do(self.redis.delete, key)

        self.logger.info("redis_delete_pattern", extra={"redis_key": pattern})


def key_builder(prefix: str, key: str | int) -> str:
    return f"{prefix}:{key}"


@lru_cache
def get_redis() -> Redis:
    return Redis.from_url(
        settings.redis.REDIS_URL,
        max_connections=settings.redis.CONNECTION_POOL_MAXSIZE,
        decode_responses=True,
    )


cache = RedisCache(get_redis())
