"""Maxsus turkumlar boshqaruvi — Boss va Bosh Admin uchun.

Oqim: "⚙️ Turkumlar" → bo'lim tanlash (Moliya / Shaxsiy) →
      ro'yxat + ➕ qo'shish / 🗑 o'chirish.
Yangi turkum: joy tanlash → nom kiritish (FSM) → saqlash.
Yozuvlarda custom turkum kaliti "c{id}" ko'rinishida saqlanadi.
"""
import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import texts
import keyboards as kb
from states import CategoryManage
from database import (
    get_employee_by_telegram_id,
    add_custom_category,
    get_custom_categories,
    get_custom_category_by_id,
    deactivate_custom_category,
)

logger = logging.getLogger(__name__)
router = Router()


def _can_use(emp) -> bool:
    if not emp:
        return False
    try:
        return emp["role"] in ("boss", "bosh_admin")
    except (KeyError, IndexError):
        return False


def _section_cats(owner_id: int, src: str):
    """Bo'limga tegishli barcha aktiv custom turkumlar."""
    if src == "fin":
        return (list(get_custom_categories(owner_id, "fin"))
                + list(get_custom_categories(owner_id, "fin_personal")))
    return list(get_custom_categories(owner_id, "pf"))


def _manage_menu_text(cats, src: str) -> str:
    header = (texts.CCAT_MENU_HEADER_FIN if src == "fin"
              else texts.CCAT_MENU_HEADER_PF)
    if not cats:
        header += texts.CCAT_MENU_EMPTY
    return header


def _split_emoji_name(raw: str) -> tuple:
    """Bosh token harf-raqamsiz bo'lsa — emoji, qolgani nom."""
    raw = raw.strip()
    parts = raw.split(maxsplit=1)
    if len(parts) == 2 and not any(ch.isalnum() for ch in parts[0]):
        return parts[0][:8], parts[1].strip()
    return "🏷", raw


# ===== Kirish =====

@router.message(F.text == texts.BTN_CATEGORY_MANAGE)
async def ccat_open(message: Message, state: FSMContext):
    me = get_employee_by_telegram_id(message.from_user.id)
    if not _can_use(me):
        await message.answer(texts.FINANCE_NO_PERMISSION)
        return
    await state.clear()
    await message.answer(texts.CCAT_PICK_SECTION,
                         reply_markup=kb.ccat_sections_kb())


# ===== Bo'lim menyusi / navigatsiya =====

@router.callback_query(F.data == "ccat:home")
async def ccat_home(call: CallbackQuery, state: FSMContext):
    me = get_employee_by_telegram_id(call.from_user.id)
    if not _can_use(me):
        await call.answer(texts.FINANCE_NO_PERMISSION, show_alert=True)
        return
    await state.clear()
    await call.message.edit_text(texts.CCAT_PICK_SECTION,
                                 reply_markup=kb.ccat_sections_kb())
    await call.answer()


