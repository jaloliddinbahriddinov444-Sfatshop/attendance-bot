"""Telegram klaviaturalari"""
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton
)
import texts


def remove_kb():
    return ReplyKeyboardRemove()


def main_menu_kb(is_admin: bool = False, is_boss: bool = False,
                 is_bosh_admin: bool = False) -> ReplyKeyboardMarkup:
    # Bosh Admin uchun: to'g'ridan-to'g'ri Moliya bo'limi + Admin panel
    if is_bosh_admin:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=texts.BTN_BOSS_FINANCE)],
                [KeyboardButton(text=texts.BTN_ATTENDANCE)],
                [KeyboardButton(text=texts.BTN_PROFILE), KeyboardButton(text=texts.BTN_STATS)],
                [KeyboardButton(text=texts.BTN_TASKS), KeyboardButton(text=texts.BTN_SALARY)],
                [KeyboardButton(text=texts.BTN_ADMIN)],
            ],
            resize_keyboard=True,
        )

    # Boss uchun asosiy menyu
    if is_boss:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=texts.BTN_BOSS_ATTENDANCE)],
                [KeyboardButton(text=texts.BTN_ADMIN_TASKS),
                 KeyboardButton(text=texts.BTN_BOSS_FINANCE)],
            ],
            resize_keyboard=True,
        )

    rows = [
        [KeyboardButton(text=texts.BTN_ATTENDANCE)],
        [KeyboardButton(text=texts.BTN_PROFILE), KeyboardButton(text=texts.BTN_STATS)],
        [KeyboardButton(text=texts.BTN_TASKS), KeyboardButton(text=texts.BTN_SALARY)],
    ]
    if is_admin:
        rows.append([KeyboardButton(text=texts.BTN_ADMIN)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=texts.BTN_CANCEL)]],
        resize_keyboard=True
    )


def phone_request_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_SHARE_PHONE, request_contact=True)],
            [KeyboardButton(text=texts.BTN_CANCEL)],
        ],
        resize_keyboard=True
    )


def location_request_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_SHARE_LOCATION, request_location=True)],
            [KeyboardButton(text=texts.BTN_CANCEL)],
        ],
        resize_keyboard=True
    )


def attendance_menu_kb(can_check_in: bool, can_check_out: bool) -> ReplyKeyboardMarkup:
    rows = []
    if can_check_in:
        rows.append([KeyboardButton(text=texts.BTN_CHECK_IN)])
    if can_check_out:
        rows.append([KeyboardButton(text=texts.BTN_CHECK_OUT)])
    rows.append([KeyboardButton(text=texts.BTN_BACK)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def wifi_confirm_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_WIFI_CONFIRMED)],
            [KeyboardButton(text=texts.BTN_CANCEL)],
        ],
        resize_keyboard=True
    )


def admin_menu_kb(is_bosh_admin: bool = False) -> ReplyKeyboardMarkup:
    # Bosh Admin uchun — tugmalar bo'limlarga yig'ilgan (qisqa, tartibli panel).
    # Har bo'lim alohida submenyu ochadi (grp_*_kb).
    if is_bosh_admin:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=texts.BTN_GRP_EMPLOYEES),
                 KeyboardButton(text=texts.BTN_GRP_ATTENDANCE)],
                [KeyboardButton(text=texts.BTN_GRP_FINANCE),
                 KeyboardButton(text=texts.BTN_ADMIN_TASKS)],
                [KeyboardButton(text=texts.BTN_GRP_CONTROL)],
                [KeyboardButton(text=texts.BTN_BACK)],
            ],
            resize_keyboard=True,
        )

    # Oddiy admin uchun — eski tekis menyu (o'zgarmaydi).
    rows = [
        [KeyboardButton(text=texts.BTN_ADMIN_ADD_EMPLOYEE)],
        [KeyboardButton(text=texts.BTN_ADMIN_LIST),
         KeyboardButton(text=texts.BTN_ADMIN_TODAY)],
        [KeyboardButton(text=texts.BTN_ADMIN_ATT_EDIT),
         KeyboardButton(text=texts.BTN_ADMIN_RATES)],
        [KeyboardButton(text=texts.BTN_ADMIN_SALARY),
         KeyboardButton(text=texts.BTN_ADMIN_TASKS)],
        [KeyboardButton(text=texts.BTN_ADMIN_EXPORT),
         KeyboardButton(text=texts.BTN_ADMIN_EMP_EXCEL)],
        [KeyboardButton(text=texts.BTN_ADMIN_REMOVE),
         KeyboardButton(text=texts.BTN_ADMIN_PROMOTE)],
        [KeyboardButton(text=texts.BTN_ADMIN_SETTINGS)],
        [KeyboardButton(text=texts.BTN_BACK)],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


# ===== Bosh Admin: bo'lim submenyulari =====

def grp_employees_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_ADMIN_ADD_EMPLOYEE)],
            [KeyboardButton(text=texts.BTN_SET_POSITION)],
            [KeyboardButton(text=texts.BTN_ADMIN_LIST)],
            [KeyboardButton(text=texts.BTN_ADMIN_REMOVE)],
            [KeyboardButton(text=texts.BTN_ADMIN_EMP_EXCEL)],
            [KeyboardButton(text=texts.BTN_ADMIN_BACK)],
        ],
        resize_keyboard=True,
    )


