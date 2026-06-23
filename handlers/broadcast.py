"""Xabarnoma (Broadcast) — Boss va Bosh Admin uchun."""
import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import texts
import keyboards as kb
from database import (
    get_employee_by_telegram_id, get_employee_by_id,
    get_all_employees, get_all_positions,
    get_employees_by_position_id,
    create_broadcast, save_broadcast_reaction,
    get_broadcast_sender, save_broadcast_comment,
)
from states import Broadcast, BroadcastComment

logger = logging.getLogger(__name__)
router = Router()

_CONTENT_LABELS = {
    "text": "📝 Matn",
    "photo": "🖼 Rasm",
    "video": "🎬 Video",
    "file": "📄 Fayl",
    "poll": "📊 So'rovnoma",
}


def _require_boss_or_bosh(emp) -> bool:
    if not emp:
        return False
    try:
        return emp["role"] in ("boss", "bosh_admin")
    except (KeyError, IndexError):
        return False


# ─── Step 1: ochilish ──────────────────────────────────────────────────────

@router.message(F.text == texts.BTN_BROADCAST)
async def bc_start(message: Message, state: FSMContext):
    me = get_employee_by_telegram_id(message.from_user.id)
    if not me or not _require_boss_or_bosh(me):
        await message.answer(texts.NO_PERMISSION)
        return
    await state.clear()
    await state.update_data(sender_emp_id=me["id"])
    await message.answer(texts.BC_CHOOSE_TARGET, reply_markup=kb.bc_target_kb())
    await state.set_state(Broadcast.target)


# ─── Step 2a: barcha xodimlar ──────────────────────────────────────────────

@router.callback_query(Broadcast.target, F.data == "bc_target:all")
async def bc_target_all(call: CallbackQuery, state: FSMContext):
    employees = get_all_employees(active_only=True)
    count = len(employees)
    await state.update_data(
        target_type="all", target_id=None,
        target_label=f"Barcha xodimlar ({count} nafar)"
    )
    await call.message.edit_text(
        texts.BC_CHOOSE_CONTENT, reply_markup=kb.bc_content_type_kb()
    )
    await state.set_state(Broadcast.content_type)
    await call.answer()


# ─── Step 2b: lavozim bo'yicha ─────────────────────────────────────────────

@router.callback_query(Broadcast.target, F.data == "bc_target:pos")
async def bc_target_pos(call: CallbackQuery, state: FSMContext):
    positions = get_all_positions()
    if not positions:
        await call.answer("Hech qanday lavozim topilmadi.", show_alert=True)
        return
    await call.message.edit_text(
        texts.BC_CHOOSE_POS, reply_markup=kb.bc_positions_kb(positions)
    )
    await state.set_state(Broadcast.choosing_position)
    await call.answer()


@router.callback_query(Broadcast.choosing_position, F.data.startswith("bc_pos:"))
async def bc_position_chosen(call: CallbackQuery, state: FSMContext):
    try:
        pos_id = int(call.data.split(":", 1)[1])
    except (ValueError, IndexError):
        await call.answer("Xato", show_alert=True)
        return
    positions = get_all_positions()
    pos = next((p for p in positions if p["id"] == pos_id), None)
    if not pos:
        await call.answer("Topilmadi", show_alert=True)
        return
    employees = get_employees_by_position_id(pos_id)
    count = len(employees)
    await state.update_data(
        target_type="position", target_id=pos_id,
        target_label=f"💼 {pos['name']} ({count} nafar)"
    )
    await call.message.edit_text(
        texts.BC_CHOOSE_CONTENT, reply_markup=kb.bc_content_type_kb()
    )
    await state.set_state(Broadcast.content_type)
    await call.answer()


# ─── Step 2c: alohida xodim ────────────────────────────────────────────────

@router.callback_query(Broadcast.target, F.data == "bc_target:emp")
async def bc_target_emp(call: CallbackQuery, state: FSMContext):
    employees = get_all_employees(active_only=True)
    if not employees:
        await call.answer("Hech qanday xodim topilmadi.", show_alert=True)
        return
    await call.message.edit_text(
        texts.BC_CHOOSE_EMP, reply_markup=kb.bc_employees_kb(employees)
    )
    await state.set_state(Broadcast.choosing_employee)
    await call.answer()


@router.callback_query(Broadcast.choosing_employee, F.data.startswith("bc_emp:"))
async def bc_employee_chosen(call: CallbackQuery, state: FSMContext):
    try:
        emp_id = int(call.data.split(":", 1)[1])
    except (ValueError, IndexError):
        await call.answer("Xato", show_alert=True)
        return
    emp = get_employee_by_id(emp_id)
    if not emp:
        await call.answer("Topilmadi", show_alert=True)
        return
    await state.update_data(
        target_type="employee", target_id=emp_id,
        target_label=f"👤 {emp['full_name']}"
    )
    await call.message.edit_text(
        texts.BC_CHOOSE_CONTENT, reply_markup=kb.bc_content_type_kb()
    )
    await state.set_state(Broadcast.content_type)
    await call.answer()


