"""Shaxsiy moliya — Boss va Bosh Admin uchun shaxsiy kirim/chiqim hisobkitob."""
import io
import calendar
import logging
from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, BufferedInputFile

import texts
import keyboards as kb
from database import (
    get_employee_by_telegram_id,
    pf_add_entry, pf_get_monthly,
    pf_get_summary, pf_get_entry, pf_delete_entry,
    pf_get_today_totals, get_custom_category_by_id,
)
from catutil import resolve_category, custom_id
from states import PersonalFinance
from tzutil import now as tz_now

logger = logging.getLogger(__name__)
router = Router()


def _can_use(emp) -> bool:
    if not emp:
        return False
    try:
        return emp["role"] in ("boss", "bosh_admin")
    except (KeyError, IndexError):
        return False


def _parse_date(raw: str):
    """DD.MM.YYYY formatini qabul qiladi, datetime.date qaytaradi yoki None."""
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except ValueError:
            continue
    return None


# ─── Menyu ─────────────────────────────────────────────────────────────────

@router.message(F.text == texts.BTN_PERSONAL_FINANCE)
async def pf_open(message: Message, state: FSMContext):
    me = get_employee_by_telegram_id(message.from_user.id)
    if not _can_use(me):
        await message.answer(texts.NO_PERMISSION)
        return
    await state.clear()
    await message.answer(texts.PF_MENU, reply_markup=kb.pf_menu_kb())


# ─── Kirim boshlash ─────────────────────────────────────────────────────────

@router.message(F.text == texts.BTN_PF_INCOME)
async def pf_income_start(message: Message, state: FSMContext):
    me = get_employee_by_telegram_id(message.from_user.id)
    if not _can_use(me):
        await message.answer(texts.NO_PERMISSION)
        return
    await state.clear()
    await state.update_data(pf_emp_id=me["id"], pf_type="income")
    await message.answer(texts.PF_PICK_CAT_INCOME,
                         reply_markup=kb.pf_income_cats_kb(me["id"]))
    await state.set_state(PersonalFinance.choosing_category)


# ─── Chiqim boshlash ────────────────────────────────────────────────────────

@router.message(F.text == texts.BTN_PF_EXPENSE)
async def pf_expense_start(message: Message, state: FSMContext):
    me = get_employee_by_telegram_id(message.from_user.id)
    if not _can_use(me):
        await message.answer(texts.NO_PERMISSION)
        return
    await state.clear()
    await state.update_data(pf_emp_id=me["id"], pf_type="expense")
    await message.answer(texts.PF_PICK_CAT_EXPENSE,
                         reply_markup=kb.pf_expense_cats_kb(me["id"]))
    await state.set_state(PersonalFinance.choosing_category)


# ─── Kategoriya tanlash ─────────────────────────────────────────────────────

@router.callback_query(PersonalFinance.choosing_category, F.data.startswith("pf_cat:"))
async def pf_cat_chosen(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":", 2)
    # "pf_cat:cancel" 2 qismli keladi — uzunlik tekshiruvidan oldin ushlanadi
    if parts[-1] == "cancel":
        await state.clear()
        await call.message.edit_text(texts.CANCELLED)
        await call.answer()
        return
    if len(parts) < 3:
        await call.answer()
        return
    _, entry_type, cat_key = parts

    all_cats = {**texts.PF_INCOME_CATS, **texts.PF_EXPENSE_CATS}
    if cat_key in all_cats:
        emoji, cat_name = all_cats[cat_key]
    else:
        data = await state.get_data()
        cid = custom_id(cat_key)
        row = get_custom_category_by_id(cid) if cid is not None else None
        ok = (row and row["scope"] == "pf" and row["is_active"]
              and row["owner_id"] == data.get("pf_emp_id")
              and row["entry_type"] == entry_type)
        if not ok:
            await call.answer("Noma'lum kategoriya", show_alert=True)
            return
        emoji, cat_name = row["emoji"] or "🏷", row["name"]
    await state.update_data(pf_cat_key=cat_key, pf_cat_name=f"{emoji} {cat_name}")

    await call.message.edit_text(
        texts.PF_ENTER_AMOUNT.format(cat=f"{emoji} {cat_name}")
    )
    await state.set_state(PersonalFinance.entering_amount)
    await call.answer()


# ─── Summa kiritish ─────────────────────────────────────────────────────────

