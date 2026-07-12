import asyncio, sys
sys.path.insert(0, "/opt/davomat")
async def main():
    from config import BOT_TOKEN, DB_PATH, PUBLIC_URL, OFFICE_PUBLIC_IPS
    print("✅ config yuklandi. DB:", DB_PATH, "| Office IPs:", OFFICE_PUBLIC_IPS)
    from database import init_db, get_all_employees
    init_db()
    emps = get_all_employees(active_only=True)
    print(f"✅ baza ochildi — faol xodimlar: {len(emps)}")
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    me = await bot.get_me()
    print(f"✅ Telegram token ISHLAYAPTI — bot: @{me.username} (id={me.id})")
    from services.wifi_verify import start_verify_server
    runner = await start_verify_server(bot)
    print("✅ Web server ishga tushdi (port 9090)")
    await asyncio.sleep(1)
    await runner.cleanup()
    await bot.session.close()
    print("✅✅✅ HAMMA TEST OʻTDI — bot tayyor")
asyncio.run(main())
