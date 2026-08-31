# 🚀 Deploy yo'riqnomasi — Bildirishnomalar bo'limi (2026-08-31)

> **Claude Code uchun:** bu fayl bitta vazifani BOSHIDAN OXIRIGACHA bajarish
> uchun yozilgan. Bosqichlarni tartib bilan bajar, har bosqich natijasini
> foydalanuvchiga ko'rsat. TO'XTASH shartlari alohida belgilangan — ular
> yuz bersa o'zboshimchalik bilan davom etma, foydalanuvchidan so'ra.

**Vazifa:** lokalda tayyor va commit qilingan «🔔 Bildirishnomalar» bo'limini
jonli serverga (`/opt/davomat`) chiqarish va ishlashini tekshirish.

**Loyiha:** `/Users/jb89/Desktop/attendance_bot` (aiogram 3.x davomat boti)
**Server:** `root@45.138.158.174`, kod `/opt/davomat/`, baza
`/opt/davomat/attendance.db`, servis `davomat`, log `/var/log/davomat.log`.
**Serverda git YO'Q** — deploy tar orqali (`deploy.sh` shu ishni qiladi).

---

## 0. Nima o'zgargani (kontekst)

Moliya bo'limi pastiga «🔔 Bildirishnomalar» tugmasi qo'shildi (Boss va Bosh
Admin ko'radi). Ichida 3 ta ekran:

| Ekran | Vazifasi |
|---|---|
| 📅 Eslatma kunlari | Haftaning qaysi kunlari davomat eslatmasi yuboriladi (7 ta toggle) |
| 🎉 Bayram kunlari | Inline kalendar. Belgilangan kunda **eslatma yo'q + har xodimga to'liq kunlik stavka** |
| 🏖 Dam olish kunlari | Inline kalendar. Belgilangan kunda **eslatma yo'q, ish haqqi hisoblanmaydi** |

Bayram va dam olish ATAYIN ikki alohida tugma: dam berilib ish haqqi
hisoblanmasligi ham, bayram bo'lib to'liq stavka yozilishi ham mumkin.

**O'zgargan/yangi fayllar** (git commit `3432cfa` va `db2174c`):

```
bot.py                     notifications routerini ulash
database.py                calendar_days jadvali + CRUD + get_monthly_holiday_pay
keyboards.py               MENU_REGISTRY: notify_menu, finance_menu ga notifications;
                           calendar_kb(), remind_days_kb(), notify_menu_kb()
texts.py                   yangi tugma matnlari va ekran matnlari
services/reminders.py      WEEKEND_DAYS o'chdi -> reminder_days + calendar_days
handlers/notifications.py  YANGI router
test_notifications.py      YANGI test (6 blok)
deploy.sh                  YANGI: check / push
docs/LOYIHA_MALUMOT.md     2026-08-31 yozuvi
```

**Baza migratsiyasi:** `init_db()` ichida `CREATE TABLE IF NOT EXISTS
calendar_days (...)`. Bot ishga tushganda avtomatik yaratiladi, mavjud
ma'lumotga tegmaydi, orqaga qaytish (rollback) xavfsiz — eski kod bu
jadvalni shunchaki ko'rmaydi.

---

## 1. Lokal holatni tasdiqlash

```bash
cd ~/Desktop/attendance_bot
git log --oneline -3
git status --short
./venv/bin/python test_notifications.py
./venv/bin/python test_menu_parity.py
./venv/bin/python test_menu_layout.py
./venv/bin/python test_menu_webapp.py
./venv/bin/python test_month_nav.py
./venv/bin/python test_shift_norm.py
./venv/bin/python test_pf_archive.py
```

Kutiladi: oxirgi 2 commit `db2174c` (deploy.sh) va `3432cfa` (Bildirishnomalar),
barcha testlar «HAMMASI O'TDI» / «Barcha testlar o'tdi».

**⛔️ TO'XTA:** biror test yiqilsa — deploy QILMA, xatoni foydalanuvchiga
ko'rsat va sababini tekshir.

> Eslatma: `attendance.db` (jonli lokal nusxa) hech qaysi testda
> o'zgartirilmaydi — hammasi vaqtinchalik bazada ishlaydi.
> **Lokal botni polling bilan ishga TUSHIRMA** — produksiya bilan
> to'qnashadi (Telegram 409).

## 2. Server bilan solishtirish (MAJBURIY)

```bash
./deploy.sh check
```

Bu barcha `.py` fayllarni server bilan md5 bo'yicha solishtiradi.

- `✅ Server bilan sinxron.` chiqsa — 3-bosqichga o't.
- Faqat men o'zgartirgan fayllar (`bot.py`, `database.py`, `keyboards.py`,
  `texts.py`, `services/reminders.py`, `handlers/notifications.py`) farq
  qilsa — bu KUTILGAN holat, davom et.
