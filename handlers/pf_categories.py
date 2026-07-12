"""Shaxsiy moliya (PF) turkumlari boshqaruvi — Boss va Bosh Admin.

"🏷 Shaxsiy turkumlar" tugmasi orqali PF kirim/chiqim turkumlarini
qo'shish/o'chirish. Har bir ega FAQAT o'z turkumlarini ko'radi va boshqaradi.
fin_categories.py bilan bir xil oqim, faqat pf_categories jadvali ustida.
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
from states import PFCategoryManage
from database import (
    get_employee_by_telegram_id,
    get_all_pf_categories, get_pf_category,
    create_pf_category, delete_pf_category,
    ensure_owner_pf_categories,
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
    return texts.PFCAT_MENU_HEADER.format(list=lst)


def _menu_kb(cats) -> InlineKeyboardMarkup:
    rows = []
    for c in cats:
        rows.append([InlineKeyboardButton(
            text=f"🗑 {c['emoji']} {c['name']}",
            callback_data=f"pfcat_del:{c['id']}"
        )])
    rows.append([InlineKeyboardButton(
        text=texts.BTN_FINCAT_ADD, callback_data="pfcat_add"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ===== Menyu =====

@router.message(F.text == texts.BTN_PF_CATEGORIES)
async def pfcat_menu(message: Message, state: FSMContext):
    emp = _owner_emp(message)
    if not emp:
        return
    await state.clear()
    ensure_owner_pf_categories(emp["id"])
    cats = get_all_pf_categories(emp["id"], active_only=True)
    await message.answer(_menu_text(cats), reply_markup=_menu_kb(cats))


# ===== O'chirish =====

@router.callback_query(F.data.startswith("pfcat_del:"))
async def pfcat_delete(call: CallbackQuery):
    emp = _owner_emp(call)
    if not emp:
        await call.answer(texts.NO_PERMISSION, show_alert=True)
        return
    try:
        cat_id = int(call.data.split(":")[1])
    except (IndexError, ValueError):
        await call.answer("❌ Xato", show_alert=True)
        return
    cat = get_pf_category(cat_id)
    if not cat or cat["owner_id"] != emp["id"]:
        await call.answer("Topilmadi", show_alert=True)
        return
    if not delete_pf_category(cat_id, emp["id"]):
        await call.answer(texts.FINCAT_DELETE_PROTECTED, show_alert=True)
        return
    await call.answer("✅")
    cats = get_all_pf_categories(emp["id"], active_only=True)
    await call.message.edit_text(
        texts.FINCAT_DELETED.format(emoji=cat["emoji"], name=cat["name"]),
    )
    await call.message.answer(_menu_text(cats), reply_markup=_menu_kb(cats))
    logger.info("PF category deleted id=%s owner=%s by tg=%s",
                cat_id, emp["id"], call.from_user.id)


# ===== Qo'shish (FSM) =====

@router.callback_query(F.data == "pfcat_add")
async def pfcat_add_start(call: CallbackQuery, state: FSMContext):
    emp = _owner_emp(call)
    if not emp:
        await call.answer(texts.NO_PERMISSION, show_alert=True)
        return
    await call.message.answer(
        texts.FINCAT_ASK_TYPE,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📥 Kirim", callback_data="pfcat_type:income"),
             InlineKeyboardButton(text="📤 Chiqim", callback_data="pfcat_type:expense")],
            [InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data="pfcat_type:cancel")],
        ])
    )
    await state.set_state(PFCategoryManage.choose_type)
    await call.answer()


@router.callback_query(PFCategoryManage.choose_type, F.data.startswith("pfcat_type:"))
async def pfcat_choose_type(call: CallbackQuery, state: FSMContext):
    val = call.data.split(":")[1]
    if val == "cancel":
        await state.clear()
        await call.message.edit_text(texts.CANCELLED)
        await call.answer()
        return
    await state.update_data(pfc_type=val)
    await call.message.answer(
        texts.FINCAT_ASK_EMOJI.format(skip=texts.FINCAT_EMOJI_SKIP),
        reply_markup=kb.cancel_kb()
    )
    await state.set_state(PFCategoryManage.waiting_emoji)
    await call.answer()


# Bekor qilish — har qanday qo'shish bosqichida
@router.message(StateFilter(PFCategoryManage), F.text == texts.BTN_CANCEL)
async def pfcat_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(texts.CANCELLED, reply_markup=kb.pf_menu_kb())
    emp = _owner_emp(message)
    if emp:
        cats = get_all_pf_categories(emp["id"], active_only=True)
        await message.answer(_menu_text(cats), reply_markup=_menu_kb(cats))


@router.message(PFCategoryManage.waiting_emoji, F.text)
async def pfcat_emoji(message: Message, state: FSMContext):
    txt = message.text.strip()
    if txt.lower() == texts.FINCAT_EMOJI_SKIP:
        emoji = "🏷"
    else:
        emoji = txt[:4]
    await state.update_data(pfc_emoji=emoji)
    await message.answer(texts.FINCAT_ASK_NAME, reply_markup=kb.cancel_kb())
    await state.set_state(PFCategoryManage.waiting_name)


@router.message(PFCategoryManage.waiting_name, F.text)
async def pfcat_name(message: Message, state: FSMContext):
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
    entry_type = data["pfc_type"]
    emoji = data.get("pfc_emoji", "🏷")
    create_pf_category(entry_type, emoji, name, emp["id"])
    type_label = "Kirim" if entry_type == "income" else "Chiqim"
    await message.answer(
        texts.FINCAT_ADDED.format(emoji=emoji, name=name, type=type_label),
        reply_markup=kb.pf_menu_kb()
    )
    cats = get_all_pf_categories(emp["id"], active_only=True)
    await message.answer(_menu_text(cats), reply_markup=_menu_kb(cats))
    logger.info("PF category created (%s, %s) owner=%s by tg=%s",
                entry_type, name, emp["id"], message.from_user.id)
