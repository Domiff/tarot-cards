import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.core.config import settings
from bot.core.logging import setup_logging
from bot.tarot.router import router

bot = Bot(
    token=settings.bot.BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
        link_preview_is_disabled=True,
    ),
)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        text=(
            f"Привет, <b>{message.from_user.full_name}</b>! 👋\n"
            "Добро пожаловать в мир карт! 🔮\n\n"
            "Меня зовут <b>Наталия</b>, и я предлагаю заглянуть в тайны Таро. "
            "Помогу найти ответы на важные вопросы и сделаю расклад на любую тему. 🃏\n\n"
            f'📣 <a href="{settings.bot.CHANNEL_URL}">Канал «Таромир»</a> — разборы карт и расклады\n'
            f'💬 <a href="{settings.bot.CHAT_URL}">Чат</a> — вопросы и общение\n\n'
            "А бот покажет колоду и расскажет о каждой карте.\n"
            "Отправь /help, чтобы увидеть список команд. ☕️"
        )
    )


@dp.message(Command("help"))
async def help_(message: Message) -> None:
    await message.answer(
        text=(
            "<b>Доступные команды</b>\n\n"
            "/cards — вся колода по арканам\n"
            "/card <i>название</i> — одна карта с описанием\n"
            "/daily — карта дня\n"
            "/history — история Таро\n"
            "/start — приветствие\n"
            "/help — показать это сообщение\n\n"
            f'📣 <a href="{settings.bot.CHANNEL_URL}">Канал</a> · '
            f'💬 <a href="{settings.bot.CHAT_URL}">Чат</a>'
        )
    )


async def main() -> None:
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
