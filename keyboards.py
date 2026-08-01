"""Telegram klaviaturalari"""
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton
)
import texts
import tzutil
from database import (
    get_finance_categories, get_finance_personal_categories,
    finance_category_label,
    get_pf_categories, pf_category_label,
    get_menu_layout,
)


def remove_kb():
    return ReplyKeyboardRemove()


# ===== Menyu reyestri =====
# Bosh Admin bot ichidan tahrirlay oladigan reply-menyular.
# "buttons" — kalit -> texts.py tugma matni (matnlar handler filtrlariga
# bog'langan, ular O'ZGARMAYDI — faqat joylashuv o'zgaradi).
# "default" — hozirgi kod tartibi AYNAN; bazada yozuv bo'lmasa shu ishlatiladi.
MAX_ROW_BUTTONS = 2  # Telegram'da 3+ tugma matni qisqarib ketadi

MENU_REGISTRY = {
    "main_employee": {
        "title": "🏠 Asosiy menyu — xodim",
        "buttons": {
            "attendance": texts.BTN_ATTENDANCE,
            "profile": texts.BTN_PROFILE,
            "stats": texts.BTN_STATS,
            "tasks": texts.BTN_TASKS,
            "salary": texts.BTN_SALARY,
            "personal_finance": texts.BTN_PERSONAL_FINANCE,
            "admin": texts.BTN_ADMIN,
        },
        "default": [["attendance"], ["profile", "stats"], ["tasks", "salary"],
                    ["personal_finance"], ["admin"]],
        "targets": {"personal_finance": "pf_menu", "admin": "admin_panel"},
        "conditional": {"admin", "personal_finance"},
    },
    "main_boss": {
        "title": "🏠 Asosiy menyu — Boss",
        "buttons": {
            "boss_attendance": texts.BTN_BOSS_ATTENDANCE,
            "admin_tasks": texts.BTN_ADMIN_TASKS,
            "boss_finance": texts.BTN_BOSS_FINANCE,
        },
        "default": [["boss_attendance"], ["admin_tasks", "boss_finance"]],
        "targets": {"boss_finance": "finance_menu"},
    },
    "main_bosh_admin": {
        "title": "🏠 Asosiy menyu — Bosh Admin",
        "buttons": {
            "boss_finance": texts.BTN_BOSS_FINANCE,
            "attendance": texts.BTN_ATTENDANCE,
            "profile": texts.BTN_PROFILE,
            "stats": texts.BTN_STATS,
            "tasks": texts.BTN_TASKS,
            "salary": texts.BTN_SALARY,
            "admin": texts.BTN_ADMIN,
        },
        "default": [["boss_finance"], ["attendance"], ["profile", "stats"],
                    ["tasks", "salary"], ["admin"]],
        "targets": {"boss_finance": "finance_menu", "admin": "admin_panel_bosh"},
    },
    "admin_panel_bosh": {
        "title": "⚙️ Admin panel — Bosh Admin",
        "buttons": {
            "grp_employees": texts.BTN_GRP_EMPLOYEES,
            "grp_attendance": texts.BTN_GRP_ATTENDANCE,
            "admin_tasks": texts.BTN_ADMIN_TASKS,
            "grp_control": texts.BTN_GRP_CONTROL,
            "back": texts.BTN_BACK,
        },
        "default": [["grp_employees", "grp_attendance"], ["admin_tasks"],
                    ["grp_control"], ["back"]],
        "targets": {"grp_employees": "grp_employees", "grp_attendance": "grp_attendance",
                    "grp_control": "grp_control", "back": "back"},
    },
    "admin_panel": {
        "title": "⚙️ Admin panel — oddiy admin",
        "buttons": {
            "admin_add_employee": texts.BTN_ADMIN_ADD_EMPLOYEE,
            "admin_list": texts.BTN_ADMIN_LIST,
            "admin_today": texts.BTN_ADMIN_TODAY,
            "admin_att_edit": texts.BTN_ADMIN_ATT_EDIT,
            "admin_rates": texts.BTN_ADMIN_RATES,
            "fix_requests": texts.BTN_FIX_REQUESTS_ADMIN,
            "admin_salary": texts.BTN_ADMIN_SALARY,
            "admin_tasks": texts.BTN_ADMIN_TASKS,
            "admin_export": texts.BTN_ADMIN_EXPORT,
            "admin_emp_excel": texts.BTN_ADMIN_EMP_EXCEL,
            "admin_remove": texts.BTN_ADMIN_REMOVE,
            "admin_promote": texts.BTN_ADMIN_PROMOTE,
            "admin_settings": texts.BTN_ADMIN_SETTINGS,
            "back": texts.BTN_BACK,
        },
        "default": [["admin_add_employee"], ["admin_list", "admin_today"],
                    ["admin_att_edit", "admin_rates"], ["fix_requests"],
                    ["admin_salary", "admin_tasks"],
                    ["admin_export", "admin_emp_excel"],
                    ["admin_remove", "admin_promote"], ["admin_settings"],
                    ["back"]],
        "targets": {"admin_settings": "admin_settings", "back": "back"},
    },
    "grp_employees": {
        "title": "👥 Bo'lim — Xodimlar",
        "buttons": {
            "admin_list": texts.BTN_ADMIN_LIST,
            "admin_emp_excel": texts.BTN_ADMIN_EMP_EXCEL,
            "admin_add_employee": texts.BTN_ADMIN_ADD_EMPLOYEE,
            "admin_remove": texts.BTN_ADMIN_REMOVE,
            "set_position": texts.BTN_SET_POSITION,
            "admin_salary": texts.BTN_ADMIN_SALARY,
            "admin_back": texts.BTN_ADMIN_BACK,
        },
        "default": [["admin_list", "admin_emp_excel"],
                    ["admin_add_employee", "admin_remove"],
                    ["set_position", "admin_salary"], ["admin_back"]],
        "targets": {"admin_back": "back"},
    },
    "grp_attendance": {
        "title": "🕒 Bo'lim — Davomat",
        "buttons": {
            "admin_today": texts.BTN_ADMIN_TODAY,
            "admin_att_edit": texts.BTN_ADMIN_ATT_EDIT,
            "fix_requests": texts.BTN_FIX_REQUESTS_ADMIN,
            "admin_back": texts.BTN_ADMIN_BACK,
        },
        "default": [["admin_today"], ["admin_att_edit"], ["fix_requests"],
                    ["admin_back"]],
        "targets": {"admin_back": "back"},
    },
    "grp_finance": {
        "title": "💵 Bo'lim — Ish haqi",
        "buttons": {
            "admin_salary": texts.BTN_ADMIN_SALARY,
            "admin_back": texts.BTN_ADMIN_BACK,
        },
        "default": [["admin_salary"], ["admin_back"]],
        "targets": {"admin_back": "back"},
    },
    "grp_control": {
        "title": "🎛 Bo'lim — Boshqaruv",
        "buttons": {
            "admin_settings": texts.BTN_ADMIN_SETTINGS,
            "web_dashboard": texts.BTN_WEB_DASHBOARD,
            "reminders": texts.BTN_REMINDERS,
            "office_ip": texts.BTN_OFFICE_IP,
            "positions": texts.BTN_POSITIONS,
            "finance_categories": texts.BTN_FINANCE_CATEGORIES,
            "admin_promote": texts.BTN_ADMIN_PROMOTE,
            "admin_boss_assign": texts.BTN_ADMIN_BOSS_ASSIGN,
            "admin_pf_access": texts.BTN_ADMIN_PF_ACCESS,
            "menu_layout": texts.BTN_MENU_LAYOUT,
            "broadcast": texts.BTN_BROADCAST,
            "admin_back": texts.BTN_ADMIN_BACK,
        },
        "default": [["admin_settings"], ["web_dashboard", "reminders"],
                    ["office_ip"], ["positions", "finance_categories"],
                    ["admin_promote", "admin_boss_assign"],
                    ["admin_pf_access"], ["menu_layout"], ["broadcast"],
                    ["admin_back"]],
        "targets": {"admin_settings": "admin_settings", "office_ip": "ip_menu",
                    "admin_back": "back"},
    },
    "admin_settings": {
        "title": "🔧 Sozlamalar",
        "buttons": {
            "set_hours": texts.BTN_SET_HOURS,
            "back": texts.BTN_BACK,
        },
        "default": [["set_hours"], ["back"]],
        "targets": {"back": "back"},
    },
    "ip_menu": {
        "title": "📡 Ofis IP boshqaruvi",
        "buttons": {
            "office_ip_add": texts.BTN_OFFICE_IP_ADD,
            "office_ip_list": texts.BTN_OFFICE_IP_LIST,
            "office_beacon": texts.BTN_OFFICE_BEACON,
            "back": texts.BTN_BACK,
        },
        "default": [["office_ip_add"], ["office_ip_list"], ["office_beacon"],
                    ["back"]],
        "targets": {"back": "back"},
    },
    "boss_panel": {
        "title": "🏆 Boss panel",
        "buttons": {
            "boss_attendance": texts.BTN_BOSS_ATTENDANCE,
            "admin_tasks": texts.BTN_ADMIN_TASKS,
            "boss_finance": texts.BTN_BOSS_FINANCE,
            "broadcast": texts.BTN_BROADCAST,
            "back": texts.BTN_BACK,
        },
        "default": [["boss_attendance"], ["admin_tasks", "boss_finance"],
                    ["broadcast"], ["back"]],
        "targets": {"boss_finance": "finance_menu", "back": "back"},
    },
    "finance_menu": {
        "title": "💰 Moliya bo'limi",
        "buttons": {
            "income": texts.BTN_FINANCE_INCOME,
            "expense": texts.BTN_FINANCE_EXPENSE,
            "summary": texts.BTN_FINANCE_SUMMARY,
            "excel": texts.BTN_FINANCE_EXCEL,
            "delete": texts.BTN_FINANCE_DELETE,
            "archive": texts.BTN_FINANCE_ARCHIVE,
            "categories": texts.BTN_FINANCE_CATEGORIES,
            "personal_finance": texts.BTN_PERSONAL_FINANCE,
            "back": texts.BTN_BACK,
        },
        "default": [["income", "expense"], ["summary", "excel"], ["delete"],
                    ["archive"], ["categories"], ["personal_finance"],
                    ["back"]],
        "targets": {"personal_finance": "pf_menu", "back": "back"},
    },
    "pf_menu": {
        "title": "📊 Shaxsiy xarajatlarim",
        "buttons": {
            "income": texts.BTN_PF_INCOME,
            "expense": texts.BTN_PF_EXPENSE,
            "summary": texts.BTN_PF_SUMMARY,
            "excel": texts.BTN_PF_EXCEL,
            "delete": texts.BTN_PF_DELETE,
            "archive": texts.BTN_PF_ARCHIVE,
            "categories": texts.BTN_PF_CATEGORIES,
            "back": texts.BTN_BACK,
        },
        "default": [["income", "expense"], ["summary", "excel"], ["delete"],
                    ["archive"], ["categories"], ["back"]],
        "targets": {"back": "back"},
    },
}


