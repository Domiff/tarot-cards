from textwrap import shorten
from typing import Any

from markupsafe import Markup
from wtforms.validators import Length
import sqladmin

from bot.admin.base import BaseAdmin
from bot.admin.filters import RuOperationColumnFilter
from bot.tarot.models import Card, DailyCard, History

MESSAGE_LIMIT = 4096
CATEGORY = "Таро"
CATEGORY_ICON = "fa-solid fa-wand-magic-sparkles"


def _max_len(limit: int) -> Length:
    return Length(max=limit, message=f"Не длиннее {limit} символов")


def _preview(length: int = 80, max_width: str = "42ch"):
    """Усечённый текст, который переносится по словам вместо горизонтальной прокрутки."""

    def formatter(model: Any, attribute: str) -> Markup:
        value = shorten(getattr(model, attribute) or "", width=length, placeholder="…")
        return Markup(
            '<span class="d-inline-block text-wrap" style="max-width: {width}">{text}</span>'
        ).format(width=max_width, text=value)

    return formatter


class CardAdmin(BaseAdmin, model=Card):
    column_list = [Card.name, Card.description, Card.image, Card.updated_at]
    column_details_list = [
        Card.name,
        Card.description,
        Card.image,
        Card.created_at,
        Card.updated_at,
    ]
    column_labels = {
        Card.name: "Название",
        Card.description: "Краткое описание",
        Card.image: "Картинка",
        Card.daily_card: "Карта дня",
        Card.created_at: "Создана",
        Card.updated_at: "Изменена",
    }
    column_formatters = {Card.description: _preview()}
    column_searchable_list = [Card.name, Card.description]
    column_sortable_list = [Card.name, Card.updated_at]
    column_default_sort = [(Card.name, False)]
    column_filters = [RuOperationColumnFilter(Card.name, title="Название")]

    form_columns = [Card.name, Card.description, Card.image]
    form_args = {
        "name": {"validators": [_max_len(64)]},
        "description": {"validators": [_max_len(1024)]},
    }
    form_widget_args = {
        "description": {"rows": 8},
        "image": {"placeholder": "media/cards/sun.jpg"},
    }

    can_delete = False

    name = "Карта"
    name_plural = "Карты"
    icon = "fa-solid fa-clone"
    category = CATEGORY
    category_icon = CATEGORY_ICON


class DailyCardAdmin(BaseAdmin, model=DailyCard):
    column_list = [DailyCard.card, DailyCard.text, DailyCard.updated_at]
    column_details_list = [
        DailyCard.card,
        DailyCard.text,
        DailyCard.created_at,
        DailyCard.updated_at,
    ]
    column_labels = {
        DailyCard.card: "Карта",
        DailyCard.text: "Текст поста",
        DailyCard.created_at: "Создана",
        DailyCard.updated_at: "Изменена",
    }
    column_formatters = {DailyCard.text: _preview(100)}
    column_searchable_list = [DailyCard.text]
    column_sortable_list = [DailyCard.updated_at]

    form_columns = [DailyCard.card, DailyCard.text]
    form_args = {"text": {"validators": [_max_len(MESSAGE_LIMIT)]}}
    form_widget_args = {"text": {"rows": 20}}

    name = "Карта дня"
    name_plural = "Карты дня"
    icon = "fa-solid fa-sun"
    category = CATEGORY
    category_icon = CATEGORY_ICON


class HistoryAdmin(BaseAdmin, model=History):
    column_list = [History.text, History.updated_at]
    column_labels = {
        History.text: "Текст",
        History.created_at: "Создана",
        History.updated_at: "Изменена",
    }
    column_formatters = {History.text: _preview(100)}
    column_searchable_list = [History.text]
    column_sortable_list = [History.updated_at]

    form_columns = [History.text]
    form_args = {"text": {"validators": [_max_len(MESSAGE_LIMIT)]}}
    form_widget_args = {"text": {"rows": 24}}

    name = "История Таро"
    name_plural = "История Таро"
    icon = "fa-solid fa-book"
    category = CATEGORY
    category_icon = CATEGORY_ICON