# ─── Step 3: content type tanlash ──────────────────────────────────────────

@router.callback_query(Broadcast.content_type, F.data.startswith("bc_type:"))
async def bc_type_chosen(call: CallbackQuery, state: FSMContext):
    ctype = call.data.split(":", 1)[1]
    await state.update_data(content_type=ctype)

    if ctype == "text":
        await call.message.edit_text(texts.BC_ENTER_TEXT)
        await state.set_state(Broadcast.entering_text)
    elif ctype == "photo":
        await call.message.edit_text(texts.BC_SEND_PHOTO)
        await state.set_state(Broadcast.waiting_media)
    elif ctype == "video":
        await call.message.edit_text(texts.BC_SEND_VIDEO)
        await state.set_state(Broadcast.waiting_media)
    elif ctype == "file":
        await call.message.edit_text(texts.BC_SEND_FILE)
        await state.set_state(Broadcast.waiting_media)
    elif ctype == "poll":
        await call.message.edit_text(texts.BC_POLL_QUESTION)
        await state.set_state(Broadcast.poll_question)
    await call.answer()


# ─── Step 4a: matn kiritish ────────────────────────────────────────────────

@router.message(Broadcast.entering_text, F.text)
async def bc_text_entered(message: Message, state: FSMContext):
    await state.update_data(bc_text=message.text, bc_file_id=None, bc_caption=None)
    await _show_confirm(message, state)


# ─── Step 4b: media qabul qilish ───────────────────────────────────────────

