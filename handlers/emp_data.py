"""Admin: Xodimlar ma'lumotlari — lavozim bo'yicha guruhlash + to'liq profil."""
import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import texts
import keyboards as kb
from tzutil import now as tz_now, to_local
from database import (
    get_employee_by_telegram_id, get_all_employees, get_employee_by_id,
    get_all_positions, get_position,
    get_monthly_attendance, get_monthly_worked_minutes, get_monthly_base_salary,
    get_active_salary_entries, get_salary_totals_by_type,
    get_open_tasks_with_skips,
)

logger = logging.getLogger(__name__)
router = Router()

WEEKDAYS = ["Du", "Se", "Cho", "Pa", "Ju", "Sha", "Ya"]


def _is_admin(uid: int) -> bool:
    emp = get_employee_by_telegram_id(uid)
    return bool(emp and emp["is_admin"])


def _fmt_time(ts: str, fmt="%H:%M") -> str:
    try:
        return to_local(ts).strftime(fmt)
    except Exception:
        return "—"


def _build_full_profile(emp_id: int) -> str:
    """Xodimning to'liq profili — admin uchun."""
    emp = get_employee_by_id(emp_id)
    if not emp:
        return "❌ Xodim topilmadi."

    now = tz_now()
    year, month = now.year, now.month

    # Rol belgisi
    role = emp["role"] if "role" in emp.keys() else "employee"
    role_badge = {
        "bosh_admin": " 👑",
        "boss": " 🏆",
        "admin": " 🛠",
    }.get(role, "")

    # Karta
    card_num = emp["card_number"] if "card_number" in emp.keys() else ""
    card_holder = emp["card_holder_name"] if "card_holder_name" in emp.keys() else ""
    card = texts.format_card(card_num, card_holder)

    # Ro'yxatdan sana
    try:
        reg = to_local(emp["registered_at"]).strftime("%d.%m.%Y")
    except Exception:
        reg = "—"

    # Lavozim va stavka
    pos_id = emp["position_id"] if "position_id" in emp.keys() else None
    daily_rate = emp["daily_rate"] if "daily_rate" in emp.keys() else 0
    pos = get_position(pos_id) if pos_id else None
    pos_name = pos["name"] if pos else emp["position"]

    out = texts.EMP_FULL_PROFILE.format(
        name=emp["full_name"],
        position=pos_name,
        role_badge=role_badge,
        phone=emp["phone"],
        card=card,
        registered=reg,
    )
    if daily_rate and pos:
        out += texts.EMP_FULL_POSITION_RATE.format(
            rate=daily_rate, hours=pos["work_hours"]
        )

    # Davomat — bu oy
    records = get_monthly_attendance(emp_id, year, month)
    out += texts.EMP_FULL_MONTH_HEADER.format(
        month=texts.MONTHS_UZ[month], year=year
    )
    total_minutes = 0
    for _r in records:
        if _r["first_in"] and _r["last_out"]:
            try:
                _ih,_im,_=map(int,_r["first_in"].split(":"))
                _oh,_om,_=map(int,_r["last_out"].split(":"))
                _m=(_oh*60+_om)-(_ih*60+_im)
                if _m>0: total_minutes+=_m
            except Exception: pass
    days_shown = 0
    if records:
        for rec in records[-15:]:  # Oxirgi 15 kun
            day_str = rec["day"]
            try:
                from datetime import date as _date
                d = _date.fromisoformat(day_str)
                wd = WEEKDAYS[d.weekday()]
                date_label = d.strftime("%d.%m")
            except Exception:
                wd = "—"
                date_label = day_str

            fi = rec["first_in"]
            lo = rec["last_out"]

            if fi and lo:
                try:
                    ih, im, _ = map(int, fi.split(":"))
                    oh, om, _ = map(int, lo.split(":"))
                    mins = (oh * 60 + om) - (ih * 60 + im)
                    if mins > 0:
                        worked_str = f"{mins//60}s {mins%60}d"
                    else:
                        worked_str = "—"
                except Exception:
                    worked_str = "—"
                out += texts.EMP_FULL_DAY_LINE.format(
                    date=date_label, weekday=wd,
                    inn=fi[:5], out=lo[:5], worked=worked_str
                )
            elif fi:
                out += texts.EMP_FULL_DAY_NO_OUT.format(
                    date=date_label, weekday=wd, inn=fi[:5]
                )
            else:
                out += texts.EMP_FULL_DAY_ABSENT.format(
                    date=date_label, weekday=wd
                )
            days_shown += 1
    else:
        out += "  <i>Bu oyda davomat yo'q</i>\n"

    out += texts.EMP_FULL_MONTH_TOTAL.format(
        hours=total_minutes // 60, mins=total_minutes % 60
    )

    # Ish haqqi — bu oy
    base = get_monthly_base_salary(emp_id, year, month)
    totals = get_salary_totals_by_type(emp_id, year, month)
    total_sal = (base - totals["avans"] - totals["jarima"]
                 + totals["mukofot"] + totals["bonus"] - totals["mahsulot"])

    out += texts.EMP_FULL_SALARY_HEADER.format(
        month=texts.MONTHS_UZ[month], year=year
    )
    out += texts.EMP_FULL_SALARY_BASE.format(base=base)
    entries = get_active_salary_entries(emp_id, year, month)
    for e in entries:
        info = texts.SALARY_TYPES.get(e["entry_type"], ("📋", "?", ""))
        emoji, type_name, sign = info
        out += texts.EMP_FULL_SALARY_LINE.format(
            emoji=emoji, type=type_name, sign=sign,
            amount=e["amount"], reason=e["reason"] or "—"
        )
    out += texts.EMP_FULL_SALARY_TOTAL.format(total=total_sal)

    # Vazifalar
    open_tasks = get_open_tasks_with_skips(emp_id)
    if open_tasks:
        out += texts.EMP_FULL_TASKS_HEADER
        for t in open_tasks:
            skip_frag = ""
            if t["skip_count"]:
                skip_frag = texts.EMP_DETAIL_TASK_SKIPS.format(count=t["skip_count"])
            out += texts.EMP_FULL_TASK_LINE.format(
                title=t["title"],
                by=t["assigned_by_name"] or "—",
                skips=skip_frag,
            )

    return out


