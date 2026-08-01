"""Yangi xodimni ro'yxatdan o'tkazish"""
import asyncio
import io
import re
import logging
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType

import texts
import keyboards as kb
from states import Registration
from database import (
    create_employee, get_employee_by_telegram_id,
    get_active_employees_count, get_employee_by_id,
    find_employee_by_phone, link_pending_to_telegram, update_employee_card,
)
from services.face_service import encode_face_from_bytes
from config import MAX_EMPLOYEES, INITIAL_ADMIN_ID

logger = logging.getLogger(__name__)
router = Router()


def _menu_for(employee):
    """Xodim yozuviga mos asosiy menyu klaviaturasi."""
    is_admin = bool(employee["is_admin"]) if employee else False
    is_boss = (employee["role"] == "boss") if employee else False
    has_pf = bool(employee["pf_access"]) if employee else False
    return kb.main_menu_kb(is_admin=is_admin, is_boss=is_boss, has_pf=has_pf)


# ===== Phase 4: begona /start -> telefon orqali bog'lash =====

@router.message(Registration.linking_phone, F.contact)
async def link_phone_contact(message: Message, state: FSMContext):
    # Faqat o'z raqamini yuborishi mumkin
    if message.contact.user_id != message.from_user.id:
        await message.answer("❌ Iltimos, o'z raqamingizni yuboring.")
        return
    emp = find_employee_by_phone(
        message.contact.phone_number, only_pending=True, include_inactive=False
    )
    if emp is None:
        await message.answer(
            texts.LINK_NOT_FOUND.format(tg_id=message.from_user.id),
            reply_markup=kb.remove_kb()
        )
        await state.clear()
        return
    # Topildi — selfi so'raymiz
    await state.update_data(pending_emp_id=emp["id"])
    await message.answer(texts.REG_ASK_FACE, reply_markup=kb.cancel_kb())
    await state.set_state(Registration.waiting_face_photo)


@router.message(Registration.linking_phone)
async def link_phone_invalid(message: Message):
    await message.answer(texts.REG_PHONE_INVALID)


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

    data = await state.get_data()
    pending_emp_id = data.get("pending_emp_id")

    # Limit qayta tekshirish — faqat YANGI yozuv yaratilganda (Oqim A).
    # Oqim B (bog'lash)da yozuv allaqachon mavjud, limit hisobga olingan.
    if pending_emp_id is None and get_active_employees_count() >= MAX_EMPLOYEES:
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

    if pending_emp_id is not None:
        # Oqim B — admin oldindan qo'shgan yozuvni bog'lash
        link_pending_to_telegram(pending_emp_id, message.from_user.id, encoding)
        emp_id = pending_emp_id
        logger.info("Pending employee linked: id=%s tg=%s",
                    emp_id, message.from_user.id)
    else:
        # Oqim A — INITIAL_ADMIN bootstrap
        emp_id = create_employee(
            telegram_id=message.from_user.id,
            full_name=data["full_name"],
            phone=data["phone"],
            position=data["position"],
            face_encoding=encoding,
        )
        logger.info("New employee created: id=%s tg=%s",
                    emp_id, message.from_user.id)

    # Ikkala oqimda ham — karta ma'lumotlari so'raladi
    await state.update_data(new_emp_id=emp_id)
    await message.answer(texts.CARD_ASK_NUMBER, reply_markup=kb.cancel_kb())
    await state.set_state(Registration.waiting_card_number)


@router.message(Registration.waiting_face_photo)
async def reg_face_invalid(message: Message):
    await message.answer(texts.REG_PHOTO_REQUIRED)


# ===== Phase 4: karta qadamlari (ro'yxatdan o'tish oxirida) =====

@router.message(Registration.waiting_card_number, F.text == texts.BTN_CANCEL)
@router.message(Registration.waiting_card_holder_name, F.text == texts.BTN_CANCEL)
async def reg_card_cancel(message: Message, state: FSMContext):
    # Karta yarim qoldirilsa ham yozuv bor — keyin Profil orqali qo'shadi.
    await state.clear()
    emp = get_employee_by_telegram_id(message.from_user.id)
    if emp:
        await message.answer(
            "ℹ️ Kartani keyinroq <b>Profilim → 💳 Karta ma'lumotlari</b> "
            "orqali qo'shishingiz mumkin.",
            reply_markup=_menu_for(emp)
        )
    else:
        await message.answer(texts.CANCELLED, reply_markup=kb.remove_kb())


@router.message(Registration.waiting_card_number, F.text)
async def reg_card_number(message: Message, state: FSMContext):
    digits = re.sub(r"\D", "", message.text)
    if len(digits) != 16:
        await message.answer(texts.CARD_INVALID_NUMBER)
        return
    await state.update_data(card_number=digits)
    await message.answer(texts.CARD_ASK_HOLDER)
    await state.set_state(Registration.waiting_card_holder_name)


@router.message(Registration.waiting_card_number)
async def reg_card_number_invalid(message: Message):
    await message.answer(texts.CARD_INVALID_NUMBER)


@router.message(Registration.waiting_card_holder_name, F.text)
async def reg_card_holder(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 3:
        await message.answer(texts.CARD_INVALID_HOLDER)
        return
    data = await state.get_data()
    emp_id = data.get("new_emp_id")
    update_employee_card(emp_id, data["card_number"], name)
    await state.clear()

    emp = get_employee_by_id(emp_id)
    is_admin = emp_id is not None and emp and message.from_user.id == INITIAL_ADMIN_ID
    admin_note = texts.ADMIN_BADGE_NOTE if is_admin else ""
    formatted = texts.format_card(data["card_number"], name)
    await message.answer(
        texts.REG_SUCCESS_WITH_CARD.format(card=formatted, admin_note=admin_note),
        reply_markup=_menu_for(emp)
    )
    logger.info("Card saved for employee id=%s", emp_id)


@router.message(Registration.waiting_card_holder_name)
async def reg_card_holder_invalid(message: Message):
    await message.answer(texts.CARD_INVALID_HOLDER)
