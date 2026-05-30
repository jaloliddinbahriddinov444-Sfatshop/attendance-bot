"""Davomat boti - asosiy fayl (Render mosligi)"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, PUBLIC_URL, OFFICE_PUBLIC_IPS, DB_PATH
from database import init_db
from services.wifi_verify import start_verify_server

# Handlerlar
from handlers import common, registration, attendance, profile, admin


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    # Bazani ishga tushirish
    init_db()
    logger.info("📊 Database: %s", DB_PATH)
    logger.info("🌐 Public URL: %s", PUBLIC_URL or "(local rejim)")
    logger.info("🏢 Office IPs: %s", OFFICE_PUBLIC_IPS or "(filtr yo'q)")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Routerlar tartibi muhim — common eng oxirida
    dp.include_routers(
        registration.router,
        attendance.router,
        admin.router,
        profile.router,
        common.router,
    )

    me = await bot.get_me()
    logger.info("🤖 Bot ishga tushdi: @%s (id=%s)", me.username, me.id)

    # Web serverni ishga tushirish (verify + face)
    runner = await start_verify_server()

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
