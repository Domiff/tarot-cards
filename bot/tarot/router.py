from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from sqlalchemy.exc import NoResultFound

from bot.tarot.keyboards import (
    DeckCallback,
    card_keyboard,
    cards_keyboard,
    groups_keyboard,
)
from bot.tarot.repository import get_history, get_cards, get_card
from bot.tarot.service import (
    EMPTY,
    HINT,
    format_card,
    format_deck,
    format_group,
    format_not_found,
    group_cards,
    group_index,
)

router = Router()


async def _edit(query: CallbackQuery, text: str, markup: InlineKeyboardMarkup) -> None:
    """Повторное нажатие той же кнопки ничего не меняет — Telegram отвечает ошибкой."""
    try:
        await query.message.edit_text(text, reply_markup=markup)
    except TelegramBadRequest as error:
        if "message is not modified" not in str(error):
            raise
    finally:
        await query.answer()


@router.message(Command("history"))
async def history(message: Message) -> None:
    data = await get_history()
    await message.answer(str(data.text))


@router.message(Command("cards"))
async def cards(message: Message) -> None:
    deck = await get_cards()

    if not deck:
        await message.answer(EMPTY)
        return

    await message.answer(format_deck(deck), reply_markup=groups_keyboard(deck))


@router.callback_query(DeckCallback.filter(F.action == "deck"))
async def show_deck(query: CallbackQuery) -> None:
    deck = await get_cards()
    await _edit(query, format_deck(deck), groups_keyboard(deck))


@router.callback_query(DeckCallback.filter(F.action == "group"))
async def show_group(query: CallbackQuery, callback_data: DeckCallback) -> None:
    group = group_cards(await get_cards(), callback_data.value)
    await _edit(
        query,
        format_group(callback_data.value, group),
        cards_keyboard(group),
    )


@router.callback_query(DeckCallback.filter(F.action == "card"))
async def show_card(query: CallbackQuery, callback_data: DeckCallback) -> None:
    deck = await get_cards()
    card = next((item for item in deck if item.id == callback_data.value), None)

    if card is None:
        await query.answer("Карта не найдена", show_alert=True)
        return

    await _edit(query, format_card(card), card_keyboard(group_index(card)))


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
