"""Xabarnoma (Broadcast) — Boss va Bosh Admin uchun.

Ikkita rejim:
  1. Kanal/Guruhga  — sozlangan kanalga post, Telegram o'zi reaksiya+izohni boshqaradi
  2. Alohida xodimga DM — bitta xodimning shaxsiy chatiga yuborish
"""
import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import texts
import keyboards as kb
from database import (
    get_employee_by_telegram_id, get_employee_by_id,
    get_all_employees,
    create_broadcast,
    get_setting, set_setting,
)
from states import Broadcast

logger = logging.getLogger(__name__)
router = Router()

_CONTENT_LABELS = {
    "text": "📝 Matn",
    "photo": "🖼 Rasm",
    "video": "🎬 Video",
    "file": "📄 Fayl",
    "poll": "📊 So'rovnoma",
}

BC_CHAT_KEY = "bc_chat_id"
BC_CHAT_TITLE_KEY = "bc_chat_title"


def _require_boss_or_bosh(emp) -> bool:
    if not emp:
        return False
    try:
        return emp["role"] in ("boss", "bosh_admin")
    except (KeyError, IndexError):
        return False


# ─── Ochilish ──────────────────────────────────────────────────────────────

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


# ─── Target: kanal ─────────────────────────────────────────────────────────

@router.callback_query(Broadcast.target, F.data == "bc_target:channel")
async def bc_target_channel(call: CallbackQuery, state: FSMContext):
    chat_id = get_setting(BC_CHAT_KEY)
    if not chat_id:
        await state.set_state(Broadcast.setup_chat)
        await call.message.edit_text(texts.BC_NO_CHAT)
        await call.answer()
        return
    chat_title = get_setting(BC_CHAT_TITLE_KEY) or chat_id
    await state.update_data(target_type="channel", target_chat_id=chat_id,
                            target_label=chat_title)
    await call.message.edit_text(texts.BC_CHOOSE_CONTENT,
                                 reply_markup=kb.bc_content_type_kb())
    await state.set_state(Broadcast.content_type)
    await call.answer()


# ─── Target: alohida xodim ─────────────────────────────────────────────────

@router.callback_query(Broadcast.target, F.data == "bc_target:emp")
async def bc_target_emp(call: CallbackQuery, state: FSMContext):
    employees = get_all_employees(active_only=True)
    if not employees:
        await call.answer("Hech qanday xodim topilmadi.", show_alert=True)
        return
    await call.message.edit_text(texts.BC_CHOOSE_EMP,
                                 reply_markup=kb.bc_employees_kb(employees))
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
    await state.update_data(target_type="employee", target_emp_id=emp_id,
                            target_label=emp["full_name"])
    await call.message.edit_text(texts.BC_CHOOSE_CONTENT,
                                 reply_markup=kb.bc_content_type_kb())
    await state.set_state(Broadcast.content_type)
    await call.answer()


# ─── Kanal sozlash ─────────────────────────────────────────────────────────

@router.message(Broadcast.setup_chat)
async def bc_setup_chat(message: Message, state: FSMContext, bot: Bot):
    # Forward qilingan xabar
    if message.forward_from_chat:
        chat_id = str(message.forward_from_chat.id)
        chat_title = message.forward_from_chat.title or chat_id
    else:
        raw = (message.text or "").strip()
        if not raw:
            await message.answer(texts.BC_CHAT_ERROR)
            return
        chat_id = raw
        chat_title = raw

    await message.answer(texts.BC_CHAT_CHECKING)
    try:
        chat = await bot.get_chat(chat_id)
        chat_id = str(chat.id)
        chat_title = chat.title or chat_id
        # Bot kanalda admin ekanligini tekshirish
        member = await bot.get_chat_member(chat_id, (await bot.get_me()).id)
        if member.status not in ("administrator", "creator"):
            await message.answer(texts.BC_CHAT_ERROR)
            return
    except Exception as e:
        logger.warning("bc_setup_chat: %s", e)
        await message.answer(texts.BC_CHAT_ERROR)
        return

    set_setting(BC_CHAT_KEY, chat_id)
    set_setting(BC_CHAT_TITLE_KEY, chat_title)

    await message.answer(texts.BC_CHAT_SAVED.format(
        title=chat_title, chat_id=chat_id
    ))
    # Muvaffaqiyatli sozlangandan keyin content type tanlashga o'tish
    await state.update_data(target_type="channel", target_chat_id=chat_id,
                            target_label=chat_title)
    await message.answer(texts.BC_CHOOSE_CONTENT,
                         reply_markup=kb.bc_content_type_kb())
    await state.set_state(Broadcast.content_type)


