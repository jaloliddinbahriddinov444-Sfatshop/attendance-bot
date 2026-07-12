"""Profil va statistika ko'rsatish"""
import re
import logging
from datetime import datetime, timedelta
from tzutil import now as tz_now, to_local
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import texts
import keyboards as kb
from states import CardUpdate
from database import (
    get_employee_by_telegram_id, get_monthly_attendance, get_office_config,
    get_monthly_worked_minutes, get_salary_totals_by_type,
    get_active_salary_entries, update_employee_card,
    get_position, get_monthly_base_salary,
)

logger = logging.getLogger(__name__)
router = Router()


def _menu_for(employee):
    return kb.main_menu_kb(is_admin=bool(employee["is_admin"]),
                           is_boss=(employee["role"] == "boss"))


@router.message(F.text == texts.BTN_PROFILE)
async def show_profile(message: Message):
    employee = get_employee_by_telegram_id(message.from_user.id)
    if not employee:
        await message.answer(texts.NOT_REGISTERED)
        return

    registered = to_local(employee["registered_at"]).strftime("%d.%m.%Y")
    admin_badge = texts.ADMIN_BADGE if employee["is_admin"] else ""
    card = texts.format_card(
        employee["card_number"] if "card_number" in employee.keys() else "",
        employee["card_holder_name"] if "card_holder_name" in employee.keys() else "",
    )

    await message.answer(
        texts.PROFILE_INFO.format(
            name=employee["full_name"],
            phone=employee["phone"],
            position=employee["position"],
            card=card,
            registered=registered,
            admin_badge=admin_badge,
        ),
        reply_markup=kb.profile_card_inline_kb()
    )


# ===== Phase 4: karta ma'lumotlarini yangilash =====

@router.callback_query(F.data == "profile_card")
async def card_update_start(call: CallbackQuery, state: FSMContext):
    emp = get_employee_by_telegram_id(call.from_user.id)
    if not emp:
        await call.answer(texts.NOT_REGISTERED, show_alert=True)
        return
    await state.update_data(card_emp_id=emp["id"])
    await call.message.answer(texts.CARD_UPDATE_ASK_NUMBER, reply_markup=kb.cancel_kb())
    await state.set_state(CardUpdate.waiting_number)
    await call.answer()


@router.message(CardUpdate.waiting_number, F.text == texts.BTN_CANCEL)
@router.message(CardUpdate.waiting_holder_name, F.text == texts.BTN_CANCEL)
async def card_update_cancel(message: Message, state: FSMContext):
    await state.clear()
    emp = get_employee_by_telegram_id(message.from_user.id)
    await message.answer(
        texts.CANCELLED,
        reply_markup=_menu_for(emp) if emp else kb.remove_kb()
    )


@router.message(CardUpdate.waiting_number, F.text)
async def card_update_number(message: Message, state: FSMContext):
    digits = re.sub(r"\D", "", message.text)
    if len(digits) != 16:
        await message.answer(texts.CARD_INVALID_NUMBER)
        return
    await state.update_data(card_number=digits)
    await message.answer(texts.CARD_ASK_HOLDER)
    await state.set_state(CardUpdate.waiting_holder_name)


@router.message(CardUpdate.waiting_number)
async def card_update_number_invalid(message: Message):
    await message.answer(texts.CARD_INVALID_NUMBER)


