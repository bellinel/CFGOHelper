import logging
from aiogram import Bot, Dispatcher
from database.engine import Database
from user.user_handlers import user_router
from admin.admin_handlers import admin_router
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))

dp = Dispatcher()

dp.include_router(user_router)
dp.include_router(admin_router)


async def main():
    db = Database()
    await db.init()
    logging.basicConfig(level=logging.INFO)
    print('Bot is running...')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())