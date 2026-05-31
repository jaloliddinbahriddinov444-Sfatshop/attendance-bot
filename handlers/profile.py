"""Profil va statistika ko'rsatish"""
from datetime import datetime, timedelta
from tzutil import now as tz_now, to_local
from aiogram import Router, F
from aiogram.types import Message

import texts
import keyboards as kb
from database import (
    get_employee_by_telegram_id, get_monthly_attendance, get_office_config,
    get_monthly_worked_minutes, get_salary_totals_by_type,
    get_active_salary_entries
)

router = Router()


@router.message(F.text == texts.BTN_PROFILE)
async def show_profile(message: Message):
    employee = get_employee_by_telegram_id(message.from_user.id)
    if not employee:
        await message.answer(texts.NOT_REGISTERED)
        return

    registered = to_local(employee["registered_at"]).strftime("%d.%m.%Y")
    admin_badge = texts.ADMIN_BADGE if employee["is_admin"] else ""

    await message.answer(
        texts.PROFILE_INFO.format(
            name=employee["full_name"],
            phone=employee["phone"],
            position=employee["position"],
            registered=registered,
            admin_badge=admin_badge,
        ),
        reply_markup=kb.main_menu_kb(is_admin=bool(employee["is_admin"]), is_boss=(employee["role"] == "boss"))
    )


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
        await message.answer(
            texts.NO_STATS,
            reply_markup=kb.main_menu_kb(is_admin=bool(employee["is_admin"]), is_boss=(employee["role"] == "boss"))
        )
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
        reply_markup=kb.main_menu_kb(is_admin=bool(employee["is_admin"]), is_boss=(employee["role"] == "boss"))
    )


@router.message(F.text == texts.BTN_SALARY)
async def show_salary(message: Message):
    """Xodim — joriy oy ish haqqi xulosasi"""
    employee = get_employee_by_telegram_id(message.from_user.id)
    if not employee:
        await message.answer(texts.NOT_REGISTERED)
        return

    rate = employee["hourly_rate"] if "hourly_rate" in employee.keys() else 0
    if not rate or rate == 0:
        await message.answer(
            texts.SALARY_NO_RATE,
            reply_markup=kb.main_menu_kb(is_admin=bool(employee["is_admin"]), is_boss=(employee["role"] == "boss"))
        )
        return

    now = tz_now()
    year, month = now.year, now.month

    # Ishlangan daqiqalar
    minutes = get_monthly_worked_minutes(employee["id"], year, month)
    hours = minutes // 60
    mins = minutes % 60

    # Asosiy ish haqqi (soatbay)
    base = int((minutes / 60.0) * rate)

    # Kategoriyalar bo'yicha
    totals = get_salary_totals_by_type(employee["id"], year, month)

    # Jami hisoblash: +ish haqqi −avans −jarima +mukofot +bonus −mahsulot
    total = (base
             - totals["avans"]
             - totals["jarima"]
             + totals["mukofot"]
             + totals["bonus"]
             - totals["mahsulot"])

    summary = texts.SALARY_HEADER.format(
        month=texts.MONTHS_UZ[month], year=year,
        hours=hours, minutes=mins,
        rate=rate,
        base=base,
        avans=totals["avans"],
        jarima=totals["jarima"],
        mukofot=totals["mukofot"],
        bonus=totals["bonus"],
        mahsulot=totals["mahsulot"],
        total=total,
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
