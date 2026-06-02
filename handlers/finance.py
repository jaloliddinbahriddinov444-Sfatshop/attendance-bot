"""Moliya bo'limi — Boss va Bosh Admin uchun shaxsiy daftarlar.

Konventsiya: har bir Boss va Bosh Admin alohida daftarga ega.
Yozuvlar `finance_entries.owner_id` orqali ajratiladi.
"""
import io
import logging
import asyncio
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, BufferedInputFile

import texts
import keyboards as kb
from states import FinanceEntry
from database import (
    get_employee_by_telegram_id,
    create_finance_entry,
    get_monthly_finance_entries,
    get_monthly_finance_summary,
)
from tzutil import now as tz_now, fmt as fmt_local

logger = logging.getLogger(__name__)
router = Router()


def _can_use_finance(emp) -> bool:
    if not emp:
        return False
    try:
        return emp["role"] in ("boss", "bosh_admin")
    except (KeyError, IndexError):
        return False


def _back_kb(emp):
    """Moliyadan chiqqanda qaytadigan menyu (Bosh Admin → admin menyu, Boss → Boss uy menyusi)."""
    try:
        role = emp["role"]
    except (KeyError, IndexError):
        role = "employee"
    if role == "boss":
        return kb.main_menu_kb(is_boss=True)
    if role == "bosh_admin":
        return kb.admin_menu_kb(is_bosh_admin=True)
    return kb.main_menu_kb(is_admin=bool(emp["is_admin"]))


# ===== Kirish: "Moliya bo'limi" =====

@router.message(F.text == texts.BTN_BOSS_FINANCE)
async def finance_open(message: Message, state: FSMContext):
    me = get_employee_by_telegram_id(message.from_user.id)
    if not _can_use_finance(me):
        await message.answer(texts.FINANCE_NO_PERMISSION)
        return
    await state.clear()
    await message.answer(texts.FINANCE_MENU, reply_markup=kb.finance_menu_kb())


# ===== Kirim/chiqim qo'shish: turkum tanlash =====

@router.message(F.text == texts.BTN_FINANCE_INCOME)
async def finance_add_income_start(message: Message, state: FSMContext):
    me = get_employee_by_telegram_id(message.from_user.id)
    if not _can_use_finance(me):
        await message.answer(texts.FINANCE_NO_PERMISSION)
        return
    await state.clear()
    await message.answer(texts.FINANCE_PICK_CATEGORY_INCOME,
                         reply_markup=kb.finance_categories_kb("income"))


@router.message(F.text == texts.BTN_FINANCE_EXPENSE)
async def finance_add_expense_start(message: Message, state: FSMContext):
    me = get_employee_by_telegram_id(message.from_user.id)
    if not _can_use_finance(me):
        await message.answer(texts.FINANCE_NO_PERMISSION)
        return
    await state.clear()
    await message.answer(texts.FINANCE_PICK_CATEGORY_EXPENSE,
                         reply_markup=kb.finance_categories_kb("expense"))


@router.callback_query(F.data.startswith("fin_cat:"))
async def finance_category_chosen(call: CallbackQuery, state: FSMContext):
    me = get_employee_by_telegram_id(call.from_user.id)
    if not _can_use_finance(me):
        await call.answer(texts.FINANCE_NO_PERMISSION, show_alert=True)
        return

    parts = call.data.split(":")
    if len(parts) != 3:
        await call.answer("❌ Xato", show_alert=True)
        return
    _, entry_type, cat_key = parts
    if cat_key == "cancel":
        await state.clear()
        await call.message.edit_text(texts.CANCELLED)
        await call.answer()
        return
    if cat_key not in texts.FINANCE_CATEGORIES:
        await call.answer("❌ Noma'lum turkum", show_alert=True)
        return

    emoji, cat_name = texts.FINANCE_CATEGORIES[cat_key]
    type_name = "Kirim" if entry_type == "income" else "Chiqim"
    await state.update_data(
        fin_owner=me["id"],
        fin_type=entry_type,
        fin_cat_key=cat_key,
        fin_cat_name=cat_name,
        fin_cat_emoji=emoji,
    )
    await call.message.edit_text(
        texts.FINANCE_ASK_AMOUNT.format(
            emoji="➕" if entry_type == "income" else "➖",
            type_name=type_name,
            category=f"{emoji} {cat_name}",
        )
    )
    await state.set_state(FinanceEntry.entering_amount)
    await call.answer()


# ===== Summa kiritish =====