@router.callback_query(F.data == "ccat:close")
async def ccat_close(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(texts.CANCELLED)
    await call.answer()


@router.callback_query(F.data.startswith("ccat:sec:"))
async def ccat_section(call: CallbackQuery, state: FSMContext):
    me = get_employee_by_telegram_id(call.from_user.id)
    if not _can_use(me):
        await call.answer(texts.FINANCE_NO_PERMISSION, show_alert=True)
        return
    src = call.data.split(":")[-1]
    if src not in ("fin", "pf"):
        await call.answer("Xato", show_alert=True)
        return
    await state.clear()
    cats = _section_cats(me["id"], src)
    await call.message.edit_text(_manage_menu_text(cats, src),
                                 reply_markup=kb.ccat_manage_kb(cats, src))
    await call.answer()


@router.callback_query(F.data.startswith("ccat:back:"))
async def ccat_back(call: CallbackQuery, state: FSMContext):
    me = get_employee_by_telegram_id(call.from_user.id)
    if not _can_use(me):
        await call.answer(texts.FINANCE_NO_PERMISSION, show_alert=True)
        return
    src = call.data.split(":")[-1]
    if src not in ("fin", "pf"):
        await call.answer("Xato", show_alert=True)
        return
    await state.clear()
    cats = _section_cats(me["id"], src)
    await call.message.edit_text(_manage_menu_text(cats, src),
                                 reply_markup=kb.ccat_manage_kb(cats, src))
    await call.answer()


# ===== Qo'shish =====

@router.callback_query(F.data.startswith("ccat:add:"))
async def ccat_add(call: CallbackQuery):
    me = get_employee_by_telegram_id(call.from_user.id)
    if not _can_use(me):
        await call.answer(texts.FINANCE_NO_PERMISSION, show_alert=True)
        return
    src = call.data.split(":")[-1]
    if src not in ("fin", "pf"):
        await call.answer("Xato", show_alert=True)
        return
    await call.message.edit_text(texts.CCAT_PICK_DEST,
                                 reply_markup=kb.ccat_dest_kb(src))
    await call.answer()


@router.callback_query(F.data.startswith("ccat:new:"))
async def ccat_new(call: CallbackQuery, state: FSMContext):
    me = get_employee_by_telegram_id(call.from_user.id)
    if not _can_use(me):
        await call.answer(texts.FINANCE_NO_PERMISSION, show_alert=True)
        return
    parts = call.data.split(":")
    if len(parts) != 4:
        await call.answer("Xato", show_alert=True)
        return
    _, _, scope, etype = parts
    if (scope, etype) not in texts.CCAT_DEST_LABELS:
        await call.answer("Xato", show_alert=True)
        return
    src = "pf" if scope == "pf" else "fin"
    await state.update_data(cc_scope=scope, cc_etype=etype, cc_src=src)
    await state.set_state(CategoryManage.entering_name)
    await call.message.edit_text(
        texts.CCAT_ASK_NAME.format(dest=texts.CCAT_DEST_LABELS[(scope, etype)])
    )
    await call.answer()


@router.message(CategoryManage.entering_name, F.text)
async def ccat_name_entered(message: Message, state: FSMContext):
    me = get_employee_by_telegram_id(message.from_user.id)
    if not _can_use(me):
        await state.clear()
        await message.answer(texts.FINANCE_NO_PERMISSION)
        return

    data = await state.get_data()
    src = data.get("cc_src", "fin")
    back_kb = kb.finance_menu_kb() if src == "fin" else kb.pf_menu_kb()

    if message.text in (texts.BTN_CANCEL, texts.BTN_BACK):
        await state.clear()
        await message.answer(texts.CANCELLED, reply_markup=back_kb)
        return

    emoji, name = _split_emoji_name(message.text)
    if not (2 <= len(name) <= 30) or "<" in name or ">" in name:
        await message.answer(texts.CCAT_NAME_INVALID)
        return

    scope = data["cc_scope"]
    etype = data["cc_etype"]
    await state.clear()
    cat_id = add_custom_category(me["id"], scope, etype, emoji, name)
    logger.info("Custom turkum yaratildi: id=%s owner=%s %s/%s %s",
                cat_id, me["id"], scope, etype, name)
    await message.answer(
        texts.CCAT_SAVED.format(
            emoji=emoji, name=name,
            dest=texts.CCAT_DEST_LABELS[(scope, etype)]
        ),
        reply_markup=back_kb
    )
    cats = _section_cats(me["id"], src)
    await message.answer(_manage_menu_text(cats, src),
                         reply_markup=kb.ccat_manage_kb(cats, src))


# ===== O'chirish =====

@router.callback_query(F.data.startswith("ccat:del:"))
async def ccat_delete_pick(call: CallbackQuery):
    me = get_employee_by_telegram_id(call.from_user.id)
    if not _can_use(me):
        await call.answer(texts.FINANCE_NO_PERMISSION, show_alert=True)
        return
    parts = call.data.split(":")
    if len(parts) != 4:
        await call.answer("Xato", show_alert=True)
        return
    src = parts[2]
    try:
        cat_id = int(parts[3])
    except ValueError:
        await call.answer("Xato ID", show_alert=True)
        return
    row = get_custom_category_by_id(cat_id)
    if not row or row["owner_id"] != me["id"] or not row["is_active"]:
        await call.answer("Turkum topilmadi", show_alert=True)
        return
    dest = texts.CCAT_DEST_LABELS.get((row["scope"], row["entry_type"]), "")
    await call.message.edit_text(
        texts.CCAT_DELETE_CONFIRM.format(
            emoji=row["emoji"] or "🏷", name=row["name"], dest=dest
        ),
        reply_markup=kb.ccat_del_confirm_kb(src, cat_id)
    )
    await call.answer()


@router.callback_query(F.data.startswith("ccat:delc:"))
async def ccat_delete_confirm(call: CallbackQuery):
    me = get_employee_by_telegram_id(call.from_user.id)
    if not _can_use(me):
        await call.answer(texts.FINANCE_NO_PERMISSION, show_alert=True)
        return
    parts = call.data.split(":")
    if len(parts) != 4:
        await call.answer("Xato", show_alert=True)
        return
    src = parts[2]
    try:
        cat_id = int(parts[3])
    except ValueError:
        await call.answer("Xato ID", show_alert=True)
        return
    row = get_custom_category_by_id(cat_id)
    if not row or not deactivate_custom_category(cat_id, me["id"]):
        await call.answer("Turkum topilmadi", show_alert=True)
        return
    logger.info("Custom turkum o'chirildi: id=%s owner=%s", cat_id, me["id"])
    await call.answer(
        texts.CCAT_DELETED.format(emoji=row["emoji"] or "🏷", name=row["name"])
    )
    cats = _section_cats(me["id"], src)
    await call.message.edit_text(_manage_menu_text(cats, src),
                                 reply_markup=kb.ccat_manage_kb(cats, src))
