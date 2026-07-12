"""Davomatni tuzatish so'rovlari (regularization).

Xodim oqimi (callback prefiks `fixreq`):
  📊 Statistika → "✏️ Davomatni tuzatish so'rovi" → kun (7 kun) → tur
  (in/out/both) → vaqt(lar) HH:MM → sabab → tasdiqlash → adminlarga xabar.

Admin oqimi (callback prefiks `fixrev`):
  ✅ Tasdiqlash — attendance yozuvlari yangilanadi (delete+add, UTC
  konvertatsiya add_manual_attendance ichida), ❌ Rad etish — izoh (FSM).
  Poyga himoyasi: claim_fix_request atomik UPDATE (status='pending' shart).
"""
import html
import logging
import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import texts
import keyboards as kb
from states import FixRequest, FixReview
from database import (
    get_employee_by_telegram_id, get_all_admins,
    create_fix_request, has_pending_fix_request, count_fix_requests_today,
    get_fix_request, get_pending_fix_requests, claim_fix_request,
    get_day_attendance, delete_day_attendance, delete_day_attendance_by_type,
    add_manual_attendance, is_month_closed,
)
from tzutil import fmt as tz_fmt, now as tz_now

logger = logging.getLogger(__name__)
router = Router()

TIME_RE = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")

MAX_REQUESTS_PER_DAY = 3

TYPE_LABELS = {
    "in": texts.FIXREQ_TYPE_IN,
    "out": texts.FIXREQ_TYPE_OUT,
    "both": texts.FIXREQ_TYPE_BOTH,
}


# ===== Yordamchilar =====

def _parse_time(text: str):
    """'H:MM'/'HH:MM' -> normallashtirilgan 'HH:MM' yoki None."""
    m = TIME_RE.match((text or "").strip())
    if not m:
        return None
    return f"{int(m.group(1)):02d}:{m.group(2)}"


def _to_minutes(hhmm: str) -> int:
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


def _times_block(request_type: str, proposed_in, proposed_out) -> str:
    lines = ""
    if request_type in ("in", "both") and proposed_in:
        lines += texts.FIXREQ_TIME_IN_LINE.format(time=proposed_in)
    if request_type in ("out", "both") and proposed_out:
        lines += texts.FIXREQ_TIME_OUT_LINE.format(time=proposed_out)
    return lines


def _current_records_block(employee_id: int, date_local: str) -> str:
    """Kunning joriy davomat yozuvlari (Toshkent vaqtida)."""
    records = get_day_attendance(employee_id, date_local)
    if not records:
        return texts.FIXREQ_NO_RECORDS
    lines = []
    for r in records:
        emoji = "🟢" if r["check_type"] == "in" else "🔴"
        lines.append(f"   {emoji} {tz_fmt(r['timestamp'])}")
    return "\n".join(lines)


def _request_summary(req_id, name, date, request_type, proposed_in,
                     proposed_out, reason, employee_id) -> str:
    return texts.FIXREQ_ADMIN_NOTIFY.format(
        req_id=req_id,
        name=html.escape(name),
        date=date,
        type=TYPE_LABELS.get(request_type, request_type),
        times=_times_block(request_type, proposed_in, proposed_out),
        reason=html.escape(reason or ""),
        current=_current_records_block(employee_id, date),
    )


async def _notify(bot, telegram_id: int, text: str, reply_markup=None) -> bool:
    try:
        await bot.send_message(telegram_id, text, reply_markup=reply_markup)
        return True
    except Exception as e:
        logger.warning("Xabar yuborilmadi (tg=%s): %s", telegram_id, e)
        return False


def _is_admin_call(call: CallbackQuery):
    """Callback egasi admin bo'lsa employee qatorini, aks holda None."""
    emp = get_employee_by_telegram_id(call.from_user.id)
    if not emp or not emp["is_admin"]:
        return None
    return emp


# ===== Xodim oqimi =====

