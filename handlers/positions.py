"""Lavozimlar tizimi: CRUD (Bosh Admin) + xodimga lavozim/stavka belgilash."""
import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import texts
import keyboards as kb
from states import PositionManage, EmployeePositionSet
from database import (
    get_employee_by_telegram_id, get_all_employees, get_employee_by_id,
    get_all_positions, get_position, create_position, delete_position,
    set_employee_position,
)

logger = logging.getLogger(__name__)
router = Router()


def _is_bosh_admin(msg_or_call) -> bool:
    uid = msg_or_call.from_user.id
    emp = get_employee_by_telegram_id(uid)
    return bool(emp and emp["role"] == "bosh_admin")


def _is_admin(msg_or_call) -> bool:
    uid = msg_or_call.from_user.id
    emp = get_employee_by_telegram_id(uid)
    return bool(emp and emp["is_admin"])


def _pos_list_text() -> str:
    positions = get_all_positions()
    if not positions:
        return texts.POS_EMPTY
    return "".join(
        texts.POS_ITEM.format(
            name=p["name"], hours=p["work_hours"],
            min=p["min_rate"], max=p["max_rate"]
        )
        for p in positions
    )


# ===== Lavozimlar menyusi =====

@router.message(F.text == texts.BTN_POSITIONS)
async def positions_menu(message: Message, state: FSMContext):
    if not _is_bosh_admin(message):
        return
    await state.clear()
    positions = get_all_positions()
    lst = _pos_list_text()
    await message.answer(
        texts.POS_MENU_HEADER.format(list=lst),
        reply_markup=kb.cancel_kb()
    )
    # Inline: har lavozim uchun o'chirish tugmasi + yangi qo'shish
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    for p in positions:
        rows.append([InlineKeyboardButton(
            text=f"🗑 {p['name']}",
            callback_data=f"pos_del:{p['id']}"
        )])
    rows.append([InlineKeyboardButton(
        text=texts.BTN_POS_ADD, callback_data="pos_add"
    )])
    if rows:
        await message.answer("Amallar:", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


# ===== Lavozim qo'shish =====

@router.callback_query(F.data == "pos_add")
async def pos_add_start(call: CallbackQuery, state: FSMContext):
    if not _is_bosh_admin(call):
        await call.answer(texts.NO_PERMISSION, show_alert=True)
        return
    await call.message.answer(texts.POS_ASK_NAME, reply_markup=kb.cancel_kb())
    await state.set_state(PositionManage.waiting_name)
    await call.answer()


@router.message(PositionManage.waiting_name, F.text)
async def pos_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 3:
        await message.answer(texts.POS_NAME_SHORT)
        return
    await state.update_data(pos_name=name)
    await message.answer(texts.POS_ASK_HOURS)
    await state.set_state(PositionManage.waiting_work_hours)


@router.message(PositionManage.waiting_work_hours, F.text)
async def pos_hours(message: Message, state: FSMContext):
    try:
        hours = int(message.text.strip())
        assert 1 <= hours <= 24
    except Exception:
        await message.answer(texts.POS_HOURS_INVALID)
        return
    await state.update_data(pos_hours=hours)
    await message.answer(texts.POS_ASK_MIN_RATE)
    await state.set_state(PositionManage.waiting_min_rate)


@router.message(PositionManage.waiting_min_rate, F.text)
async def pos_min_rate(message: Message, state: FSMContext):
    try:
        rate = int(message.text.strip().replace(" ", "").replace(",", ""))
        assert rate > 0
    except Exception:
        await message.answer(texts.POS_RATE_INVALID)
        return
    await state.update_data(pos_min=rate)
    await message.answer(texts.POS_ASK_MAX_RATE)
    await state.set_state(PositionManage.waiting_max_rate)


@router.message(PositionManage.waiting_max_rate, F.text)
async def pos_max_rate(message: Message, state: FSMContext):
    try:
        rate = int(message.text.strip().replace(" ", "").replace(",", ""))
        assert rate > 0
    except Exception:
        await message.answer(texts.POS_RATE_INVALID)
        return
    data = await state.get_data()
    await state.clear()
    pos_id = create_position(
        data["pos_name"], data["pos_hours"], data["pos_min"], rate
    )
    emp = get_employee_by_telegram_id(message.from_user.id)
    await message.answer(
        texts.POS_ADDED.format(
            name=data["pos_name"], hours=data["pos_hours"],
            min=data["pos_min"], max=rate
        ),
        reply_markup=kb.admin_menu_kb(is_bosh_admin=True)
    )
    logger.info("Position created id=%s by tg=%s", pos_id, message.from_user.id)


# ===== Lavozim o'chirish =====

@router.callback_query(F.data.startswith("pos_del:"))
async def pos_delete(call: CallbackQuery):
    if not _is_bosh_admin(call):
        await call.answer(texts.NO_PERMISSION, show_alert=True)
        return
    val = call.data.split(":")[1]
    if val == "cancel":
        await call.message.edit_text(texts.CANCELLED)
        await call.answer()
        return
    pos_id = int(val)
    pos = get_position(pos_id)
    if not pos:
        await call.answer("Topilmadi", show_alert=True)
        return
    # Bog'liq xodimlar bormi?
    from database import get_db
    with get_db() as conn:
        cnt = conn.execute(
            "SELECT COUNT(*) FROM employees WHERE position_id=? AND is_active=1",
            (pos_id,)
        ).fetchone()[0]
    if cnt > 0:
        await call.answer(
            texts.POS_DELETE_HAS_EMPLOYEES.format(count=cnt),
            show_alert=True
        )
        return
    delete_position(pos_id)
    await call.message.edit_text(texts.POS_DELETED.format(name=pos["name"]))
    await call.answer("✅")
    logger.info("Position deleted id=%s by tg=%s", pos_id, call.from_user.id)


# ===== Xodimga lavozim + stavka belgilash =====

@router.message(F.text == texts.BTN_SET_POSITION)
async def set_pos_start(message: Message, state: FSMContext):
    if not _is_admin(message):
        return
    await state.clear()
    employees = get_all_employees(active_only=True)
    # Faqat bog'langan xodimlar (telegram_id > 0)
    employees = [e for e in employees if e["telegram_id"] > 0]
    if not employees:
        await message.answer("Xodimlar yo'q.")
        return
    await message.answer(
        texts.SET_POS_PICK_EMP,
        reply_markup=kb.employees_inline_kb(employees, "setpos_emp")
    )
    await state.set_state(EmployeePositionSet.choose_employee)


@router.callback_query(F.data.startswith("setpos_emp:"))
async def set_pos_pick_emp(call: CallbackQuery, state: FSMContext):
    val = call.data.split(":")[1]
    if val == "cancel":
        await state.clear()
        await call.message.edit_text(texts.CANCELLED)
        await call.answer()
        return
    emp_id = int(val)
    emp = get_employee_by_id(emp_id)
    if not emp:
        await call.answer("Topilmadi", show_alert=True)
        return
    await state.update_data(sp_emp_id=emp_id, sp_emp_name=emp["full_name"])
    positions = get_all_positions()
    if not positions:
        await call.message.edit_text("Lavozimlar yo'q. Avval lavozim qo'shing.")
        await state.clear()
        await call.answer()
        return
    pos_list = "".join(
        texts.SET_POS_POS_ITEM.format(
            name=p["name"], hours=p["work_hours"],
            min=p["min_rate"], max=p["max_rate"]
        )
        for p in positions
    )
    await call.message.edit_text(
        texts.SET_POS_PICK_POS.format(name=emp["full_name"], list=pos_list),
        reply_markup=kb.positions_list_kb(positions, "setpos_pos")
    )
    await state.set_state(EmployeePositionSet.choose_position)
    await call.answer()


@router.callback_query(F.data.startswith("setpos_pos:"))
async def set_pos_pick_pos(call: CallbackQuery, state: FSMContext):
    val = call.data.split(":")[1]
    if val == "cancel":
        await state.clear()
        await call.message.edit_text(texts.CANCELLED)
        await call.answer()
        return
    pos_id = int(val)
    pos = get_position(pos_id)
    if not pos:
        await call.answer("Topilmadi", show_alert=True)
        return
    data = await state.get_data()
    await state.update_data(sp_pos_id=pos_id, sp_pos_name=pos["name"],
                            sp_hours=pos["work_hours"],
                            sp_min=pos["min_rate"], sp_max=pos["max_rate"])
    await call.message.answer(
        texts.SET_POS_ASK_RATE.format(
            emp_name=data["sp_emp_name"], pos_name=pos["name"],
            min=pos["min_rate"], max=pos["max_rate"]
        ),
        reply_markup=kb.cancel_kb()
    )
    await state.set_state(EmployeePositionSet.enter_daily_rate)
    await call.answer()


@router.message(EmployeePositionSet.enter_daily_rate, F.text)
async def set_pos_rate(message: Message, state: FSMContext):
    try:
        rate = int(message.text.strip().replace(" ", "").replace(",", ""))
        assert rate > 0
    except Exception:
        await message.answer(texts.SET_POS_RATE_INVALID)
        return
    data = await state.get_data()
    await state.clear()
    set_employee_position(data["sp_emp_id"], data["sp_pos_id"], rate)
    emp = get_employee_by_telegram_id(message.from_user.id)
    await message.answer(
        texts.SET_POS_DONE.format(
            emp_name=data["sp_emp_name"],
            pos_name=data["sp_pos_name"],
            hours=data["sp_hours"],
            rate=rate,
        ),
        reply_markup=kb.admin_menu_kb(is_bosh_admin=(emp and emp["role"] == "bosh_admin"))
    )
    logger.info("Position set: emp=%s pos=%s rate=%s by tg=%s",
                data["sp_emp_id"], data["sp_pos_id"], rate, message.from_user.id)
