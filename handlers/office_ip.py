"""Ofis IP boshqaruvi — dinamik whitelist (faqat Bosh Admin)."""
from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext

import texts
import keyboards as kb
from database import (
    get_employee_by_telegram_id,
    get_office_ips_detailed,
    add_office_ip,
    remove_office_ip,
)
from services.wifi_verify import create_setip_token, to_office_network

router = Router()


def _is_bosh_admin(uid: int) -> bool:
    emp = get_employee_by_telegram_id(uid)
    if not emp:
        return False
    try:
        return emp["role"] == "bosh_admin"
    except (KeyError, IndexError):
        return False


@router.message(F.text == texts.BTN_OFFICE_IP)
async def office_ip_menu(message: Message, state: FSMContext):
    if not _is_bosh_admin(message.from_user.id):
        await message.answer(texts.NO_PERMISSION)
        return
    await state.clear()
    await message.answer(texts.OFFICE_IP_MENU, reply_markup=kb.ip_menu_kb())


@router.message(F.text == texts.BTN_OFFICE_IP_ADD)
async def office_ip_add(message: Message):
    if not _is_bosh_admin(message.from_user.id):
        await message.answer(texts.NO_PERMISSION)
        return
    from config import PUBLIC_URL
    token = create_setip_token(message.from_user.id)
    if PUBLIC_URL:
        url = f"{PUBLIC_URL.rstrip('/')}/setip/{token}"
    else:
        from services.wifi_verify import get_local_ip
        from config import WEB_PORT
        url = f"http://{get_local_ip()}:{WEB_PORT}/setip/{token}"
    link_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📍 Joriy IP'ni qo'shish", url=url)]
    ])
    await message.answer(texts.OFFICE_IP_SETLINK, reply_markup=link_kb)


@router.message(F.text == texts.BTN_OFFICE_IP_LIST)
async def office_ip_list(message: Message):
    if not _is_bosh_admin(message.from_user.id):
        await message.answer(texts.NO_PERMISSION)
        return
    rows = get_office_ips_detailed()
    if not rows:
        await message.answer(texts.OFFICE_IP_LIST_EMPTY)
        return
    inline = [
        [InlineKeyboardButton(text=f"🗑 {r['ip']}  ({r['label'] or '—'})",
                              callback_data=f"ipdel:{r['ip']}")]
        for r in rows
    ]
    await message.answer(
        texts.OFFICE_IP_LIST_HEADER.format(n=len(rows)),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=inline),
    )


@router.callback_query(F.data.startswith("ipdel:"))
async def cb_ip_del(call: CallbackQuery):
    if not _is_bosh_admin(call.from_user.id):
        await call.answer(texts.NO_PERMISSION, show_alert=True)
        return
    ip = call.data.split(":", 1)[1]
    remove_office_ip(ip)
    await call.answer("🗑 O'chirildi")
    try:
        await call.message.edit_text(texts.IP_REMOVED.format(ip=ip))
    except Exception:
        pass


@router.callback_query(F.data.startswith("ipadd:"))
async def cb_ip_add(call: CallbackQuery):
    if not _is_bosh_admin(call.from_user.id):
        await call.answer(texts.NO_PERMISSION, show_alert=True)
        return
    ip = call.data.split(":", 1)[1]
    net = to_office_network(ip)
    add_office_ip(net, label="ogohlantirishdan (/24)", added_by=call.from_user.id)
    await call.answer("✅ Qo'shildi")
    try:
        await call.message.edit_text(texts.SETIP_ADDED.format(ip=net))
    except Exception:
        pass


@router.callback_query(F.data.startswith("ipign:"))
async def cb_ip_ignore(call: CallbackQuery):
    await call.answer()
    try:
        await call.message.edit_text(texts.IP_IGNORED)
    except Exception:
        pass
