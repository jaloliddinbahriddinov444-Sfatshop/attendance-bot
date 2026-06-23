"""Barcha bot matnlari — O'zbek tilida"""

# ===== Umumiy =====
WELCOME_NEW = (
    "Assalomu alaykum! 👋\n\n"
    "<b>Davomat botiga xush kelibsiz.</b>\n\n"
    "Botdan foydalanish uchun avval ro'yxatdan o'tishingiz kerak."
)

WELCOME_BACK = "Assalomu alaykum, {name}! 👋\n\nAsosiy menyudan kerakli bo'limni tanlang."

NOT_REGISTERED = (
    "❌ Siz hali ro'yxatdan o'tmagansiz.\n\n"
    "Ro'yxatdan o'tish uchun /start buyrug'ini bering."
)

MAX_EMPLOYEES_REACHED = (
    "❌ Bot maksimal xodimlar soniga yetdi ({max}). "
    "Yangi xodim qo'shish uchun admin bilan bog'laning."
)

ACCOUNT_DEACTIVATED = (
    "🚫 <b>Hisobingiz faolsizlantirilgan.</b>\n\n"
    "Botdan foydalanish to'xtatilgan. Savollar bo'lsa admin bilan bog'laning."
)

CANCELLED = "❌ Amal bekor qilindi.\n\nAsosiy menyuga qaytdingiz."

UNKNOWN_COMMAND = "🤔 Tushunmadim. Iltimos, menyudagi tugmalardan foydalaning."

# ===== Ro'yxatdan o'tish =====
REG_START = (
    "📝 <b>Ro'yxatdan o'tish</b>\n\n"
    "Iltimos, F.I.Sh ingizni to'liq yozing:\n\n"
    "<i>Misol: Aliyev Vali Salimovich</i>"
)

REG_NAME_TOO_SHORT = "❌ Ism juda qisqa. Iltimos, to'liq F.I.Sh yozing (kamida 5 ta harf)."

REG_ASK_PHONE = (
    "📱 Endi telefon raqamingizni yuboring.\n\n"
    "Pastdagi <b>«Telefon raqamni yuborish»</b> tugmasini bosing."
)

REG_PHONE_INVALID = "❌ Iltimos, pastdagi tugma orqali raqamingizni yuboring."

REG_ASK_POSITION = (
    "💼 Lavozimingizni yozing:\n\n"
    "<i>Misol: Dasturchi, Buxgalter, Menejer, Sotuvchi</i>"
)

REG_POSITION_TOO_SHORT = "❌ Lavozim nomi juda qisqa. Iltimos, to'liqroq yozing."

REG_ASK_FACE = (
    "🤳 <b>Endi yuzingizning selfisini yuboring</b>\n\n"
    "Bu rasm keyinchalik sizni tanish uchun asos bo'ladi.\n\n"
    "⚠️ <b>Diqqat:</b>\n"
    "• Yorug' joyda turing\n"
    "• Yuzingiz kameraga to'g'ridan-to'g'ri qarasin\n"
    "• Niqob va quyosh ko'zoynagi bo'lmasin\n"
    "• Faqat siz ko'rinishingiz kerak\n\n"
    "📸 <b>Telefonning kamera tugmasi orqali yangi rasm oling</b> "
    "(eski rasm yubormang)"
)

REG_FACE_NOT_DETECTED = (
    "❌ Rasmda yuz topilmadi.\n\n"
    "Iltimos, yuzingiz aniq ko'rinadigan boshqa rasm yuboring."
)

REG_FACE_MULTIPLE = (
    "❌ Rasmda bir nechta yuz topildi.\n\n"
    "Iltimos, faqat <b>o'zingiz</b> ko'rinadigan rasm yuboring."
)

REG_PHOTO_REQUIRED = "❌ Iltimos, rasm yuboring (fayl yoki matn emas)."

REG_SUCCESS = (
    "✅ <b>Tabriklaymiz!</b>\n\n"
    "Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n"
    "Endi davomatni qayd qilishingiz mumkin.\n\n"
    "👤 {name}\n"
    "💼 {position}\n"
    "{admin_note}"
)

ADMIN_BADGE_NOTE = "🛡 <b>Siz administrator sifatida ro'yxatdan o'tdingiz</b>"

# ===== Phase 4: bog'lash + plastik karta =====

# --- Stranger /start: kontakt so'rash ---
LINK_ASK_PHONE = (
    "👋 Assalomu alaykum!\n\n"
    "Botdan foydalanish uchun telefon raqamingizni yuboring — admin sizni "
    "ro'yxatga qo'shgan bo'lsa, avtomatik aniqlanasiz.\n\n"
    "Pastdagi <b>«Telefon raqamni yuborish»</b> tugmasini bosing."
)

LINK_NOT_FOUND = (
    "🚫 <b>Ruxsat yo'q.</b>\n\n"
    "Sizning raqamingiz ro'yxatda yo'q. Avval admin sizni qo'shishi kerak.\n\n"
    "Adminga quyidagi Telegram ID raqamingizni ayting:\n"
    "🆔 <code>{tg_id}</code>"
)

# --- Karta ma'lumotlari (ro'yxatdan o'tish oxirida) ---
CARD_ASK_NUMBER = (
    "💳 <b>Plastik karta ma'lumotlari</b>\n\n"
    "Ish haqqi o'tkaziladigan karta raqamini yuboring (16 ta raqam).\n\n"
    "<i>Misol: 0000 1212 2412 3040</i>"
)

CARD_INVALID_NUMBER = "❌ Karta raqami 16 ta raqamdan iborat bo'lishi kerak. Qayta kiriting."

CARD_ASK_HOLDER = (
    "👤 Kartada yozilgan ism-familiyani yozing:\n\n"
    "<i>Misol: ALIYEV KAMRON</i>"
)

CARD_INVALID_HOLDER = "❌ Kartadagi ism-familiyani to'liq yozing."

REG_SUCCESS_WITH_CARD = (
    "✅ <b>Tabriklaymiz!</b>\n\n"
    "Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n"
    "Endi davomatni qayd qilishingiz mumkin.\n\n"
    "💳 Karta: {card}\n"
    "{admin_note}"
)

# --- Karta yangilash (Profil orqali) ---
BTN_PROFILE_CARD = "💳 Karta ma'lumotlari"
CARD_UPDATE_ASK_NUMBER = (
    "💳 <b>Karta ma'lumotlarini yangilash</b>\n\n"
    "Yangi karta raqamini yuboring (16 ta raqam).\n\n"
    "<i>Misol: 0000 1212 2412 3040</i>"
)
CARD_UPDATE_SUCCESS = (
    "✅ Karta ma'lumotlari saqlandi.\n\n"
    "💳 {card}"
)


def format_card(number: str, holder: str = "") -> str:
    """Karta raqamini 4 talab ko'rsatish + qavsda egasi ismi.
    Masalan: '0000 1212 2412 3040 (ALIYEV KAMRON)'."""
    digits = "".join(ch for ch in (number or "") if ch.isdigit())
    if not digits:
        return PROFILE_CARD_NONE
    grouped = " ".join(digits[i:i + 4] for i in range(0, len(digits), 4))
    holder = (holder or "").strip()
    return f"{grouped} ({holder})" if holder else grouped

# ===== Asosiy menyu =====
MAIN_MENU = "🏠 <b>Asosiy menyu</b>\n\nKerakli bo'limni tanlang:"

BTN_ATTENDANCE = "📋 Davomat"
BTN_PROFILE = "👤 Profilim"
BTN_STATS = "📊 Statistikam"
BTN_ADMIN = "⚙️ Admin panel"
BTN_BACK = "⬅️ Ortga"
BTN_CANCEL = "❌ Bekor qilish"
BTN_SHARE_PHONE = "📱 Telefon raqamni yuborish"
BTN_SHARE_LOCATION = "📍 Lokatsiyani yuborish"

# ===== Davomat =====
ATTENDANCE_MENU = (
    "📋 <b>Davomat bo'limi</b>\n\n"
    "Bugungi holatingiz: {status}\n\n"
    "Qaysi amalni tanlaysiz?"
)

