"""Menyu tartibi muharriri — Bosh Admin reply-menyulardagi tugmalar
joylashuvini Telegram Mini App ichida surib o'zgartiradi. Tugma MATNLARI
tegilmaydi (ular handler filtrlariga bog'langan), faqat qator/joylashuv.
"""
import json
import logging
from html import escape as _esc

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import texts
import keyboards as kb
from config import PUBLIC_URL
from database import (
    get_employee_by_telegram_id, set_menu_layout, reset_menu_layout,
)

logger = logging.getLogger(__name__)
router = Router()


def _is_bosh_admin(user_id: int) -> bool:
    emp = get_employee_by_telegram_id(user_id)
    if not emp:
        return False
    try:
        return (emp["role"] or "") == "bosh_admin"
    except (KeyError, IndexError):
        return False


def _scheme_text(menu_key: str) -> str:
    """Joriy joylashuvning matnli sxemasi (tasdiq xabari uchun)."""
    buttons = kb.MENU_REGISTRY[menu_key]["buttons"]
    lines = []
    for n, row in enumerate(kb.get_layout(menu_key), 1):
        # quote=False — o'zbekcha apostrof (qo'shish) &#x27; ga aylanmasin
        names = "  |  ".join(_esc(buttons[k], quote=False) for k in row)
        lines.append(texts.MENU_EDITOR_ROW.format(n=n, buttons=names))
    return "\n".join(lines)


# ─── Kirish: darhol Mini App ────────────────────────────────────────────────

@router.message(F.text == texts.BTN_MENU_LAYOUT)
async def menu_layout_open(message: Message, state: FSMContext):
    if not _is_bosh_admin(message.from_user.id):
        return
    await state.clear()
    if not PUBLIC_URL:
        await message.answer(texts.MENU_EDITOR_NO_PUBLIC_URL)
        return
    await message.answer(
        texts.MENU_EDITOR_WEBAPP_ASK.format(btn=texts.BTN_MENU_EDITOR_OPEN),
        reply_markup=kb.menu_editor_webapp_kb(PUBLIC_URL)
    )


# ─── Mini App'dan kelgan natija ─────────────────────────────────────────────

@router.message(F.web_app_data)
async def menu_layout_webapp_save(message: Message, state: FSMContext):
    """Mini App'da "Saqlash" bosilganda keladi.

    Format: {"layouts": {"finance_menu": [[...]], "pf_menu": [[...]]}} —
    faqat O'ZGARGAN menyular. Ma'lumot Telegram tomonidan imzolangan holda
    keladi, lekin yuboruvchi Bosh Admin ekani ALBATTA tekshiriladi.
    """
    if not _is_bosh_admin(message.from_user.id):
        await message.answer(texts.NO_PERMISSION, reply_markup=kb.remove_kb())
        return

    try:
        payload = json.loads(message.web_app_data.data)
        layouts = payload["layouts"]
        if not isinstance(layouts, dict) or not layouts:
            raise ValueError("layouts bo'sh yoki lug'at emas")
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        logger.warning("Mini App'dan buzuq ma'lumot: %s", e)
        await message.answer(texts.MENU_EDITOR_WEBAPP_BAD_DATA,
                             reply_markup=kb.remove_kb())
        return

    saqlangan = []
    for menu_key, raw_layout in layouts.items():
        if menu_key not in kb.MENU_REGISTRY:
            logger.warning("Noma'lum menyu tashlab ketildi: %s", menu_key)
            continue
        if not isinstance(raw_layout, list):
            continue
        # Faqat reyestrdagi kalitlar, har biri 1 marta, qatorda maks 2,
        # yetishmagani oxiriga — hammasini normalize_layout qiladi
        clean = [r for r in raw_layout if isinstance(r, list)]
        if not any(r for r in clean):
            continue
        layout = kb.normalize_layout(menu_key, clean)
        # Standart tartibga qaytarilgan bo'lsa — yozuvni o'chiramiz, saqlamaymiz.
        # Shunda kelajakda koddagi standart o'zgarsa, menyu eskisida muzlab
        # qolmaydi (jadval ham keraksiz yozuvlar bilan to'lmaydi).
        if layout == kb.normalize_layout(menu_key,
                                         kb.MENU_REGISTRY[menu_key]["default"]):
            reset_menu_layout(menu_key)
        else:
            set_menu_layout(menu_key, layout)
        saqlangan.append(menu_key)

    if not saqlangan:
        await message.answer(texts.MENU_EDITOR_WEBAPP_BAD_MENU,
                             reply_markup=kb.remove_kb())
        return

    await state.clear()
    bloklar = "\n\n".join(
        f"<b>{kb.MENU_REGISTRY[k]['title']}</b>\n{_scheme_text(k)}"
        for k in saqlangan
    )
    await message.answer(
        texts.MENU_EDITOR_WEBAPP_SAVED.format(cnt=len(saqlangan), menus=bloklar),
        reply_markup=kb.remove_kb()
    )
    # Bosh Admin panelini qaytaramiz — reply klaviatura bo'sh qolmasin
    await message.answer(texts.ADMIN_MENU,
                         reply_markup=kb.admin_menu_kb(is_bosh_admin=True))