def normalize_layout(menu_key: str, layout=None):
    """Joylashuvni xavfsiz holatga keltiradi.

    - reyestrda yo'q yoki takrorlangan kalitlar tashlanadi;
    - bir qatorda ko'pi bilan MAX_ROW_BUTTONS ta tugma;
    - bo'sh qatorlar chiqariladi;
    - reyestrda bor, lekin joylashuvda yo'q tugmalar OXIRIGA qo'shiladi
      (kodga yangi tugma qo'shilganda yo'qolib qolmasligi uchun).
    """
    reg = MENU_REGISTRY[menu_key]
    known = reg["buttons"]
    rows, seen = [], set()
    for row in (layout if layout is not None else reg["default"]):
        cur = []
        for key in row:
            if key not in known or key in seen:
                continue
            seen.add(key)
            cur.append(key)
            if len(cur) == MAX_ROW_BUTTONS:
                rows.append(cur)
                cur = []
        if cur:
            rows.append(cur)
    for key in known:
        if key not in seen:
            rows.append([key])
    return rows


def get_layout(menu_key: str):
    """Bazadagi (yoki standart) joylashuv — har doim normallashtirilgan."""
    return normalize_layout(menu_key, get_menu_layout(menu_key))


def build_menu_kb(menu_key: str, visible_keys=None,
                  overrides=None) -> ReplyKeyboardMarkup:
    """Reyestr + saqlangan joylashuv asosida reply-klaviatura quradi.

    visible_keys — berilsa, faqat shu kalitlar chiqadi (shartli tugmalar:
                   admin, personal_finance va h.k.). Bo'sh qolgan qator tushadi.
    overrides    — {kalit: matn}, tugma matnini almashtirish (pf_menu'dagi
                   ortga tugmasi kirish nuqtasiga qarab o'zgaradi).
    """
    buttons = MENU_REGISTRY[menu_key]["buttons"]
    rows = []
    for row in get_layout(menu_key):
        keys = [k for k in row if visible_keys is None or k in visible_keys]
        if not keys:
            continue
        rows.append([
            KeyboardButton(text=(overrides or {}).get(k, buttons[k]))
            for k in keys
        ])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def main_menu_kb(is_admin: bool = False, is_boss: bool = False,
                 is_bosh_admin: bool = False,
                 has_pf: bool = False) -> ReplyKeyboardMarkup:
    # has_pf — faqat oddiy xodim menyusiga ta'sir qiladi; Boss va Bosh Admin
    # uchun "Shaxsiy xarajatlarim" Moliya bo'limi ichida turadi.
    if is_bosh_admin:
        return build_menu_kb("main_bosh_admin")
    if is_boss:
        return build_menu_kb("main_boss")

    # Oddiy xodim — shartli tugmalar joylashuvdan qat'i nazar filtrlanadi
    visible = {"attendance", "profile", "stats", "tasks", "salary"}
    if has_pf:
        visible.add("personal_finance")
    if is_admin:
        visible.add("admin")
    return build_menu_kb("main_employee", visible_keys=visible)


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
        return build_menu_kb("admin_panel_bosh")
    # Oddiy admin uchun — eski tekis menyu.
    return build_menu_kb("admin_panel")