STATUS_NOT_CHECKED = "❌ Bugun belgilanmagan"
STATUS_CHECKED_IN = "🟢 Keldim: {time}"
STATUS_CHECKED_OUT = "🔴 Ketdim: {time}"

BTN_CHECK_IN = "🟢 Keldim"
BTN_CHECK_OUT = "🔴 Ketdim"

ASK_VERIFY_AND_SELFIE = (
    "📸 <b>Wi-Fi va selfi tekshiruvi</b>\n\n"
    "Quyidagi tugmani bosing — brauzerda sahifa ochiladi.\n"
    "Sahifada <b>kamera</b> ochiladi — selfi oling.\n\n"
    "📶 Sahifa ochilishi = Wi-Fi tasdiqlangan\n"
    "🤳 Selfi = yuzingiz tekshiriladi\n\n"
    "⚠️ Sahifa faqat <b>ishxona Wi-Fi</b>'ida ochiladi."
)

BTN_WIFI_CONFIRMED = "✅ Tasdiqladim"

WIFI_TAP_CONFIRM = (
    "☝️ Yuqoridagi tugmani bosib, <b>selfi</b> oling.\n\n"
    "Sahifada <b>«✅ Tasdiqlandi»</b> chiqgandan keyin\n"
    "shu yerda <b>«✅ Tasdiqladim»</b> bosing."
)

WIFI_NOT_VERIFIED_YET = (
    "❌ <b>Wi-Fi hali tasdiqlanmagan.</b>\n\n"
    "Yuqoridagi havolani bosing.\n"
    "Agar sahifa ochilmasa — ishxona Wi-Fi'iga ulaning."
)

FACE_NOT_VERIFIED_YET = (
    "❌ <b>Selfi hali olinmagan.</b>\n\n"
    "Sahifada 📸 tugmani bosib selfi oling.\n"
    "Yuzingiz tekshirilgach «✅ Tasdiqlandi» chiqadi."
)

TOKEN_EXPIRED = (
    "⏰ <b>Havola muddati tugadi.</b>\n\n"
    "Qaytadan «Keldim» yoki «Ketdim» bosing."
)

WIFI_TOO_SHORT = "❌ Wi-Fi nomi juda qisqa. To'g'ri nomni kiriting."

ASK_SELFIE = (
    "🤳 <b>Hozirgi selfingizni yuboring</b>\n\n"
    "📸 Telefonning kamera tugmasi orqali <b>yangi rasm oling</b>.\n\n"
    "⚠️ Eski rasm yuborilsa, tizim aniqlaydi va rad etadi."
)

SELFIE_REQUIRED = "❌ Iltimos, rasm yuboring."

PHOTO_ALREADY_USED = (
    "❌ <b>Bu rasm avval ishlatilgan!</b>\n\n"
    "Galereyadan eski rasm yuborib bo'lmaydi.\n"
    "Iltimos, <b>hozir yangi selfi</b> oling 📸"
)

SELFIE_NO_FACE = "❌ Rasmda yuz topilmadi. Yuzingiz aniq ko'rinadigan rasm yuboring."

SELFIE_NO_MATCH = (
    "❌ <b>Yuz mos kelmadi!</b>\n\n"
    "Rasmdagi yuz sizning ro'yxatdagi rasmingizga mos emas.\n\n"
    "Iltimos, o'zingizning aniq rasmingizni yangidan oling."
)

CHECK_IN_SUCCESS = (
    "✅ <b>Ishga kelganingiz qayd etildi!</b>\n\n"
    "🕐 Vaqt: <b>{time}</b>\n"
    "📶 Wi-Fi: ✅ tasdiqlangan\n"
    "👤 Yuz mosligi: {face_score:.1%}\n"
    "{late_warning}"
)

CHECK_OUT_SUCCESS = (
    "✅ <b>Ishdan ketganingiz qayd etildi!</b>\n\n"
    "🕐 Vaqt: <b>{time}</b>\n"
    "⏱ Bugun ishlagan vaqt: <b>{worked}</b>\n"
    "📶 Wi-Fi: ✅ tasdiqlangan"
)

WIFI_OK = "✅ tasdiqlangan"
WIFI_WRONG = "❌ tasdiqlanmagan"

LATE_WARNING = "\n⏰ <b>Eslatma:</b> Siz {minutes} daqiqaga kechikdingiz"

ALREADY_CHECKED_IN_TODAY = (
    "ℹ️ Siz bugun allaqachon ishga kelganingizni qayd qilgansiz.\n\n"
    "Soat: <b>{time}</b>"
)

NEED_CHECK_IN_FIRST = (
    "⚠️ Siz hali bugun <b>Keldim</b> deb belgilamagansiz.\n\n"
    "Avval kelganingizni qayd qiling."
)

ALREADY_CHECKED_OUT = (
    "ℹ️ Siz bugun allaqachon ishdan ketganingizni qayd qilgansiz.\n\n"
    "Soat: <b>{time}</b>"
)

# ===== Profil =====
PROFILE_INFO = (
    "👤 <b>Mening profilim</b>\n\n"
    "📝 F.I.Sh: {name}\n"
    "📱 Telefon: <code>{phone}</code>\n"
    "💼 Lavozim: {position}\n"
    "💳 Karta: {card}\n"
    "📅 Ro'yxatdan o'tgan: {registered}\n"
    "{admin_badge}"
)

PROFILE_CARD_NONE = "<i>belgilanmagan</i>"

ADMIN_BADGE = "🛡 <b>Status:</b> Administrator"

# ===== Statistika =====
STATS_HEADER = (
    "📊 <b>{month} {year} oyi statistikasi</b>\n\n"
    "✅ Kelgan kunlar: <b>{days}</b>\n"
    "⏰ Kechikishlar: <b>{late}</b>\n"
    "🕒 O'rtacha ish vaqti: <b>{avg}</b>\n\n"
    "<b>Kunma-kun:</b>\n{details}"
)

NO_STATS = "📊 Bu oy uchun ma'lumot topilmadi."

# ===== Admin panel =====
ADMIN_MENU = "⚙️ <b>Admin panel</b>\n\nKerakli amalni tanlang:"

NO_PERMISSION = "🚫 Sizda admin huquqlari yo'q."

BTN_ADMIN_LIST = "👥 Xodimlar ma'lumotlari"
BTN_ADMIN_REMOVE = "❌ Xodim o'chirish"
BTN_ADMIN_PROMOTE = "👑 Admin tayinlash"
BTN_ADMIN_TODAY = "📅 Bugungi hisobot"
BTN_ADMIN_SETTINGS = "🏢 Ishxona sozlamalari"
BTN_ADMIN_EXPORT = "📊 Excel hisobot"
BTN_ADMIN_EMP_EXCEL = "📋 Xodimlar ish haqqi (Excel)"

# ===== Bosh Admin: bo'limlarga guruhlash (faqat bosh_admin menyusi) =====
# Asosiy admin paneldagi tugmalar bo'limlarga yig'ildi. Har bo'lim bosilganda
# alohida submenyu ochiladi; "⬅️ Admin panel" submenyudan panelga qaytaradi.
BTN_GRP_EMPLOYEES = "👥 Xodimlar"
BTN_GRP_ATTENDANCE = "📅 Davomat"
BTN_GRP_FINANCE = "💰 Moliya"
BTN_GRP_CONTROL = "⚙️ Boshqaruv"
BTN_ADMIN_BACK = "⬅️ Admin panel"

GRP_EMPLOYEES_HEADER = "👥 <b>Xodimlar</b>\n\nKerakli amalni tanlang:"
GRP_ATTENDANCE_HEADER = "📅 <b>Davomat</b>\n\nKerakli amalni tanlang:"
GRP_FINANCE_HEADER = "💰 <b>Moliya</b>\n\nKerakli amalni tanlang:"
GRP_CONTROL_HEADER = "⚙️ <b>Boshqaruv</b>\n\nKerakli amalni tanlang:"

# ===== Phase 4: Admin xodim qo'shish =====
BTN_ADMIN_ADD_EMPLOYEE = "➕ Xodim qo'shish"

