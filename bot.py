import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
import database as db
from handlers import user, admin, elon

# Logging
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Routerlarni ulash
dp.include_router(user.router)
dp.include_router(admin.router)
dp.include_router(elon.router)

async def main():
    # Bazani yaratish
    db.create_tables()
    print("✅ Bot ishga tushdi!")
    # Polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