def grp_attendance_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_ADMIN_TODAY)],
            [KeyboardButton(text=texts.BTN_ADMIN_ATT_EDIT)],
            [KeyboardButton(text=texts.BTN_ADMIN_BACK)],
        ],
        resize_keyboard=True,
    )


def grp_finance_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_ADMIN_RATES),
             KeyboardButton(text=texts.BTN_ADMIN_SALARY)],
            [KeyboardButton(text=texts.BTN_ADMIN_EXPORT)],
            [KeyboardButton(text=texts.BTN_ADMIN_BACK)],
        ],
        resize_keyboard=True,
    )


def grp_control_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_ADMIN_SETTINGS)],
            [KeyboardButton(text=texts.BTN_OFFICE_IP)],
            [KeyboardButton(text=texts.BTN_POSITIONS)],
            [KeyboardButton(text=texts.BTN_ADMIN_PROMOTE),
             KeyboardButton(text=texts.BTN_ADMIN_BOSS_ASSIGN)],
            [KeyboardButton(text=texts.BTN_BROADCAST)],
            [KeyboardButton(text=texts.BTN_ADMIN_BACK)],
        ],
        resize_keyboard=True,
    )


def ip_menu_kb() -> ReplyKeyboardMarkup:
    """Ofis IP boshqaruvi submenyusi (Bosh Admin)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_OFFICE_IP_ADD)],
            [KeyboardButton(text=texts.BTN_OFFICE_IP_LIST)],
            [KeyboardButton(text=texts.BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def admin_settings_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_SET_HOURS)],
            [KeyboardButton(text=texts.BTN_BACK)],
        ],
        resize_keyboard=True
    )


# ===== Inline klaviaturalar =====

def employees_inline_kb(employees, prefix: str) -> InlineKeyboardMarkup:
    """Xodimlar ro'yxati inline tugmalar bilan"""
    rows = []
    for emp in employees:
        admin_icon = "👑 " if emp["is_admin"] else ""
        rows.append([InlineKeyboardButton(
            text=f"{admin_icon}{emp['full_name']}",
            callback_data=f"{prefix}:{emp['id']}"
        )])
    rows.append([InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data=f"{prefix}:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_inline_kb(action: str, target_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data=f"{action}:yes:{target_id}"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data=f"{action}:no:{target_id}"),
        ]
    ])