ADD_EMP_ASK_NAME = (
    "➕ <b>Yangi xodim qo'shish</b>\n\n"
    "Xodimning to'liq F.I.Sh ini yozing:\n\n"
    "<i>Misol: Aliyev Vali Salimovich</i>"
)
ADD_EMP_NAME_TOO_SHORT = "❌ Ism juda qisqa. To'liq F.I.Sh yozing (kamida 5 ta harf)."
ADD_EMP_ASK_PHONE = (
    "📱 Xodimning telefon raqamini yozing:\n\n"
    "<i>Misol: +998 90 123 45 67</i>"
)
ADD_EMP_PHONE_INVALID = "❌ Telefon raqami noto'g'ri. Kamida 9 ta raqam bo'lishi kerak."
ADD_EMP_ASK_POSITION = (
    "💼 Xodimning lavozimini yozing:\n\n"
    "<i>Misol: Sotuvchi, Menejer, Buxgalter</i>"
)
ADD_EMP_POSITION_TOO_SHORT = "❌ Lavozim nomi juda qisqa."
ADD_EMP_CONFIRM = (
    "❓ <b>Tasdiqlang</b>\n\n"
    "👤 F.I.Sh: {name}\n"
    "📱 Telefon: <code>{phone}</code>\n"
    "💼 Lavozim: {position}\n\n"
    "Qo'shilsinmi?"
)
ADD_EMP_ALREADY_ACTIVE = (
    "⚠️ Bu telefon allaqachon faol xodim <b>{name}</b> ga tegishli.\n"
    "Qo'shilmadi."
)
ADD_EMP_ADDED = (
    "✅ Xodim qo'shildi: <b>{name}</b> (<code>{phone}</code>).\n\n"
    "U botga <b>/start</b> bersa, telefoni orqali aniqlanib selfi va karta "
    "ma'lumotlari so'raladi."
)
ADD_EMP_UPDATED = (
    "✅ Mavjud (hali bog'lanmagan) yozuv yangilandi: <b>{name}</b> "
    "(<code>{phone}</code>).\n\n"
    "U botga <b>/start</b> berishi kutilmoqda."
)
ADD_EMP_REACTIVATED = (
    "✅ Eski xodim qayta jonlantirildi: <b>{name}</b> (<code>{phone}</code>).\n"
    "Davomat tarixi saqlandi."
)
ADD_EMP_LIMIT = (
    "❌ Xodimlar soni maksimal chegaraga yetdi ({max}). "
    "Yangi xodim qo'shib bo'lmaydi."
)

ADMIN_INVITE_LINK = (
    "➕ <b>Yangi xodim qo'shish</b>\n\n"
    "Xodimga quyidagi havolani yuboring:\n"
    "🔗 https://t.me/{bot_username}\n\n"
    "Xodim botga <b>/start</b> bersa, ro'yxatdan o'tish jarayoni boshlanadi.\n\n"
    "ℹ️ Hozir botda <b>{count}/{max}</b> xodim ro'yxatdan o'tgan."
)

EMPLOYEES_LIST_HEADER = "📋 <b>Xodimlar ro'yxati ({count}/{max})</b>\n\n"
EMPLOYEE_ITEM = "{idx}. {admin_icon} <b>{name}</b>\n   💼 {position}\n   📱 <code>{phone}</code>\n\n"

ADMIN_REMOVE_PROMPT = "❌ <b>Xodim o'chirish</b>\n\nO'chirilishi kerak bo'lgan xodimni tanlang:"
ADMIN_REMOVE_CONFIRM = (
    "❓ Haqiqatan ham <b>{name}</b> ni o'chirmoqchimisiz?\n\n"
    "Xodim ma'lumotlari saqlanib qoladi (faqat faolsizlanadi)."
)
ADMIN_REMOVE_DONE = "✅ <b>{name}</b> ro'yxatdan o'chirildi."

ADMIN_PROMOTE_PROMPT = "👑 <b>Admin tayinlash</b>\n\nAdmin huquqlarini berish/olib tashlashni tanlang:"
ADMIN_PROMOTE_DONE = "✅ {name} ning admin huquqlari yangilandi."

ADMIN_TODAY_HEADER = "📅 <b>Bugungi hisobot</b>\n📆 {date}\n\n"
ADMIN_TODAY_ITEM_PRESENT = "✅ <b>{name}</b>\n   🟢 Keldi: {in_time}\n   {out_line}{wifi_warn}\n"
ADMIN_TODAY_ITEM_ABSENT = "❌ <b>{name}</b> — kelmagan\n"
OUT_LINE_PRESENT = "🔴 Ketdi: {out_time}\n   "
OUT_LINE_ABSENT = ""
WIFI_WARN = "⚠️ Wi-Fi nomi mos emas edi\n"

ADMIN_SETTINGS_VIEW = (
    "🏢 <b>Ishxona sozlamalari</b>\n\n"
    "📶 Wi-Fi tekshiruv serveri: <code>http://{server_ip}:9090</code>\n"
    "🕐 Ish vaqti: <b>{start} — {end}</b>\n\n"
    "O'zgartirish uchun tugmani bosing:"
)

BTN_SET_HOURS = "🕐 Ish vaqtini o'zgartirish"

ADMIN_SET_WORK_START = "🕐 Ish boshlanish vaqtini yozing (masalan, 09:00):"
ADMIN_SET_WORK_END = "🕐 Ish tugash vaqtini yozing (masalan, 18:00):"
ADMIN_TIME_INVALID = "❌ Vaqt formati noto'g'ri. Misol: 09:00"
ADMIN_HOURS_DONE = "✅ Ish vaqti saqlandi: <b>{start} — {end}</b>"

ADMIN_NOTIFY_WIFI_MISMATCH = (
    "⚠️ <b>Wi-Fi tasdiqlanmadi</b>\n\n"
    "👤 Xodim: {name}\n"
    "🕐 Vaqt: {time}\n\n"
    "Xodim ishxona Wi-Fi'iga ulanmagan holda davomat qayd qilishga urindi."
)

ADMIN_NOTIFY_FACE_FAIL = (
    "🚨 <b>Yuz mos kelmadi</b>\n\n"
    "👤 Xodim: {name}\n"
    "👤 Mosligi: {score:.1%}\n"
    "🕐 Vaqt: {time}"
)

# Oy nomlari
MONTHS_UZ = {
    1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
    5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
    9: "Sentabr", 10: "Oktabr", 11: "Noyabr", 12: "Dekabr"
}

# ===== Admin davomat tahrirlash =====
BTN_ADMIN_ATT_EDIT = "📝 Davomatni tahrirlash"

# Hafta kunlari — 0=Dushanba, 6=Yakshanba (datetime.weekday() bilan mos)
WEEKDAYS_UZ = [
    "Dushanba", "Seshanba", "Chorshanba", "Payshanba",
    "Juma", "Shanba", "Yakshanba"
]

ADMIN_ATT_SELECT_EMPLOYEE = "📝 <b>Davomat tahrirlash</b>\n\nXodimni tanlang:"

ADMIN_ATT_SELECT_DAY = (
    "📅 <b>{name}</b>\n\n"
    "Qaysi kunni tahrirlaysiz? (oxirgi 7 kun)"
)

ADMIN_ATT_DAY_ACTIONS = (
    "📝 <b>{name}</b> — {date} ({weekday})\n\n"
    "<b>Hozirgi yozuvlar:</b>\n{records}\n\n"
    "Qaysi amalni bajarasiz?"
)

ADMIN_ATT_DAY_RECORD_LINE = "{emoji} {time} ({label})\n"
ADMIN_ATT_DAY_NO_RECORDS = "<i>Hozircha yozuv yo'q</i>"

ADMIN_ATT_MONTH_CLOSED = (
    "🔒 <b>{month_name} {year}</b> oyi yopilgan — bu oyga davomat "
    "o'zgartirib bo'lmaydi.\n\n"
    "Avval Bosh Admin oyni qayta ochishi kerak."
)
ADMIN_ATT_MONTH_CLOSED_ALERT = (
    "🔒 {month_name} {year} oyi yopilgan — o'zgartirib bo'lmaydi."
)