# ─── Content type ──────────────────────────────────────────────────────────

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


# ─── Matn ──────────────────────────────────────────────────────────────────

@router.message(Broadcast.entering_text, F.text)
async def bc_text_entered(message: Message, state: FSMContext):
    await state.update_data(bc_text=message.text, bc_file_id=None, bc_caption=None)
    await _show_confirm(message, state)


# ─── Media ─────────────────────────────────────────────────────────────────

@router.message(Broadcast.waiting_media, F.photo)
async def bc_photo_received(message: Message, state: FSMContext):
    await state.update_data(content_type="photo",
                            bc_file_id=message.photo[-1].file_id,
                            bc_caption=message.caption or "", bc_text=None)
    await _show_confirm(message, state)


@router.message(Broadcast.waiting_media, F.video)
async def bc_video_received(message: Message, state: FSMContext):
    await state.update_data(content_type="video",
                            bc_file_id=message.video.file_id,
                            bc_caption=message.caption or "", bc_text=None)
    await _show_confirm(message, state)


@router.message(Broadcast.waiting_media, F.document)
async def bc_doc_received(message: Message, state: FSMContext):
    await state.update_data(content_type="file",
                            bc_file_id=message.document.file_id,
                            bc_caption=message.caption or "", bc_text=None)
    await _show_confirm(message, state)


@router.message(Broadcast.waiting_media)
async def bc_media_wrong(message: Message):
    await message.answer("❌ Iltimos, rasm, video yoki fayl yuboring.")


# ─── So'rovnoma ────────────────────────────────────────────────────────────

@router.message(Broadcast.poll_question, F.text)
async def bc_poll_question_entered(message: Message, state: FSMContext):
    await state.update_data(bc_poll_question=message.text)
    await message.answer(texts.BC_POLL_OPTIONS)
    await state.set_state(Broadcast.poll_options)


@router.message(Broadcast.poll_options, F.text)
async def bc_poll_options_entered(message: Message, state: FSMContext):
    options = [o.strip() for o in message.text.strip().splitlines() if o.strip()]
    if len(options) < 2:
        await message.answer(texts.BC_POLL_MIN_OPTIONS)
        return
    if len(options) > 10:
        await message.answer(texts.BC_POLL_MAX_OPTIONS)
        return
    await state.update_data(bc_poll_options=options,
                            bc_text=None, bc_file_id=None, bc_caption=None)
    await _show_confirm(message, state)


# ─── Confirm ───────────────────────────────────────────────────────────────

async def _show_confirm(source: Message, state: FSMContext):
    data = await state.get_data()
    ctype = data.get("content_type", "text")
    ctype_label = _CONTENT_LABELS.get(ctype, ctype)
    target_type = data.get("target_type")

    if target_type == "channel":
        text = texts.BC_CONFIRM_CHANNEL.format(
            chat_title=data.get("target_label", "—"),
            ctype=ctype_label,
        )
    else:
        text = texts.BC_CONFIRM_DM.format(
            emp_name=data.get("target_label", "—"),
            ctype=ctype_label,
        )
    await source.answer(text, reply_markup=kb.bc_confirm_kb())
    await state.set_state(Broadcast.confirming)


