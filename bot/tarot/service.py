from html import escape

from bot.tarot.schemas import CardSchema, Deck, DailyCardSchema

HEADER = "🔮 <b>Колода Таро</b>"
EMPTY = "🔮 В колоде пока нет ни одной карты."
EMPTY_HISTORY = "🔮 История еще не добавлена."
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


def group_index(card: CardSchema) -> int:
    """Индекс аркана: он же значение в callback_data, поэтому не строка."""
    for index, (suffix, _) in enumerate(SUITS, start=1):
        if card.name.endswith(suffix):
            return index
    return 0


def group_cards(cards: Deck, index: int) -> Deck:
    """Карты аркана в порядке колоды: сортировка по алфавиту ломает её строй."""
    return sorted(
        (card for card in cards if group_index(card) == index),
        key=lambda card: card.id,
    )


def format_deck(cards: Deck) -> str:
    return f"{HEADER}\nВсего карт: <b>{len(cards)}</b>"


def format_group(index: int, cards: Deck) -> str:
    return f"<b>{GROUPS[index]}</b> · {len(cards)}\n\n{CHOOSE_CARD}"


def format_card(card: CardSchema) -> str:
    return f"🃏 <b>{escape(card.name)}</b>\n\n{escape(card.description)}"


def format_daily_card(daily_card: DailyCardSchema) -> str:
    return f"🃏 <b>{escape(daily_card.card.name)}</b>\n\n{escape(daily_card.text)}"


def format_not_found(query: str) -> str:
    return NOT_FOUND.format(query=escape(query), hint=HINT)
