"""Boss paneli: davomat ma'lumotlari, vazifa berish (admin'dan ulashilgan), moliya (Phase 4)."""
import logging
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import texts
import keyboards as kb
from database import (
    get_employee_by_telegram_id, get_all_employees, get_employee_by_id,
    get_today_attendance, get_monthly_worked_minutes,
    get_active_salary_entries, get_open_tasks_with_skips,
)
from tzutil import now as tz_now, fmt as fmt_local

logger = logging.getLogger(__name__)
router = Router()


def _require_boss_or_bosh(emp) -> bool:
    if not emp:
        return False
    try:
        return emp["role"] in ("boss", "bosh_admin")
    except (KeyError, IndexError):
        return False


@router.message(F.text == texts.BTN_BOSS_PANEL)
async def boss_panel(message: Message, state: FSMContext):
    me = get_employee_by_telegram_id(message.from_user.id)
    if not me or not _require_boss_or_bosh(me):
        await message.answer(texts.NO_PERMISSION)
        return
    await state.clear()
    await message.answer(texts.BOSS_PANEL_MENU, reply_markup=kb.boss_panel_kb())


@router.message(F.text == texts.BTN_BOSS_ATTENDANCE)
async def boss_attendance(message: Message):
    me = get_employee_by_telegram_id(message.from_user.id)
    if not me or not _require_boss_or_bosh(me):
        await message.answer(texts.NO_PERMISSION)
        return

    employees = get_all_employees(active_only=True)
    if not employees:
        await message.answer(texts.BOSS_ATTENDANCE_EMPTY)
        return

    today_str = tz_now().strftime("%d.%m.%Y")
    # Sarlavha + inline tugmalar (har xodim — bitta tugma)
    lines = []
    rows = []
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    for emp in employees:
        recs = get_today_attendance(emp["id"])
        if recs:
            last = recs[-1]
            t = fmt_local(last["timestamp"], "%H:%M")
            if last["check_type"] == "in":
                badge = "✅"
                line = texts.BOSS_EMP_STATUS_IN.format(name=emp["full_name"], time=t)
            else:
                badge = "🔴"
                line = texts.BOSS_EMP_STATUS_OUT.format(name=emp["full_name"], time=t)
        else:
            badge = "❌"
            line = texts.BOSS_EMP_STATUS_NONE.format(name=emp["full_name"])
        lines.append(line)
        rows.append([InlineKeyboardButton(
            text=f"{badge} {emp['full_name']}",
            callback_data=f"boss_emp:{emp['id']}"
        )])

    await message.answer(
        texts.BOSS_ATTENDANCE_HEADER.format(date=today_str) +
        "\n\n" + "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("boss_emp:"))
async def boss_emp_detail(call: CallbackQuery):
    me = get_employee_by_telegram_id(call.from_user.id)
    if not me or not _require_boss_or_bosh(me):
        await call.answer(texts.NO_PERMISSION, show_alert=True)
        return

    try:
        emp_id = int(call.data.split(":", 1)[1])
    except (ValueError, IndexError):
        await call.answer("❌ Xato", show_alert=True)
        return
    emp = get_employee_by_id(emp_id)
    if not emp:
        await call.answer("❌ Topilmadi", show_alert=True)
        return

    text = _format_employee_detail(emp)
    await call.message.edit_text(text)
    await call.answer()


def _format_employee_detail(emp) -> str:
    """Boss/Bosh Admin uchun xodim profili: davomat, oy, maosh yozuvlari (tasdiqlanganlar),
    tugatilmagan vazifalar.
    """
    role = ""
    try:
        r = emp["role"]
        if r == "bosh_admin":
            role = "👑 <i>Bosh Admin</i>"
        elif r == "boss":
            role = "🏆 <i>Boss</i>"
        elif r == "admin":
            role = "🛠 <i>Admin</i>"
    except (KeyError, IndexError):
        pass

    out = texts.EMP_DETAIL_HEADER.format(
        name=emp["full_name"],
        position=emp["position"],
        phone=emp["phone"],
        role_badge=role,
    )

    # Bugungi davomat
    today = get_today_attendance(emp["id"])
    if today:
        body = "\n".join(
            texts.EMP_DETAIL_TODAY_LINE.format(
                emoji="🟢" if t["check_type"] == "in" else "🔴",
                when=fmt_local(t["timestamp"], "%H:%M"),
                kind="Keldi" if t["check_type"] == "in" else "Ketdi",
            )
            for t in today
        )
    else:
        body = texts.EMP_DETAIL_TODAY_NONE
    out += texts.EMP_DETAIL_TODAY.format(today=body)

    # Plastik karta (faqat boss/bosh_admin ko'radi)
    try:
        card_num = emp["card_number"] if "card_number" in emp.keys() else ""
        card_holder = emp["card_holder_name"] if "card_holder_name" in emp.keys() else ""
    except Exception:
        card_num, card_holder = "", ""
    card_str = texts.format_card(card_num, card_holder)
    out += texts.EMP_DETAIL_CARD.format(card=card_str)

    # Bu oyda ishlangan
    now = tz_now()
    minutes = get_monthly_worked_minutes(emp["id"], now.year, now.month)
    out += texts.EMP_DETAIL_MONTH.format(hours=minutes // 60, minutes=minutes % 60)

    # Maosh yozuvlari (faol) — Phase 3B kelguncha hammasi "active" hisoblanadi
    entries = get_active_salary_entries(emp["id"], now.year, now.month)
    out += texts.EMP_DETAIL_SALARY_HEADER
    if entries:
        for e in entries:
            info = texts.SALARY_TYPES.get(e["entry_type"], ("📋", "?", ""))
            emoji, type_name, sign = info
            out += texts.EMP_DETAIL_SALARY_LINE.format(
                emoji=emoji, type_name=type_name, sign=sign,
                amount=e["amount"], reason=e["reason"] or "—"
            )
    else:
        out += texts.EMP_DETAIL_SALARY_NONE

    # Tugatilmagan vazifalar
    open_tasks = get_open_tasks_with_skips(emp["id"])
    out += texts.EMP_DETAIL_TASKS_HEADER
    if open_tasks:
        for t in open_tasks:
            skip_frag = ""
            if t["skip_count"]:
                skip_frag = texts.EMP_DETAIL_TASK_SKIPS.format(count=t["skip_count"])
            out += texts.EMP_DETAIL_TASK_LINE.format(
                title=t["title"],
                by=t["assigned_by_name"] or "—",
                created=fmt_local(t["created_at"], "%d.%m"),
                skips=skip_frag,
            )
    else:
        out += texts.EMP_DETAIL_TASKS_NONE

    return out
