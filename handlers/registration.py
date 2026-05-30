"""Yangi xodimni ro'yxatdan o'tkazish"""
import asyncio
import io
import logging
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType

import texts
import keyboards as kb
from states import Registration
from database import (
    create_employee, get_employee_by_telegram_id,
    get_active_employees_count
)
from services.face_service import encode_face_from_bytes
from config import MAX_EMPLOYEES, INITIAL_ADMIN_ID

logger = logging.getLogger(__name__)
router = Router()


@router.message(Registration.waiting_full_name, F.text)
async def reg_full_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 5:
        await message.answer(texts.REG_NAME_TOO_SHORT)
        return
    await state.update_data(full_name=name)
    await message.answer(texts.REG_ASK_PHONE, reply_markup=kb.phone_request_kb())
    await state.set_state(Registration.waiting_phone)


@router.message(Registration.waiting_phone, F.contact)
async def reg_phone_contact(message: Message, state: FSMContext):
    # Faqat o'z raqamini yuborishi mumkin
    if message.contact.user_id != message.from_user.id:
        await message.answer("❌ Iltimos, o'z raqamingizni yuboring.")
        return
    await state.update_data(phone=message.contact.phone_number)
    await message.answer(texts.REG_ASK_POSITION, reply_markup=kb.cancel_kb())
    await state.set_state(Registration.waiting_position)


@router.message(Registration.waiting_phone)
async def reg_phone_invalid(message: Message):
    await message.answer(texts.REG_PHONE_INVALID)


@router.message(Registration.waiting_position, F.text)
async def reg_position(message: Message, state: FSMContext):
    position = message.text.strip()
    if len(position) < 2:
        await message.answer(texts.REG_POSITION_TOO_SHORT)
        return
    await state.update_data(position=position)
    await message.answer(texts.REG_ASK_FACE, reply_markup=kb.cancel_kb())
    await state.set_state(Registration.waiting_face_photo)


@router.message(Registration.waiting_face_photo, F.photo)
async def reg_face_photo(message: Message, state: FSMContext, bot: Bot):
    # Eng yuqori sifatli rasm
    photo = message.photo[-1]

    # Limit qayta tekshirish (race condition)
    if get_active_employees_count() >= MAX_EMPLOYEES:
        await message.answer(texts.MAX_EMPLOYEES_REACHED.format(max=MAX_EMPLOYEES),
                             reply_markup=kb.remove_kb())
        await state.clear()
        return

    await message.answer("⏳ Yuzingiz tahlil qilinmoqda...")

    # Rasmni yuklab olish
    buf = io.BytesIO()
    await bot.download(photo, destination=buf)
    img_bytes = buf.getvalue()

    encoding, err = await asyncio.to_thread(encode_face_from_bytes, img_bytes)

    if err == "no_face":
        await message.answer(texts.REG_FACE_NOT_DETECTED)
        return
    if err == "multiple_faces":
        await message.answer(texts.REG_FACE_MULTIPLE)
        return
    if err:
        logger.error("Face encoding error: %s", err)
        await message.answer(f"❌ Xatolik: {err}")
        return

    # Saqlash
    data = await state.get_data()
    employee_id = create_employee(
        telegram_id=message.from_user.id,
        full_name=data["full_name"],
        phone=data["phone"],
        position=data["position"],
        face_encoding=encoding,
    )

    is_admin = message.from_user.id == INITIAL_ADMIN_ID
    admin_note = texts.ADMIN_BADGE_NOTE if is_admin else ""

    await state.clear()
    await message.answer(
        texts.REG_SUCCESS.format(
            name=data["full_name"],
            position=data["position"],
            admin_note=admin_note,
        ),
        reply_markup=kb.main_menu_kb(is_admin=is_admin)
    )
    logger.info("New employee registered: %s (id=%s, tg=%s)",
                data["full_name"], employee_id, message.from_user.id)


@router.message(Registration.waiting_face_photo)
async def reg_face_invalid(message: Message):
    await message.answer(texts.REG_PHOTO_REQUIRED)
