from html import escape
from typing import Sequence

from bot.tarot.models import Card

HEADER = "🔮 <b>Колода Таро</b>"
EMPTY = "🔮 В колоде пока нет ни одной карты."
MAJOR_TITLE = "🌟 Старшие арканы"
HINT = "Отправьте /card и название карты, например <code>/card Шут</code>."
NOT_FOUND = "🤷 Карта <b>{query}</b> не найдена.\n\n{hint}"
CHOOSE_CARD = "Выберите карту."
SUITS: tuple[tuple[str, str], ...] = (
    ("Жезлов", "🪄 Жезлы"),
    ("Кубков", "🏆 Кубки"),
    ("Мечей", "⚔️ Мечи"),
    ("Пентаклей", "🪙 Пентакли"),
)


GROUPS: tuple[str, ...] = (MAJOR_TITLE, *(title for _, title in SUITS))


def group_index(card: Card) -> int:
    """Индекс аркана: он же значение в callback_data, поэтому не строка."""
    for index, (suffix, _) in enumerate(SUITS, start=1):
        if card.name.endswith(suffix):
            return index
    return 0


def group_cards(cards: Sequence[Card], index: int) -> list[Card]:
    """Карты аркана в порядке колоды: сортировка по алфавиту ломает её строй."""
    return sorted(
        (card for card in cards if group_index(card) == index),
        key=lambda card: card.id,
    )


def format_deck(cards: Sequence[Card]) -> str:
    return f"{HEADER}\nВсего карт: <b>{len(cards)}</b>"


def format_group(index: int, cards: Sequence[Card]) -> str:
    return f"<b>{GROUPS[index]}</b> · {len(cards)}\n\n{CHOOSE_CARD}"


def format_card(card: Card) -> str:
    return f"🃏 <b>{escape(card.name)}</b>\n\n{escape(card.description)}"


def format_not_found(query: str) -> str:
    return NOT_FOUND.format(query=escape(query), hint=HINT)
