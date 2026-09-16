from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.core.database import Base


class History(Base):
    __tablename__ = "history"

    text: Mapped[str] = mapped_column(Text)

    def __str__(self) -> str:
        return "История карт Таро"


class Card(Base):
    __tablename__ = "cards"

    name: Mapped[str] = mapped_column(String(length=64), unique=True)
    description: Mapped[str] = mapped_column(String(length=1024))
    image: Mapped[str | None] = mapped_column(String(length=255))
    daily_card: Mapped["DailyCard | None"] = relationship(
        back_populates="card", cascade="all, delete-orphan", lazy="selectin"
    )

    def __str__(self) -> str:
        return self.name


class DailyCard(Base):
    __tablename__ = "daily_cards"

    text: Mapped[str] = mapped_column(Text)
    card_id: Mapped[int] = mapped_column(
        ForeignKey("cards.id", ondelete="CASCADE"), unique=True
    )
    card: Mapped[Card] = relationship(
        back_populates="daily_card", lazy="selectin"
    )

    def __str__(self) -> str:
        return self.card.name
