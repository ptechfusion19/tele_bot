# bot.py
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from middlewares import CancelFSMOnNewEventMiddleware
from handlers import auth, admin, user, review, media


async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(CancelFSMOnNewEventMiddleware())
    dp.callback_query.middleware(CancelFSMOnNewEventMiddleware())

    dp.include_router(auth.router)
    dp.include_router(admin.router)
    dp.include_router(user.router)
    dp.include_router(review.router)
    dp.include_router(media.router)

    print("🤖 Bot is running...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped.")
