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

### 2026-07-12 (2) — MUHIM: server kodi lokaldan yangi edi!

Deploy oldidan aniqlandi: boshqa chatdan serverga (6-iyul) katta o'zgarishlar
deploy qilingan, lokal nusxa 29-iyunda qolib ketgan edi. Server kodi lokalga
sinxronlandi (git commit 8716c89). **Qoida: har ishdan oldin server bilan
solishtirish kerak** (`ssh root@45.138.158.174`, kod `/opt/davomat/`).

Serverda allaqachon bor bo'lgan (boshqa chatdan): `finance_categories`
jadvali (Moliya turkumlari TO'LIQ bazada, owner_id + protected + is_personal,
ckey='c{id}'), `handlers/fin_categories.py` ("🏷 Moliya turkumlari" tugmasi),
`finance_category_label()` resolveri, beacon tizimi, PF o'chirish sana bo'yicha,
PF Excel yangi format.

**Deploy ma'lumotlari:**
- Servis: `systemctl restart davomat`, holat: `systemctl is-active davomat`
- Kod: `/opt/davomat/`, baza: `/opt/davomat/attendance.db`
- Log: `/var/log/davomat.log` (journald'da faqat systemd qatorlari)
- Zaxiralar: `/opt/davomat/backups/pre-deploy-*.tgz` (deploy oldidan olinadi)
- Deploy usuli: `tar czf - fayllar | ssh root@... "cd /opt/davomat && tar xzf -"`
  keyin serverda py_compile va restart. Serverda git YO'Q.

### 2026-07-12 — 3 yangi funksiya qo'shildi va DEPLOY QILINDI

Eslatma: quyidagi 1-bandning dastlabki (custom_categories/catutil) versiyasi
bekor qilindi — server dizayni bilan to'qnashdi. Yakuniy versiya server
uslubida yozildi (arxiv: `arxiv-lokal-turkumlar` git branchi).

**1. PF (Shaxsiy moliya) turkumlari — bazaga ko'chirildi:**
- Yangi jadval `pf_categories` — `finance_categories` bilan bir xil naqsh:
  owner_id, entry_type, ckey, emoji, name, protected, is_active,
  UNIQUE(owner_id, entry_type, ckey). Har egaga 13 ta default seed
  (PF_EXPENSE_CATS + PF_INCOME_CATS asosida), custom ckey='c{id}', soft delete.
- database.py: `init_pf_categories` (init_db ichida), `ensure_owner_pf_categories`,
  `get_pf_categories`, `get_all_pf_categories`, `get_pf_category`,
  `get_pf_category_by_ckey`, `pf_category_label`, `create_pf_category`,
  `delete_pf_category`.
- Yangi handler `handlers/pf_categories.py` — "🏷 Shaxsiy turkumlar" tugmasi
  (PF menyusida), fin_categories.py bilan bir xil oqim: tur → emoji → nom.
  Callback prefiksi `pfcat_*`, FSM `PFCategoryManage`.
- PF klaviaturalari (`pf_income_cats_kb(owner_id)`, `pf_expense_cats_kb(owner_id)`)
  endi bazadan o'qiydi; `pf_cat_chosen` bazadan tekshiradi.
- Bonus fix: `pf_cat:cancel` (Bekor tugmasi) ilgari ishlamasdi — tuzatildi.

**2. Moliya "Bu oylik xulosa"ga bugungi blok:**
- `get_today_finance_summary(owner_id, date_str)` — `date(entry_date,'+5 hours')`.
- Balansdan oldin: "📅 Bugun (KK.OO): −X so'm (N ta yozuv)" + turkum qatorlari
  + "➕ Bugungi kirim". Yozuv bo'lmasa "📅 Bugun hali yozuv yo'q."

**3. PF "Bu oy hisoboti"ga bugungi blok + kunlik byudjet:**
- `pf_get_today_totals(employee_id, date_str)` — entry_date lokal string tenglik.
- Sof qoldiqdan keyin: Bugun / Qoldiq / Oy oxirigacha N kun /
  Kunlik limit (`net // max(days_in_month - today.day, 1)`);
  net ≤ 0 bo'lsa 🔻 limit hisoblanmaydi.

Deploy: 2026-07-12 14:28, zaxira `backups/pre-deploy-20260712-142651.tgz`,
bot toza ishga tushdi, pf_categories 3 egaga seed bo'ldi (13 tadan).

### (BEKOR QILINGAN) 2026-07-12 — dastlabki custom_categories versiyasi

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

### 2026-07-12 (3) — 3 yangi funksiya: Dashboard, Tuzatish so'rovlari, Eslatmalar

Ish oldidan server↔lokal solishtirildi (md5) — 100% sinxron edi.

**1. Web Dashboard** (`services/dashboard.py`, wifi_verify'dagi 9090-port serverga
ulangan): `GET /dashboard?key=`, `/api/dashboard/today`, `/api/dashboard/month`.
Auth: `DASHBOARD_API_KEY` env (bo'sh = 403, hmac.compare_digest), CORS:
`DASHBOARD_ALLOWED_ORIGIN`. Bosh Admin tugmasi: Boshqaruv → 🖥 Web Dashboard.
DIQQAT: serverdagi nginx'ga /dashboard va /api/dashboard/ location bloklari
kerak (README'da namuna) — deploy paytida qo'shiladi.

**2. Davomat tuzatish so'rovlari** (`handlers/fix_requests.py`, jadval
`attendance_fix_requests`): xodim 📊 Statistika → "✏️ Davomatni tuzatish
so'rovi" (7 kun, in/out/both, HH:MM, sabab ≥5 belgi, kuniga max 3, kunga 1
pending). Adminlarga inline ✅/❌; tasdiqlash `claim_fix_request` atomik UPDATE
bilan (ikki admin poygasi), qo'llash `delete_day_attendance[_by_type]` +
`add_manual_attendance` (UTC konvertatsiya tayyor). Cancel prefiksi
`FixReview:` common.py ro'yxatiga qo'shilgan.

**3. Avtomatik eslatmalar** (`services/reminders.py`, bot.py'da
`asyncio.create_task`): 60s loop, work_start−15 (pre_start), +20 (late, xodim +
adminlarga bitta jamlanma), work_end+10 (forgot_out). Dedup: `reminder_log`
jadvali (atomik INSERT OR IGNORE, restart-safe), oyna 10 daqiqa. Toggle:
Boshqaruv → 🔔 Eslatmalar (settings 'reminders_enabled', default '1').
`WEEKEND_DAYS = set()` kelajak uchun.

Yangi env: `DASHBOARD_API_KEY`, `DASHBOARD_ALLOWED_ORIGIN` (.env.example'da).
40 ta avtomatik test vaqtinchalik bazada o'tdi; dashboard brauzerda (desktop +
mobil) tekshirildi. Jonli attendance.db tegilmagan. LOKAL BOTNI TO'LIQ ISHGA
TUSHIRMANG — polling produksiya bilan to'qnashadi (409).
Reja: `~/.claude/plans/telegram-botimga-aiogram-3-x-cuddly-giraffe.md`

### 2026-07-12 (4) — Dashboard API kengaytirildi: hodimlar CRUD

`services/dashboard.py`ga qo'shildi: GET `/api/dashboard/employees` (faol+nofaol,
lavozim join — `get_employees_admin()` database.py'da), GET `/api/dashboard/positions`,
PATCH `/api/dashboard/employees/{id}` (full_name, position_id+daily_rate,
daily_rate, hourly_rate, karta, is_active — bot validatsiyalari bilan, mavjud
db funksiyalari orqali). Sfatshop paneli shu API'dan foydalanadi (proxy).
Deploy qilingan (2026-07-12 kech).

### 2026-07-20 — Arxiv (o'tgan oylar) + PF huquqi (pf_access)

Ish oldidan server↔lokal md5 solishtirildi — 100% sinxron edi.

**1. Arxiv — oxirgi 6 oy (faqat O'QISH, closed_months mantig'iga tegilmagan):**
- `tzutil.last_months(6)` — joriy oydan orqaga (yil chegarasi hisobga olingan).
- PF: "🗂 Shaxsiy arxiv" tugmasi → `pf_arc:{YYYY-MM}` → xulosa + "📥 Shu oy uchun
  Excel" (`pf_arcx:{YYYY-MM}`). Moliya: "🗂 Arxiv" → `fin_arc:` / `fin_arcx:`.
  Tugma matnlari ATAYIN har xil — bir xil bo'lsa finance router (bot.py'da
  oldinroq) PF tugmasini ham o'ziga tortib ketardi.