# ─── Yuborish ──────────────────────────────────────────────────────────────

@router.callback_query(Broadcast.confirming, F.data == "bc_confirm:yes")
async def bc_do_send(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()

    target_type = data.get("target_type")
    ctype = data.get("content_type", "text")
    sender_emp_id = data.get("sender_emp_id")
    bc_text = data.get("bc_text")
    bc_file_id = data.get("bc_file_id")
    bc_caption = data.get("bc_caption") or ""
    bc_poll_question = data.get("bc_poll_question")
    bc_poll_opts = data.get("bc_poll_options", [])

    await call.message.edit_text(texts.BC_SENDING)

    # ── Kanalga yuborish ──
    if target_type == "channel":
        chat_id = data.get("target_chat_id") or get_setting(BC_CHAT_KEY)
        if not chat_id:
            await call.message.edit_text(texts.BC_NO_CHAT)
            await call.answer()
            return
        try:
            await _send_content(bot, chat_id, ctype,
                                bc_text, bc_file_id, bc_caption,
                                bc_poll_question, bc_poll_opts)
            create_broadcast(sender_emp_id, "channel", None, ctype)
            await call.message.edit_text(texts.BC_DONE_CHANNEL)
        except Exception as e:
            logger.error("bc_do_send channel: %s", e)
            await call.message.edit_text(
                f"❌ Xato yuz berdi: <code>{e}</code>\n\n"
                "Bot kanalda admin ekanligini tekshiring."
            )

    # ── DM ──
    else:
        emp_id = data.get("target_emp_id")
        emp = get_employee_by_id(emp_id) if emp_id else None
        if not emp:
            await call.message.edit_text(texts.BC_NO_RECIPIENTS)
            await call.answer()
            return
        tg_id = emp["telegram_id"]
        sender_emp = get_employee_by_id(sender_emp_id)
        sender_name = sender_emp["full_name"] if sender_emp else "Admin"
        header = texts.BC_HEADER.format(sender=sender_name)

        try:
            if bc_text:
                full_text = f"{header}\n\n{bc_text}"
                await bot.send_message(tg_id, full_text)
            elif bc_file_id:
                cap = f"{header}\n\n{bc_caption}" if bc_caption else header
                await _send_content(bot, tg_id, ctype,
                                    None, bc_file_id, cap,
                                    bc_poll_question, bc_poll_opts,
                                    header=header)
            else:
                await _send_content(bot, tg_id, ctype,
                                    bc_text, bc_file_id, bc_caption,
                                    bc_poll_question, bc_poll_opts,
                                    header=header)
            create_broadcast(sender_emp_id, "employee", emp_id, ctype)
            await call.message.edit_text(
                texts.BC_DONE_DM.format(name=emp["full_name"])
            )
        except Exception as e:
            logger.error("bc_do_send DM: %s", e)
            await call.message.edit_text(
                f"❌ Xato: <code>{e}</code>"
            )

    await call.answer()


async def _send_content(bot: Bot, chat_id, ctype: str,
                        bc_text, bc_file_id, bc_caption,
                        bc_poll_question, bc_poll_opts,
                        header: str = ""):
    if ctype == "text":
        await bot.send_message(chat_id, bc_text)
    elif ctype == "photo":
        await bot.send_photo(chat_id, bc_file_id, caption=bc_caption or None)
    elif ctype == "video":
        await bot.send_video(chat_id, bc_file_id, caption=bc_caption or None)
    elif ctype == "file":
        await bot.send_document(chat_id, bc_file_id, caption=bc_caption or None)
    elif ctype == "poll":
        if header:
            await bot.send_message(chat_id, header)
        await bot.send_poll(chat_id, bc_poll_question, options=bc_poll_opts)


# ─── Bekor qilish (inline) ─────────────────────────────────────────────────

@router.callback_query(F.data == "bc_cancel")
async def bc_cancel_inline(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Xabarnoma bekor qilindi.")
    await call.answer()