ADMIN_ATT_ENTER_TIME = (
    "🕐 <b>{name}</b> — {date} ({weekday})\n"
    "{action}\n\n"
    "Vaqtni kiriting (masalan, <code>09:15</code>):"
)

ADMIN_ATT_SAVED = (
    "✅ <b>{name}</b> — {date} ({weekday})\n"
    "{action} soat <b>{time}</b> da qayd etildi."
)

ADMIN_ATT_RESET_DONE = (
    "🗑 <b>{name}</b> — {date} ({weekday})\n"
    "Davomat yozuvlari tozalandi.\n\n"
    "O'chirilgan yozuvlar: <b>{count}</b> ta"
)

# ===== Ish haqqi =====
BTN_SALARY = "💰 Ish haqqim"
BTN_ADMIN_RATES = "💵 Stavkalarni belgilash"
BTN_EMP_RATE_CHANGE = "💰 Hodim ish haqqini o'zgartirish"

EMP_RATE_CHANGE_PROMPT = (
    "💰 <b>{name}</b> — kunlik ish haqqini o'zgartirish\n\n"
    "📋 Lavozim: <b>{position}</b>\n"
    "⏱ Ish soati: <b>{hours} soat/kun</b>\n"
    "📊 Tavsiya etilgan diapazon: <b>{min:,} – {max:,} so'm/kun</b>\n\n"
    "Hozirgi stavka: <b>{current:,} so'm/kun</b>\n\n"
    "Yangi kunlik stavkani kiriting (faqat son):"
)

EMP_RATE_CHANGE_NO_POSITION = (
    "⚠️ <b>{name}</b> uchun lavozim hali belgilanmagan.\n\n"
    "Avval <b>Lavozimlar → Xodimga lavozim berish</b> orqali lavozim belgilang."
)

EMP_RATE_CHANGE_INVALID = "❌ Iltimos, to'g'ri musbat son kiriting (masalan: <code>220000</code>)"

EMP_RATE_CHANGE_SAVED = (
    "✅ <b>{name}</b> ish haqqi yangilandi!\n\n"
    "📋 Lavozim: <b>{position}</b>\n"
    "💰 Yangi kunlik stavka: <b>{rate:,} so'm/kun</b>\n\n"
    "<i>Joriy oy hisobi avtomatik qayta hisoblandi.</i>"
)

EMP_RATE_CHANGE_NOTIFY = (
    "💰 <b>Kunlik ish haqqingiz yangilandi</b>\n\n"
    "📋 Lavozim: <b>{position}</b>\n"
    "💰 Yangi kunlik stavka: <b>{rate:,} so'm/kun</b>\n\n"
    "<i>Joriy oy hisobi avtomatik ravishda yangi stavka asosida hisoblanadi.</i>"
)

SALARY_NO_RATE = (
    "💰 <b>Mening ish haqqim</b>\n\n"
    "⚠️ Sizning soatbay stavkangiz hali belgilanmagan.\n"
    "Iltimos, admin bilan bog'laning."
)

SALARY_HEADER = (
    "💰 <b>Mening ish haqqim — {month} {year}</b>\n\n"
    "🕐 Ishlangan soat: <b>{hours}s {minutes}d</b>\n"
    "💵 Stavka: <b>{rate:,} so'm/soat</b>\n"
    "━━━━━━━━━━━━━━━━━\n"
    "📊 <b>Hisob-kitob:</b>\n\n"
    "🕐 Soatbay ish haqqi: <b>+{base:,} so'm</b>\n"
    "💸 Avanslar: <b>−{avans:,} so'm</b>\n"
    "⚠️ Jarimalar: <b>−{jarima:,} so'm</b>\n"
    "⭐ Mukofotlar: <b>+{mukofot:,} so'm</b>\n"
    "🎁 Bonuslar: <b>+{bonus:,} so'm</b>\n"
    "🛒 Mahsulot xaridi: <b>−{mahsulot:,} so'm</b>\n"
    "━━━━━━━━━━━━━━━━━\n"
    "💰 <b>Jami: {total:,} so'm</b>"
)

# Admin: stavka belgilash
ADMIN_RATES_PROMPT = "💵 <b>Soatbay stavka belgilash</b>\n\nXodimni tanlang:"

ADMIN_RATE_ENTER = (
    "💵 <b>{name}</b> uchun stavka\n\n"
    "Hozirgi stavka: <b>{current:,} so'm/soat</b>\n\n"
    "Yangi stavkani kiriting (faqat son, masalan: <code>25000</code>):"
)

ADMIN_RATE_INVALID = "❌ Iltimos, to'g'ri son kiriting (masalan: 25000)"
ADMIN_RATE_SAVED = "✅ <b>{name}</b> uchun stavka belgilandi: <b>{rate:,} so'm/soat</b>"

# Ish haqqi kategoriyalari: (emoji, nom, belgi)
SALARY_TYPES = {
    "avans": ("💸", "Avans", "−"),
    "jarima": ("⚠️", "Jarima", "−"),
    "mukofot": ("⭐", "Mukofot", "+"),
    "bonus": ("🎁", "Bonus", "+"),
    "mahsulot": ("🛒", "Mahsulot xaridi", "−"),
}

# ===== Admin: Ish haqqi yozuvi qo'shish/bekor qilish =====
BTN_ADMIN_SALARY = "💼 Ish haqqi yozuvi"

SALARY_ADMIN_MENU = "💼 <b>Ish haqqi boshqaruvi</b>\n\nQuyidagi amallardan birini tanlang:"

SALARY_ADD_CHOOSE_EMPLOYEE = "👤 <b>Yozuv qo'shish</b>\n\nXodimni tanlang:"

SALARY_ADD_CHOOSE_TYPE = "📋 <b>{name}</b>\n\nKategoriyani tanlang:"

SALARY_ADD_AMOUNT = (
    "{emoji} <b>{type_name}</b> — {name}\n\n"
    "Summani so'mda kiriting (faqat son, masalan: <code>500000</code>):"
)

SALARY_ADD_REASON = (
    "{emoji} <b>{type_name}</b> — {name}\n"
    "Summa: <b>{amount:,} so'm</b>\n\n"
    "Sababni kiriting (masalan: 'Bayram uchun avans'):"
)

SALARY_ADD_CONFIRM = (
    "⚠️ <b>Tasdiqlash kerak</b>\n\n"
    "{emoji} {type_name}\n"
    "Xodim: <b>{name}</b>\n"
    "Summa: <b>{amount:,} so'm</b>\n"
    "Sabab: {reason}\n\n"
    "Bu katta summa. Tasdiqlaysizmi?"
)

SALARY_AMOUNT_INVALID = "❌ Iltimos, to'g'ri son kiriting (masalan: 500000)"
SALARY_REASON_SHORT = "❌ Sabab juda qisqa. Kamida 3 ta belgi."

SALARY_ADD_SAVED = (
    "✅ <b>Saqlandi</b>\n\n"
    "{emoji} {type_name}\n"
    "Xodim: <b>{name}</b>\n"
    "Summa: <b>{amount:,} so'm</b>\n"
    "Sabab: {reason}"
)

SALARY_CANCEL_CHOOSE_EMPLOYEE = "❌ <b>Yozuvni bekor qilish</b>\n\nXodimni tanlang:"
SALARY_CANCEL_NO_ENTRIES = "ℹ️ <b>{name}</b> uchun bu oy faol yozuv yo'q."
SALARY_CANCEL_CHOOSE_ENTRY = "❌ <b>{name}</b>\n\nBekor qilinadigan yozuvni tanlang:"

SALARY_CANCEL_REASON = (
    "❌ <b>Bekor qilish</b>\n\n"
    "{emoji} {type_name}: <b>{amount:,} so'm</b>\n"
    "Asl sabab: {reason}\n\n"
    "Endi bekor qilish sababini yozing:"
)

SALARY_CANCEL_DONE = (
    "✅ <b>Bekor qilindi</b>\n\n"
    "{emoji} {type_name}: <b>{amount:,} so'm</b>\n"
    "Bekor qilish sababi: {cancel_reason}"
)

