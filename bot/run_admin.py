import asyncio

import uvicorn
from starlette.applications import Starlette

from bot.admin.setup import setup_admin
from bot.core.config import settings
from bot.core.logging import setup_logging
from bot.tarot.admin import HistoryAdmin, CardAdmin, DailyCardAdmin


def setup_app() -> Starlette:
    app = Starlette(debug=settings.IS_DEBUG)
    admin = setup_admin(app)
    admin.add_view(HistoryAdmin)
    admin.add_view(CardAdmin)
    admin.add_view(DailyCardAdmin)
    return app


def setup_server() -> uvicorn.Server:
    return uvicorn.Server(
        uvicorn.Config(
            setup_app(),
            host=settings.admin.ADMIN_HOST,
            port=settings.admin.ADMIN_PORT,
            loop="uvloop",
            log_config=None,
        )
    )


if __name__ == "__main__":
    setup_logging()
    asyncio.run(setup_server().serve())
