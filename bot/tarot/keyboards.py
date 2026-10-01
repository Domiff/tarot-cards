from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.tarot.schemas import Deck
from bot.tarot.service import GROUPS, group_cards

BACK_TO_DECK = "◀ К арканам"
BACK_TO_GROUP = "◀ Назад"


class DeckCallback(CallbackData, prefix="deck"):
    """action: deck — список арканов, group — карты аркана, card — одна карта."""

    action: str
    value: int = 0


def groups_keyboard(cards: Deck) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for index, title in enumerate(GROUPS):
        group = group_cards(cards, index)
        if not group:
            continue

        builder.button(
            text=title,
            callback_data=DeckCallback(action="group", value=index),
        )

    builder.adjust(1)
    return builder.as_markup()


def cards_keyboard(cards: Deck) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for card in cards:
        builder.button(
            text=card.name,
            callback_data=DeckCallback(action="card", value=card.id),
        )

    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(
            text=BACK_TO_DECK,
            callback_data=DeckCallback(action="deck").pack(),
        )
    )
    return builder.as_markup()


def card_keyboard(index: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=BACK_TO_GROUP,
        callback_data=DeckCallback(action="group", value=index),
    )
    return builder.as_markup()
