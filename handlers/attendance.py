"""Davomat: Keldim / Ketdim — Wi-Fi + Selfi bitta qadamda"""
import logging
from datetime import datetime
from tzutil import now as tz_now, fmt as fmt_local
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

import texts
import keyboards as kb
from states import Attendance
from database import (
    get_employee_by_telegram_id, get_today_attendance,
    record_attendance, get_office_config, get_all_admins,
    get_setting
)
from services.wifi_verify import (
    create_token, is_fully_verified, get_token_data,
    cleanup_token, get_local_ip
)

logger = logging.getLogger(__name__)
router = Router()

VERIFY_PORT = 9090


def _today_status(today_records) -> str:
    if not today_records:
        return texts.STATUS_NOT_CHECKED
    last = today_records[-1]
    t = fmt_local(last["timestamp"])
    if last["check_type"] == "in":
        return texts.STATUS_CHECKED_IN.format(time=t)
    return texts.STATUS_CHECKED_OUT.format(time=t)


@router.message(F.text == texts.BTN_ATTENDANCE)
async def attendance_menu(message: Message, state: FSMContext):
    employee = get_employee_by_telegram_id(message.from_user.id)
    if not employee:
        await message.answer(texts.NOT_REGISTERED)
        return
    # Boss davomatdan ozod
    if employee["role"] == "boss":
        await message.answer("ℹ️ Boss uchun davomat talab qilinmaydi.")
        return
    await state.clear()
    today = get_today_attendance(employee["id"])
    last = today[-1] if today else None
    can_check_in = last is None
    can_check_out = last is not None and last["check_type"] == "in"
    await message.answer(
        texts.ATTENDANCE_MENU.format(status=_today_status(today)),
        reply_markup=kb.attendance_menu_kb(can_check_in, can_check_out)
    )


@router.message(F.text.in_({texts.BTN_CHECK_IN, texts.BTN_CHECK_OUT}))
async def start_attendance(message: Message, state: FSMContext):
    employee = get_employee_by_telegram_id(message.from_user.id)
    if not employee:
        await message.answer(texts.NOT_REGISTERED)
        return

    check_type = "in" if message.text == texts.BTN_CHECK_IN else "out"
    today = get_today_attendance(employee["id"])
    last = today[-1] if today else None

    if check_type == "in" and last is not None:
        if last["check_type"] == "in":
            t = fmt_local(last["timestamp"])
            await message.answer(texts.ALREADY_CHECKED_IN_TODAY.format(time=t))
        return

    if check_type == "out":
        if last is None:
            await message.answer(texts.NEED_CHECK_IN_FIRST)
            return
        if last["check_type"] == "out":
            t = fmt_local(last["timestamp"])
            await message.answer(texts.ALREADY_CHECKED_OUT.format(time=t))
            return

    # Token yaratish va verify URL
    token = create_token(employee["id"], employee["full_name"])
    from config import PUBLIC_URL
    if PUBLIC_URL:
        # Render rejim: HTTPS public URL
        verify_url = f"{PUBLIC_URL.rstrip('/')}/verify/{token}"
    else:
        # Local rejim: Mac lokal IP
        office_ip = get_setting("office_ip", get_local_ip())
        verify_url = f"http://{office_ip}:{VERIFY_PORT}/verify/{token}"

    await state.update_data(check_type=check_type, wifi_token=token)

    # Havola tugmasi
    link_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Ochish: Wi-Fi + Selfi", url=verify_url)]
    ])
    await message.answer(texts.ASK_VERIFY_AND_SELFIE, reply_markup=link_kb)
    await message.answer(texts.WIFI_TAP_CONFIRM, reply_markup=kb.wifi_confirm_kb())
    await state.set_state(Attendance.waiting_wifi_confirm)


@router.message(Attendance.waiting_wifi_confirm, F.text == texts.BTN_WIFI_CONFIRMED)
async def check_verified(message: Message, state: FSMContext):
    data = await state.get_data()
    token = data.get("wifi_token", "")

    if not is_fully_verified(token):
        # Nimasi tasdiqlanmagan — aniq xabar berish
        token_data = get_token_data(token)
        if not token_data:
            await message.answer(texts.TOKEN_EXPIRED)
            await state.clear()
            return
        if not token_data["wifi_verified"]:
            await message.answer(texts.WIFI_NOT_VERIFIED_YET)
        else:
            await message.answer(texts.FACE_NOT_VERIFIED_YET)
        return

    # Hammasi tasdiqlangan!
    token_data = get_token_data(token)
    employee = get_employee_by_telegram_id(message.from_user.id)
    check_type = data["check_type"]
    cfg = get_office_config()

    record_attendance(
        employee_id=employee["id"],
        check_type=check_type,
        latitude=None,
        longitude=None,
        distance=None,
        wifi_name="Wi-Fi+Selfi tasdiqlangan",
        wifi_match=True,
        face_score=token_data["face_score"],
        photo_file_id=None,
    )

    cleanup_token(token)
    now = tz_now()
    time_str = now.strftime("%H:%M")

    if check_type == "in":
        # Kechikish tekshiruvi
        late_warning = ""
        try:
            ws_h, ws_m = map(int, cfg["work_start"].split(":"))
            work_start = now.replace(hour=ws_h, minute=ws_m, second=0, microsecond=0)
            if now > work_start:
                minutes_late = int((now - work_start).total_seconds() / 60)
                if minutes_late > 0:
                    late_warning = texts.LATE_WARNING.format(minutes=minutes_late)
        except Exception:
            pass

        await message.answer(
            texts.CHECK_IN_SUCCESS.format(
                time=time_str,
                face_score=token_data["face_score"],
                late_warning=late_warning,
            ),
            reply_markup=kb.main_menu_kb(is_admin=bool(employee["is_admin"]), is_boss=(employee["role"] == "boss"))
        )
    else:
        worked_str = _calculate_worked_time(employee["id"])
        await message.answer(
            texts.CHECK_OUT_SUCCESS.format(time=time_str, worked=worked_str),
            reply_markup=kb.main_menu_kb(is_admin=bool(employee["is_admin"]), is_boss=(employee["role"] == "boss"))
        )
        # Phase 2: ochiq vazifalar bo'lsa, "Hammasini tugatdingizmi?" savolini chiqarish
        from handlers.tasks import maybe_prompt_checkout_tasks
        await maybe_prompt_checkout_tasks(message, employee["id"])

    await state.clear()


def _calculate_worked_time(employee_id: int) -> str:
    today = get_today_attendance(employee_id)
    in_time = None
    total_seconds = 0
    for rec in today:
        ts = datetime.fromisoformat(rec["timestamp"])
        if rec["check_type"] == "in":
            in_time = ts
        elif rec["check_type"] == "out" and in_time:
            total_seconds += (ts - in_time).total_seconds()
            in_time = None
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    return f"{hours}s {minutes}d"
