"""Bildirishnomalar bo'limi — Moliya bo'limi ostida (Boss / Bosh Admin).

Uchta ekran:
  📅 Eslatma kunlari   — haftaning qaysi kunlari davomat eslatmasi yuboriladi
  🎉 Bayram kunlari    — eslatma yo'q + o'sha kunga to'liq kunlik stavka
  🏖 Dam olish kunlari — eslatma yo'q, ish haqqi hisoblanmaydi

Kalendar callbacklari:
  cal:{mode}:{YYYY-MM-DD}  — kunni belgilash / belgini olib tashlash
  caln:{mode}:{yil}:{oy}   — oy almashtirish
  cal:close, calnop        — yopish / bo'sh katak
Hafta kunlari: rday:{0..6}, rday:close
"""
import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

import texts
import keyboards as kb
from database import (
    get_employee_by_telegram_id,
    get_calendar_month,
    toggle_calendar_day,
    get_reminder_days,
    toggle_reminder_day,
    HOLIDAY, DAYOFF,
)
import tzutil

logger = logging.getLogger(__name__)
router = Router()

# Kalendarda ruxsat etilgan oy oralig'i (joriy oydan)
NAV_BACK = kb.CAL_NAV_BACK
NAV_FWD = kb.CAL_NAV_FWD

MODE_TYPES = {"h": HOLIDAY, "o": DAYOFF}
MODE_OF_TYPE = {HOLIDAY: "h", DAYOFF: "o"}


def _can_use(emp) -> bool:
    if not emp:
        return False
    try:
        return emp["role"] in ("boss", "bosh_admin")
    except (KeyError, IndexError):
        return False


def _guard(source) -> bool:
    """Foydalanuvchi ruxsatini tekshiradi (message yoki callback uchun)."""
    return _can_use(get_employee_by_telegram_id(source.from_user.id))


def _in_range(year: int, month: int) -> bool:
    d = tzutil.now()
    cur = d.year * 12 + d.month - 1
    val = year * 12 + month - 1
    return cur - NAV_BACK <= val <= cur + NAV_FWD


def _marked_list(year: int, month: int, day_type: str) -> str:
    """Oydagi shu turdagi kunlar ro'yxati matni."""
    days = sorted(d for d, t in get_calendar_month(year, month).items()
                  if t == day_type)
    if not days:
        return texts.CAL_MARKED_NONE
    mark = kb.CAL_MARKS[day_type]
    lines = []
    for d in days:
        weekday = texts.WEEKDAYS_UZ[_weekday(d)]
        lines.append(f"{mark} {d[8:]}.{d[5:7]} ({weekday})")
    return texts.CAL_MARKED_LIST.format(days="\n".join(lines))


def _weekday(date_str: str) -> int:
    from datetime import date
    y, m, d = map(int, date_str.split("-"))
    return date(y, m, d).weekday()


def _cal_text(mode: str, year: int, month: int) -> str:
    day_type = MODE_TYPES[mode]
    tpl = (texts.CAL_HOLIDAY_HEADER if day_type == HOLIDAY
           else texts.CAL_DAYOFF_HEADER)
    return tpl.format(month=texts.MONTHS_UZ[month], year=year) + \
        _marked_list(year, month, day_type)


def _days_text() -> str:
    text = texts.REMIND_DAYS_HEADER
    if not get_reminder_days():
        text += "\n\n" + texts.REMIND_DAYS_ALL_OFF
    return text


async def _safe_edit(call: CallbackQuery, text: str, markup):
    """Xabar o'zgarmasa Telegram xato beradi — uni jimgina yutamiz."""
    try:
        await call.message.edit_text(text, reply_markup=markup)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise


# ===== Bo'lim menyusi =====

@router.message(F.text == texts.BTN_NOTIFICATIONS)
async def notify_open(message: Message, state: FSMContext):
    if not _guard(message):
        await message.answer(texts.FINANCE_NO_PERMISSION)
        return
    await state.clear()
    await message.answer(texts.NOTIFY_MENU, reply_markup=kb.notify_menu_kb())


@router.message(F.text == texts.BTN_NOTIFY_BACK)
async def notify_back(message: Message, state: FSMContext):
    if not _guard(message):
        return
    await state.clear()
    await message.answer(texts.FINANCE_MENU, reply_markup=kb.finance_menu_kb())


