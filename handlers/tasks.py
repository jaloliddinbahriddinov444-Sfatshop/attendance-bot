"""Vazifalar — xodim oynasi va Ketdim oqimi integratsiyasi.

Vazifa yaratish admin/Boss tomonidan handlers/admin.py'da amalga oshiriladi.
Bu yerda asosan xodim ko'rinishi va vazifa holatini o'zgartirish bor.
"""
import logging
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery

import texts
import keyboards as kb
from database import (
    get_employee_by_telegram_id,
    get_recent_tasks_for_employee, get_open_tasks,
    get_task, complete_task, skip_task,
)
from tzutil import now as tz_now, to_local, fmt as fmt_local

logger = logging.getLogger(__name__)
router = Router()


def _format_task_lines(tasks) -> str:
    """Vazifalar ro'yxatini matn shaklida tayyorlash (xodim oynasi uchun)."""
    parts = []
    for t in tasks:
        if t["status"] == "open":
            deadline = ""
            if t["deadline"]:
                deadline = texts.TASK_DEADLINE_FRAGMENT.format(
                    deadline=to_local(t["deadline"]).strftime("%d.%m %H:%M")
                )
            desc = ""
            if t["description"]:
                desc = texts.TASK_DESC_FRAGMENT.format(desc=t["description"])
            parts.append(texts.TASK_LINE_OPEN.format(
                title=t["title"],
                by=t["assigned_by_name"] or "—",
                created=fmt_local(t["created_at"], "%d.%m %H:%M"),
                deadline=deadline,
                desc=desc,
            ))
        elif t["status"] == "completed":
            parts.append(texts.TASK_LINE_DONE.format(
                title=t["title"],
                completed=fmt_local(t["completed_at"], "%d.%m %H:%M")
                          if t["completed_at"] else "—",
            ))
        else:  # cancelled
            parts.append(texts.TASK_LINE_CANCELLED.format(title=t["title"]))
    return "".join(parts)


@router.message(F.text == texts.BTN_TASKS)
async def employee_tasks(message: Message):
    employee = get_employee_by_telegram_id(message.from_user.id)
    if not employee:
        await message.answer(texts.NOT_REGISTERED)
        return

    tasks = get_recent_tasks_for_employee(employee["id"], limit=20)
    if not tasks:
        await message.answer(texts.TASKS_EMPTY)
        return

    # Ro'yxatni alohida xabar, keyin har bir ochiq vazifa uchun "Tugatdim" tugmasi
    body = texts.TASKS_HEADER + _format_task_lines(tasks)
    await message.answer(body)

    for t in tasks:
        if t["status"] == "open":
            await message.answer(
                f"🟡 <b>{t['title']}</b>",
                reply_markup=kb.task_complete_kb(t["id"])
            )


@router.callback_query(F.data.startswith("task_done:"))
async def employee_complete_task(call: CallbackQuery, bot: Bot):
    employee = get_employee_by_telegram_id(call.from_user.id)
    if not employee:
        await call.answer(texts.NOT_REGISTERED, show_alert=True)
        return

    try:
        task_id = int(call.data.split(":", 1)[1])
    except (ValueError, IndexError):
        await call.answer("❌ Xato", show_alert=True)
        return

    task = get_task(task_id)
    if not task or task["assigned_to"] != employee["id"]:
        await call.answer("❌ Topilmadi", show_alert=True)
        return
    if task["status"] != "open":
        await call.answer(texts.TASK_ALREADY_DONE, show_alert=True)
        try:
            await call.message.edit_text(f"✅ <s>{task['title']}</s>")
        except Exception:
            pass
        return

    complete_task(task_id)
    try:
        await call.message.edit_text(f"✅ <s>{task['title']}</s>")
    except Exception:
        pass
    await call.answer(texts.TASK_COMPLETED_OK)

    # Tayinlovchiga xabar
    if task["assigned_by_tg"]:
        await _notify(bot, task["assigned_by_tg"],
                      texts.TASK_NOTIFY_DONE.format(
                          title=task["title"],
                          employee=employee["full_name"],
                          when=tz_now().strftime("%d.%m %H:%M"),
                      ))


# ===== Ketdim oqimi uchun yordamchilar (attendance.py ishlatadi) =====

async def maybe_prompt_checkout_tasks(message: Message, employee_id: int) -> None:
    """Ketdim muvaffaqiyatli yakunlangach chaqiriladi.
    Agar ochiq vazifalar bo'lsa, "Hammasini tugatdingizmi?" savolini chiqaradi.
    """
    open_tasks = get_open_tasks(employee_id)
    if not open_tasks:
        return

    lines = "\n".join(
        texts.CHECKOUT_TASKS_SHORT_LINE.format(title=t["title"])
        for t in open_tasks
    )
    await message.answer(
        texts.CHECKOUT_TASKS_PROMPT.format(count=len(open_tasks), list=lines),
        reply_markup=kb.checkout_tasks_yes_no_kb()
    )


@router.callback_query(F.data.startswith("ck_tasks:"))
async def checkout_tasks_response(call: CallbackQuery, bot: Bot):
    employee = get_employee_by_telegram_id(call.from_user.id)
    if not employee:
        await call.answer(texts.NOT_REGISTERED, show_alert=True)
        return

    answer = call.data.split(":", 1)[1]
    open_tasks = get_open_tasks(employee["id"])

    when_str = tz_now().strftime("%d.%m %H:%M")
    notified = {}  # assigner_tg -> count

    if answer == "yes":
        # Hammasi tugatildi
        for t in open_tasks:
            complete_task(t["id"])
        await call.message.edit_text(texts.CHECKOUT_TASKS_DONE_OK)
        # Tayinlovchilarga
        for t in open_tasks:
            full_t = get_task(t["id"])
            if full_t and full_t["assigned_by_tg"]:
                await _notify(bot, full_t["assigned_by_tg"],
                              texts.TASK_NOTIFY_DONE.format(
                                  title=full_t["title"],
                                  employee=employee["full_name"],
                                  when=when_str,
                              ))
    else:
        # Tugatilmadi — har biriga skip yozuvi va xabar
        for t in open_tasks:
            skip_task(t["id"])
        await call.message.edit_text(texts.CHECKOUT_TASKS_NOT_DONE)
        for t in open_tasks:
            full_t = get_task(t["id"])
            if full_t and full_t["assigned_by_tg"]:
                await _notify(bot, full_t["assigned_by_tg"],
                              texts.TASK_NOTIFY_SKIPPED.format(
                                  title=full_t["title"],
                                  employee=employee["full_name"],
                                  when=when_str,
                              ))

    await call.answer()


async def _notify(bot: Bot, telegram_id: int, text: str):
    """Foydalanuvchiga xabar yuborish — xatolarga chidamli."""
    try:
        await bot.send_message(telegram_id, text, parse_mode="HTML")
    except Exception as e:
        logger.warning("Xabar yuborilmadi tg=%s: %s", telegram_id, e)