@router.message(FinanceEntry.entering_amount, F.text)
async def finance_amount_handler(message: Message, state: FSMContext):
    if message.text == texts.BTN_CANCEL:
        me = get_employee_by_telegram_id(message.from_user.id)
        await state.clear()
        await message.answer(texts.CANCELLED, reply_markup=kb.finance_menu_kb())
        return
    try:
        cleaned = message.text.replace(" ", "").replace(",", "").replace(".", "").strip()
        amount = int(cleaned)
        if amount <= 0 or amount > 10_000_000_000:
            raise ValueError()
    except ValueError:
        await message.answer(texts.FINANCE_AMOUNT_INVALID)
        return

    data = await state.get_data()
    type_name = "Kirim" if data["fin_type"] == "income" else "Chiqim"
    await state.update_data(fin_amount=amount)
    await message.answer(
        texts.FINANCE_ASK_NOTE.format(
            emoji="➕" if data["fin_type"] == "income" else "➖",
            type_name=type_name,
            category=f"{data['fin_cat_emoji']} {data['fin_cat_name']}",
            amount=amount,
        ),
        reply_markup=kb.finance_note_skip_kb()
    )
    await state.set_state(FinanceEntry.entering_note)


# ===== Izoh va saqlash =====

@router.message(FinanceEntry.entering_note, F.text)
async def finance_note_handler(message: Message, state: FSMContext):
    me = get_employee_by_telegram_id(message.from_user.id)

    if message.text == texts.BTN_CANCEL:
        await state.clear()
        await message.answer(texts.CANCELLED, reply_markup=kb.finance_menu_kb())
        return

    note = None
    if message.text != texts.BTN_FINANCE_NOTE_SKIP:
        note = message.text.strip()
        if len(note) > 500:
            note = note[:500]

    data = await state.get_data()
    entry_id = create_finance_entry(
        owner_id=data["fin_owner"],
        entry_type=data["fin_type"],
        category=data["fin_cat_key"],
        amount=data["fin_amount"],
        note=note,
    )
    logger.info("Finance entry %s yaratildi: owner=%s, %s %s",
                entry_id, data["fin_owner"], data["fin_type"], data["fin_amount"])

    type_emoji = "➕" if data["fin_type"] == "income" else "➖"
    type_name = "Kirim" if data["fin_type"] == "income" else "Chiqim"
    note_line = texts.FINANCE_NOTE_FRAGMENT.format(note=note) if note else ""

    await message.answer(
        texts.FINANCE_SAVED.format(
            type_emoji=type_emoji,
            type_name=type_name,
            cat_emoji=data["fin_cat_emoji"],
            category=data["fin_cat_name"],
            amount=data["fin_amount"],
            when=tz_now().strftime("%d.%m.%Y %H:%M"),
            note_line=note_line,
        ),
        reply_markup=kb.finance_menu_kb()
    )
    await state.clear()


# ===== Bu oylik xulosa =====

@router.message(F.text == texts.BTN_FINANCE_SUMMARY)
async def finance_summary(message: Message):
    me = get_employee_by_telegram_id(message.from_user.id)
    if not _can_use_finance(me):
        await message.answer(texts.FINANCE_NO_PERMISSION)
        return

    now = tz_now()
    summary = get_monthly_finance_summary(me["id"], now.year, now.month)
    out = texts.FINANCE_SUMMARY_HEADER.format(
        month=texts.MONTHS_UZ[now.month], year=now.year
    )

    if not summary["by_category"]["income"] and not summary["by_category"]["expense"]:
        out += texts.FINANCE_SUMMARY_EMPTY
        await message.answer(out)
        return

    if summary["by_category"]["income"]:
        out += texts.FINANCE_SUMMARY_INCOME.format(total=summary["income_total"])
        for row in summary["by_category"]["income"]:
            cat_info = texts.FINANCE_CATEGORIES.get(row["category"], ("📋", row["category"]))
            out += texts.FINANCE_SUMMARY_CAT_LINE.format(
                emoji=cat_info[0], category=cat_info[1],
                total=row["total"], cnt=row["cnt"]
            )

    if summary["by_category"]["expense"]:
        out += texts.FINANCE_SUMMARY_EXPENSE.format(total=summary["expense_total"])
        for row in summary["by_category"]["expense"]:
            cat_info = texts.FINANCE_CATEGORIES.get(row["category"], ("📋", row["category"]))
            out += texts.FINANCE_SUMMARY_CAT_LINE.format(
                emoji=cat_info[0], category=cat_info[1],
                total=row["total"], cnt=row["cnt"]
            )

    net = summary["net"]
    if net > 0:
        out += texts.FINANCE_SUMMARY_NET_POS.format(net=net)
    elif net < 0:
        out += texts.FINANCE_SUMMARY_NET_NEG.format(net=net)
    else:
        out += texts.FINANCE_SUMMARY_NET_ZERO

    await message.answer(out)


# ===== Excel hisobot =====

@router.message(F.text == texts.BTN_FINANCE_EXCEL)
async def finance_excel(message: Message):
    me = get_employee_by_telegram_id(message.from_user.id)
    if not _can_use_finance(me):
        await message.answer(texts.FINANCE_NO_PERMISSION)
        return

    now = tz_now()
    entries = get_monthly_finance_entries(me["id"], now.year, now.month)
    if not entries:
        await message.answer(texts.FINANCE_EXCEL_EMPTY)
        return

    summary = get_monthly_finance_summary(me["id"], now.year, now.month)
    file_bytes = await asyncio.to_thread(
        _build_finance_excel, entries, summary, now.year, now.month, me["full_name"]
    )
    filename = f"moliya_{now.year}_{now.month:02d}_{me['full_name'].split()[0]}.xlsx"
    await message.answer_document(
        BufferedInputFile(file_bytes, filename=filename),
        caption=f"📥 Moliya hisoboti — {texts.MONTHS_UZ[now.month]} {now.year}"
    )