@router.message(PersonalFinance.entering_amount, F.text)
async def pf_amount_entered(message: Message, state: FSMContext):
    raw = message.text.replace(" ", "").replace(",", "").replace(".", "")
    if not raw.isdigit() or int(raw) <= 0:
        await message.answer(texts.PF_AMOUNT_INVALID)
        return
    await state.update_data(pf_amount=int(raw))
    await message.answer(texts.PF_ENTER_NOTE, reply_markup=kb.pf_note_kb())
    await state.set_state(PersonalFinance.entering_note)


# ─── Izoh kiritish ──────────────────────────────────────────────────────────

@router.message(PersonalFinance.entering_note, F.text)
async def pf_note_entered(message: Message, state: FSMContext):
    note = "" if message.text == texts.BTN_PF_NOTE_SKIP else message.text
    await state.update_data(pf_note=note)
    await message.answer(texts.PF_ENTER_DATE, reply_markup=kb.pf_date_kb())
    await state.set_state(PersonalFinance.entering_date)


# ─── Sana kiritish ──────────────────────────────────────────────────────────

@router.message(PersonalFinance.entering_date, F.text)
async def pf_date_entered(message: Message, state: FSMContext):
    raw = message.text.strip()
    if raw == texts.BTN_PF_TODAY:
        entry_date = tz_now().date()
    else:
        entry_date = _parse_date(raw)
        if not entry_date:
            await message.answer(texts.PF_DATE_INVALID)
            return

    data = await state.get_data()
    await state.clear()

    emp_id = data["pf_emp_id"]
    entry_type = data["pf_type"]
    cat_key = data["pf_cat_key"]
    cat_name = data["pf_cat_name"]
    amount = data["pf_amount"]
    note = data.get("pf_note", "")

    pf_add_entry(emp_id, entry_type, cat_key, amount, note, str(entry_date))
    sign = "+" if entry_type == "income" else "-"
    await message.answer(
        texts.PF_SAVED.format(sign=sign, amount=amount, cat=cat_name),
        reply_markup=kb.pf_menu_kb()
    )


# ─── Bu oy hisoboti ─────────────────────────────────────────────────────────

@router.message(F.text == texts.BTN_PF_SUMMARY)
async def pf_summary(message: Message, state: FSMContext):
    me = get_employee_by_telegram_id(message.from_user.id)
    if not _can_use(me):
        await message.answer(texts.NO_PERMISSION)
        return
    await state.clear()

    now = tz_now()
    summary = pf_get_summary(me["id"], now.year, now.month)
    month_name = texts.MONTHS_UZ[now.month]

    if not summary["income"] and not summary["expense"]:
        await message.answer(texts.PF_SUMMARY_EMPTY)
        return

    out = texts.PF_SUMMARY_HEADER.format(month=month_name, year=now.year)

    # Kirim
    if summary["income"]:
        out += texts.PF_SUMMARY_INCOME.format(total=summary["income"])
        for (etype, cat_key), amount in summary["by_cat"].items():
            if etype != "income":
                continue
            emoji, name = resolve_category(cat_key, "pf")
            out += texts.PF_SUMMARY_LINE.format(emoji=emoji, name=name, amount=amount)

    # Chiqim
    if summary["expense"]:
        out += texts.PF_SUMMARY_EXPENSE.format(total=summary["expense"])
        for (etype, cat_key), amount in summary["by_cat"].items():
            if etype != "expense":
                continue
            emoji, name = resolve_category(cat_key, "pf")
            out += texts.PF_SUMMARY_LINE.format(emoji=emoji, name=name, amount=amount)

    # Sof
    net = summary["net"]
    if net >= 0:
        out += texts.PF_SUMMARY_NET_PLUS.format(net=net)
    else:
        out += texts.PF_SUMMARY_NET_MINUS.format(net=abs(net))

    # Bugungi chiqim + kunlik byudjet
    today = pf_get_today_totals(me["id"], now.strftime("%Y-%m-%d"))
    if today["expense"] > 0:
        out += texts.PF_SUMMARY_TODAY.format(today=today["expense"])
    else:
        out += texts.PF_SUMMARY_TODAY_NONE

    days_in_month = calendar.monthrange(now.year, now.month)[1]
    remaining_days = max(days_in_month - now.day, 1)
    qoldiq = net
    if qoldiq <= 0:
        out += texts.PF_SUMMARY_NO_LIMIT
    else:
        out += texts.PF_SUMMARY_BUDGET.format(
            qoldiq=qoldiq, days=remaining_days,
            limit=qoldiq // remaining_days
        )

    await message.answer(out)


# ─── Excel hisobot ──────────────────────────────────────────────────────────

