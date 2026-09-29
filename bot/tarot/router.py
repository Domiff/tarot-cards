from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy.exc import NoResultFound

from bot.tarot.repository import get_history, get_cards, get_card
from bot.tarot.service import HINT, format_card, format_cards, format_not_found

router = Router()


@router.message(Command("history"))
async def history(message: Message) -> None:
    data = await get_history()
    await message.answer(str(data.text))


@router.message(Command("cards"))
async def cards(message: Message) -> None:
    deck = await get_cards()

    for text in format_cards(deck):
        await message.answer(text)


@router.message(Command("card"))
async def card(message: Message, command: CommandObject) -> None:
    name = (command.args or "").strip()

    if not name:
        await message.answer(HINT)
        return

    try:
        found = await get_card(name)
    except NoResultFound:
        await message.answer(format_not_found(name))
        return

    await message.answer(format_card(found))
