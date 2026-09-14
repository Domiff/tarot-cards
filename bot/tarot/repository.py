from typing import Sequence

from sqlalchemy import select

from bot.core.database import session_maker
from bot.tarot.models import History, Card, DailyCard


async def get_history() -> History | None:
    async with session_maker() as session:
        query = select(History)
        history = await session.execute(query)
        return history.scalar_one_or_none()


async def get_cards() -> Sequence[Card]:
    async with session_maker() as session:
        query = select(Card)
        cards = await session.execute(query)
        return cards.scalars().all()


async def get_daily_card() -> DailyCard:
    async with session_maker() as session:
        query = select(DailyCard)
        daily_card = await session.execute(query)
        return daily_card.scalar_one()
