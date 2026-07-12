"""Ofis IP boshqaruvi — dinamik whitelist (faqat Bosh Admin)."""
import time
import uuid

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
from states import BeaconDevice

router = Router()


def _gen_beacon_secret() -> str:
    """Uzun tasodifiy maxfiy token — referens qurilma URL'i uchun."""
    return "bcn_" + uuid.uuid4().hex + uuid.uuid4().hex[:12]


def _beacon_url(secret: str) -> str:
    from config import PUBLIC_URL
    if PUBLIC_URL:
        return f"{PUBLIC_URL.rstrip('/')}/beacon/{secret}"
    from services.wifi_verify import get_local_ip
    from config import WEB_PORT
    return f"http://{get_local_ip()}:{WEB_PORT}/beacon/{secret}"


def _ago(seconds: float) -> str:
    seconds = int(max(0, seconds))
    if seconds < 60:
        return f"{seconds} soniya"
    if seconds < 3600:
        return f"{seconds // 60} daqiqa"
    if seconds < 86400:
        return f"{seconds // 3600} soat"
    return f"{seconds // 86400} kun"


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


# ===== Referens qurilmalar (beacon) =====

def _render_devices():
    """Qurilmalar ro'yxati matni + inline klaviatura."""
    from database import get_beacon_devices
    from services.wifi_verify import BEACON_STALE_SEC

    devices = get_beacon_devices()
    add_btn = [InlineKeyboardButton(text=texts.BTN_BEACON_ADD_DEVICE, callback_data="bcnadd")]
    if not devices:
        return texts.BEACON_DEVICES_EMPTY, InlineKeyboardMarkup(inline_keyboard=[add_btn])

    lines, rows = [], []
    now = time.time()
    for d in devices:
        star = "⭐ " if d["is_primary"] else ""
        if not d["last_at"]:
            status, ip = "⚪️ hali signal yo'q", "—"
        else:
            age = now - d["last_at"]
            ip = d["last_ip"] or "—"
            if age <= BEACON_STALE_SEC:
                status = f"🟢 {_ago(age)} oldin"
            else:
                status = f"🔴 signal yo'q ({_ago(age)} oldin)"
        lines.append(texts.BEACON_DEVICE_LINE.format(star=star, label=d["label"], ip=ip, status=status))
        rows.append([
            InlineKeyboardButton(text=f"🔗 {d['label']}", callback_data=f"bcnurl:{d['id']}"),
            InlineKeyboardButton(text="⭐", callback_data=f"bcnprimary:{d['id']}"),
            InlineKeyboardButton(text="🗑", callback_data=f"bcndel:{d['id']}"),
        ])
    rows.append(add_btn)
    text = texts.BEACON_DEVICES_HEADER.format(n=len(devices), body="\n\n".join(lines))
    return text, InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(F.text == texts.BTN_OFFICE_BEACON)
async def office_beacon_status(message: Message, state: FSMContext):
    if not _is_bosh_admin(message.from_user.id):
        await message.answer(texts.NO_PERMISSION)
        return
    await state.clear()
    text, markup = _render_devices()
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data == "bcnadd")
async def cb_beacon_add(call: CallbackQuery, state: FSMContext):
    if not _is_bosh_admin(call.from_user.id):
        await call.answer(texts.NO_PERMISSION, show_alert=True)
        return
    await state.set_state(BeaconDevice.waiting_label)
    await call.answer()
    await call.message.answer(texts.BEACON_ADD_PROMPT)


@router.message(BeaconDevice.waiting_label)
async def beacon_add_label(message: Message, state: FSMContext):
    if not _is_bosh_admin(message.from_user.id):
        await state.clear()
        return
    label = (message.text or "").strip()[:40] or "Qurilma"
    from database import add_beacon_device, get_beacon_devices
    is_first = len(get_beacon_devices()) == 0
    secret = _gen_beacon_secret()
    add_beacon_device(label, secret, message.from_user.id, is_primary=is_first)
    await state.clear()
    url = _beacon_url(secret)
    await message.answer(
        texts.BEACON_DEVICE_ADDED.format(label=label, url=url, guide=texts.BEACON_SETUP_GUIDE)
    )
    text, markup = _render_devices()
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data.startswith("bcnurl:"))
async def cb_beacon_url(call: CallbackQuery):
    if not _is_bosh_admin(call.from_user.id):
        await call.answer(texts.NO_PERMISSION, show_alert=True)
        return
    dev_id = int(call.data.split(":", 1)[1])
    from database import get_beacon_device
    d = get_beacon_device(dev_id)
    if not d:
        await call.answer("Topilmadi", show_alert=True)
        return
    await call.answer()
    await call.message.answer(
        texts.BEACON_DEVICE_URL.format(label=d["label"], url=_beacon_url(d["secret"]))
    )


@router.callback_query(F.data.startswith("bcnprimary:"))
async def cb_beacon_primary(call: CallbackQuery):
    if not _is_bosh_admin(call.from_user.id):
        await call.answer(texts.NO_PERMISSION, show_alert=True)
        return
    dev_id = int(call.data.split(":", 1)[1])
    from database import get_beacon_device, set_primary_beacon_device
    d = get_beacon_device(dev_id)
    if not d:
        await call.answer("Topilmadi", show_alert=True)
        return
    set_primary_beacon_device(dev_id)
    await call.answer("⭐ Asosiy qilib belgilandi")
    text, markup = _render_devices()
    try:
        await call.message.edit_text(text, reply_markup=markup)
    except Exception:
        pass


@router.callback_query(F.data.startswith("bcndel:"))
async def cb_beacon_del(call: CallbackQuery):
    if not _is_bosh_admin(call.from_user.id):
        await call.answer(texts.NO_PERMISSION, show_alert=True)
        return
    dev_id = int(call.data.split(":", 1)[1])
    from database import remove_beacon_device
    remove_beacon_device(dev_id)
    await call.answer("🗑 O'chirildi")
    text, markup = _render_devices()
    try:
        await call.message.edit_text(text, reply_markup=markup)
    except Exception:
        pass