# Bildirishnomalar — xodimga
NOTIFY_SALARY_ADDED = (
    "{emoji} <b>Sizga yangi ish haqqi yozuvi qo'shildi</b>\n\n"
    "Turi: <b>{type_name}</b>\n"
    "Summa: <b>{sign}{amount:,} so'm</b>\n"
    "Sabab: {reason}\n\n"
    "Batafsil: 💰 <b>Ish haqqim</b> tugmasi"
)

NOTIFY_SALARY_CANCELLED = (
    "❌ <b>Ish haqqi yozuvi bekor qilindi</b>\n\n"
    "{emoji} {type_name}: <b>{amount:,} so'm</b>\n"
    "Bekor qilish sababi: {cancel_reason}\n\n"
    "Batafsil: 💰 <b>Ish haqqim</b> tugmasi"
)

SALARY_DETAILS_HEADER = "\n\n━━━━━━━━━━━━━━━━━\n📋 <b>Yozuvlar tafsiloti:</b>"

SALARY_DETAILS_EMPTY = "\n\n━━━━━━━━━━━━━━━━━\nℹ️ <i>Bu oy uchun yozuvlar yo'q.</i>"

SALARY_DETAIL_LINE = (
    "\n\n{date} • {emoji} <b>{type_name}</b>: {sign}{amount:,} so'm"
    "\n💬 <i>{reason}</i>"
)

# ===== Phase 3: Hisobot, Audit, Oy yopish =====

# Salary submenu (kengaytirilgan)
SAL_REPORT_GENERATING = "⏳ Excel hisobot tayyorlanmoqda..."
SAL_REPORT_DONE = "✅ <b>{month} {year}</b> oyi uchun ish haqqi hisoboti tayyor."

AUDIT_HEADER = "📜 <b>Audit tarixi — {month} {year}</b>\nSo'nggi {limit} ta yozuv:"
AUDIT_EMPTY = "ℹ️ Bu oy uchun yozuvlar yo'q."
AUDIT_LINE = (
    "\n━━━━━━━━━━\n"
    "📅 <b>{date}</b>\n"
    "{emoji} <b>{type_name}</b>: <b>{sign}{amount:,} so'm</b>\n"
    "👤 Xodim: <i>{employee}</i>\n"
    "👨‍💼 Qo'shgan: <i>{creator}</i>\n"
    "💬 Sabab: <i>{reason}</i>"
)
AUDIT_CANCELLED = "\n❌ <b>BEKOR QILINGAN</b> ({canceller})\n   Sabab: <i>{cancel_reason}</i>"

MONTH_CLOSE_CONFIRM = (
    "🔒 <b>Oy yopish</b>\n\n"
    "<b>{month} {year}</b> oyini yopmoqchimisiz?\n\n"
    "⚠️ Yopilgandan keyin:\n"
    "• Yangi yozuv qo'sha olmaysiz\n"
    "• Eski yozuvlarni bekor qila olmaysiz\n"
    "• Soatbay vaqtlar va xulosalar saqlanadi\n\n"
    "Davom etamizmi?"
)

MONTH_CLOSE_DONE = "✅ <b>{month} {year}</b> oyi yopildi."
MONTH_REOPEN_DONE = "✅ <b>{month} {year}</b> oyi qayta ochildi."

MONTH_BLOCKED = (
    "🔒 <b>{month} {year}</b> oyi yopilgan.\n"
    "Bu oy uchun yozuvlarni o'zgartirib bo'lmaydi."
)

MONTH_ALREADY_CLOSED = "ℹ️ Bu oy allaqachon yopilgan. Qayta ochaymi?"


# ===== Vazifalar (Phase 2) =====

# Tugmalar
BTN_TASKS = "📝 Vazifalarim"
BTN_ADMIN_TASKS = "📝 Vazifa berish"
BTN_TASK_SKIP_DEADLINE = "⏭ Muddatsiz"
BTN_TASK_SKIP_DESCRIPTION = "⏭ Izohsiz"

# Xodim oynasi
TASKS_EMPTY = "📭 Sizda hozirda vazifalar yo'q."
TASKS_HEADER = "📝 <b>Sizning vazifalaringiz</b>\n\nAktivlari yuqorida turadi. Tugatish uchun pastdagi tugmalarni bosing."
TASK_LINE_OPEN = "\n━━━━━━━━━━\n🟡 <b>{title}</b>\n👨‍💼 Tayinlagan: <i>{by}</i>\n📅 Yaratilgan: <i>{created}</i>{deadline}{desc}"
TASK_LINE_DONE = "\n━━━━━━━━━━\n✅ <s>{title}</s>\n📅 Tugatilgan: <i>{completed}</i>"
TASK_LINE_CANCELLED = "\n━━━━━━━━━━\n❌ <s>{title}</s> (bekor qilingan)"
TASK_DEADLINE_FRAGMENT = "\n⏰ Muddat: <i>{deadline}</i>"
TASK_DESC_FRAGMENT = "\n💬 {desc}"
TASK_MARK_DONE_BTN = "✅ Tugatdim"
TASK_COMPLETED_OK = "✅ Vazifa tugatilgan deb belgilandi."
TASK_ALREADY_DONE = "ℹ️ Bu vazifa allaqachon yopilgan."

# Admin/Boss vazifa berish
ADMIN_TASK_PICK_EMP = "👤 Kim uchun vazifa beramiz? Xodimni tanlang:"
ADMIN_TASK_ASK_TITLE = "📝 <b>{name}</b> uchun vazifa.\n\nVazifa sarlavhasini yozing (qisqa va aniq):"
ADMIN_TASK_TITLE_SHORT = "⚠️ Sarlavha juda qisqa. Kamida 3 belgi."
ADMIN_TASK_ASK_DESC = "💬 Izoh qo'shasizmi? (ixtiyoriy — kerak bo'lmasa pastdagi tugmani bosing)"
ADMIN_TASK_ASK_DEADLINE = "⏰ Muddat qo'shasizmi?\n\nFormat: <code>DD.MM</code> yoki <code>DD.MM HH:MM</code> (masalan: <code>05.06</code> yoki <code>05.06 18:00</code>).\n\nMuddatsiz bo'lsa pastdagi tugmani bosing."
ADMIN_TASK_DEADLINE_INVALID = "⚠️ Sana noto'g'ri. Format: <code>DD.MM</code> yoki <code>DD.MM HH:MM</code>."
ADMIN_TASK_SAVED = (
    "✅ Vazifa saqlandi.\n\n"
    "👤 Kim uchun: <b>{name}</b>\n"
    "📝 Sarlavha: <b>{title}</b>{deadline}{desc}"
)
ADMIN_TASK_NOTIFY_EMP = (
    "📝 <b>Yangi vazifa</b>\n\n"
    "<b>{title}</b>\n"
    "👨‍💼 Tayinlagan: <i>{by}</i>{deadline}{desc}\n\n"
    "«📝 Vazifalarim» bo'limidan ko'rishingiz mumkin."
)

# Ketdim — vazifa savoli
CHECKOUT_TASKS_PROMPT = (
    "📝 <b>Ketishdan oldin:</b> sizda <b>{count}</b> ta tugatilmagan vazifa bor.\n\n"
    "{list}\n\n"
    "Hammasini tugatdingizmi?"
)
CHECKOUT_TASKS_SHORT_LINE = "• {title}"
CHECKOUT_TASKS_DONE_OK = "✅ Vazifalar tugatilgan deb belgilandi. Yaxshi ish kuni bo'ldi!"
CHECKOUT_TASKS_NOT_DONE = "📌 Tugatilmagan vazifalar qayd qilindi. Tayinlovchiga xabar berildi."