def salary_admin_menu_kb() -> InlineKeyboardMarkup:
    """Admin ish haqqi boshqaruv menyusi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yozuv qo'shish", callback_data="sal_add"),
         InlineKeyboardButton(text="❌ Bekor qilish", callback_data="sal_cancel")],
        [InlineKeyboardButton(text="📊 Excel hisobot", callback_data="sal_report"),
         InlineKeyboardButton(text="📜 Audit tarixi", callback_data="sal_audit")],
        [InlineKeyboardButton(text="🔒 Oyni yopish/ochish", callback_data="sal_close_month")],
        [InlineKeyboardButton(text="🚪 Yopish", callback_data="sal_close")],
    ])


def month_close_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, yopish", callback_data="sal_cm_yes"),
         InlineKeyboardButton(text="❌ Yo'q", callback_data="sal_cm_no")],
    ])


def month_reopen_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔓 Ha, qayta ochish", callback_data="sal_cm_reopen"),
         InlineKeyboardButton(text="❌ Yo'q", callback_data="sal_cm_no")],
    ])


def salary_types_kb() -> InlineKeyboardMarkup:
    """Kategoriya tanlash"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💸 Avans", callback_data="sal_type:avans")],
        [InlineKeyboardButton(text="⚠️ Jarima", callback_data="sal_type:jarima")],
        [InlineKeyboardButton(text="⭐ Mukofot", callback_data="sal_type:mukofot")],
        [InlineKeyboardButton(text="🎁 Bonus", callback_data="sal_type:bonus")],
        [InlineKeyboardButton(text="🛒 Mahsulot xaridi", callback_data="sal_type:mahsulot")],
        [InlineKeyboardButton(text="❌ Bekor", callback_data="sal_type:cancel")],
    ])


def salary_employees_kb(employees, prefix: str) -> InlineKeyboardMarkup:
    rows = []
    for emp in employees:
        rows.append([InlineKeyboardButton(
            text=f"👤 {emp['full_name']}",
            callback_data=f"{prefix}:{emp['id']}"
        )])
    rows.append([InlineKeyboardButton(text="❌ Bekor", callback_data=f"{prefix}:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def salary_entries_kb(entries, prefix: str) -> InlineKeyboardMarkup:
    """Yozuvlar ro'yxati (bekor qilish uchun)"""
    rows = []
    for entry in entries:
        info = texts.SALARY_TYPES.get(entry["entry_type"], ("📋", "?", ""))
        emoji, type_name, _ = info
        rows.append([InlineKeyboardButton(
            text=f"{emoji} {type_name}: {entry['amount']:,} so'm",
            callback_data=f"{prefix}:{entry['id']}"
        )])
    rows.append([InlineKeyboardButton(text="❌ Bekor", callback_data=f"{prefix}:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def salary_confirm_kb() -> InlineKeyboardMarkup:
    """Katta summa uchun tasdiqlash"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="sal_confirm:yes"),
         InlineKeyboardButton(text="❌ Bekor qilish", callback_data="sal_confirm:no")],
    ])


# ===== Vazifalar (Phase 2) =====

def task_complete_kb(task_id: int) -> InlineKeyboardMarkup:
    """Xodim oynasida har bir ochiq vazifa uchun "Tugatdim" tugmasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.TASK_MARK_DONE_BTN,
                              callback_data=f"task_done:{task_id}")]
    ])


def task_description_skip_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_TASK_SKIP_DESCRIPTION)],
            [KeyboardButton(text=texts.BTN_CANCEL)],
        ],
        resize_keyboard=True
    )


def task_deadline_skip_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_TASK_SKIP_DEADLINE)],
            [KeyboardButton(text=texts.BTN_CANCEL)],
        ],
        resize_keyboard=True
    )


def checkout_tasks_yes_no_kb() -> InlineKeyboardMarkup:
    """Ketdim oxiridagi "Hammasini tugatdingizmi?" savoli."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, tugatdim",
                              callback_data="ck_tasks:yes"),
         InlineKeyboardButton(text="❌ Yo'q, tugatmadim",
                              callback_data="ck_tasks:no")],
    ])


# ===== Boss panel (Phase 3A) =====

def boss_panel_kb() -> ReplyKeyboardMarkup:
    """Boss bo'lim menyusi."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_BOSS_ATTENDANCE)],
            [KeyboardButton(text=texts.BTN_ADMIN_TASKS),
             KeyboardButton(text=texts.BTN_BOSS_FINANCE)],
            [KeyboardButton(text=texts.BTN_BROADCAST)],
            [KeyboardButton(text=texts.BTN_BACK)],
        ],
        resize_keyboard=True
    )


def assign_boss_confirm_kb(emp_id: int) -> InlineKeyboardMarkup:
    """Boss tayinlashni tasdiqlash (Bosh Admin uchun)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, Boss qil",
                              callback_data=f"boss_set:yes:{emp_id}"),
         InlineKeyboardButton(text="❌ Bekor",
                              callback_data=f"boss_set:no:{emp_id}")],
    ])


def remove_boss_confirm_kb() -> InlineKeyboardMarkup:
    """Mavjud Bossni o'chirish tasdig'i."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, o'chir",
                              callback_data="boss_remove:yes"),
         InlineKeyboardButton(text="❌ Bekor",
                              callback_data="boss_remove:no")],
    ])


