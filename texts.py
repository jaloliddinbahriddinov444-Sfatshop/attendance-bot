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
    "📅 Ro'yxatdan o'tgan: {registered}\n"
    "{admin_badge}"
)

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

BTN_ADMIN_LIST = "📋 Xodimlar ro'yxati"
BTN_ADMIN_REMOVE = "❌ Xodim o'chirish"
BTN_ADMIN_PROMOTE = "👑 Admin tayinlash"
BTN_ADMIN_TODAY = "📅 Bugungi hisobot"
BTN_ADMIN_SETTINGS = "🏢 Ishxona sozlamalari"
BTN_ADMIN_EXPORT = "📊 Excel hisobot"

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

ADMIN_ATT_SELECT_EMPLOYEE = "📝 <b>Davomat tahrirlash</b>\n\nXodimni tanlang:"

ADMIN_ATT_ACTIONS = (
    "📝 <b>{name}</b> uchun:\n\n"
    "Qaysi amalni bajarasiz?"
)

ADMIN_ATT_ENTER_TIME = (
    "🕐 <b>{name}</b> — {action}\n\n"
    "Vaqtni kiriting (masalan, <code>09:15</code>):"
)

ADMIN_ATT_SAVED = "✅ <b>{name}</b> — {action} soat <b>{time}</b> da qayd etildi."

ADMIN_ATT_RESET_DONE = (
    "🗑 <b>{name}</b> bugungi davomat yozuvlari tozalandi.\n\n"
    "O'chirilgan yozuvlar: <b>{count}</b> ta"
)

# ===== Ish haqqi =====
BTN_SALARY = "💰 Ish haqqim"
BTN_ADMIN_RATES = "💵 Stavkalarni belgilash"

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