@router.message(F.text == texts.BTN_PF_EXCEL)
async def pf_excel(message: Message, state: FSMContext):
    me = get_employee_by_telegram_id(message.from_user.id)
    if not _can_use(me):
        await message.answer(texts.NO_PERMISSION)
        return
    await state.clear()

    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
    except ImportError:
        await message.answer("❌ openpyxl kutubxonasi yo'q.")
        return

    now = tz_now()
    entries = pf_get_monthly(me["id"], now.year, now.month)
    month_name = texts.MONTHS_UZ[now.month]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Shaxsiy {month_name} {now.year}"

    # Sarlavha
    header_fill = PatternFill("solid", fgColor="1F4E79")
    header_font = Font(color="FFFFFF", bold=True)
    headers = ["#", "Sana", "Tur", "Kategoriya", "Summa (so'm)", "Izoh"]
    col_widths = [5, 12, 10, 22, 16, 30]
    for col_idx, (h, w) in enumerate(zip(headers, col_widths), 1):
        cell = ws.cell(row=1, column=col_idx, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
        ws.column_dimensions[
            openpyxl.utils.get_column_letter(col_idx)
        ].width = w

    income_fill = PatternFill("solid", fgColor="E2EFDA")
    expense_fill = PatternFill("solid", fgColor="FDECEA")

    for row_idx, e in enumerate(entries, 2):
        etype = "Kirim" if e["entry_type"] == "income" else "Chiqim"
        cat_info = resolve_category(e["category"], "pf")
        cat_name = f"{cat_info[0]} {cat_info[1]}"
        fill = income_fill if e["entry_type"] == "income" else expense_fill
        row_data = [row_idx - 1, e["entry_date"], etype,
                    cat_name, e["amount"], e["note"] or ""]
        for col_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.fill = fill

    # Jami
    if entries:
        total_row = len(entries) + 3
        income_sum = sum(e["amount"] for e in entries if e["entry_type"] == "income")
        expense_sum = sum(e["amount"] for e in entries if e["entry_type"] == "expense")
        ws.cell(row=total_row, column=3, value="Jami kirim:").font = Font(bold=True)
        ws.cell(row=total_row, column=5, value=income_sum).font = Font(bold=True, color="006100")
        ws.cell(row=total_row + 1, column=3, value="Jami chiqim:").font = Font(bold=True)
        ws.cell(row=total_row + 1, column=5, value=expense_sum).font = Font(bold=True, color="9C0006")
        net = income_sum - expense_sum
        ws.cell(row=total_row + 2, column=3, value="Sof:").font = Font(bold=True)
        net_cell = ws.cell(row=total_row + 2, column=5, value=net)
        net_cell.font = Font(bold=True,
                              color="006100" if net >= 0 else "9C0006")

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    filename = f"shaxsiy_moliya_{now.year}_{now.month:02d}.xlsx"
    await message.answer_document(
        BufferedInputFile(buf.read(), filename=filename),
        caption=f"📥 Shaxsiy moliya — {month_name} {now.year}"
    )


# ─── Yozuvni o'chirish ──────────────────────────────────────────────────────

@router.message(F.text == texts.BTN_PF_DELETE)
async def pf_delete_start(message: Message, state: FSMContext):
    me = get_employee_by_telegram_id(message.from_user.id)
    if not _can_use(me):
        await message.answer(texts.NO_PERMISSION)
        return
    await state.clear()

    now = tz_now()
    entries = pf_get_monthly(me["id"], now.year, now.month)
    if not entries:
        await message.answer(texts.PF_DELETE_EMPTY)
        return

    month_name = texts.MONTHS_UZ[now.month]
    await message.answer(
        texts.PF_DELETE_PICK.format(month=month_name),
        reply_markup=kb.pf_entries_kb(entries)
    )
    await state.update_data(pf_emp_id=me["id"])
    await state.set_state(PersonalFinance.deleting)


@router.callback_query(PersonalFinance.deleting, F.data.startswith("pf_del:"))
async def pf_delete_confirm(call: CallbackQuery, state: FSMContext):
    raw = call.data.split(":", 1)[1]
    if raw == "cancel":
        await state.clear()
        await call.message.edit_text(texts.CANCELLED)
        await call.answer()
        return

    try:
        entry_id = int(raw)
    except ValueError:
        await call.answer("Xato", show_alert=True)
        return

    data = await state.get_data()
    emp_id = data.get("pf_emp_id")
    row = pf_get_entry(entry_id, emp_id)
    if not row:
        await call.answer("Topilmadi yoki ruxsat yo'q.", show_alert=True)
        return

    pf_delete_entry(entry_id, emp_id)
    await state.clear()
    await call.message.edit_text(texts.PF_DELETED)
    await call.answer()
