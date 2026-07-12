"""Avtomatik eslatmalar — polling bilan parallel background task.

Har 60 soniyada tekshiradi (apscheduler'siz, oddiy loop):
  a) pre_start   — ish boshlanishidan 15 daqiqa OLDIN, hali "in" qilmaganlarga
  b) late        — ish boshlanganidan 20 daqiqa KEYIN, hali ham "in"
                   qilmaganlarga + adminlarga bitta jamlanma (late_summary)
  c) forgot_out  — ish tugashidan 10 daqiqa KEYIN, "in" holatida qolganlarga

Takrorlanish himoyasi: reminder_log jadvali (try_mark_reminder, atomik
INSERT OR IGNORE) — har tur har xodimga kuniga 1 marta, restart'da ham.
Yoqish/o'chirish: settings 'reminders_enabled' ('1'/'0', default '1').
"""
import asyncio
import logging

from database import (
    get_dashboard_today, get_office_config, get_setting,
    get_all_admins, try_mark_reminder,
)
from tzutil import now as tz_now

logger = logging.getLogger(__name__)

# Dam olish kunlari — datetime.weekday() raqamlari (0=Dushanba ... 6=Yakshanba).
# Hozircha bo'sh; kelajakda masalan {6} = yakshanba.
WEEKEND_DAYS: set = set()

# Nishon daqiqadan keyin necha daqiqagacha yuborish mumkin (loop kechiksa ham)
WINDOW_MINUTES = 10
CHECK_INTERVAL = 60

# Jamlanma xabar uchun sentinel (haqiqiy xodim id'lari 1 dan boshlanadi)
SUMMARY_SENTINEL_ID = 0


def _parse_hhmm(value: str, fallback: tuple) -> tuple:
    try:
        h, m = map(int, str(value).split(":")[:2])
        return h, m
    except Exception:
        return fallback


async def _safe_send(bot, telegram_id: int, text: str) -> bool:
    """Bitta xodimga yuborilmasa (bot bloklangan) — log yozib davom etamiz."""
    try:
        await bot.send_message(telegram_id, text)
        return True
    except Exception as e:
        logger.warning("Eslatma yuborilmadi (tg=%s): %s", telegram_id, e)
        return False


async def _tick(bot):
    import texts

    now = tz_now()  # Toshkent vaqti (naive)
    if now.weekday() in WEEKEND_DAYS:
        return
    if get_setting("reminders_enabled", "1") != "1":
        return

    cfg = get_office_config()
    ws_h, ws_m = _parse_hhmm(cfg["work_start"], (9, 0))
    we_h, we_m = _parse_hhmm(cfg["work_end"], (18, 0))
    ws_min = ws_h * 60 + ws_m
    we_min = we_h * 60 + we_m

    now_min = now.hour * 60 + now.minute
    today = now.strftime("%Y-%m-%d")

    def in_window(target_min: int) -> bool:
        return target_min <= now_min < target_min + WINDOW_MINUTES

    pre_start = in_window(ws_min - 15)
    late = in_window(ws_min + 20)
    forgot_out = in_window(we_min + 10)
    if not (pre_start or late or forgot_out):
        return

    rows = get_dashboard_today()  # faol xodimlar, boss'siz

    # a) Ish boshlanishidan 15 daqiqa oldin — hali kelmaganlarga
    if pre_start:
        text = texts.REMIND_PRE_START.format(work_start=cfg["work_start"])
        for r in rows:
            if r["last_type"] is None and try_mark_reminder(r["id"], "pre_start", today):
                await _safe_send(bot, r["telegram_id"], text)

    # b) Ish boshlanganidan 20 daqiqa keyin — hali ham kelmaganlarga
    #    + adminlarga bitta jamlanma ro'yxat
    if late:
        absent = [r for r in rows if r["last_type"] is None]
        for r in absent:
            if try_mark_reminder(r["id"], "late", today):
                await _safe_send(bot, r["telegram_id"], texts.REMIND_LATE)
        if absent and try_mark_reminder(SUMMARY_SENTINEL_ID, "late_summary", today):
            names = "\n".join(
                f"{i}. {r['full_name']}" for i, r in enumerate(absent, 1)
            )
            summary = texts.REMIND_ADMIN_SUMMARY.format(
                time=now.strftime("%H:%M"), names=names
            )
            for admin in get_all_admins():
                await _safe_send(bot, admin["telegram_id"], summary)

    # c) Ish tugashidan 10 daqiqa keyin — "Ketdim" ni unutganlarga
    if forgot_out:
        for r in rows:
            if r["last_type"] == "in" and try_mark_reminder(r["id"], "forgot_out", today):
                await _safe_send(bot, r["telegram_id"], texts.REMIND_FORGOT_OUT)


async def reminders_loop(bot):
    """Har 60 soniyada tekshiradigan abadiy sikl — hech qachon yiqilmaydi."""
    logger.info("🔔 Eslatmalar sikli ishga tushdi (har %ss)", CHECK_INTERVAL)
    while True:
        try:
            await _tick(bot)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Eslatma siklida xato — davom etamiz")
        await asyncio.sleep(CHECK_INTERVAL)