@router.callback_query(F.data == "fixreq:start")
async def fixreq_start(call: CallbackQuery, state: FSMContext):
    employee = get_employee_by_telegram_id(call.from_user.id)
    if not employee:
        await call.answer(texts.NOT_REGISTERED, show_alert=True)
        return
    if count_fix_requests_today(employee["id"]) >= MAX_REQUESTS_PER_DAY:
        await call.answer(texts.FIXREQ_LIMIT_DAY, show_alert=True)
        return
    await state.clear()
    await call.message.answer(texts.FIXREQ_PICK_DAY, reply_markup=kb.fixreq_days_kb())
    await call.answer()


@router.callback_query(F.data == "fixreq:cancel")
async def fixreq_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(texts.CANCELLED)
    await call.answer()


@router.callback_query(F.data.startswith("fixreq:day:"))
async def fixreq_day(call: CallbackQuery, state: FSMContext):
    employee = get_employee_by_telegram_id(call.from_user.id)
    if not employee:
        await call.answer(texts.NOT_REGISTERED, show_alert=True)
        return
    date_str = call.data.split(":", 2)[2]
    try:
        year, month, _ = map(int, date_str.split("-"))
    except ValueError:
        await call.answer()
        return
    if is_month_closed(year, month):
        await call.answer(texts.FIXREQ_MONTH_CLOSED, show_alert=True)
        return
    if has_pending_fix_request(employee["id"], date_str):
        await call.answer(texts.FIXREQ_ALREADY_PENDING, show_alert=True)
        return
    await state.update_data(target_date=date_str)
    await call.message.edit_text(
        texts.FIXREQ_PICK_TYPE.format(date=date_str),
        reply_markup=kb.fixreq_type_kb(),
    )
    await call.answer()