# ===== Bosh Admin: bo'lim submenyulari =====

def grp_employees_kb() -> ReplyKeyboardMarkup:
    return build_menu_kb("grp_employees")


def grp_attendance_kb() -> ReplyKeyboardMarkup:
    return build_menu_kb("grp_attendance")


def grp_finance_kb() -> ReplyKeyboardMarkup:
    return build_menu_kb("grp_finance")


def grp_control_kb() -> ReplyKeyboardMarkup:
    return build_menu_kb("grp_control")


def ip_menu_kb() -> ReplyKeyboardMarkup:
    """Ofis IP boshqaruvi submenyusi (Bosh Admin)."""
    return build_menu_kb("ip_menu")


def admin_settings_kb() -> ReplyKeyboardMarkup:
    return build_menu_kb("admin_settings")


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
        [InlineKeyboardButton(text="📂 Arxiv (eski oylar)", callback_data="sal_archive"),
         InlineKeyboardButton(text="📜 Audit tarixi", callback_data="sal_audit")],
        [InlineKeyboardButton(text="🔒 Oyni yopish/ochish", callback_data="sal_close_month")],
        [InlineKeyboardButton(text="🚪 Yopish", callback_data="sal_close")],
    ])


def month_close_confirm_kb(year: int, month: int) -> InlineKeyboardMarkup:
    """Tanlangan oyni yopish tasdig'i — oy callback ichida olib yuriladi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, yopish",
                              callback_data=f"sal_cm_yes:{year}:{month}"),
         InlineKeyboardButton(text="❌ Yo'q", callback_data="sal_cm_no")],
    ])


def month_reopen_confirm_kb(year: int, month: int) -> InlineKeyboardMarkup:
    """Tanlangan oyni qayta ochish tasdig'i."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔓 Ha, qayta ochish",
                              callback_data=f"sal_cm_reopen:{year}:{month}"),
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