# ===== Handlerlar =====

@router.message(F.text == texts.BTN_ADMIN_LIST)
async def emp_data_start(message: Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return
    await state.clear()
    positions = get_all_positions()

    # Lavozim belgilanmagan xodimlar soni
    all_emps = [e for e in get_all_employees(active_only=True) if e["telegram_id"] > 0]
    assigned_ids = set()
    for pos in positions:
        for emp in all_emps:
            if emp["position_id"] == pos["id"]:
                assigned_ids.add(emp["id"])
    unassigned = len([e for e in all_emps if e["id"] not in assigned_ids])

    await message.answer(
        texts.EMP_DATA_PICK_POS,
        reply_markup=kb.emp_positions_kb(positions, unassigned)
    )


@router.callback_query(F.data == "empdata_back")
async def emp_data_back(call: CallbackQuery):
    positions = get_all_positions()
    all_emps = [e for e in get_all_employees(active_only=True) if e["telegram_id"] > 0]
    assigned_ids = set()
    for pos in positions:
        for emp in all_emps:
            if emp["position_id"] == pos["id"]:
                assigned_ids.add(emp["id"])
    unassigned = len([e for e in all_emps if e["id"] not in assigned_ids])
    await call.message.edit_text(
        texts.EMP_DATA_PICK_POS,
        reply_markup=kb.emp_positions_kb(positions, unassigned)
    )
    await call.answer()


@router.callback_query(F.data.startswith("empdata_pos:"))
async def emp_data_pick_pos(call: CallbackQuery):
    if not _is_admin(call.from_user.id):
        await call.answer(texts.NO_PERMISSION, show_alert=True)
        return
    val = call.data.split(":")[1]
    if val == "cancel":
        await call.message.edit_text(texts.CANCELLED)
        await call.answer()
        return

    pos_id = int(val)
    all_emps = [e for e in get_all_employees(active_only=True) if e["telegram_id"] > 0]

    if pos_id == 0:
        # Lavozim belgilanmagan
        assigned_pos_ids = {e["position_id"] for e in all_emps if e["position_id"]}
        emps = [e for e in all_emps if not e["position_id"]]
        pos_label = "Lavozim belgilanmagan"
    else:
        pos = get_position(pos_id)
        if not pos:
            await call.answer("Topilmadi", show_alert=True)
            return
        emps = [e for e in all_emps if e["position_id"] == pos_id]
        pos_label = pos["name"]

    if not emps:
        await call.answer(texts.EMP_DATA_NO_EMPS, show_alert=True)
        return

    await call.message.edit_text(
        texts.EMP_DATA_PICK_EMP.format(pos_name=pos_label, count=len(emps)),
        reply_markup=kb.emp_in_position_kb(emps, pos_id)
    )
    await call.answer()


@router.callback_query(F.data.startswith("empdata_emp:"))
async def emp_data_detail(call: CallbackQuery):
    if not _is_admin(call.from_user.id):
        await call.answer(texts.NO_PERMISSION, show_alert=True)
        return
    emp_id = int(call.data.split(":")[1])
    profile_text = _build_full_profile(emp_id)

    # Telegram xabar limiti: 4096 belgi
    if len(profile_text) > 4000:
        profile_text = profile_text[:4000] + "\n\n<i>... (qisqartirildi)</i>"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    back_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"empdata_back_emp:{emp_id}")
    ]])

    await call.message.edit_text(profile_text, reply_markup=back_kb)
    await call.answer()


@router.callback_query(F.data.startswith("empdata_back_emp:"))
async def emp_data_back_to_pos(call: CallbackQuery):
    emp_id = int(call.data.split(":")[1])
    emp = get_employee_by_id(emp_id)
    pos_id = emp["position_id"] if emp and emp["position_id"] else 0
    all_emps = [e for e in get_all_employees(active_only=True) if e["telegram_id"] > 0]

    if pos_id:
        pos = get_position(pos_id)
        emps = [e for e in all_emps if e["position_id"] == pos_id]
        pos_label = pos["name"] if pos else "—"
    else:
        emps = [e for e in all_emps if not e["position_id"]]
        pos_label = "Lavozim belgilanmagan"

    await call.message.edit_text(
        texts.EMP_DATA_PICK_EMP.format(pos_name=pos_label, count=len(emps)),
        reply_markup=kb.emp_in_position_kb(emps, pos_id)
    )
    await call.answer()
