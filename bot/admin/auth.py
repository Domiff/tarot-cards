import secrets

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from bot.core.config import settings
from bot.core.logging import get_logger

logger = get_logger(__name__)


class AdminAuth(AuthenticationBackend):
    SESSION_USER_KEY = "admin"

    @staticmethod
    def _verify(username: str, password: str) -> bool:
        valid_username = secrets.compare_digest(
            username.encode(), settings.admin.ADMIN_USERNAME.encode()
        )
        valid_password = secrets.compare_digest(
            password.encode(), settings.admin.ADMIN_PASSWORD.encode()
        )
        return valid_username and valid_password

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = str(form.get("username", ""))
        password = str(form.get("password", ""))

        if not self._verify(username, password):
            logger.warning(
                "admin_login_failed",
                extra={"username": username},
            )
            return False

        request.session.update({self.SESSION_USER_KEY: username})
        logger.info("admin_login_success", extra={"username": username})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return secrets.compare_digest(
            str(request.session.get(self.SESSION_USER_KEY, "")).encode(),
            settings.admin.ADMIN_USERNAME.encode(),
        )