# ===== Smena normasini o'zgartirish =====

def emp_card_actions_kb(emp_id: int, show_shift_norm: bool = False,
                        back_callback: str = None) -> InlineKeyboardMarkup:
    """Xodim kartochkasi amallari — Boss paneli va Xodimlar bo'limida bir xil ishlatiladi."""
    rows = [
        [InlineKeyboardButton(text="📥 Hodim ma'lumotlari excel hisoboti",
                              callback_data=f"empdata_excel:{emp_id}")],
        [InlineKeyboardButton(text=texts.BTN_EMP_RATE_CHANGE,
                              callback_data=f"empdata_rate:{emp_id}")],
    ]
    # Ish vaqti normasi — faqat Boss/Bosh Admin uchun
    if show_shift_norm:
        rows.append([InlineKeyboardButton(text=texts.BTN_SHIFT_NORM,
                                          callback_data=f"empdata_shnorm:{emp_id}")])
    if back_callback:
        rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=back_callback)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def shift_norm_scope_kb(emp_name: str, pos_name: str = None) -> InlineKeyboardMarkup:
    """Qamrov tanlash: faqat shu xodim yoki butun lavozim (lavozim bo'lsa)."""
    rows = [[InlineKeyboardButton(
        text=texts.BTN_SHIFT_NORM_EMPLOYEE.format(name=emp_name),
        callback_data="shnorm_scope:employee"
    )]]
    if pos_name:
        rows.append([InlineKeyboardButton(
            text=texts.BTN_SHIFT_NORM_POSITION.format(position=pos_name),
            callback_data="shnorm_scope:position"
        )])
    rows.append([InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data="shnorm_scope:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def shift_norm_month_kb(current_month: str) -> InlineKeyboardMarkup:
    """Amal qilish oyi: joriy oyni tezkor tanlash yoki matn bilan boshqa oy kiritish."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=texts.BTN_SHIFT_NORM_CURRENT_MONTH.format(current_month=current_month),
            callback_data=f"shnorm_month:{current_month}"
        )],
        [InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data="shnorm_month:cancel")],
    ])


def shift_norm_reason_kb() -> InlineKeyboardMarkup:
    """Sabab kiritish — ixtiyoriy, o'tkazib yuborish mumkin."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.BTN_SHIFT_NORM_SKIP_REASON, callback_data="shnorm_reason:skip")],
        [InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data="shnorm_reason:cancel")],
    ])


