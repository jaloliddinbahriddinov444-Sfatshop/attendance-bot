"""Umumiy handlerlar: /start, /cancel, /help"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import texts
import keyboards as kb
from database import get_employee_by_telegram_id, get_active_employees_count
from config import MAX_EMPLOYEES, INITIAL_ADMIN_ID

router = Router()


def _main_kb(employee):
    """Xodim roliga qarab to'g'ri asosiy klaviaturani qaytaradi."""
    role = employee["role"] if employee else "employee"
    if role == "bosh_admin":
        return kb.main_menu_kb(is_bosh_admin=True)
    if role == "boss":
        return kb.main_menu_kb(is_boss=True)
    return kb.main_menu_kb(is_admin=bool(employee["is_admin"]))


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    employee = get_employee_by_telegram_id(message.from_user.id)

    if employee:
        await message.answer(
            texts.WELCOME_BACK.format(name=employee["full_name"]),
            reply_markup=_main_kb(employee)
        )
        return

    from states import Registration

    if message.from_user.id == INITIAL_ADMIN_ID and get_active_employees_count() == 0:
        await message.answer(texts.WELCOME_NEW, reply_markup=kb.remove_kb())
        await message.answer(texts.REG_START, reply_markup=kb.cancel_kb())
        await state.set_state(Registration.waiting_full_name)
        return

    await message.answer(texts.LINK_ASK_PHONE, reply_markup=kb.phone_request_kb())
    await state.set_state(Registration.linking_phone)


@router.message(Command("cancel"))
@router.message(F.text == texts.BTN_CANCEL)
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    employee = get_employee_by_telegram_id(message.from_user.id)
    if employee:
        await message.answer(texts.CANCELLED, reply_markup=_main_kb(employee))
    else:
        await message.answer(texts.CANCELLED, reply_markup=kb.remove_kb())


@router.message(F.text == texts.BTN_BACK)
async def go_back(message: Message, state: FSMContext):
    await state.clear()
    employee = get_employee_by_telegram_id(message.from_user.id)
    if not employee:
        await message.answer(texts.NOT_REGISTERED)
        return
    await message.answer(texts.MAIN_MENU, reply_markup=_main_kb(employee))


@router.message(F.text)
async def unknown_text(message: Message):
    employee = get_employee_by_telegram_id(message.from_user.id)
    if not employee:
        await message.answer(texts.NOT_REGISTERED)
        return
    await message.answer(texts.UNKNOWN_COMMAND, reply_markup=_main_kb(employee))