# ===== Moliya bo'limi (Phase 4) =====

def finance_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_FINANCE_INCOME),
             KeyboardButton(text=texts.BTN_FINANCE_EXPENSE)],
            [KeyboardButton(text=texts.BTN_FINANCE_SUMMARY),
             KeyboardButton(text=texts.BTN_FINANCE_EXCEL)],
            [KeyboardButton(text=texts.BTN_FINANCE_DELETE)],
            [KeyboardButton(text=texts.BTN_PERSONAL_FINANCE)],
            [KeyboardButton(text=texts.BTN_BACK)],
        ],
        resize_keyboard=True
    )


def pf_menu_kb() -> ReplyKeyboardMarkup:
    """Shaxsiy moliya menyusi."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_PF_INCOME),
             KeyboardButton(text=texts.BTN_PF_EXPENSE)],
            [KeyboardButton(text=texts.BTN_PF_SUMMARY),
             KeyboardButton(text=texts.BTN_PF_EXCEL)],
            [KeyboardButton(text=texts.BTN_PF_DELETE)],
            [KeyboardButton(text=texts.BTN_BACK)],
        ],
        resize_keyboard=True
    )


def pf_income_cats_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=f"{emoji} {name}",
            callback_data=f"pf_cat:income:{key}"
        )]
        for key, (emoji, name) in texts.PF_INCOME_CATS.items()
    ]
    rows.append([InlineKeyboardButton(
        text=texts.BTN_CANCEL, callback_data="pf_cat:cancel"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def pf_expense_cats_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=f"{emoji} {name}",
            callback_data=f"pf_cat:expense:{key}"
        )]
        for key, (emoji, name) in texts.PF_EXPENSE_CATS.items()
    ]
    rows.append([InlineKeyboardButton(
        text=texts.BTN_CANCEL, callback_data="pf_cat:cancel"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def pf_note_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_PF_NOTE_SKIP)],
            [KeyboardButton(text=texts.BTN_CANCEL)],
        ],
        resize_keyboard=True
    )


def pf_date_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_PF_TODAY)],
            [KeyboardButton(text=texts.BTN_CANCEL)],
        ],
        resize_keyboard=True
    )


def pf_entries_kb(entries) -> InlineKeyboardMarkup:
    """O'chirish uchun yozuvlar ro'yxati."""
    rows = []
    for e in entries:
        cat_info = texts.PF_ALL_CATS.get(e["category"], ("📋", e["category"]))
        emoji, name = cat_info
        sign = "+" if e["entry_type"] == "income" else "-"
        rows.append([InlineKeyboardButton(
            text=f"{sign}{e['amount']:,} — {emoji}{name} ({e['entry_date'][5:]})",
            callback_data=f"pf_del:{e['id']}"
        )])
    rows.append([InlineKeyboardButton(
        text=texts.BTN_CANCEL, callback_data="pf_del:cancel"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def finance_personal_cats_kb() -> InlineKeyboardMarkup:
    """Shaxsiy xarajatlar ichki turkumlari."""
    rows = []
    for key, (emoji, name) in texts.FINANCE_PERSONAL_CATEGORIES.items():
        label = name.replace("Shaxsiy: ", "")
        rows.append([InlineKeyboardButton(
            text=f"{emoji} {label}",
            callback_data=f"fin_cat:expense:{key}"
        )])
    rows.append([InlineKeyboardButton(
        text="⬅️ Ortga", callback_data="fin_cat:expense:backexp"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def finance_date_kb() -> ReplyKeyboardMarkup:
    """Sana tanlash: bugun tugmasi yoki qo'lda yozish."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_FINANCE_TODAY)],
            [KeyboardButton(text=texts.BTN_CANCEL)],
        ],
        resize_keyboard=True
    )