def shift_norm_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="shnorm_confirm:yes"),
         InlineKeyboardButton(text="❌ Bekor qilish", callback_data="shnorm_confirm:no")],
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
    return build_menu_kb("boss_panel")


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
    return build_menu_kb("finance_menu")


def pf_menu_kb(from_finance: bool = False) -> ReplyKeyboardMarkup:
    """Shaxsiy moliya menyusi.

    from_finance — Moliya bo'limi orqali kirilgan (Boss/Bosh Admin): ortga
    tugmasi Moliya menyusiga qaytaradi. Aks holda oddiy BTN_BACK — asosiy menyu.
    """
    overrides = {"back": texts.BTN_PF_BACK_FINANCE} if from_finance else None
    return build_menu_kb("pf_menu", overrides=overrides)


# ===== Universal oy navigatsiyasi (◀️ ▶️) =====

def month_nav_kb(prefix: str, year: int, month: int,
                 extra_rows: list | None = None) -> InlineKeyboardMarkup:
    """Universal oy navigatsiyasi: pastida oldingi/keyingi oy tugmalari.

    Qoidalar:
      - Orqaga maksimal tzutil.NAV_BACK (6) oy (joriy oydan hisoblaganda)
      - Oldinga joriy oydan oshib bo'lmaydi (kelajak oy tugmasi chiqmaydi)
      - Callback formati: {prefix}:{year}:{month}
      - extra_rows — ekranga xos qo'shimcha tugma qatorlari (masalan Excel tugmasi)
    """
    d = tzutil.now()
    cur = d.year * 12 + d.month - 1
    rows = list(extra_rows) if extra_rows else []
    nav = []
    py, pm = tzutil.prev_month(year, month)
    if py * 12 + pm - 1 >= cur - tzutil.NAV_BACK:
        nav.append(InlineKeyboardButton(
            text=f"◀️ {texts.MONTHS_UZ[pm]}",
            callback_data=f"{prefix}:{py}:{pm}"
        ))
    ny, nm = tzutil.next_month(year, month)
    if ny * 12 + nm - 1 <= cur:
        nav.append(InlineKeyboardButton(
            text=f"{texts.MONTHS_UZ[nm]} ▶️",
            callback_data=f"{prefix}:{ny}:{nm}"
        ))
    if nav:
        rows.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def month_excel_kb(prefix: str, year: int, month: int) -> InlineKeyboardMarkup:
    """Excel ekrani: «Yuklab olish» tugmasi + oy navigatsiyasi.

    Yuklab olish callbacki: {prefix}dl:{year}:{month}
    """
    return month_nav_kb(prefix, year, month, extra_rows=[[InlineKeyboardButton(
        text=texts.BTN_MONTH_EXCEL_DL,
        callback_data=f"{prefix}dl:{year}:{month}"
    )]])


