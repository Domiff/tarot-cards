from typing import Any, Callable

from starlette.requests import Request
from sqladmin.filters import OperationColumnFilter, BooleanFilter, ForeignKeyFilter
from sqlalchemy import Select


class RuOperationColumnFilter(OperationColumnFilter):
    def get_operation_options(self, column_obj: Any) -> list[tuple[str, str]]:
        if self._is_string_type(column_obj):
            return [
                ("contains", "Содержит"),
                ("equals", "Равно"),
                ("starts_with", "Начинается с"),
                ("ends_with", "Заканчивается на"),
            ]

        if self._is_numeric_type(column_obj):
            return [
                ("equals", "Равно"),
                ("greater_than", "Больше"),
                ("less_than", "Меньше"),
            ]

        if self._is_date_type(column_obj):
            return [
                ("equals", "В этот день"),
                ("greater_than", "После"),
                ("less_than", "До"),
            ]

        if self._is_uuid_type(column_obj):
            return [
                ("equals", "Равно"),
                ("contains", "Содержит"),
                ("starts_with", "Начинается с"),
            ]

        return [
            ("equals", "Равно"),
        ]


class RuBooleanFilter(BooleanFilter):
    def __init__(
        self,
        *args: Any,
        all_label: str = "Все",
        true_label: str = "Да",
        false_label: str = "Нет",
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.all_label = all_label
        self.true_label = true_label
        self.false_label = false_label

    async def lookups(
        self,
        request: Request,
        model: Any,
        run_query: Callable[[Select], Any],
    ) -> list[tuple[str, str]]:
        return [
            ("all", self.all_label),
            ("true", self.true_label),
            ("false", self.false_label),
        ]


class RuForeignKeyFilter(ForeignKeyFilter):
    def __init__(self, *args: Any, all_label: str = "Все", **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.all_label = all_label

    async def lookups(
        self,
        request: Request,
        model: Any,
        run_query: Callable[[Select], Any],
    ) -> list[tuple[str, str]]:
        options = await super().lookups(request, model, run_query)
        return [(options[0][0], self.all_label), *options[1:]]