def _build_finance_excel(entries, summary, year: int, month: int, owner_name: str) -> bytes:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    wb = Workbook()

    # Sheet 1: Yozuvlar
    ws = wb.active
    ws.title = "Yozuvlar"

    title = ws.cell(row=1, column=1,
                    value=f"💰 Moliya — {owner_name} · {texts.MONTHS_UZ[month]} {year}")
    title.font = Font(bold=True, size=14, color="FFFFFF")
    title.fill = PatternFill(start_color="2E5C8A", end_color="2E5C8A", fill_type="solid")
    title.alignment = Alignment(horizontal="center", vertical="center")
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=5)
    ws.row_dimensions[1].height = 22

    headers = ["Sana", "Tur", "Turkum", "Summa (so'm)", "Izoh"]
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    thin = Side(border_style="thin", color="808080")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=3, column=col, value=h)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = border

    for i, e in enumerate(entries, start=4):
        cat_info = texts.FINANCE_CATEGORIES.get(e["category"], ("📋", e["category"]))
        ws.cell(row=i, column=1,
                value=fmt_local(e["entry_date"], "%d.%m.%Y %H:%M"))
        ws.cell(row=i, column=2,
                value="Kirim" if e["entry_type"] == "income" else "Chiqim")
        ws.cell(row=i, column=3, value=f"{cat_info[0]} {cat_info[1]}")
        amount_cell = ws.cell(row=i, column=4, value=e["amount"])
        amount_cell.number_format = '#,##0'
        if e["entry_type"] == "income":
            amount_cell.font = Font(color="006400")
        else:
            amount_cell.font = Font(color="8B0000")
        ws.cell(row=i, column=5, value=e["note"] or "")
        for c in range(1, 6):
            ws.cell(row=i, column=c).border = border

    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["B"].width = 10
    ws.column_dimensions["C"].width = 26
    ws.column_dimensions["D"].width = 18
    ws.column_dimensions["E"].width = 40

    # Sheet 2: Xulosa
    ws2 = wb.create_sheet("Xulosa")
    ws2.cell(row=1, column=1, value="Tur").font = Font(bold=True)
    ws2.cell(row=1, column=2, value="Turkum").font = Font(bold=True)
    ws2.cell(row=1, column=3, value="Yozuvlar").font = Font(bold=True)
    ws2.cell(row=1, column=4, value="Jami (so'm)").font = Font(bold=True)
    for c in range(1, 5):
        ws2.cell(row=1, column=c).fill = header_fill
        ws2.cell(row=1, column=c).font = Font(bold=True, color="FFFFFF")
        ws2.cell(row=1, column=c).border = border

    row = 2
    for tp in ("income", "expense"):
        type_label = "Kirim" if tp == "income" else "Chiqim"
        for r in summary["by_category"].get(tp, []):
            cat_info = texts.FINANCE_CATEGORIES.get(r["category"], ("📋", r["category"]))
            ws2.cell(row=row, column=1, value=type_label)
            ws2.cell(row=row, column=2, value=f"{cat_info[0]} {cat_info[1]}")
            ws2.cell(row=row, column=3, value=r["cnt"])
            amount_cell = ws2.cell(row=row, column=4, value=r["total"])
            amount_cell.number_format = '#,##0'
            amount_cell.font = Font(color="006400" if tp == "income" else "8B0000")
            for c in range(1, 5):
                ws2.cell(row=row, column=c).border = border
            row += 1

    # Yakuniy hisob
    row += 1
    ws2.cell(row=row, column=1, value="Jami kirim").font = Font(bold=True)
    c = ws2.cell(row=row, column=4, value=summary["income_total"])
    c.number_format = '#,##0'
    c.font = Font(bold=True, color="006400")
    row += 1
    ws2.cell(row=row, column=1, value="Jami chiqim").font = Font(bold=True)
    c = ws2.cell(row=row, column=4, value=summary["expense_total"])
    c.number_format = '#,##0'
    c.font = Font(bold=True, color="8B0000")
    row += 1
    ws2.cell(row=row, column=1, value="Sof natija (foyda/zarar)").font = Font(bold=True, size=12)
    c = ws2.cell(row=row, column=4, value=summary["net"])
    c.number_format = '#,##0'
    c.font = Font(bold=True, color="006400" if summary["net"] >= 0 else "8B0000")

    ws2.column_dimensions["A"].width = 22
    ws2.column_dimensions["B"].width = 26
    ws2.column_dimensions["C"].width = 12
    ws2.column_dimensions["D"].width = 18

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()
