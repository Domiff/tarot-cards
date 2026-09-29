from html import escape
from typing import Sequence

from bot.tarot.models import Card

MESSAGE_LIMIT = 4096
HEADER = "🔮 <b>Колода Таро</b>"
EMPTY = "🔮 В колоде пока нет ни одной карты."
MAJOR_TITLE = "🌟 Старшие арканы"
HINT = "Отправьте /card и название карты, например <code>/card Шут</code>."
NOT_FOUND = "🤷 Карта <b>{query}</b> не найдена.\n\n{hint}"
SUITS: tuple[tuple[str, str], ...] = (
    ("Жезлов", "🪄 Жезлы"),
    ("Кубков", "🏆 Кубки"),
    ("Мечей", "⚔️ Мечи"),
    ("Пентаклей", "🪙 Пентакли"),
)


def _title(card: Card) -> str:
    for suffix, title in SUITS:
        if card.name.endswith(suffix):
            return title
    return MAJOR_TITLE


def _group(cards: Sequence[Card]) -> dict[str, list[Card]]:
    """Карты по арканам в порядке колоды: сортировка по алфавиту ломает её строй."""
    titles = [MAJOR_TITLE] + [title for _, title in SUITS]
    groups: dict[str, list[Card]] = {title: [] for title in titles}

    for card in sorted(cards, key=lambda card: card.id):
        groups[_title(card)].append(card)

    return {title: group for title, group in groups.items() if group}


def _block(title: str, cards: list[Card]) -> str:
    """Свернутая цитата: в чате видно заголовок, список раскрывается по тапу."""
    names = "\n".join(escape(card.name) for card in cards)
    return f"<b>{title}</b> · {len(cards)}\n<blockquote expandable>{names}</blockquote>"


def format_cards(cards: Sequence[Card]) -> list[str]:
    """Колода по арканам, готовая к отправке в HTML."""
    if not cards:
        return [EMPTY]

    blocks = [f"{HEADER}\nВсего карт: <b>{len(cards)}</b>"]
    blocks += [_block(title, group) for title, group in _group(cards).items()]

    messages: list[str] = []
    chunk = ""

    for block in blocks:
        if len(chunk) + len(block) + 2 > MESSAGE_LIMIT:
            messages.append(chunk)
            chunk = ""
        chunk = f"{chunk}\n\n{block}" if chunk else block

    if chunk:
        messages.append(chunk)

    return messages


def format_card(card: Card) -> str:
    return f"🃏 <b>{escape(card.name)}</b>\n\n{escape(card.description)}"


def format_not_found(query: str) -> str:
    return NOT_FOUND.format(query=escape(query), hint=HINT)