@router.message(Broadcast.waiting_media, F.photo)
async def bc_photo_received(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    caption = message.caption or ""
    await state.update_data(bc_file_id=file_id, bc_caption=caption, bc_text=None)
    await state.update_data(content_type="photo")
    await _show_confirm(message, state)


@router.message(Broadcast.waiting_media, F.video)
async def bc_video_received(message: Message, state: FSMContext):
    file_id = message.video.file_id
    caption = message.caption or ""
    await state.update_data(bc_file_id=file_id, bc_caption=caption, bc_text=None)
    await state.update_data(content_type="video")
    await _show_confirm(message, state)


@router.message(Broadcast.waiting_media, F.document)
async def bc_doc_received(message: Message, state: FSMContext):
    file_id = message.document.file_id
    caption = message.caption or ""
    await state.update_data(bc_file_id=file_id, bc_caption=caption, bc_text=None)
    await state.update_data(content_type="file")
    await _show_confirm(message, state)


@router.message(Broadcast.waiting_media)
async def bc_media_wrong(message: Message):
    await message.answer("❌ Iltimos, rasm, video yoki fayl yuboring.")


# ─── Step 4c: so'rovnoma ───────────────────────────────────────────────────

@router.message(Broadcast.poll_question, F.text)
async def bc_poll_question(message: Message, state: FSMContext):
    await state.update_data(bc_poll_question=message.text)
    await message.answer(texts.BC_POLL_OPTIONS)
    await state.set_state(Broadcast.poll_options)


@router.message(Broadcast.poll_options, F.text)
async def bc_poll_options(message: Message, state: FSMContext):
    options = [o.strip() for o in message.text.strip().splitlines() if o.strip()]
    if len(options) < 2:
        await message.answer(texts.BC_POLL_MIN_OPTIONS)
        return
    if len(options) > 10:
        await message.answer(texts.BC_POLL_MAX_OPTIONS)
        return
    await state.update_data(bc_poll_options=options, bc_text=None,
                             bc_file_id=None, bc_caption=None)
    await _show_confirm(message, state)


# ─── Confirm ko'rsatish ────────────────────────────────────────────────────

async def _show_confirm(source: Message, state: FSMContext):
    data = await state.get_data()
    ctype = data.get("content_type", "text")
    ctype_label = _CONTENT_LABELS.get(ctype, ctype)
    text = texts.BC_CONFIRM.format(
        target=data.get("target_label", "—"),
        ctype=ctype_label,
    )
    await source.answer(text, reply_markup=kb.bc_confirm_kb())
    await state.set_state(Broadcast.confirming)


# ─── Step 5: yuborish ──────────────────────────────────────────────────────

@router.callback_query(Broadcast.confirming, F.data == "bc_confirm:yes")
async def bc_do_send(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()

    target_type = data.get("target_type")
    target_id = data.get("target_id")
    ctype = data.get("content_type", "text")
    sender_emp_id = data.get("sender_emp_id")

    # Qabul qiluvchilarni aniqlash
    if target_type == "all":
        recipients = get_all_employees(active_only=True)
    elif target_type == "position":
        recipients = get_employees_by_position_id(target_id)
    else:
        emp = get_employee_by_id(target_id)
        recipients = [emp] if emp else []

    if not recipients:
        await call.message.edit_text(texts.BC_NO_RECIPIENTS)
        await call.answer()
        return

    await call.message.edit_text(texts.BC_SENDING)

    # DB ga broadcast yaratish
    bc_id = create_broadcast(sender_emp_id, target_type, target_id, ctype)

    # Sender ma'lumoti
    sender_emp = get_employee_by_id(sender_emp_id)
    sender_name = sender_emp["full_name"] if sender_emp else "Admin"
    header = texts.BC_HEADER.format(sender=sender_name)

    bc_text = data.get("bc_text")
    bc_file_id = data.get("bc_file_id")
    bc_caption = data.get("bc_caption") or ""
    bc_poll_question = data.get("bc_poll_question")
    bc_poll_opts = data.get("bc_poll_options", [])

    reaction_kb = kb.bc_reaction_kb(bc_id)
    sent_count = 0

    for emp in recipients:
        tg_id = emp["telegram_id"]
        if not tg_id:
            continue
        try:
            if ctype == "text":
                full_text = f"{header}\n\n{bc_text}"
                await bot.send_message(tg_id, full_text, reply_markup=reaction_kb)
            elif ctype == "photo":
                caption_full = f"{header}\n\n{bc_caption}" if bc_caption else header
                await bot.send_photo(tg_id, bc_file_id,
                                     caption=caption_full, reply_markup=reaction_kb)
            elif ctype == "video":
                caption_full = f"{header}\n\n{bc_caption}" if bc_caption else header
                await bot.send_video(tg_id, bc_file_id,
                                     caption=caption_full, reply_markup=reaction_kb)
            elif ctype == "file":
                caption_full = f"{header}\n\n{bc_caption}" if bc_caption else header
                await bot.send_document(tg_id, bc_file_id,
                                        caption=caption_full, reply_markup=reaction_kb)
            elif ctype == "poll":
                await bot.send_message(tg_id, header)
                await bot.send_poll(tg_id, bc_poll_question, options=bc_poll_opts)
            sent_count += 1
        except Exception as e:
            logger.warning("bc_do_send: tg_id=%s xato: %s", tg_id, e)

    await call.message.edit_text(texts.BC_DONE.format(sent=sent_count))
    await call.answer()


# ─── Reaksiya ──────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("bc_react:"))
async def bc_reaction(call: CallbackQuery):
    me = get_employee_by_telegram_id(call.from_user.id)
    if not me:
        await call.answer("Ruxsat yo'q.", show_alert=True)
        return
    parts = call.data.split(":")
    if len(parts) < 3:
        await call.answer()
        return
    try:
        bc_id = int(parts[1])
    except ValueError:
        await call.answer()
        return
    reaction = parts[2]
    try:
        save_broadcast_reaction(bc_id, me["id"], reaction)
    except Exception as e:
        logger.warning("bc_reaction: %s", e)
    await call.answer(texts.BC_REACT_SAVED, show_alert=False)


# ─── Izoh ──────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("bc_comment:"))
async def bc_comment_start(call: CallbackQuery, state: FSMContext):
    me = get_employee_by_telegram_id(call.from_user.id)
    if not me:
        await call.answer("Ruxsat yo'q.", show_alert=True)
        return
    try:
        bc_id = int(call.data.split(":", 1)[1])
    except (ValueError, IndexError):
        await call.answer()
        return
    await state.set_state(BroadcastComment.entering)
    await state.update_data(bc_comment_id=bc_id, bc_commenter_emp_id=me["id"])
    await call.answer()
    await call.message.answer(texts.BC_COMMENT_ASK, reply_markup=kb.cancel_kb())


@router.message(BroadcastComment.entering, F.text)
async def bc_comment_submit(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    bc_id = data.get("bc_comment_id")
    emp_id = data.get("bc_commenter_emp_id")
    await state.clear()

    if not bc_id or not emp_id:
        await message.answer("❌ Xato yuz berdi.")
        return

    try:
        save_broadcast_comment(bc_id, emp_id, message.text)
    except Exception as e:
        logger.warning("bc_comment_submit: %s", e)

    emp = get_employee_by_id(emp_id)
    emp_name = emp["full_name"] if emp else "Xodim"

    # Jo'natuvchiga xabarni yuborish
    sender_row = get_broadcast_sender(bc_id)
    if sender_row:
        forward_text = texts.BC_COMMENT_FORWARD.format(
            emp_name=emp_name,
            comment=message.text
        )
        try:
            await bot.send_message(sender_row["tg_id"], forward_text)
        except Exception as e:
            logger.warning("bc_comment_submit forward: %s", e)

    # Xodimga tasdiqlash
    from handlers.common import _main_kb
    me = get_employee_by_telegram_id(message.from_user.id)
    await message.answer(texts.BC_COMMENT_SENT,
                         reply_markup=_main_kb(me) if me else kb.remove_kb())


# ─── Bekor qilish (inline) ─────────────────────────────────────────────────

@router.callback_query(F.data == "bc_cancel")
async def bc_cancel_inline(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Xabarnoma bekor qilindi.")
    await call.answer()
