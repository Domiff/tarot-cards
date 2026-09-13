import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.core.config import settings
from bot.core.logging import setup_logging


bot = Bot(
    token=settings.bot.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        text=(
            f"Привет, <b>{message.from_user.full_name}</b>!\n"
            "Я разложу для тебя карты Таро.\n\n"
            "Отправь /help, чтобы увидеть список команд."
        )
    )


@dp.message(Command("help"))
async def help_(message: Message) -> None:
    await message.answer(
        text=(
            "<b>Доступные команды</b>\n"
            "/start — начать работу с ботом\n"
            "/help — показать это сообщение"
        )
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