def finance_del_entries_kb(entries) -> InlineKeyboardMarkup:
    """Sana bo'yicha yozuvlar — o'chirish uchun tanlash."""
    rows = []
    for e in entries:
        cat_info = texts.FINANCE_CATEGORIES.get(e["category"], ("📋", e["category"]))
        sign = "➕" if e["entry_type"] == "income" else "➖"
        rows.append([InlineKeyboardButton(
            text=f"{sign} {e['amount']:,} — {cat_info[1]}",
            callback_data=f"fin_del:{e['id']}"
        )])
    rows.append([InlineKeyboardButton(
        text=texts.BTN_CANCEL, callback_data="fin_del:cancel"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def finance_del_confirm_kb(entry_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, o'chirish",
                              callback_data=f"fin_delc:{entry_id}"),
         InlineKeyboardButton(text="❌ Bekor",
                              callback_data="fin_del:cancel")],
    ])


def finance_categories_kb(entry_type: str) -> InlineKeyboardMarkup:
    """Turkum tanlash — kirim va chiqim uchun alohida ro'yxatlar."""
    if entry_type == "income":
        cats = texts.FINANCE_INCOME_CATEGORIES
    else:
        cats = texts.FINANCE_EXPENSE_CATEGORIES
    rows = []
    for key, (emoji, name) in cats.items():
        rows.append([InlineKeyboardButton(
            text=f"{emoji} {name}",
            callback_data=f"fin_cat:{entry_type}:{key}"
        )])
    rows.append([InlineKeyboardButton(text=texts.BTN_CANCEL,
                                      callback_data=f"fin_cat:{entry_type}:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def finance_employees_kb(employees) -> InlineKeyboardMarkup:
    """Avans uchun xodim tanlash klaviaturasi."""
    rows = []
    for emp in employees:
        rows.append([InlineKeyboardButton(
            text=f"👤 {emp['full_name']}",
            callback_data=f"fin_emp:{emp['id']}"
        )])
    rows.append([InlineKeyboardButton(
        text=texts.BTN_CANCEL, callback_data="fin_emp:cancel"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def finance_note_skip_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_FINANCE_NOTE_SKIP)],
            [KeyboardButton(text=texts.BTN_CANCEL)],
        ],
        resize_keyboard=True
    )


# ===== Phase 4: karta / xodim qo'shish =====

def profile_card_inline_kb() -> InlineKeyboardMarkup:
    """Profil xabari ostidagi 'Karta ma'lumotlari' tugmasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.BTN_PROFILE_CARD,
                              callback_data="profile_card")]
    ])


def addemp_confirm_kb() -> InlineKeyboardMarkup:
    """Admin xodim qo'shishni tasdiqlash."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="addemp:yes"),
         InlineKeyboardButton(text="❌ Bekor", callback_data="addemp:no")]
    ])


# ===== Davomat tahrirlash: kun tanlash + kunga xos amallar =====