@router.message(CardUpdate.waiting_holder_name, F.text)
async def card_update_holder(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 3:
        await message.answer(texts.CARD_INVALID_HOLDER)
        return
    data = await state.get_data()
    emp_id = data.get("card_emp_id")
    update_employee_card(emp_id, data["card_number"], name)
    await state.clear()

    emp = get_employee_by_telegram_id(message.from_user.id)
    formatted = texts.format_card(data["card_number"], name)
    await message.answer(
        texts.CARD_UPDATE_SUCCESS.format(card=formatted),
        reply_markup=_menu_for(emp) if emp else kb.remove_kb()
    )
    logger.info("Card updated via profile for employee id=%s", emp_id)


@router.message(CardUpdate.waiting_holder_name)
async def card_update_holder_invalid(message: Message):
    await message.answer(texts.CARD_INVALID_HOLDER)


@router.message(F.text == texts.BTN_STATS)
async def show_stats(message: Message):
    employee = get_employee_by_telegram_id(message.from_user.id)
    if not employee:
        await message.answer(texts.NOT_REGISTERED)
        return

    now = tz_now()
    year, month = now.year, now.month
    records = get_monthly_attendance(employee["id"], year, month)

    if not records:
        await message.answer(texts.NO_STATS, reply_markup=kb.stats_inline_kb())
        return

    cfg = get_office_config()
    try:
        ws_h, ws_m = map(int, cfg["work_start"].split(":"))
    except Exception:
        ws_h, ws_m = 9, 0

    late_count = 0
    worked_minutes_total = 0
    days_with_full_data = 0
    details_lines = []

    for rec in records:
        day_str = rec["day"]
        first_in = rec["first_in"]
        last_out = rec["last_out"]

        line = f"📅 {day_str}: "
        if first_in:
            line += f"🟢 {first_in[:5]}"
            # Kechikish tekshiruvi
            try:
                in_h, in_m, _ = map(int, first_in.split(":"))
                in_minutes = in_h * 60 + in_m
                start_minutes = ws_h * 60 + ws_m
                if in_minutes > start_minutes:
                    late_count += 1
            except Exception:
                pass
        else:
            line += "—"

        if last_out:
            line += f" → 🔴 {last_out[:5]}"
            if first_in:
                try:
                    in_h, in_m, _ = map(int, first_in.split(":"))
                    out_h, out_m, _ = map(int, last_out.split(":"))
                    minutes = (out_h * 60 + out_m) - (in_h * 60 + in_m)
                    if minutes > 0:
                        worked_minutes_total += minutes
                        days_with_full_data += 1
                        line += f" ({minutes // 60}s {minutes % 60}d)"
                except Exception:
                    pass
        details_lines.append(line)

    avg_str = "—"
    if days_with_full_data > 0:
        avg_min = worked_minutes_total // days_with_full_data
        avg_str = f"{avg_min // 60}s {avg_min % 60}d"

    await message.answer(
        texts.STATS_HEADER.format(
            month=texts.MONTHS_UZ[month], year=year,
            days=len(records), late=late_count, avg=avg_str,
            details="\n".join(details_lines[:15])  # Eng yangi 15 kun
        ),
        reply_markup=kb.stats_inline_kb()
    )


@router.message(F.text == texts.BTN_SALARY)
async def show_salary(message: Message):
    """Xodim — joriy oy ish haqqi xulosasi (kunlik yoki soatbay stavka)"""
    employee = get_employee_by_telegram_id(message.from_user.id)
    if not employee:
        await message.answer(texts.NOT_REGISTERED)
        return

    now = tz_now()
    year, month = now.year, now.month

    daily_rate = employee["daily_rate"] if "daily_rate" in employee.keys() else 0
    position_id = employee["position_id"] if "position_id" in employee.keys() else None
    hourly_rate = employee["hourly_rate"] if "hourly_rate" in employee.keys() else 0

    # Asosiy ish haqqini hisoblash
    base = get_monthly_base_salary(employee["id"], year, month)

    if not base and not daily_rate and not hourly_rate:
        await message.answer(
            texts.SALARY_NO_RATE,
            reply_markup=kb.main_menu_kb(is_admin=bool(employee["is_admin"]), is_boss=(employee["role"] == "boss"))
        )
        return

    totals = get_salary_totals_by_type(employee["id"], year, month)
    total = (base - totals["avans"] - totals["jarima"]
             + totals["mukofot"] + totals["bonus"] - totals["mahsulot"])

    # Yangi kunlik stavka tizimi
    if daily_rate and position_id:
        pos = get_position(position_id)
        records = get_monthly_attendance(employee["id"], year, month)
        days_worked = sum(1 for r in records if r["first_in"] and r["last_out"])
        summary = texts.SALARY_HEADER_DAILY.format(
            month=texts.MONTHS_UZ[month], year=year,
            position=pos["name"] if pos else employee["position"],
            work_hours=pos["work_hours"] if pos else 9,
            daily_rate=daily_rate,
            days=days_worked,
            base=base,
            avans=totals["avans"], jarima=totals["jarima"],
            mukofot=totals["mukofot"], bonus=totals["bonus"],
            mahsulot=totals["mahsulot"], total=total,
        )
    else:
        # Eski soatbay tizim
        minutes = get_monthly_worked_minutes(employee["id"], year, month)
        summary = texts.SALARY_HEADER.format(
            month=texts.MONTHS_UZ[month], year=year,
            hours=minutes // 60, minutes=minutes % 60,
            rate=hourly_rate, base=base,
            avans=totals["avans"], jarima=totals["jarima"],
            mukofot=totals["mukofot"], bonus=totals["bonus"],
            mahsulot=totals["mahsulot"], total=total,
        )

    # Yozuvlar tafsiloti (sabab bilan)
    entries = get_active_salary_entries(employee["id"], year, month)
    if entries:
        details = texts.SALARY_DETAILS_HEADER
        for entry in entries:
            type_info = texts.SALARY_TYPES.get(entry["entry_type"], ("📋", "?", ""))
            emoji, type_name, sign = type_info
            try:
                d = to_local(entry["created_at"])
                date_str = d.strftime("%d.%m")
            except Exception:
                date_str = "—"
            details += texts.SALARY_DETAIL_LINE.format(
                date=date_str, emoji=emoji, type_name=type_name,
                sign=sign, amount=entry["amount"],
                reason=entry["reason"] or "—"
            )
    else:
        details = texts.SALARY_DETAILS_EMPTY

    await message.answer(
        summary + details,
        reply_markup=kb.main_menu_kb(is_admin=bool(employee["is_admin"]), is_boss=(employee["role"] == "boss"))
    )