@router.callback_query(F.data.startswith("fixreq:type:"))
async def fixreq_type(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("target_date"):
        await call.answer(texts.FIXREQ_ALREADY_REVIEWED, show_alert=True)
        return
    request_type = call.data.split(":", 2)[2]
    if request_type not in ("in", "out", "both"):
        await call.answer()
        return
    await state.update_data(request_type=request_type,
                            proposed_in=None, proposed_out=None)
    if request_type in ("in", "both"):
        await state.set_state(FixRequest.entering_time_in)
        await call.message.edit_text(texts.FIXREQ_ASK_TIME_IN)
    else:
        await state.set_state(FixRequest.entering_time_out)
        await call.message.edit_text(texts.FIXREQ_ASK_TIME_OUT)
    await call.answer()


@router.message(FixRequest.entering_time_in)
async def fixreq_time_in(message: Message, state: FSMContext):
    time_str = _parse_time(message.text)
    if not time_str:
        await message.answer(texts.FIXREQ_INVALID_TIME)
        return
    await state.update_data(proposed_in=time_str)
    data = await state.get_data()
    if data.get("request_type") == "both":
        await state.set_state(FixRequest.entering_time_out)
        await message.answer(texts.FIXREQ_ASK_TIME_OUT)
    else:
        await state.set_state(FixRequest.entering_reason)
        await message.answer(texts.FIXREQ_ASK_REASON)


@router.message(FixRequest.entering_time_out)
async def fixreq_time_out(message: Message, state: FSMContext):
    time_str = _parse_time(message.text)
    if not time_str:
        await message.answer(texts.FIXREQ_INVALID_TIME)
        return
    data = await state.get_data()
    proposed_in = data.get("proposed_in")
    if proposed_in and _to_minutes(time_str) <= _to_minutes(proposed_in):
        await message.answer(texts.FIXREQ_OUT_BEFORE_IN)
        return
    await state.update_data(proposed_out=time_str)
    await state.set_state(FixRequest.entering_reason)
    await message.answer(texts.FIXREQ_ASK_REASON)


@router.message(FixRequest.entering_reason)
async def fixreq_reason(message: Message, state: FSMContext):
    reason = (message.text or "").strip()
    if len(reason) < 5:
        await message.answer(texts.FIXREQ_REASON_TOO_SHORT)
        return
    await state.update_data(reason=reason)
    data = await state.get_data()
    await message.answer(
        texts.FIXREQ_CONFIRM.format(
            date=data["target_date"],
            type=TYPE_LABELS.get(data["request_type"], ""),
            times=_times_block(data["request_type"],
                               data.get("proposed_in"), data.get("proposed_out")),
            reason=html.escape(reason),
        ),
        reply_markup=kb.fixreq_confirm_kb(),
    )


@router.callback_query(F.data == "fixreq:confirm")
async def fixreq_confirm(call: CallbackQuery, state: FSMContext):
    employee = get_employee_by_telegram_id(call.from_user.id)
    data = await state.get_data()
    if not employee or not data.get("target_date") or not data.get("reason"):
        await call.answer(texts.FIXREQ_ALREADY_REVIEWED, show_alert=True)
        return
    # O'z-o'zi bilan poyga: tugma ikki marta bosilishi mumkin
    if has_pending_fix_request(employee["id"], data["target_date"]):
        await call.answer(texts.FIXREQ_ALREADY_PENDING, show_alert=True)
        await state.clear()
        return
    if count_fix_requests_today(employee["id"]) >= MAX_REQUESTS_PER_DAY:
        await call.answer(texts.FIXREQ_LIMIT_DAY, show_alert=True)
        await state.clear()
        return

    req_id = create_fix_request(
        employee["id"], data["target_date"], data["request_type"],
        data.get("proposed_in"), data.get("proposed_out"), data["reason"],
    )
    await state.clear()
    logger.info(
        "Tuzatish so'rovi #%s yaratildi: emp=%s, kun=%s, tur=%s",
        req_id, employee["id"], data["target_date"], data["request_type"],
    )
    await call.message.edit_text(texts.FIXREQ_SENT)
    await call.answer()

    # Barcha adminlarga xabar
    summary = _request_summary(
        req_id, employee["full_name"], data["target_date"],
        data["request_type"], data.get("proposed_in"),
        data.get("proposed_out"), data["reason"], employee["id"],
    )
    for admin in get_all_admins():
        await _notify(call.bot, admin["telegram_id"], summary,
                      reply_markup=kb.fixreq_review_kb(req_id))


# ===== Admin tomoni =====

@router.message(F.text == texts.BTN_FIX_REQUESTS_ADMIN)
async def fixreq_pending_list(message: Message):
    emp = get_employee_by_telegram_id(message.from_user.id)
    if not emp or not emp["is_admin"]:
        await message.answer(texts.NO_PERMISSION)
        return
    pending = get_pending_fix_requests()
    if not pending:
        await message.answer(texts.FIXREQ_NO_PENDING)
        return
    await message.answer(texts.FIXREQ_PENDING_HEADER.format(count=len(pending)))
    for req in pending:
        await message.answer(
            _request_summary(
                req["id"], req["full_name"], req["target_date"],
                req["request_type"], req["proposed_in"], req["proposed_out"],
                req["reason"], req["employee_id"],
            ),
            reply_markup=kb.fixreq_review_kb(req["id"]),
        )


def _apply_fix(req) -> None:
    """Tasdiqlangan so'rovni attendance jadvaliga qo'llash.
    Faqat so'ralgan turdagi yozuvlar almashtiriladi; UTC konvertatsiya
    add_manual_attendance ichida (-5 soat)."""
    emp_id = req["employee_id"]
    date_local = req["target_date"]
    if req["request_type"] == "both":
        delete_day_attendance(emp_id, date_local)
        add_manual_attendance(emp_id, "in", req["proposed_in"], date_local)
        add_manual_attendance(emp_id, "out", req["proposed_out"], date_local)
    elif req["request_type"] == "in":
        delete_day_attendance_by_type(emp_id, date_local, "in")
        add_manual_attendance(emp_id, "in", req["proposed_in"], date_local)
    else:  # 'out'
        delete_day_attendance_by_type(emp_id, date_local, "out")
        add_manual_attendance(emp_id, "out", req["proposed_out"], date_local)


@router.callback_query(F.data.startswith("fixrev:ok:"))
async def fixrev_approve(call: CallbackQuery):
    admin = _is_admin_call(call)
    if not admin:
        await call.answer(texts.NO_PERMISSION, show_alert=True)
        return
    req_id = int(call.data.split(":")[2])
    req = get_fix_request(req_id)
    if not req or req["status"] != "pending":
        await call.answer(texts.FIXREQ_ALREADY_REVIEWED, show_alert=True)
        return
    year, month, _ = map(int, req["target_date"].split("-"))
    if is_month_closed(year, month):
        await call.answer(texts.FIXREQ_MONTH_CLOSED, show_alert=True)
        return
    # Atomik band qilish — ikki admin poygasida faqat bittasi yutadi
    if not claim_fix_request(req_id, "approved", admin["id"]):
        await call.answer(texts.FIXREQ_ALREADY_REVIEWED, show_alert=True)
        return

    try:
        _apply_fix(req)
    except Exception:
        logger.exception("So'rov #%s ni qo'llashda xato", req_id)
        await call.answer(texts.FIXREQ_APPLY_ERROR, show_alert=True)
        return

    logger.info(
        "Tuzatish so'rovi #%s tasdiqlandi (admin=%s): emp=%s, kun=%s, tur=%s",
        req_id, admin["id"], req["employee_id"], req["target_date"],
        req["request_type"],
    )
    try:
        await call.message.edit_text(
            call.message.html_text
            + texts.FIXREQ_APPROVED_ADMIN.format(admin=html.escape(admin["full_name"])),
            reply_markup=None,
        )
    except Exception:
        pass
    await call.answer("✅")
    await _notify(
        call.bot, req["telegram_id"],
        texts.FIXREQ_APPROVED_EMP.format(
            date=req["target_date"],
            times=_times_block(req["request_type"],
                               req["proposed_in"], req["proposed_out"]),
        ),
    )


@router.callback_query(F.data.startswith("fixrev:no:"))
async def fixrev_reject_start(call: CallbackQuery, state: FSMContext):
    admin = _is_admin_call(call)
    if not admin:
        await call.answer(texts.NO_PERMISSION, show_alert=True)
        return
    req_id = int(call.data.split(":")[2])
    req = get_fix_request(req_id)
    if not req or req["status"] != "pending":
        await call.answer(texts.FIXREQ_ALREADY_REVIEWED, show_alert=True)
        return
    await state.set_state(FixReview.entering_reject_comment)
    await state.update_data(
        fixrev_req_id=req_id,
        fixrev_chat_id=call.message.chat.id,
        fixrev_msg_id=call.message.message_id,
    )
    await call.message.answer(texts.FIXREQ_REJECT_ASK_COMMENT)
    await call.answer()


@router.message(FixReview.entering_reject_comment)
async def fixrev_reject_finish(message: Message, state: FSMContext):
    admin = get_employee_by_telegram_id(message.from_user.id)
    data = await state.get_data()
    req_id = data.get("fixrev_req_id")
    await state.clear()
    if not admin or not admin["is_admin"] or not req_id:
        await message.answer(texts.NO_PERMISSION)
        return

    text = (message.text or "").strip()
    comment = None if text == "-" else text

    req = get_fix_request(req_id)
    if not req or not claim_fix_request(req_id, "rejected", admin["id"], comment):
        # Izoh yozilayotganda boshqa admin ko'rib chiqqan bo'lishi mumkin
        await message.answer(texts.FIXREQ_ALREADY_REVIEWED)
        return

    logger.info(
        "Tuzatish so'rovi #%s rad etildi (admin=%s): emp=%s, kun=%s",
        req_id, admin["id"], req["employee_id"], req["target_date"],
    )
    # Asl xabardagi tugmalarni olib tashlab, natijani belgilash
    try:
        await message.bot.edit_message_reply_markup(
            chat_id=data.get("fixrev_chat_id"),
            message_id=data.get("fixrev_msg_id"),
            reply_markup=None,
        )
    except Exception:
        pass

    comment_line = (
        texts.FIXREQ_REJECT_COMMENT_LINE.format(comment=html.escape(comment))
        if comment else ""
    )
    await _notify(
        message.bot, req["telegram_id"],
        texts.FIXREQ_REJECTED_EMP.format(date=req["target_date"], comment=comment_line),
    )
    await message.answer(texts.FIXREQ_REJECT_DONE)