# Tayinlovchi uchun bildirishnoma
TASK_NOTIFY_DONE = (
    "✅ <b>Vazifa tugatildi</b>\n\n"
    "<b>{title}</b>\n"
    "👤 Xodim: <i>{employee}</i>\n"
    "📅 Tugatildi: <i>{when}</i>"
)
TASK_NOTIFY_SKIPPED = (
    "📌 <b>Vazifa tugatilmadi</b>\n\n"
    "<b>{title}</b>\n"
    "👤 Xodim: <i>{employee}</i>\n"
    "📅 Sana: <i>{when}</i>\n"
    "ℹ️ Vazifa keyingi kunga qoldi."
)

# Profilda tugatilmagan vazifalar (admin/boss xodimni tekshirganda)
PROFILE_OPEN_TASKS_HEADER = "\n\n📝 <b>Tugatilmagan vazifalar:</b>"
PROFILE_OPEN_TASK_LINE = "\n• <b>{title}</b> (tayinlagan: {by}, yaratilgan: {created}){skips}"
PROFILE_TASK_SKIPS_FRAGMENT = " — <i>{count} marta o'tkazilgan</i>"


# ===== Boss panel (Phase 3A) =====

BTN_BOSS_PANEL = "🏆 Boss panel"
BTN_BOSS_ATTENDANCE = "👥 Xodimlar ma'lumotlari"
BTN_BOSS_FINANCE = "💰 Moliya bo'limi"
BTN_ADMIN_BOSS_ASSIGN = "🏆 Boss tayinlash"

BOSS_PANEL_MENU = (
    "🏆 <b>Boss panel</b>\n\n"
    "Quyidagi bo'limlardan birini tanlang:"
)
BOSS_FINANCE_COMING = "💰 <b>Moliya bo'limi</b> tez orada qo'shiladi (4-bosqich)."
BOSS_ATTENDANCE_EMPTY = "❌ Faol xodimlar yo'q."
BOSS_ATTENDANCE_HEADER = (
    "👥 <b>Xodimlar ma'lumotlari</b>\n"
    "🗓 {date}\n\n"
    "Tafsilot uchun xodimni tanlang:"
)
BOSS_EMP_STATUS_IN = "✅ {name} — keldi {time}"
BOSS_EMP_STATUS_OUT = "🔴 {name} — ketdi {time}"
BOSS_EMP_STATUS_NONE = "❌ {name} — kelmagan"

# Xodim detali (Boss/Bosh Admin uchun)
EMP_DETAIL_HEADER = (
    "👤 <b>{name}</b>\n"
    "📋 Lavozim: <i>{position}</i>\n"
    "📱 {phone}\n"
    "{role_badge}\n"
)
EMP_DETAIL_TODAY = "\n📅 <b>Bugungi davomat:</b>\n{today}"
EMP_DETAIL_TODAY_NONE = "— hech qanday yozuv yo'q —"
EMP_DETAIL_TODAY_LINE = "  • {emoji} {when} — {kind}"
EMP_DETAIL_MONTH = "\n\n🕒 <b>Bu oyda ishlangan:</b> <i>{hours} soat {minutes} daqiqa</i>"
EMP_DETAIL_SALARY_HEADER = "\n\n💰 <b>Bu oydagi ish haqqi:</b>"
EMP_DETAIL_SALARY_LINE = "\n  {emoji} <b>{type_name}</b>: {sign}{amount:,} so'm — <i>{reason}</i>"
EMP_DETAIL_SALARY_NONE = "\n— yozuvlar yo'q —"
EMP_DETAIL_TASKS_HEADER = "\n\n📝 <b>Tugatilmagan vazifalar:</b>"
EMP_DETAIL_TASK_LINE = "\n  • <b>{title}</b> (tayinlagan: {by}, yaratilgan: {created}){skips}"
EMP_DETAIL_TASK_SKIPS = " — <i>{count} marta o'tkazilgan</i>"
EMP_DETAIL_TASKS_NONE = "\n— yo'q —"
EMP_DETAIL_CARD = "\n\n💳 <b>Plastik karta:</b> {card}"

# Bosh Admin: Boss tayinlash
ADMIN_BOSS_PICK = (
    "🏆 <b>Boss tayinlash</b>\n\n"
    "Bossni tayinlash uchun xodimni tanlang.\n\n"
    "{current}"
)
ADMIN_BOSS_CURRENT = "ℹ️ Joriy Boss: <b>{name}</b>\n(Yangi tayinlasangiz, eski Boss xodim bo'lib qaytadi.)"
ADMIN_BOSS_NONE_YET = "ℹ️ Hozir Boss tayinlanmagan."
ADMIN_BOSS_CONFIRM = (
    "🏆 <b>Bossni tayinlash</b>\n\n"
    "<b>{name}</b>'ni Boss qilib tayinlamoqchimisiz?\n"
    "{warning}"
)
ADMIN_BOSS_WARNING_REPLACE = "\n⚠️ Joriy Boss (<b>{old}</b>) xodim bo'lib qaytadi."
ADMIN_BOSS_DONE = "✅ <b>{name}</b> endi Boss."
ADMIN_BOSS_REMOVE_PROMPT = (
    "🏆 <b>Bossni o'chirish</b>\n\n"
    "Joriy Boss: <b>{name}</b>\n\n"
    "O'chirilsa, oddiy xodim bo'ladi. Davom etamizmi?"
)
ADMIN_BOSS_REMOVED = "✅ Boss roli o'chirildi."
BTN_BOSS_REMOVE = "❌ Bossdan olib tashlash"
ADMIN_BOSS_REMOVE_LIST = "❌ <b>Bossdan olib tashlash</b>\n\nQaysi Bossni olib tashlaymiz?"
ADMIN_BOSS_REMOVED_NAME = "✅ <b>{name}</b> Boss rolidан olib tashlandi — endi oddiy xodim."

ADMIN_BOSS_ONLY_BOSH = "❌ Faqat Bosh Admin Boss tayinlay oladi."
BOSS_NOTIFY_ASSIGNED = (
    "🏆 <b>Tabriklaymiz!</b>\n\n"
    "Sizga Boss roli berildi.\n"
    "«🏆 Boss panel» tugmasini bosib bo'limlarni ko'rishingiz mumkin."
)
BOSS_NOTIFY_REMOVED = "ℹ️ Sizning Boss rolingiz o'chirildi."


# ===== Moliya bo'limi (Phase 4) =====

# Turkumlar: {key: (emoji, display_name)}
FINANCE_EXPENSE_CATEGORIES = {
    "food":     ("🍽", "Ovqat"),
    "transport":("🚌", "Yo'lkira"),
    "supply":   ("📦", "Ta'minot"),
    "expense":  ("💸", "Xarajat"),
    "advance":  ("👤", "Hodimlar uchun Avans"),
    "salary":   ("💼", "Ish haqqi"),
    "personal": ("🛍", "Shaxsiy xarajatlarim"),
    "other":    ("📝", "Boshqa"),
}

# Shaxsiy xarajatlar ichki turkumlari
FINANCE_PERSONAL_CATEGORIES = {
    "p_transport": ("🚌", "Shaxsiy: Yo'lkira"),
    "p_food":      ("🍽", "Shaxsiy: Ovqat"),
    "p_rent":      ("🏠", "Shaxsiy: Ijara"),
    "p_saving":    ("💰", "Shaxsiy: Jamg'arma"),
    "p_debt":      ("💳", "Shaxsiy: Qarz"),
    "p_other":     ("📝", "Shaxsiy: Boshqa"),
}

FINANCE_INCOME_CATEGORIES = {
    "podachot": ("📊", "Podachot"),
    "sales":    ("💵", "Sotuvdan tushum"),
    "other":    ("📝", "Boshqa"),
}

FINANCE_CATEGORIES = {**FINANCE_EXPENSE_CATEGORIES,
                      **FINANCE_PERSONAL_CATEGORIES,
                      **FINANCE_INCOME_CATEGORIES}

# Tugmalar
BTN_FINANCE_INCOME = "➕ Kirim qo'shish"
BTN_FINANCE_EXPENSE = "➖ Chiqim qo'shish"
BTN_FINANCE_SUMMARY = "📊 Bu oylik xulosa"
BTN_FINANCE_EXCEL = "📥 Excel hisobot"
BTN_FINANCE_NOTE_SKIP = "⏭ Izohsiz"
BTN_FINANCE_CATEGORY_OTHER = "📝 Boshqa (qo'lda izoh)"
BTN_FINANCE_TODAY = "📅 Bugungi sana"
BTN_FINANCE_DELETE = "🗑 Yozuvni o'chirish"