def salary_month_pick_kb(prefix: str, months) -> InlineKeyboardMarkup:
    """Ish haqqi yozuvi uchun oy tanlash. months — [(yil, oy, yopiqmi), ...].

    Yopiq oy 🔒 bilan ko'rsatiladi (handler alert beradi).
    Callback: {prefix}:{y}:{m}; bekor: {prefix}:cancel
    """
    rows = [
        [InlineKeyboardButton(
            text=f"{'🔒 ' if closed else ''}{texts.MONTHS_UZ[m]} {y}",
            callback_data=f"{prefix}:{y}:{m}"
        )]
        for y, m, closed in months
    ]
    rows.append([InlineKeyboardButton(
        text=texts.BTN_CANCEL, callback_data=f"{prefix}:cancel"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def month_close_pick_kb(months) -> InlineKeyboardMarkup:
    """Oy yopish uchun oy tanlash. months — [(yil, oy, yopiqmi), ...]."""
    rows = [
        [InlineKeyboardButton(
            text=f"{'🔒 ' if closed else ''}{texts.MONTHS_UZ[m]} {y}",
            callback_data=f"mclose:{y}:{m}"
        )]
        for y, m, closed in months
    ]
    rows.append([InlineKeyboardButton(
        text=texts.BTN_CANCEL, callback_data="sal_cm_no"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ===== Arxiv (o'tgan oylar) =====

def archive_months_kb(prefix: str, months) -> InlineKeyboardMarkup:
    """Oxirgi oylar ro'yxati. prefix — 'pf_arc' yoki 'fin_arc'."""
    rows = [
        [InlineKeyboardButton(
            text=f"{texts.MONTHS_UZ[m]} {y}",
            callback_data=f"{prefix}:{y}-{m:02d}"
        )]
        for y, m in months
    ]
    rows.append([InlineKeyboardButton(
        text=texts.BTN_CANCEL, callback_data=f"{prefix}:cancel"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def archive_excel_kb(prefix: str, year: int, month: int) -> InlineKeyboardMarkup:
    """Tanlangan oy uchun Excel tugmasi. prefix — 'pf_arcx' yoki 'fin_arcx'."""
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text=texts.BTN_ARCHIVE_EXCEL,
        callback_data=f"{prefix}:{year}-{month:02d}"
    )]])


def pf_access_kb(employees) -> InlineKeyboardMarkup:
    """Xodimlar ro'yxati — PF huquqi holati bilan (toggle)."""
    rows = [
        [InlineKeyboardButton(
            text=f"{'✅' if e['pf_access'] else '⬜'} {e['full_name']}",
            callback_data=f"pfacc:{e['id']}"
        )]
        for e in employees
    ]
    rows.append([InlineKeyboardButton(
        text=texts.BTN_CANCEL, callback_data="pfacc:cancel"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def menu_editor_webapp_kb(public_url: str) -> ReplyKeyboardMarkup:
    """Mini App muharririni ochuvchi klaviatura (barcha menyular bitta sahifada).

    ATAYIN KeyboardButton(web_app=...) — inline emas: saqlash
    Telegram.WebApp.sendData orqali ishlaydi, u faqat shu rejimda mavjud.
    """
    from aiogram.types import WebAppInfo
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text=texts.BTN_MENU_EDITOR_OPEN,
                web_app=WebAppInfo(url=f"{public_url}/dashboard/menu-editor")
            )],
            [KeyboardButton(text=texts.BTN_CANCEL)],
        ],
        resize_keyboard=True,
    )


def pf_income_cats_kb(owner_id: int) -> InlineKeyboardMarkup:
    """PF kirim turkumlari — egaga tegishli ro'yxat (bazadan)."""
    rows = [
        [InlineKeyboardButton(
            text=f"{cat['emoji']} {cat['name']}",
            callback_data=f"pf_cat:income:{cat['ckey']}"
        )]
        for cat in get_pf_categories("income", owner_id)
    ]
    rows.append([InlineKeyboardButton(
        text=texts.BTN_CANCEL, callback_data="pf_cat:cancel"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def pf_expense_cats_kb(owner_id: int) -> InlineKeyboardMarkup:
    """PF chiqim turkumlari — egaga tegishli ro'yxat (bazadan)."""
    rows = [
        [InlineKeyboardButton(
            text=f"{cat['emoji']} {cat['name']}",
            callback_data=f"pf_cat:expense:{cat['ckey']}"
        )]
        for cat in get_pf_categories("expense", owner_id)
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
    """O'chirish uchun yozuvlar ro'yxati (bir kun ichidagi — izoh bilan farqlanadi)."""
    rows = []
    for e in entries:
        emoji, name = (pf_category_label(e["category"])
                       or texts.PF_ALL_CATS.get(e["category"], ("📋", e["category"])))
        sign = "➕" if e["entry_type"] == "income" else "➖"
        note = (e["note"] or "").strip()
        extra = f" · {note[:16]}" if note else ""
        text = f"{sign} {e['amount']:,} {emoji}{name}{extra}"
        rows.append([InlineKeyboardButton(
            text=text[:62],
            callback_data=f"pf_del:{e['id']}"
        )])
    rows.append([InlineKeyboardButton(
        text=texts.BTN_CANCEL, callback_data="pf_del:cancel"
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def finance_personal_cats_kb(owner_id: int) -> InlineKeyboardMarkup:
    """Shaxsiy xarajatlar ichki turkumlari (egaga tegishli)."""
    rows = []
    for cat in get_finance_personal_categories(owner_id):
        label = cat["name"].replace("Shaxsiy: ", "")
        rows.append([InlineKeyboardButton(
            text=f"{cat['emoji']} {label}",
            callback_data=f"fin_cat:expense:{cat['ckey']}"
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
        cat_info = finance_category_label(e["category"]) or ("📋", e["category"])
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


def finance_categories_kb(entry_type: str, owner_id: int) -> InlineKeyboardMarkup:
    """Turkum tanlash — egaga tegishli kirim/chiqim ro'yxatlari (bazadan)."""
    rows = []
    for cat in get_finance_categories(entry_type, owner_id):
        rows.append([InlineKeyboardButton(
            text=f"{cat['emoji']} {cat['name']}",
            callback_data=f"fin_cat:{entry_type}:{cat['ckey']}"
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


# ===== Web dashboard =====

def dashboard_link_kb(url: str) -> InlineKeyboardMarkup:
    """Dashboardni brauzerda ochish tugmasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.BTN_DASHBOARD_OPEN, url=url)],
    ])


# ===== Davomat tuzatish so'rovlari =====

def stats_inline_kb() -> InlineKeyboardMarkup:
    """Statistika ostidagi 'tuzatish so'rovi' tugmasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.BTN_FIX_REQUEST, callback_data="fixreq:start")],
    ])


def fixreq_days_kb() -> InlineKeyboardMarkup:
    """Oxirgi 7 kun (bugundan orqaga). Callback: fixreq:day:YYYY-MM-DD"""
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
            text=label, callback_data=f"fixreq:day:{date_str}"
        )])
    rows.append([InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data="fixreq:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def fixreq_type_kb() -> InlineKeyboardMarkup:
    """Muammo turi. Callback: fixreq:type:{in|out|both}"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.FIXREQ_TYPE_IN, callback_data="fixreq:type:in")],
        [InlineKeyboardButton(text=texts.FIXREQ_TYPE_OUT, callback_data="fixreq:type:out")],
        [InlineKeyboardButton(text=texts.FIXREQ_TYPE_BOTH, callback_data="fixreq:type:both")],
        [InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data="fixreq:cancel")],
    ])


def fixreq_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Yuborish", callback_data="fixreq:confirm"),
         InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data="fixreq:cancel")],
    ])


def fixreq_review_kb(req_id: int) -> InlineKeyboardMarkup:
    """Admin uchun tasdiqlash/rad etish. Callback: fixrev:ok|no:{id}"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.FIXREQ_BTN_APPROVE, callback_data=f"fixrev:ok:{req_id}"),
         InlineKeyboardButton(text=texts.FIXREQ_BTN_REJECT, callback_data=f"fixrev:no:{req_id}")],
    ])


