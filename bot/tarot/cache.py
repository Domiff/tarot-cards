from typing import Any, Awaitable, Callable, TypeVar

from pydantic import TypeAdapter

from bot.core.cache import cache, key_builder

T = TypeVar("T")

CARDS_KEY = key_builder("tarot", "cards")
HISTORY_KEY = key_builder("tarot", "history")


async def get_cached(
    key: str, adapter: TypeAdapter[T], func: Callable[[], Awaitable[Any]]
) -> T:
    cached = await cache.get(key)
    if cached:
        return adapter.validate_json(cached)

    data = adapter.validate_python(await func())

    if data:
        await cache.set(key, adapter.dump_json(data))

    return data
