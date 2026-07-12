"""Moliya turkumlari (kategoriya) boshqaruvi — Boss va Bosh Admin.

"🏷 Moliya turkumlari" tugmasi orqali kirim/chiqim turkumlarini qo'shish/o'chirish.
Har bir moliya egasi (boss / bosh_admin) FAQAT o'z turkumlarini ko'radi va boshqaradi.
"""
import logging

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
)

import texts
import keyboards as kb
from states import FinanceCategoryManage
from database import (
    get_employee_by_telegram_id,
    get_all_finance_categories, get_finance_category,
    create_finance_category, delete_finance_category,
    ensure_owner_categories,
)

logger = logging.getLogger(__name__)
router = Router()


def _owner_emp(obj):
    """Moliya egasi (boss yoki bosh_admin) bo'lsa emp qaytaradi, aks holda None."""
    emp = get_employee_by_telegram_id(obj.from_user.id)
    if emp and emp["role"] in ("boss", "bosh_admin"):
        return emp
    return None


def _menu_text(cats) -> str:
    income = [c for c in cats if c["entry_type"] == "income"]
    expense = [c for c in cats if c["entry_type"] == "expense"]
    parts = []
    if income:
        parts.append(texts.FINCAT_TYPE_INCOME)
        parts += [f"  {c['emoji']} {c['name']}" for c in income]
    if expense:
        parts.append(texts.FINCAT_TYPE_EXPENSE)
        parts += [f"  {c['emoji']} {c['name']}" for c in expense]
    lst = "\n".join(parts) if parts else texts.FINCAT_EMPTY
    return texts.FINCAT_MENU_HEADER.format(list=lst)


def _menu_kb(cats) -> InlineKeyboardMarkup:
    rows = []
    for c in cats:
        if c["protected"]:
            rows.append([InlineKeyboardButton(
                text=f"🔒 {c['emoji']} {c['name']}",
                callback_data="fincat_locked"
            )])
        else:
            rows.append([InlineKeyboardButton(
                text=f"🗑 {c['emoji']} {c['name']}",
                callback_data=f"fincat_del:{c['id']}"
            )])
    rows.append([InlineKeyboardButton(
        text=texts.BTN_FINCAT_ADD, callback_data="fincat_add"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ===== Menyu =====

@router.message(F.text == texts.BTN_FINANCE_CATEGORIES)
async def fincat_menu(message: Message, state: FSMContext):
    emp = _owner_emp(message)
    if not emp:
        return
    await state.clear()
    ensure_owner_categories(emp["id"])
    cats = get_all_finance_categories(emp["id"], active_only=True)
    await message.answer(_menu_text(cats), reply_markup=_menu_kb(cats))


@router.callback_query(F.data == "fincat_locked")
async def fincat_locked(call: CallbackQuery):
    await call.answer(texts.FINCAT_DELETE_PROTECTED, show_alert=True)


# ===== O'chirish =====

@router.callback_query(F.data.startswith("fincat_del:"))
async def fincat_delete(call: CallbackQuery):
    emp = _owner_emp(call)
    if not emp:
        await call.answer(texts.NO_PERMISSION, show_alert=True)
        return
    try:
        cat_id = int(call.data.split(":")[1])
    except (IndexError, ValueError):
        await call.answer("❌ Xato", show_alert=True)
        return
    cat = get_finance_category(cat_id)
    if not cat or cat["owner_id"] != emp["id"]:
        await call.answer("Topilmadi", show_alert=True)
        return
    if cat["protected"]:
        await call.answer(texts.FINCAT_DELETE_PROTECTED, show_alert=True)
        return
    delete_finance_category(cat_id, emp["id"])
    await call.answer("✅")
    cats = get_all_finance_categories(emp["id"], active_only=True)
    await call.message.edit_text(
        texts.FINCAT_DELETED.format(emoji=cat["emoji"], name=cat["name"]),
    )
    await call.message.answer(_menu_text(cats), reply_markup=_menu_kb(cats))
    logger.info("Finance category deleted id=%s owner=%s by tg=%s",
                cat_id, emp["id"], call.from_user.id)


# ===== Qo'shish (FSM) =====

@router.callback_query(F.data == "fincat_add")
async def fincat_add_start(call: CallbackQuery, state: FSMContext):
    emp = _owner_emp(call)
    if not emp:
        await call.answer(texts.NO_PERMISSION, show_alert=True)
        return
    await call.message.answer(
        texts.FINCAT_ASK_TYPE,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📥 Kirim", callback_data="fincat_type:income"),
             InlineKeyboardButton(text="📤 Chiqim", callback_data="fincat_type:expense")],
            [InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data="fincat_type:cancel")],
        ])
    )
    await state.set_state(FinanceCategoryManage.choose_type)
    await call.answer()


@router.callback_query(FinanceCategoryManage.choose_type, F.data.startswith("fincat_type:"))
async def fincat_choose_type(call: CallbackQuery, state: FSMContext):
    val = call.data.split(":")[1]
    if val == "cancel":
        await state.clear()
        await call.message.edit_text(texts.CANCELLED)
        await call.answer()
        return
    await state.update_data(fc_type=val)
    await call.message.answer(
        texts.FINCAT_ASK_EMOJI.format(skip=texts.FINCAT_EMOJI_SKIP),
        reply_markup=kb.cancel_kb()
    )
    await state.set_state(FinanceCategoryManage.waiting_emoji)
    await call.answer()


# Bekor qilish — har qanday qo'shish bosqichida
@router.message(StateFilter(FinanceCategoryManage), F.text == texts.BTN_CANCEL)
async def fincat_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(texts.CANCELLED)
    emp = _owner_emp(message)
    if emp:
        cats = get_all_finance_categories(emp["id"], active_only=True)
        await message.answer(_menu_text(cats), reply_markup=_menu_kb(cats))


@router.message(FinanceCategoryManage.waiting_emoji, F.text)
async def fincat_emoji(message: Message, state: FSMContext):
    txt = message.text.strip()
    if txt.lower() == texts.FINCAT_EMOJI_SKIP:
        emoji = "🏷"
    else:
        emoji = txt[:4]
    await state.update_data(fc_emoji=emoji)
    await message.answer(texts.FINCAT_ASK_NAME, reply_markup=kb.cancel_kb())
    await state.set_state(FinanceCategoryManage.waiting_name)


@router.message(FinanceCategoryManage.waiting_name, F.text)
async def fincat_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer(texts.FINCAT_NAME_SHORT)
        return
    emp = _owner_emp(message)
    if not emp:
        await state.clear()
        return
    data = await state.get_data()
    await state.clear()
    entry_type = data["fc_type"]
    emoji = data.get("fc_emoji", "🏷")
    create_finance_category(entry_type, emoji, name, emp["id"])
    type_label = "Kirim" if entry_type == "income" else "Chiqim"
    await message.answer(
        texts.FINCAT_ADDED.format(emoji=emoji, name=name, type=type_label)
    )
    cats = get_all_finance_categories(emp["id"], active_only=True)
    await message.answer(_menu_text(cats), reply_markup=_menu_kb(cats))
    logger.info("Finance category created (%s, %s) owner=%s by tg=%s",
                entry_type, name, emp["id"], message.from_user.id)
