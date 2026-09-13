from aiogram import Bot, Dispatcher, loggers
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage

from bot.core.config import settings
from bot.core.cache import get_redis


def create_bot() -> Bot:
    return Bot(
        token=settings.bot.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    key_builder = DefaultKeyBuilder(with_destiny=True)
    storage = RedisStorage(get_redis(), key_builder=key_builder)
    return Dispatcher(storage=storage)
