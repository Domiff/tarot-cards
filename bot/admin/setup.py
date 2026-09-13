from starlette.requests import Request
from starlette.applications import Starlette
from sqladmin import Admin, I18nConfig
from sqladmin._menu import CategoryMenu

from bot.admin.auth import AdminAuth
from bot.core.config import settings
from bot.core.database import session_maker


def _category_is_visible(self: CategoryMenu, request: Request) -> bool:
    return any(
        child.is_visible(request) and child.is_accessible(request)
        for child in self.children
    )


def setup_admin(app: Starlette) -> Admin:
    CategoryMenu.is_visible = _category_is_visible

    return Admin(
        app,
        session_maker=session_maker,
        base_url="/admin",
        title="Tarot admin",
        templates_dir="templates",
        authentication_backend=AdminAuth(
            secret_key=settings.admin.ADMIN_SECRET_KEY,
            https_only=not settings.IS_DEBUG,
        ),
        i18n_config=I18nConfig(
            default_locale="ru",
            language_switcher=["en", "az", "de", "ru", "tr"],
        ),
    )