- **⛔️ TO'XTA:** boshqa fayl farq qilsa yoki `➖ faqat SERVERDA` chiqsa —
  serverga boshqa chatdan yangi kod deploy qilingan. Ustiga YOZMA. Avval
  farqni ko'rsat:
  ```bash
  ssh root@45.138.158.174 "cat /opt/davomat/<FAYL>" > /tmp/srv_<FAYL>
  diff /tmp/srv_<FAYL> <FAYL>
  ```
  va foydalanuvchidan qanday birlashtirishni so'ra.

## 3. Deploy

```bash
./deploy.sh push
```

Skript ketma-ket: zaxira (`/opt/davomat/backups/pre-deploy-*.tgz`) →
fayllarni tar orqali yuborish → serverda `py_compile` → `systemctl restart
davomat` → holat va log oxiri.

Kutiladi: `active` va logda `🤖 Bot ishga tushdi: @...` hamda
`🔔 Eslatmalar sikli ishga tushdi`.

**⛔️ TO'XTA:** `py_compile` xato bersa yoki servis `active` bo'lmasa —
darhol 6-bo'limdagi rollbackni bajar.

## 4. Serverda tekshirish

```bash
ssh root@45.138.158.174 "systemctl is-active davomat && \
  sqlite3 /opt/davomat/attendance.db \
  \"SELECT name FROM sqlite_master WHERE type='table' AND name='calendar_days';\" && \
  tail -n 30 /var/log/davomat.log"
```

Kutiladi: `active`, `calendar_days`, logda Traceback YO'Q.

> `sqlite3` bo'lmasa: `ssh root@45.138.158.174 "/opt/davomat/venv/bin/python -c \"import sqlite3;print(sqlite3.connect('/opt/davomat/attendance.db').execute(\\\"SELECT name FROM sqlite_master WHERE name='calendar_days'\\\").fetchall())\""`

## 5. Telegramda qo'lda tekshirish (foydalanuvchiga ro'yxatni ber)

1. Botda `/start` → **💰 Moliya bo'limi** → pastda **🔔 Bildirishnomalar** turibdimi?
2. **📅 Eslatma kunlari** → kunni bosganda ✅ ⇄ ⬜ almashadimi, xabar
   yangilanadimi?
3. **🎉 Bayram kunlari** → kalendar chiqadimi, kunni bosganda `🎉` paydo
   bo'ladimi, ◀️ ▶️ oy almashtiradimi, qayta bosganda belgi ketadimi?
4. **🏖 Dam olish kunlari** → xuddi shunday, `🏖` belgisi bilan.
5. **⬅️ Moliya bo'limiga** → Moliya menyusiga qaytaradimi?
6. Bayram belgilangan oy uchun **Ish haqqi → Excel hisobot**: o'sha xodimlar
   «Asosiy ish haqqi» ustuni har bayram kuniga bir kunlik stavkaga oshdimi?

## 6. Rollback (kerak bo'lsa)

```bash
ssh root@45.138.158.174 "cd /opt/davomat && ls -t backups | head -3"
ssh root@45.138.158.174 "cd /opt/davomat && tar xzf backups/<ENG_YANGI>.tgz && \
  systemctl restart davomat && sleep 4 && systemctl is-active davomat"
```

Baza migratsiyasi qaytarilmaydi va shart emas: eski kod `calendar_days`
jadvalini ishlatmaydi, u shunchaki bo'sh turadi.

## 7. Yakuniy qadamlar

1. `docs/LOYIHA_MALUMOT.md` dagi 2026-08-31 yozuvining oxiriga qo'sh:
   `DEPLOY QILINDI: <sana vaqt>, zaxira backups/pre-deploy-<...>.tgz`
2. Commit:
   ```bash
   git add docs/LOYIHA_MALUMOT.md && git commit -m "docs: 2026-08-31 bildirishnomalar deploy qaydi"
   ```
3. GitHub bilan sinxron bo'lsa: `git push`
4. Foydalanuvchiga qisqa hisobot: nima chiqdi, zaxira nomi, tekshiruv natijasi.