# Dialog
FINANCE_MENU = (
    "💰 <b>Moliya bo'limi</b>\n\n"
    "Bu sizning <i>shaxsiy daftaringiz</i> — boshqa hech kim ko'rmaydi.\n"
    "Quyidagilardan birini tanlang:"
)
FINANCE_PICK_CATEGORY_INCOME = "➕ <b>Kirim qo'shish</b>\n\nTurkumini tanlang:"
FINANCE_PICK_CATEGORY_EXPENSE = "➖ <b>Chiqim qo'shish</b>\n\nTurkumini tanlang:"
FINANCE_ASK_AMOUNT = (
    "{emoji} <b>{type_name}</b> · {category}\n\n"
    "Summani yozing (faqat raqam, masalan: 250000):"
)
FINANCE_AMOUNT_INVALID = "⚠️ Summa noto'g'ri. Faqat musbat raqam yozing (masalan: 250000)."
FINANCE_ASK_NOTE = (
    "{emoji} <b>{type_name}</b> · {category} · <b>{amount:,} so'm</b>\n\n"
    "Izoh qo'shasizmi? Yozing yoki pastdagi tugmani bosing."
)
FINANCE_SAVED = (
    "✅ <b>Saqlandi</b>\n\n"
    "{type_emoji} <b>{type_name}</b>\n"
    "{cat_emoji} Turkum: <i>{category}</i>\n"
    "💵 Summa: <b>{amount:,} so'm</b>\n"
    "📅 Sana: <i>{when}</i>{note_line}"
)
FINANCE_NOTE_FRAGMENT = "\n💬 Izoh: <i>{note}</i>"

FINANCE_PICK_PERSONAL = (
    "🛍 <b>Shaxsiy xarajatlarim</b>\n\n"
    "Ichki turkumini tanlang:"
)
FINANCE_ASK_DATE = (
    "📅 <b>Sana</b>\n\n"
    "Bugungi sana uchun pastdagi tugmani bosing,\n"
    "yoki boshqa sanani qo'lda yozing (masalan: <code>05.06.2026</code>):"
)
FINANCE_DATE_INVALID = (
    "⚠️ Sana noto'g'ri. <code>KK.OO.YYYY</code> formatida yozing "
    "(masalan: <code>05.06.2026</code>) yoki «📅 Bugungi sana» tugmasini bosing."
)
FINANCE_DELETE_ASK_DATE = (
    "🗑 <b>Yozuvni o'chirish</b>\n\n"
    "Qaysi sanadagi yozuvlarni ko'rasiz?\n"
    "Bugungi kun uchun tugmani bosing yoki sanani qo'lda yozing "
    "(masalan: <code>05.06.2026</code>):"
)
FINANCE_DELETE_EMPTY = "ℹ️ <b>{date}</b> sanasida sizning yozuvlaringiz yo'q. Boshqa sana yozing yoki Bekor qilish ni bosing."
FINANCE_DELETE_PICK = "🗑 <b>{date}</b> — o'chirish uchun yozuvni tanlang:"
FINANCE_DELETE_CONFIRM = (
    "🗑 <b>Rostdan o'chirilsinmi?</b>\n\n"
    "{type_emoji} <b>{type_name}</b>\n"
    "{cat_emoji} Turkum: <i>{category}</i>\n"
    "💵 Summa: <b>{amount:,} so'm</b>\n"
    "📅 Sana: <i>{when}</i>{note_line}{advance_warn}"
)
FINANCE_DELETE_ADVANCE_WARN = (
    "\n\n⚠️ Diqqat: bu avans yozuvi. O'chirilsa, xodimning ish haqqidagi "
    "avans chegirmasi <b>o'chmaydi</b> — uni Admin panel → Ish haqqi "
    "bo'limidan alohida bekor qiling."
)
FINANCE_DELETED = "🗑 Yozuv o'chirildi: {type_emoji} {amount:,} so'm — {category}"

FINANCE_SUMMARY_BALANCE = "\n\n💵 <b>Joriy qoldiq (umumiy):</b> {balance:,} so'm"

FINANCE_SUMMARY_HEADER = "📊 <b>{month} {year}</b> — sizning moliya xulosangiz\n"
FINANCE_SUMMARY_EMPTY = "\nℹ️ Bu oyda yozuvlar yo'q."
FINANCE_SUMMARY_INCOME = "\n\n➕ <b>Kirimlar</b> — jami: <b>{total:,} so'm</b>"
FINANCE_SUMMARY_EXPENSE = "\n\n➖ <b>Chiqimlar</b> — jami: <b>{total:,} so'm</b>"
FINANCE_SUMMARY_NET_POS = "\n\n💚 <b>Foyda:</b> +{net:,} so'm"
FINANCE_SUMMARY_NET_NEG = "\n\n🔻 <b>Zarar:</b> {net:,} so'm"
FINANCE_SUMMARY_NET_ZERO = "\n\n⚖️ <b>Hisob:</b> 0 so'm"
FINANCE_SUMMARY_CAT_LINE = "\n  {emoji} {category}: {total:,} so'm ({cnt})"

FINANCE_EXCEL_EMPTY = "ℹ️ Bu oyda yozuvlar yo'q — Excel yaratish ma'nosiz."
FINANCE_NO_PERMISSION = "❌ Moliya bo'limi faqat Boss va Bosh Admin uchun."
FINANCE_PICK_EMPLOYEE_ADVANCE = (
    "👤 <b>Hodimlar uchun Avans</b>\n\n"
    "Avans qaysi xodimga berilishini tanlang:"
)
FINANCE_ADVANCE_SALARY_NOTED = (
    "\n\n💼 Xodimning ish haqqidan <b>−{amount:,} so'm</b> avans sifatida "
    "chegirildi va unga xabar yuborildi."
)
FINANCE_ADVANCE_MONTH_CLOSED = (
    "🔒 {month} {year} oyi yopilgan — bu oyga avans yozib bo'lmaydi.\n"
    "Avval oyni qayta oching."
)


# ===== Ofis IP boshqaruvi (dinamik whitelist) =====
BTN_OFFICE_IP = "📍 Ofis IP boshqaruvi"
BTN_OFFICE_IP_ADD = "➕ Joriy IP'ni qo'shish"
BTN_OFFICE_IP_LIST = "📋 Ofis IP'lari ro'yxati"

OFFICE_IP_MENU = (
    "📍 <b>Ofis IP boshqaruvi</b>\n\n"
    "Bot xodim ofis Wi-Fi'sida ekanini public IP orqali tekshiradi. "
    "Provayder IP'ni vaqti-vaqti bilan o'zgartiradi — shunda quyidagi tugma "
    "orqali yangi IP'ni qo'shasiz (Render sozlamalariga tegmasdan).\n\n"
    "➕ <b>Joriy IP'ni qo'shish</b> — havolani <u>ofis Wi-Fi'sida turib</u> oching, "
    "bot o'sha IP'ni avtomatik qo'shadi.\n"
    "📋 <b>Ro'yxat</b> — qo'shilgan IP'larni ko'rish va o'chirish."
)
OFFICE_IP_SETLINK = (
    "📍 Quyidagi havolani <b>ofis Wi-Fi'sida turib</b> oching — joriy IP "
    "avtomatik ofis IP sifatida qo'shiladi.\n\n"
    "⚠️ Mobil internetda ochmang, aks holda noto'g'ri IP qo'shiladi.\n"
    "Havola 5 daqiqa amal qiladi."
)
OFFICE_IP_LIST_HEADER = (
    "📋 <b>Ofis IP'lari</b> (jami {n} ta)\n\nO'chirish uchun tegishli tugmani bosing:"
)
OFFICE_IP_LIST_EMPTY = (
    "📋 Hozircha bironta ofis IP'si yo'q.\n\n"
    "⚠️ Bu holatda bot HAMMA IP'ni qabul qiladi (filtr o'chiq). "
    "Xavfsizlik uchun ofisda turib «➕ Joriy IP'ni qo'shish» tugmasini bosing."
)
SETIP_ADDED = "✅ Yangi ofis IP qo'shildi: <code>{ip}</code>"
SETIP_ALREADY = "ℹ️ Bu IP allaqachon ro'yxatda: <code>{ip}</code>"
IP_REMOVED = "🗑 IP o'chirildi: <code>{ip}</code>"
IP_IGNORED = "❌ E'tiborsiz qoldirildi."
IP_CHANGED_ALERT = (
    "⚠️ <b>Ofis IP'si o'zgargan bo'lishi mumkin</b>\n\n"
    "<b>{name}</b> hozir <code>{ip}</code> IP'sidan davomat qilmoqchi, lekin bu IP "
    "ofis ro'yxatida yo'q.\n\n"
    "Agar bu HAQIQATAN ofis Wi-Fi'si bo'lsa — «qo'sh»ni bosing. "
    "Aks holda (xodim uydan yoki mobil internetdan) — e'tiborsiz qoldiring."
)