# ===== Eslatma kunlari (haftalik jadval) =====

@router.message(F.text == texts.BTN_REMIND_DAYS)
async def remind_days_open(message: Message, state: FSMContext):
    if not _guard(message):
        return
    await state.clear()
    await message.answer(_days_text(), reply_markup=kb.remind_days_kb())


@router.callback_query(F.data.startswith("rday:"))
async def remind_day_toggle(call: CallbackQuery):
    if not _guard(call):
        await call.answer()
        return
    arg = call.data.split(":", 1)[1]
    if arg == "close":
        await call.message.delete()
        await call.answer()
        return
    try:
        index = int(arg)
    except ValueError:
        await call.answer()
        return
    if not 0 <= index <= 6:
        await call.answer()
        return

    state_on = toggle_reminder_day(index)
    logger.info("Eslatma kuni %s -> %s (tg=%s)",
                texts.WEEKDAYS_UZ[index], state_on, call.from_user.id)
    await _safe_edit(call, _days_text(), kb.remind_days_kb())
    await call.answer(texts.REMIND_DAY_TOGGLED.format(
        day=texts.WEEKDAYS_UZ[index],
        state=texts.REMIND_DAY_ON if state_on else texts.REMIND_DAY_OFF,
    ))


# ===== Bayram / dam olish kalendari =====

@router.message(F.text == texts.BTN_HOLIDAYS)
async def holidays_open(message: Message, state: FSMContext):
    await _open_calendar(message, state, "h")


@router.message(F.text == texts.BTN_DAYOFFS)
async def dayoffs_open(message: Message, state: FSMContext):
    await _open_calendar(message, state, "o")


async def _open_calendar(message: Message, state: FSMContext, mode: str):
    if not _guard(message):
        return
    await state.clear()
    d = tzutil.now()
    await message.answer(_cal_text(mode, d.year, d.month),
                         reply_markup=kb.calendar_kb(mode, d.year, d.month))


@router.callback_query(F.data == "calnop")
async def calendar_nop(call: CallbackQuery):
    await call.answer()


@router.callback_query(F.data.startswith("caln:"))
async def calendar_nav(call: CallbackQuery):
    if not _guard(call):
        await call.answer()
        return
    try:
        _, mode, year, month = call.data.split(":")
        year, month = int(year), int(month)
    except ValueError:
        await call.answer()
        return
    if mode not in MODE_TYPES or not 1 <= month <= 12:
        await call.answer()
        return
    if not _in_range(year, month):
        await call.answer(texts.CAL_LIMIT, show_alert=True)
        return
    await _safe_edit(call, _cal_text(mode, year, month),
                     kb.calendar_kb(mode, year, month))
    await call.answer()


@router.callback_query(F.data.startswith("cal:"))
async def calendar_pick(call: CallbackQuery):
    if not _guard(call):
        await call.answer()
        return
    parts = call.data.split(":")
    if len(parts) == 2 and parts[1] == "close":
        await call.message.delete()
        await call.answer()
        return
    if len(parts) != 3:
        await call.answer()
        return

    mode, date_str = parts[1], parts[2]
    if mode not in MODE_TYPES:
        await call.answer()
        return
    try:
        year, month, day = map(int, date_str.split("-"))
        from datetime import date as _date
        _date(year, month, day)
    except (ValueError, TypeError):
        await call.answer()
        return
    if not _in_range(year, month):
        await call.answer(texts.CAL_LIMIT, show_alert=True)
        return

    day_type = MODE_TYPES[mode]
    new_state = toggle_calendar_day(date_str, day_type, call.from_user.id)
    logger.info("Kalendar: %s -> %s (tg=%s)", date_str, new_state,
                call.from_user.id)

    human = f"{date_str[8:]}.{date_str[5:7]}.{date_str[:4]}"
    if new_state == HOLIDAY:
        note = texts.CAL_DAY_SET_HOLIDAY.format(date=human)
    elif new_state == DAYOFF:
        note = texts.CAL_DAY_SET_DAYOFF.format(date=human)
    else:
        note = texts.CAL_DAY_CLEARED.format(date=human)

    await _safe_edit(call, _cal_text(mode, year, month),
                     kb.calendar_kb(mode, year, month))
    await call.answer(note)
