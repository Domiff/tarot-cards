from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.tarot.repository import get_history

router = Router()


@router.message(Command("history"))
async def history(message: Message) -> None:
    data = await get_history()
    await message.answer(str(data.text))
