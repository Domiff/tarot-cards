import asyncio

from bot.core.logging import setup_logging
from bot.core.setup import create_bot, create_dispatcher


async def main():
    bot = create_bot()
    dp = create_dispatcher()

    await dp.start_polling(bot)


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
