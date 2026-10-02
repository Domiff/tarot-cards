from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from bot.tarot.cache import CARDS_KEY, HISTORY_KEY, get_cached
from bot.tarot.keyboards import (
    DeckCallback,
    card_keyboard,
    cards_keyboard,
    groups_keyboard,
)
from bot.tarot.repository import get_history, get_cards
from bot.tarot.schemas import (
    DeckAdapter,
    HistoryAdapter,
)
from bot.tarot.service import (
    EMPTY,
    EMPTY_HISTORY,
    HINT,
    format_card,
    format_deck,
    format_group,
    format_not_found,
    group_cards,
    group_index,
)

router = Router()


CAPTION_LIMIT = 1024


def _photo(card: CardSchema, caption: str) -> URLInputFile | None:
    if not card.image or len(caption) > CAPTION_LIMIT:
        return None

    return URLInputFile(card.image, filename=f"{card.id}.jpg")


async def _send(message: Message, card: CardSchema, text: str) -> None:
    photo = _photo(card, text)

    if photo is None:
        await message.answer(text)
        return

    await message.answer_photo(photo, caption=text)


async def _render(
    query: CallbackQuery,
    text: str,
    markup: InlineKeyboardMarkup,
    photo: URLInputFile | None = None,
) -> None:
    message = query.message

    try:
        if photo is not None:
            await message.answer_photo(photo, caption=text, reply_markup=markup)
            await message.delete()
        elif message.photo:
            await message.delete()
            await message.answer(text, reply_markup=markup)
        else:
            await message.edit_text(text, reply_markup=markup)
    except TelegramBadRequest as error:
        if "message is not modified" not in str(error):
            raise
    finally:
        await query.answer()


@router.message(Command("history"))
async def history_command(message: Message) -> None:
    history = await get_cached(HISTORY_KEY, HistoryAdapter, get_history)

    await message.answer(history.text if history else EMPTY_HISTORY)


@router.message(Command("cards"))
async def cards_command(message: Message) -> None:
    deck = await get_cached(CARDS_KEY, DeckAdapter, get_cards)

    if not deck:
        await message.answer(EMPTY)
        return

    await message.answer(format_deck(deck), reply_markup=groups_keyboard(deck))


@router.callback_query(DeckCallback.filter(F.action == "deck"))
async def deck_callback(query: CallbackQuery) -> None:
    deck = await get_cached(CARDS_KEY, DeckAdapter, get_cards)
    await _edit(query, format_deck(deck), groups_keyboard(deck))


@router.callback_query(DeckCallback.filter(F.action == "group"))
async def group_callback(query: CallbackQuery, callback_data: DeckCallback) -> None:
    deck = await get_cached(CARDS_KEY, DeckAdapter, get_cards)
    group = group_cards(deck, callback_data.value)
    await _edit(
        query,
        format_group(callback_data.value, group),
        cards_keyboard(group),
    )


@router.callback_query(DeckCallback.filter(F.action == "card"))
async def card_callback(query: CallbackQuery, callback_data: DeckCallback) -> None:
    deck = await get_cached(CARDS_KEY, DeckAdapter, get_cards)
    card = next((item for item in deck if item.id == callback_data.value), None)

    if card is None:
        await query.answer("Карта не найдена", show_alert=True)
        return

    await _edit(query, format_card(card), card_keyboard(group_index(card)))


@router.message(Command("card"))
async def card_command(message: Message, command: CommandObject) -> None:
    name = (command.args or "").strip()

    if not name:
        await message.answer(HINT)
        return

    deck = await get_cached(CARDS_KEY, DeckAdapter, get_cards)

    wanted = name.casefold()
    found = next((card for card in deck if card.name.casefold() == wanted), None)

    if found is None:
        await message.answer(format_not_found(name))
        return

    await message.answer(format_card(found))