- Refaktor (kod dublikatsiyasi yo'q, joriy oy ham shularni chaqiradi):
  `_pf_summary_text(emp_id, year, month, with_today)`,
  `_finance_summary_text(owner_id, year, month, with_today)`,
  `_send_pf_excel(...)`, `_send_finance_excel(...)`.
  `with_today=False` — arxivda "Bugun"/kunlik limit/joriy balans bloklari
  chiqmaydi (ular faqat joriy oy uchun ma'noli).
- `fin_arc:` prefiksi `fin_arcx:` ni tutib qolmaydi (':' vs 'x') — mavjud
  `fin_del:`/`fin_delc:` bilan bir xil naqsh.

**2. pf_access — "📊 Shaxsiy xarajatlarim"ni xodimga ochish:**
- Migratsiya: `employees.pf_access INTEGER DEFAULT 0` (PRAGMA tekshiruvi bilan,
  idempotent). `set_pf_access(employee_id, value)`. Ro'yxat uchun alohida so'rov
  yozilmadi — `get_all_employees()` SELECT * bo'lgani uchun pf_access ni beradi.
- Bosh Admin: Boshqaruv → "📊 PF huquqi berish" → inline ro'yxat (✅/⬜),
  `pfacc:{emp_id}` toggle + `edit_reply_markup`. Xodimga DM + yangi main_menu_kb.
- `main_menu_kb(..., has_pf=False)` — faqat oddiy xodim menyusiga ta'sir qiladi.
  Chaqiruvchilar: common.py, finance.py, profile.py (3 joy), registration.py.
- Kirish: `_can_use` = boss | bosh_admin | pf_access==1 (yangi router yo'q).

**3. PF "Ortga" kirish nuqtasi — FSM'siz:**
`pf_menu_kb(from_finance)` Boss/Bosh Adminga "⬅️ Moliya bo'limi" tugmasini
beradi, oddiy xodimga BTN_BACK (uni common.py asosiy menyuga qaytaradi).
FSM holati bilan qilingan dastlabki variant BEKOR QILINDI: holat boshqa
bo'limlarga o'tganda tozalanmay qolib, Davomatdan "Ortga" ni ham Moliyaga
yo'naltirardi.

Test: `test_pf_archive.py` (yangi baza + jonli baza NUSXASI ustida — migratsiya
idempotentligi, last_months, toggle, arxiv xulosalari, klaviaturalar, prefiks
to'qnashuvi). Excel va +5 soat oy chegarasi alohida sun'iy ma'lumotda sinaldi.
Jonli attendance.db tegilmagan. HALI DEPLOY QILINMAGAN.

### 2026-07-20 (2) — Menyu tartibi muharriri (MENU_REGISTRY + menu_layouts)

Ish oldidan server↔lokal md5 solishtirildi — sinxron edi.

**Maqsad:** Bosh Admin kod yozmasdan reply-menyulardagi tugmalar JOYLASHUVINI
o'zgartira olsin. Tugma MATNLARI tegilmaydi (ular handler filtrlariga bog'langan).

**Baza:** `menu_layouts (menu_key PK, layout_json, updated_at)`. Yozuv yo'q =
standart tartib. `get_menu_layout` (buzuq JSON'da None qaytaradi — bot yiqilmaydi),
`set_menu_layout` (UPSERT), `reset_menu_layout` (DELETE).

**Reyestr (keyboards.py `MENU_REGISTRY`):** 14 ta menyu — main_employee /
main_boss / main_bosh_admin, admin_panel_bosh / admin_panel, grp_employees /
grp_attendance / grp_finance / grp_control, admin_settings, ip_menu, boss_panel,
finance_menu, pf_menu. Har birida `title`, `buttons` (kalit -> texts.py matni),
`default` (hozirgi kod tartibi AYNAN).

**`build_menu_kb(menu_key, visible_keys=None, overrides=None)`:**
- `visible_keys` — shartli tugmalar (main_employee'da admin/personal_finance).
  Filtr layoutdan QAT'I NAZAR ishlaydi, bo'sh qolgan qator tushadi.
- `overrides` — {kalit: matn}; pf_menu'da ortga tugmasi kirish nuqtasiga qarab
  BTN_BACK yoki BTN_PF_BACK_FINANCE bo'ladi.
- `normalize_layout()` — notanish/takroriy kalit tashlanadi, qatorda maks 2 ta
  tugma (MAX_ROW_BUTTONS), bo'sh qator olib tashlanadi, reyestrda bor-u
  layoutda yo'q tugma OXIRIGA qo'shiladi (yangi tugma yo'qolib qolmasin).
Mavjud 8 ta kb funksiyasi ichi shunga almashtirildi — imzolar va chaqiruv
joylari O'ZGARMADI, handlerlarga tegilmadi.

**Muharrir (`handlers/menu_editor.py`, router common'dan oldin):**
Boshqaruv → "🧩 Menyu tartibi". Callbacklar: `mlay:{menu_key}` (`:list`/`:cancel`),
`mmv:{menu_key}:{btn_key}:up|dn|mrg`, `mlayr:{menu_key}[:yes]` (reset, tasdiq bilan),
`mnop` (nom tugmasi). Ichki model — tekis ro'yxat `[[kalit, qo'shilganmi]]`:
up/dn faqat KALITLARNI almashtiradi (qatorlar shakli saqlanadi), mrg esa
"qo'shilganmi" bayrog'ini toggle qiladi (3 ta tugma yig'ilib qolmasligi
tekshiriladi). Chekka holatda callback answer bildirish beradi, xato emas.

DIQQAT: `mlay:` prefiksi `mlayr:` ni tutmaydi (':' vs 'r') — mavjud
`fin_del:`/`fin_delc:` bilan bir xil naqsh. Eng uzun callback 40 bayt (limit 64).

Testlar: `test_menu_parity.py` (17 ta menyu refaktordan keyin AYNAN eskidek —
yangi va eski baza nusxasida), `test_menu_layout.py` (surish/birlashtirish/
ajratish/reset, shartli tugmalar, normalizatsiya, buzuq JSON, chekka holatlar).
Jonli attendance.db tegilmagan. HALI DEPLOY QILINMAGAN.

### 2026-07-20 (3) — Mini App drag-and-drop menyu muharriri

1-QISM (menu_layouts + MENU_REGISTRY + build_menu_kb) oldingi bosqichda
qilingan edi — faqat 2-QISM (Mini App) qo'shildi.

**MUHIM — nginx'ga tegilmadi:** serverdagi nginx'da faqat sanab o'tilgan
yo'llar 9090 (bot) ga boradi, qolgani 8000 (sfatshop backend) ga. `location
/dashboard` PREFIKS bo'yicha ishlagani uchun muharrir yo'li ATAYIN
`/dashboard/menu-editor` qilib olindi — yangi nginx bloki va reload KERAK EMAS.
Boshqa yo'l (masalan `/menu-editor`) tanlansa 8000-portga tushib 404 berardi.

**Web (`services/menu_editor_web.py`, `setup_menu_editor_routes(app)`)**:
`GET /dashboard/menu-editor?menu={key}` → HTML. Ma'lumot (yorliqlar + joriy
layout + default + maxRow) server tomonda `__DATA__` o'rniga JSON qilib
joylanadi — alohida ochiq API endpoint YO'Q. Notanish/bo'sh menu → 404.
Sahifa kalitsiz ochiladi, lekin faqat tugma YORLIQLARINI ko'rsatadi (ular
botda ham ko'rinadi); saqlash esa Telegram imzolagan web_app_data orqali va
faqat Bosh Adminga.

**Sahifa:** vanilla JS/CSS, tashqi kutubxonasiz (telegram-web-app.js dan
tashqari). Ranglar `themeParams` dan (qorong'i/yorug'). Surish — Pointer
Events (HTML5 draggable mobilda ishlamaydi): 300ms bosib ushlash → ghost
element ko'tariladi (scale+soya+haptic), qatorlar orasi = yangi qator (ko'k
chiziq), qator ustiga = birlashtirish (to'la qatorda qizil ramka, rad).
300ms tugamasdan surilsa drag bekor bo'ladi — sahifa skrolli buzilmaydi.

**Bot (`handlers/menu_editor.py`):** `mlay:{menu_key}` endi
`KeyboardButton(web_app=WebAppInfo(...))` yuboradi (inline EMAS — sendData
faqat keyboard-button rejimida ishlaydi). PUBLIC_URL bo'sh bo'lsa eski inline
muharrir fallback sifatida qoladi (lokal ishlab chiqish uchun).
`@router.message(F.web_app_data)` — JSON parse → Bosh Admin tekshiruvi →
`normalize_layout` (notanish/takroriy kalit tashlanadi, qatorda maks 2,
yetishmagani oxiriga) → `set_menu_layout` → tasdiq + admin menyu qaytariladi.

Testlar: `test_menu_webapp.py` (route 200/404, ma'lumot inyeksiyasi, saqlash,
3-tugma rad, ruxsatsiz foydalanuvchi, 8 xil buzuq JSON, shartli tugmalar,
normalizatsiya, sendData hajmi 278 bayt). Surish mantig'i BRAUZERDA haqiqiy
pointer hodisalari bilan sinaldi: birlashtirish, to'la qatorni rad etish,
qatorlar orasiga qo'yish, ajratish, qisqa bosish, skroll niyati, Standart
tugmasi, qorong'i mavzu, sendData yuki — hammasi to'g'ri, konsolda xato yo'q.
Jonli attendance.db tegilmagan. HALI DEPLOY QILINMAGAN.

### 2026-07-20 (4) — Menyu muharriri: yagona navigatsiyali Mini App

Oldingi versiyada har menyu alohida tanlanib alohida tahrirlanardi. Endi bitta
kirish nuqtasi: «🧩 Menyu tartibi» → darhol Mini App (menu parametrisiz URL),
ichida menyular bo'ylab yuriladi.

**Navigatsiya grafi:** `MENU_REGISTRY` ga har menyu uchun `"targets"` qo'shildi
(tugma kaliti → ochiladigan menyu, yoki `"back"`). Xarita HAQIQIY handlerlardan
olindi: `BTN_ADMIN`→admin_panel/admin_panel_bosh (rolga qarab), `BTN_BOSS_FINANCE`
→finance_menu, `BTN_PERSONAL_FINANCE`→pf_menu, `BTN_GRP_*`→grp_*,
`BTN_OFFICE_IP`→ip_menu, `BTN_ADMIN_SETTINGS`→admin_settings,
`BTN_BACK`/`BTN_ADMIN_BACK`→back. `main_employee` da `"conditional"` to'plami
(admin, personal_finance) — muharrirda ◌ belgisi bilan xira ko'rsatiladi.

**DIQQAT — yetim menyular:** `boss_panel` va `grp_finance` navigatsiya orqali
OCHILMAYDI, chunki `BTN_BOSS_PANEL` hech qaysi klaviaturada yo'q (faqat handleri
bor, boss.py:30) va `BTN_GRP_FINANCE` Bosh Admin panelida yo'q. Ular tahrirlab
bo'lmas bo'lib qolmasligi uchun sahifa ildizida "Alohida menyular" ro'yxatida
chiqadi (`_reachable()` grafni hisoblab, yetimlarni topadi — yangi menyu
qo'shilsa avtomatik ishlaydi).

**Sahifa:** rol almashtirgich (Xodim/Boss/Bosh Admin — asosiy menyuning 3
varianti), breadcrumb + Telegram BackButton, slide animatsiya. ODDIY BOSISH =
navigatsiya, BOSIB USHLASH (300ms) = surish. Target'siz tugma bosilsa toast.
O'zgarishlar JS state'da menyular bo'ylab yig'iladi; pastda "💾 Saqlash (N)".

**sendData formati:** `{"layouts": {menu_key: [[...]], ...}}` — FAQAT o'zgargan
menyular. Eski bitta-menyuli format OLIB TASHLANDI (inline muharrir ham —
o'lik kod qoldirilmadi: `_apply/_flatten/_unflatten/_editor_kb`, `mlay:`/`mmv:`/
`mlayr:`/`mnop` handlerlari va 12 ta MENU_EDITOR_* matn o'chirildi).

**Nozik joy:** agar kelgan layout koddagi standart bilan bir xil bo'lsa, bot
`set_menu_layout` emas, `reset_menu_layout` chaqiradi (yozuv O'CHADI). Aks holda
kelajakda koddagi standart o'zgarganda menyu eskisida muzlab qolardi.

Testlar: `test_menu_webapp.py` (11 tekshiruv — barcha menyu inyeksiyasi,
target'lar, orphans, 2 menyuni bir yuborishda saqlash, standartga qaytarishda
yozuv o'chishi, 3-tugma rad, ruxsatsiz foydalanuvchi, 9 xil buzuq JSON —
ESKI format ham rad etiladi, sendData eng yomon holatda 1647 bayt).
`test_menu_layout.py` da navigatsiya grafi butunligi tekshiriladi.
BRAUZERDA sinaldi: rol almashtirish, 3 darajali breadcrumb, ortga qaytish,
menyular orasida yurganda o'zgarishlar yo'qolmasligi, target'siz tugma toast'i,
3-tugma rad, "Shu menyuni standartga", yetim menyu ochilishi — konsolda xato yo'q.
Jonli attendance.db tegilmagan. HALI DEPLOY QILINMAGAN.

### 2026-08-01 — Hisobotlarda 6 oylik arxiv navigatsiyasi (◀️ ▶️) + oy tanlab yopish

Muammo: yangi oy boshlanganda barcha "Bu oy" ekranlari bo'sh Avgustni
ko'rsatardi, Iyulni UI dan ko'rib bo'lmasdi; "Oy yopish" joriy oyga qotirilgan
edi. DB va SQL o'zgarmadi — faqat handler/klaviatura qatlami.

Qo'shildi: `tzutil.prev_month/next_month/months_back/nav_ym` (6 oy chegara,
buzuq callback → joriy oy), universal `kb.month_nav_kb` / `month_excel_kb` /
`month_close_pick_kb`. 8 ekranga nav: moliya xulosa (`finsum`) va Excel
(`finxl`/`finxldl`), PF hisobot (`pfsum`) va Excel (`pfxl`/`pfxldl`), xodim
"Ish haqqim" (`mysal`, faqat o'z ma'lumoti), audit (`audit`), davomat Excel
(`attxl`), xodimlar ish haqqi Excel (`salrep`). Excel ekranlari endi
"{Oy} {yil} uchun Excel tayyorlaymi?" + «📥 Yuklab olish» ko'rinishida.
"Oy yopish" oxirgi 3 oydan tanlaydi (`mclose:{y}:{m}`); tasdiq klaviaturalari
oyni callback ichida olib yuradi (`sal_cm_yes:{y}:{m}`, `sal_cm_reopen:{y}:{m}`).
Yopiq oy sarlavhasida 🔒 (`MONTH_CLOSED_BADGE`). Eski arxiv oqimlari
(`fin_arc`, `pf_arc`, `sal_arc`) va davomat tahriridagi `is_month_closed`
tekshiruvlariga tegilmadi. Test: `test_month_nav.py`.

DEPLOY QILINDI: 2026-08-01 12:08, zaxira `backups/pre-deploy-20260801-120824.tgz`.
Shu deployda menyu muharriri va boshqa to'plangan lokal ishlar ham serverga
chiqdi (md5 solishtiruv: server allaqachon deyarli sinxron edi, faqat nav
fayllari va `requirements.txt` (numpy 2.2.6 — venv'dagi haqiqiy versiyaga
moslandi) yangilandi). GitHub bilan ham sinxron (merge c080759).
Eslatma: serverda git repo YO'Q — deploy tar orqali.

### 2026-08-01 (2) — Ish haqqi yozuvida oy tanlash (for_ym) + eski oy yozuvini bekor qilish

Muammo: bonus/avans/jarima doim `created_at` oyiga tushardi — yangi oy
boshlangach o'tgan oy uchun bonus yozib bo'lmasdi (Excel/hisobotlarga chiqmasdi),
bekor qilish ham faqat joriy oy yozuvlarini ko'rsatardi.

Yechim: `salary_entries.for_ym TEXT` ustuni (migratsiya init_db da; eski
yozuvlar NULL → created_at oyidan hisoblanadi). `add_salary_entry(for_ym=...)`.
Oy filtrlari `COALESCE(for_ym, strftime('%Y-%m', created_at, '+5 hours'))`.
Qo'shish oqimi: xodim → tur → **oy (oxirgi 3 oy, yopiqlari 🔒 alert)** → summa
→ sabab. Bekor qilish: xodim → **oy** → yozuvlar. Yopiq oyga yozish/bekor
qilish barcha nuqtalarda bloklanadi (saqlash oldidan qayta tekshiriladi).
Audit qatorida boshqa oyga tegishli yozuvga "Tegishli oy: ..." qo'shiladi.
SALARY_ADD_SAVED / NOTIFY_SALARY_ADDED endi oyni ko'rsatadi (moliya avans
bildirishnomasi ham moslandi). Prefikslar: `sal_month:`, `sal_cancmon:`.
Test: `test_month_nav.py` ga for_ym stsenariylari qo'shildi.

### 2026-08-31 — Bildirishnomalar bo'limi: eslatma kunlari + bayram/dam olish kalendari

Moliya bo'limi pastiga «🔔 Bildirishnomalar» tugmasi qo'shildi (Boss va Bosh
Admin uchun). Ichida uchta ekran:

**1. 📅 Eslatma kunlari** — haftaning qaysi kunlari davomat eslatmasi
yuborilishi. Sozlama: `settings['reminder_days']` — 7 belgili satr, indeks
0=Dushanba ... 6=Yakshanba, '1'=yuboriladi. Standart `'1111111'`; buzuq qiymat
kelsa jimgina standartga qaytadi (bot yiqilmaydi). `get_reminder_days()`,
`set_reminder_days()`, `toggle_reminder_day()`. Callback: `rday:{0..6}`,
`rday:close`.

**2. 🎉 Bayram kunlari** va **3. 🏖 Dam olish kunlari** — ATAYIN ikki alohida
tugma, chunki dam berilib ish haqqi hisoblanmasligi ham, bayram bo'lib to'liq
stavka yozilishi ham mumkin:

| Tur | Jadval qiymati | Eslatma | Ish haqqi |
|---|---|---|---|
| Bayram | `calendar_days.day_type='holiday'` | yuborilmaydi | har xodimga **+1 kunlik to'liq stavka** |
| Dam olish | `calendar_days.day_type='dayoff'` | yuborilmaydi | hisoblanmaydi (kelib ishlasa — odatdagidek) |

**Baza:** yangi jadval `calendar_days (day_date PK, day_type CHECK IN
('holiday','dayoff'), title, created_by, created_at)`. Funksiyalar:
`get_calendar_day(_type)`, `set_calendar_day`, `clear_calendar_day`,
`toggle_calendar_day` (bo'sh→tur, o'sha tur→bo'sh, boshqa tur→almashadi),
`get_calendar_month`, `get_calendar_days_by_type`, `is_non_working_day`.

**Ish haqqi:** `get_monthly_holiday_pay(emp, y, m)` — YAGONA joy,
`get_monthly_base_salary` oxirida qo'shiladi, shuning uchun Excel, "Ish haqqim",
xodim kartochkasi, audit — hammasi avtomatik moslashdi. Qoida: bayram kuni
hammaga bir kunlik stavka, ishga kelgan bo'lsa ishlagani ham USTIGA qo'shiladi.
Istisnolar: kunlik stavkasi yo'q (eski soatbay) xodimga qo'llanmaydi; faolsiz
(o'chirilgan) xodimga yozilmaydi (aks holda hisobotda barcha o'chirilganlar
paydo bo'lardi); xodim ro'yxatdan o'tgan kundan OLDINGI bayramlar hisoblanmaydi.

**Eslatmalar (`services/reminders.py`):** eski `WEEKEND_DAYS` konstantasi
o'chirildi. `_tick` boshida tartib: `reminders_enabled` → hafta kuni jadvali →
`is_non_working_day(bugun)`.

**Kalendar klaviaturasi (`kb.calendar_kb(mode, year, month)`):** oy sarlavhasi,
Du–Ya qatori, kunlar to'ri (belgilangan kun emoji bilan: 🎉 / 🏖), pastda
◀️ / 🚪 Yopish / ▶️. Callbacklar: `cal:{h|o}:{YYYY-MM-DD}` (toggle),
`caln:{h|o}:{yil}:{oy}` (oy), `calnop` (bo'sh katak), `cal:close`.
DIQQAT: `cal:` prefiksi `caln:` ni tutmaydi (':' vs 'n') — `fin_del:`/`fin_delc:`
bilan bir xil naqsh. Oy oralig'i: joriy oydan −12 … +12 (`CAL_NAV_BACK/FWD`).

**Yangi/o'zgargan fayllar:** `handlers/notifications.py` (yangi router, bot.py da
`finance` dan keyin), `database.py`, `keyboards.py` (MENU_REGISTRY: `notify_menu`
+ `finance_menu` ga `notifications`), `texts.py`, `services/reminders.py`,
`bot.py`. Testlar: yangi `test_notifications.py` (kalendar CRUD, hafta kunlari,
bayram stavkasi, klaviaturalar, eslatma sikli, handlerlar — ruxsatsiz
foydalanuvchi va buzuq callbacklar bilan); `test_menu_parity.py` va
`test_menu_webapp.py` yangi tugmaga moslandi. Jonli `attendance.db` tegilmagan.

DEPLOY QILINDI: 2026-08-31 17:34, zaxira `backups/pre-deploy-20260831-173418.tgz`.
Serverda `calendar_days` jadvali avtomatik yaratildi, log toza, servis `active`.
`deploy.sh` FILES ro'yxatiga uchala test fayli ham qo'shildi (aks holda serverdagi
eski nusxalar tufayli `./deploy.sh check` doim ogohlantirardi). Python 3.14 da
`asyncio.get_event_loop()` endi loop yaratmagani uchun `test_notifications.py`
`asyncio.run` ga o'tkazildi.

**Payroll hisoboti — faqat `role='employee'`.** `get_all_employees_salary_summary`
endi rahbariyatni (boss / bosh_admin) o'tkazib yuboradi: ular kunbay
hisoblanmaydi, shuning uchun ish haqqi Excelida ko'rinmasligi kerak
(Jaloliddin — bosh_admin, Azizjon va Kamron — boss). Test:
`test_payroll_roles.py`.

Tekshiruv (2026-08-31, jonli baza): bayram haqqi barcha haqiqiy xodimlarga
qo'shilgan — `base − davomat_qismi` har birida aynan bir kunlik stavkaga teng
(Manzura/Maftuna/Nodira/Jahongir +150 000, Feruza +130 000, Fayozbek +230 000).
DIQQAT: bayram summasi hech qayerda alohida qator bo'lib ko'rinmaydi, jimgina
«Asosiy ish haqqi» ichiga qo'shiladi — shuning uchun tashqaridan «hisoblanmadi»
bo'lib tuyuladi.