# ===== Lavozimlar tizimi =====
BTN_POSITIONS = "📋 Lavozimlar"
BTN_POS_ADD = "➕ Lavozim qo'shish"
BTN_POS_EDIT = "✏️ Tahrirlash"
BTN_POS_DELETE = "🗑 O'chirish"
BTN_SET_POSITION = "💼 Lavozim/Stavka belgilash"

POS_MENU_HEADER = (
    "📋 <b>Lavozimlar tizimi</b>\n\n"
    "Hozirgi lavozimlar:\n{list}\n\n"
    "Yangi qo'shish yoki tahrirlash:"
)
POS_EMPTY = "<i>Hozircha lavozimlar yo'q</i>"
POS_ITEM = "• <b>{name}</b> — {hours} soat/kun | {min:,}–{max:,} so'm\n"

POS_ASK_NAME = "➕ <b>Yangi lavozim</b>\n\nLavozim nomini yozing:\n<i>Misol: Upakovkachilar</i>"
POS_NAME_SHORT = "❌ Nom juda qisqa (kamida 3 belgi)."
POS_ASK_HOURS = "🕐 Kunlik ish soatini yozing (masalan: <code>9</code> yoki <code>10</code>):"
POS_HOURS_INVALID = "❌ Noto'g'ri. 1 dan 24 gacha son kiriting."
POS_ASK_MIN_RATE = "💵 Minimal kunlik stavkani yozing (so'mda, masalan: <code>120000</code>):"
POS_ASK_MAX_RATE = "💵 Maksimal kunlik stavkani yozing (so'mda, masalan: <code>150000</code>):"
POS_RATE_INVALID = "❌ Noto'g'ri summa. Faqat musbat son kiriting."
POS_ADDED = "✅ Lavozim qo'shildi: <b>{name}</b> ({hours} soat/kun, {min:,}–{max:,} so'm)"
POS_DELETED = "🗑 Lavozim o'chirildi: <b>{name}</b>"
POS_DELETE_HAS_EMPLOYEES = (
    "❌ Bu lavozimga <b>{count}</b> ta xodim bog'langan — o'chirib bo'lmaydi.\n"
    "Avval ularning lavozimini o'zgartiring."
)

SET_POS_PICK_EMP = "💼 <b>Lavozim/Stavka belgilash</b>\n\nXodimni tanlang:"
SET_POS_PICK_POS = (
    "💼 <b>{name}</b>\n\nLavozimni tanlang:\n\n"
    "{list}"
)
SET_POS_POS_ITEM = "• <b>{name}</b> — {hours} soat | {min:,}–{max:,} so'm\n"
SET_POS_ASK_RATE = (
    "💵 <b>{emp_name}</b> → <b>{pos_name}</b>\n\n"
    "Kunlik stavkani yozing (so'mda):\n"
    "Diapazon: <b>{min:,} – {max:,} so'm</b>"
)
SET_POS_RATE_INVALID = "❌ Noto'g'ri summa. Faqat musbat son kiriting."
SET_POS_DONE = (
    "✅ Belgilandi:\n"
    "👤 <b>{emp_name}</b>\n"
    "💼 Lavozim: <b>{pos_name}</b> ({hours} soat/kun)\n"
    "💵 Kunlik stavka: <b>{rate:,} so'm</b>"
)

# Ish haqqi ko'rsatish (yangi tizim)
SALARY_HEADER_DAILY = (
    "💰 <b>Mening ish haqqim — {month} {year}</b>\n\n"
    "💼 Lavozim: <b>{position}</b>\n"
    "🕐 Smena: <b>{work_hours} soat/kun</b>\n"
    "💵 Kunlik stavka: <b>{daily_rate:,} so'm</b>\n"
    "📅 Ishlagan kunlar: <b>{days} kun</b>\n"
    "━━━━━━━━━━━━━━━━━\n"
    "📊 <b>Hisob-kitob:</b>\n\n"
    "🕐 Asosiy ish haqqi: <b>+{base:,} so'm</b>\n"
    "💸 Avanslar: <b>−{avans:,} so'm</b>\n"
    "⚠️ Jarimalar: <b>−{jarima:,} so'm</b>\n"
    "⭐ Mukofotlar: <b>+{mukofot:,} so'm</b>\n"
    "🎁 Bonuslar: <b>+{bonus:,} so'm</b>\n"
    "🛒 Mahsulot xaridi: <b>−{mahsulot:,} so'm</b>\n"
    "━━━━━━━━━━━━━━━━━\n"
    "💰 <b>Jami: {total:,} so'm</b>"
)

# ===== Admin: Xodimlar ma'lumotlari (lavozim bo'yicha) =====
EMP_DATA_PICK_POS = (
    "👥 <b>Xodimlar ma'lumotlari</b>\n\n"
    "Avval lavozimni tanlang:"
)
EMP_DATA_NO_POSITION = "📋 Lavozim belgilanmagan ({count} ta xodim)"
EMP_DATA_PICK_EMP = "👥 <b>{pos_name}</b>\n\nXodimni tanlang ({count} ta):"
EMP_DATA_NO_EMPS = "Bu lavozimda xodim yo'q."

EMP_FULL_PROFILE = (
    "👤 <b>{name}</b>\n"
    "💼 Lavozim: <i>{position}</i>{role_badge}\n"
    "📱 Telefon: <code>{phone}</code>\n"
    "💳 Karta: {card}\n"
    "📅 Ro'yxatdan: {registered}\n"
)
EMP_FULL_POSITION_RATE = "💵 Kunlik stavka: <b>{rate:,} so'm</b> ({hours} soat/kun)\n"
EMP_FULL_MONTH_HEADER = "\n📅 <b>{month} {year} — davomat:</b>\n"
EMP_FULL_DAY_LINE = "  {date} ({weekday}): 🟢{inn} → 🔴{out} ({worked})\n"
EMP_FULL_DAY_NO_OUT = "  {date} ({weekday}): 🟢{inn} → —\n"
EMP_FULL_DAY_ABSENT = "  {date} ({weekday}): ❌ kelmagan\n"
EMP_FULL_MONTH_TOTAL = "⏱ Jami: <b>{hours} soat {mins} daqiqa</b>\n"
EMP_FULL_SALARY_HEADER = "\n💰 <b>Ish haqqi ({month} {year}):</b>\n"
EMP_FULL_SALARY_BASE = "  Asosiy: <b>+{base:,} so'm</b>\n"
EMP_FULL_SALARY_LINE = "  {emoji} {type}: {sign}<b>{amount:,}</b> — <i>{reason}</i>\n"
EMP_FULL_SALARY_TOTAL = "  <b>Jami: {total:,} so'm</b>\n"
EMP_FULL_TASKS_HEADER = "\n📝 <b>Tugatilmagan vazifalar:</b>\n"
EMP_FULL_TASK_LINE = "  • <b>{title}</b> ({by}){skips}\n"
EMP_FULL_NO_DATA = "<i>Ma'lumot yo'q</i>"