def att_days_kb(emp_id: int) -> InlineKeyboardMarkup:
    """Oxirgi 7 kun (bugundan boshlab orqaga) — har biri tugma.
    Callback: att_day:{emp_id}:YYYY-MM-DD"""
    from datetime import timedelta
    from tzutil import now as tz_now
    today = tz_now().date()
    rows = []
    for i in range(7):
        d = today - timedelta(days=i)
        date_str = d.strftime("%Y-%m-%d")
        label_date = d.strftime("%d.%m")
        if i == 0:
            label = f"📅 {label_date} (Bugun)"
        elif i == 1:
            label = f"📅 {label_date} (Kecha)"
        else:
            label = f"📅 {label_date} ({texts.WEEKDAYS_UZ[d.weekday()]})"
        rows.append([InlineKeyboardButton(
            text=label, callback_data=f"att_day:{emp_id}:{date_str}"
        )])
    rows.append([InlineKeyboardButton(
        text=texts.BTN_CANCEL, callback_data="att_edit:cancel"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def att_actions_kb(emp_id: int, date_str: str) -> InlineKeyboardMarkup:
    """Tanlangan kun uchun amallar. Sana callback'da olib ketiladi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🟢 Keldim qo'shish",
            callback_data=f"att_add:in:{emp_id}:{date_str}"
        )],
        [InlineKeyboardButton(
            text="🔴 Ketdim qo'shish",
            callback_data=f"att_add:out:{emp_id}:{date_str}"
        )],
        [InlineKeyboardButton(
            text="🗑 Bu kun yozuvlarini tozalash",
            callback_data=f"att_reset:{emp_id}:{date_str}"
        )],
        [InlineKeyboardButton(
            text="⬅️ Boshqa kun",
            callback_data=f"att_edit:{emp_id}"
        )],
    ])


# ===== Lavozimlar tizimi =====

def positions_list_kb(positions, prefix: str) -> InlineKeyboardMarkup:
    """Lavozimlar ro'yxati inline tugmalar bilan."""
    rows = []
    for pos in positions:
        rows.append([InlineKeyboardButton(
            text=f"💼 {pos['name']} ({pos['work_hours']}h | {pos['min_rate']//1000}–{pos['max_rate']//1000}k)",
            callback_data=f"{prefix}:{pos['id']}"
        )])
    rows.append([InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data=f"{prefix}:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def position_actions_kb(pos_id: int) -> InlineKeyboardMarkup:
    """Lavozimga amallar: tahrirlash / o'chirish."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.BTN_POS_DELETE,
                              callback_data=f"pos_del:{pos_id}")],
        [InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data="pos_del:cancel")],
    ])


# ===== Admin: Xodimlar ma'lumotlari (lavozim → xodim) =====

def emp_positions_kb(positions, unassigned_count: int = 0) -> InlineKeyboardMarkup:
    """Lavozimlar ro'yxati + 'Lavozim belgilanmagan' variant."""
    rows = []
    for pos in positions:
        rows.append([InlineKeyboardButton(
            text=f"💼 {pos['name']}",
            callback_data=f"empdata_pos:{pos['id']}"
        )])
    if unassigned_count > 0:
        rows.append([InlineKeyboardButton(
            text=f"❓ Lavozim belgilanmagan ({unassigned_count})",
            callback_data="empdata_pos:0"
        )])
    rows.append([InlineKeyboardButton(
        text=texts.BTN_CANCEL, callback_data="empdata_pos:cancel"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def emp_in_position_kb(employees, pos_id: int) -> InlineKeyboardMarkup:
    """Lavozim ichidagi xodimlar."""
    rows = []
    for emp in employees:
        rows.append([InlineKeyboardButton(
            text=f"👤 {emp['full_name']}",
            callback_data=f"empdata_emp:{emp['id']}"
        )])
    rows.append([InlineKeyboardButton(
        text="⬅️ Lavozimlar", callback_data="empdata_back"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ===== Xabarnoma (Broadcast) =====

def bc_target_kb(chat_title: str = None) -> InlineKeyboardMarkup:
    if chat_title:
        channel_btn_text = f"📢 {chat_title}"
    else:
        channel_btn_text = texts.BC_BTN_CHANNEL
    rows = [
        [InlineKeyboardButton(text=channel_btn_text, callback_data="bc_target:channel")],
    ]
    if chat_title:
        rows.append([InlineKeyboardButton(
            text="🔄 Boshqa kanal/guruhni ulash",
            callback_data="bc_change_chat"
        )])
    rows += [
        [InlineKeyboardButton(text=texts.BC_BTN_ONE_EMP, callback_data="bc_target:emp")],
        [InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data="bc_cancel")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def bc_content_type_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.BC_BTN_TEXT, callback_data="bc_type:text"),
         InlineKeyboardButton(text=texts.BC_BTN_PHOTO, callback_data="bc_type:photo")],
        [InlineKeyboardButton(text=texts.BC_BTN_VIDEO, callback_data="bc_type:video"),
         InlineKeyboardButton(text=texts.BC_BTN_FILE, callback_data="bc_type:file")],
        [InlineKeyboardButton(text=texts.BC_BTN_POLL, callback_data="bc_type:poll")],
        [InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data="bc_cancel")],
    ])


def bc_employees_kb(employees) -> InlineKeyboardMarkup:
    rows = []
    for emp in employees:
        rows.append([InlineKeyboardButton(
            text=f"👤 {emp['full_name']}",
            callback_data=f"bc_emp:{emp['id']}"
        )])
    rows.append([InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data="bc_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def bc_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.BC_BTN_SEND, callback_data="bc_confirm:yes"),
         InlineKeyboardButton(text=texts.BC_BTN_CANCEL, callback_data="bc_cancel")],
    ])


