# 📌 Attendance Bot — Loyiha ma'lumotlari

> Bu fayl loyihaning asosiy ma'lumotnomasi. Loyihaga o'zgartirish kiritishdan
> oldin shu faylni o'qing. Yangi muhim ma'lumotlar ham shu faylga yoziladi.
> Oxirgi yangilanish: 2026-07-12

---

## 1. Loyiha manzili va tuzilishi

Loyiha: `/Users/jb89/Desktop/attendance_bot`

```
attendance_bot/
├── bot.py                  # Kirish nuqtasi (routerlar ulanadi)
├── config.py               # Sozlamalar (.env dan o'qiydi)
├── database.py             # SQLite — barcha jadval va funksiyalar (~51 KB)
├── keyboards.py            # Barcha tugmalar/klaviaturalar (~26 KB)
├── texts.py                # Barcha matnlar va TURKUM lug'atlari (~45 KB)
├── states.py               # FSM holatlar
├── roles.py                # Rollar: boss, bosh_admin, admin, employee
├── middlewares.py          # Middleware'lar
├── tzutil.py               # Toshkent vaqti (UTC+5) yordamchilari
├── attendance.db           # SQLite baza (ish ma'lumotlari!)
├── .env                    # BOT_TOKEN va sirlar (gitga qo'shilmaydi)
├── requirements.txt        # aiogram 3.x, openpyxl va boshqalar
├── render.yaml             # Render deploy konfiguratsiyasi
├── handlers/               # Barcha handler'lar
│   ├── attendance.py       # Davomat
│   ├── finance.py          # Moliya bo'limi (Boss/Bosh Admin)
│   ├── personal_finance.py # Shaxsiy moliya
│   ├── admin.py, boss.py, broadcast.py, common.py, emp_data.py,
│   ├── office_ip.py, positions.py, profile.py, registration.py, tasks.py
├── services/               # face_service, location_service, wifi_verify
├── docs/                   # ← SHU PAPKA: barcha hujjat va ma'lumotlar
│   ├── LOYIHA_MALUMOT.md   # ← shu fayl
│   └── arxiv/              # Eski fayllar (Downloads/phase4 dan ko'chirilgan)
└── venv/                   # Python virtual muhit (368 MB, o'chirmang)
```

---

## 2. Moliya bo'limi — turkumlar qanday ishlaydi (2026-07-12 tahlili)

### Turkumlar QAYERDA saqlanadi
Turkumlar **bazada EMAS**, `texts.py` ichida **hardcode** qilingan Python
lug'atlarda:

| Lug'at | Joyi | Mazmuni |
|---|---|---|
| `FINANCE_EXPENSE_CATEGORIES` | texts.py:836 | 8 ta chiqim turkumi (food, transport, supply, expense, advance, salary, personal, other) |
| `FINANCE_PERSONAL_CATEGORIES` | texts.py:848 | 6 ta "Shaxsiy xarajatlarim" ichki turkumi (p_transport, p_food, p_rent, p_saving, p_debt, p_other) |
| `FINANCE_INCOME_CATEGORIES` | texts.py:857 | 3 ta kirim turkumi (podachot, sales, other) |
| `FINANCE_CATEGORIES` | texts.py:863 | Yuqoridagi uchtasining birlashmasi |
| `PF_EXPENSE_CATS` | texts.py:1152 | Shaxsiy moliya chiqim turkumlari |
| `PF_INCOME_CATS` | texts.py:1164 | Shaxsiy moliya kirim turkumlari |
| `PF_ALL_CATS` | texts.py:1171 | Ikkalasining birlashmasi |

Format: `{key: (emoji, nom)}` — masalan `"food": ("🍽", "Ovqat")`.

Bazaga faqat turkumning **key**'i yoziladi:
- `finance_entries.category` (TEXT) — database.py:123
- `personal_finance.category` (TEXT) — database.py:145

Ko'rsatishda har doim `texts.FINANCE_CATEGORIES.get(key, ("📋", key))`
fallback ishlatiladi — demak bazadagi notanish key ham buzilmaydi.

### Turkum QO'SHISH oqimi — MAVJUD EMAS ❌
- `add_category`, `addcat`, `custom_categor` — loyihada umuman yo'q
- `finance_categories` jadvali yo'q
- Foydalanuvchi o'z turkumini qo'sha olmaydi.
  Yagona chora — "📝 Boshqa" turkumi + qo'lda izoh.

### Custom turkum qo'shmoqchi bo'lsangiz kerak bo'ladi:
1. Yangi jadval: `finance_categories` (owner_id, type, key, emoji, name)
2. `database.py` — jadval + CRUD funksiyalar
3. `texts.py` lug'atlari o'rniga bazadan o'qiydigan funksiya
   (hardcode + custom birlashadigan)
4. `keyboards.py` — `finance_categories_kb()` (527-qator atrofida),
   `finance_personal_cats_kb()` (476-qator atrofida), `pf_income_cats_kb()`,
   `pf_expense_cats_kb()` larni dinamik qilish
5. `states.py` — yangi FSM (turkum nomi/emoji kiritish)
6. Yangi handler: "➕ Turkum qo'shish" tugmasi → nom → emoji → saqlash

### Moliya oqimlari (hozirgi)
- **Kirim:** Podachot | Sotuvdan tushum | Boshqa → Summa → Izoh → Sana → Saqlash
- **Chiqim:** Ovqat | Yo'lkira | Ta'minot | Xarajat | Boshqa → Summa → Izoh → Sana → Saqlash
- **Avans:** Hodimlar uchun Avans → Xodim tanlash → Summa → Izoh → Sana →
  Saqlash + xodim oyligidan avtomatik chegiriladi (`add_salary_entry`) +
  xodimga bildirishnoma
- Callback formatlari: `fin_cat:{type}:{key}`, `fin_emp:{id}`,
  `fin_del:{id}`, `fin_delc:{id}`, `pf_cat:{type}:{key}`, `pf_del:{id}`
- Ruxsat: faqat `boss` va `bosh_admin` rollari

---

## 3. Baza jadvallari (database.py, hammasi SQLite)

`employees`, `attendance`, `settings`, `used_photos`, `salary_entries`,
`closed_months`, `tasks`, `task_skips`, `finance_entries` (123-qator),
`office_ips`, `personal_finance` (145-qator), `broadcasts`,
`broadcast_reactions`, `broadcast_comments`, `positions` (1165-qator).

---

## 4. Muhim eslatmalar

- Vaqt: Toshkent UTC+5, `tzutil.py` orqali. Sana kiritishda mahalliy 12:00
  UTC ga −5 soat qilib yoziladi (finance.py:323).
- `attendance.db` — jonli ma'lumotlar, O'CHIRMANG, ustiga yozmang.
- `.env` — BOT_TOKEN shu yerda, chatga/gitga chiqarilmaydi.
- Oy yopilgan bo'lsa (`closed_months`) avans kiritib bo'lmaydi.
- `venv/` katta (368 MB) lekin botni lokal ishga tushirish uchun kerak.

---

## 5. Yangi ma'lumotlar uchun joy

Keyingi tahlillar, rejalar va qarorlar shu bo'limga (yoki `docs/` ichiga
alohida .md fayl qilib) yoziladi:

<!-- Yangi yozuvlarni shu yerdan boshlab qo'shing -->

### 2026-07-12 — 3 yangi funksiya qo'shildi (dinamik turkumlar, "Bugun" bloklari)

**1. Dinamik (custom) turkumlar tizimi:**
- Yangi jadval `custom_categories` (owner_id, scope: fin|fin_personal|pf,
  entry_type, emoji, name, is_active) — soft delete (is_active=0).
- Yozuvlarda custom turkum kaliti `c{id}` ko'rinishida (masalan `c7`).
- Yangi fayl `catutil.py`: `resolve_category(key, scope)` — turkum nomini
  yechuvchi yagona resolver (standart lug'at → custom jadval → fallback).
  Nom ko'rsatiladigan HAMMA joy shu funksiyani ishlatadi.
- Yangi fayl `handlers/categories.py`: "⚙️ Turkumlar" tugmasi (ikkala menyuda),
  callback prefiksi `ccat:` (sec/home/add/new/del/delc/back/close),
  FSM: `CategoryManage.entering_name`. Tugma bosilganda avval bo'lim
  tanlanadi (💰 Moliya / 📊 Shaxsiy) — reply-tugma kontekstsiz bo'lgani uchun.
- Klaviatura funksiyalari endi `owner_id` parametr oladi:
  `finance_categories_kb(entry_type, owner_id)`, `finance_personal_cats_kb(owner_id)`,
  `pf_income_cats_kb(owner_id)`, `pf_expense_cats_kb(owner_id)`.
- database.py CRUD: `add_custom_category`, `get_custom_categories`,
  `get_custom_category_by_id`, `deactivate_custom_category`.

**2. Moliya "Bu oylik xulosa"ga bugungi blok:**
- `get_today_finance_summary(owner_id, date_str)` — `date(entry_date,'+5 hours')`.
- Balansdan oldin: "📅 Bugun (KK.OO): −X so'm (N ta yozuv)" + turkum qatorlari
  + bugungi kirim qatori. Yozuv bo'lmasa "📅 Bugun hali yozuv yo'q."

**3. PF "Bu oy hisoboti"ga bugungi blok + kunlik byudjet:**
- `pf_get_today_totals(employee_id, date_str)` — entry_date lokal string tenglik.
- Sof qoldiqdan keyin: Bugun / Qoldiq / Oy oxirigacha N kun /
  Kunlik limit (`net // max(days_in_month - today.day, 1)`);
  net ≤ 0 bo'lsa 🔻 limit hisoblanmaydi. Faqat oyda yozuv bor bo'lganda chiqadi.

**Bonus fix:** PF kategoriya tanlashda "Bekor qilish" (`pf_cat:cancel`)
ilgari ishlamasdi (2 qismli callback 3-qism tekshiruvidan o'tmasdi) — tuzatildi.

O'zgargan fayllar: database.py, texts.py, keyboards.py, states.py, bot.py,
handlers/finance.py, handlers/personal_finance.py;
yangi: catutil.py, handlers/categories.py.
Smoke-testlar vaqtinchalik bazada o'tkazildi — jonli attendance.db tegilmagan.
Batafsil reja: `~/.claude/plans/telegram-botimga-aiogram-3-x-eager-lovelace.md`
