# 🔍 Tekshiruv yo'riqnomasi — 2026-08-31 o'zgarishlari

> **Claude Cowork uchun.** Bu **tekshiruv** yo'riqnomasi, deploy emas.
> Vazifangiz: quyidagi o'zgarishlar haqiqatan ishlayotganini mustaqil
> tasdiqlash. **Kod o'zgartirmang, deploy qilmang, serverda hech narsa
> o'chirmang.** Nomuvofiqlik topsangiz — to'xtang va foydalanuvchiga
> aniq dalil bilan xabar bering.

**Loyiha:** `/Users/jb89/Desktop/attendance_bot` (aiogram 3.x davomat boti)
**Server:** `root@45.138.158.174`, kod `/opt/davomat/`, baza
`/opt/davomat/attendance.db`, servis `davomat`, log `/var/log/davomat.log`.
**Holat:** hammasi serverga chiqarilgan va GitHub'ga push qilingan.

---

## 0. Nima tekshiriladi

| Commit | Mazmuni |
|---|---|
| `3432cfa` | 🔔 Bildirishnomalar bo'limi — eslatma kunlari + bayram/dam olish kalendari |
| `db2174c` | `deploy.sh` — server bilan solishtirish (`check`) va deploy (`push`) |
| `281e90d` | `test_notifications.py` Python 3.14 uchun `asyncio.run` ga o'tkazildi |
| `23800fa` | Deploy qaydi + `deploy.sh` FILES ro'yxatiga testlar |
| `8cf88b3` | **Payroll:** ish haqqi Excelida rahbariyat yo'q |
| `34386cc` | **Bayram summasi ko'rinadigan bo'ldi** + rahbariyat davomat/xodim Excellaridan ham chiqdi |

Ikkita asosiy da'vo tekshirilishi kerak:

1. **Bayram kuni uchun har bir xodimga bir kunlik to'liq stavka qo'shiladi.**
   Foydalanuvchi «hisoblanmadi» deb shubha qilgan edi — 4-bosqich shuni
   raqam bilan hal qiladi.
2. **Ish haqqi Excelida rahbariyat ko'rinmaydi** (kunbay hisoblanmaydi):
   Jaloliddin (`bosh_admin`), Azizjon va Kamron (`boss`).

---

## 1. Lokal holat va testlar

```bash
cd ~/Desktop/attendance_bot && git log --oneline -5
```

```bash
cd ~/Desktop/attendance_bot && for t in test_notifications test_menu_parity test_menu_layout test_menu_webapp test_month_nav test_shift_norm test_pf_archive test_payroll_roles; do printf "%-22s " $t; ./venv/bin/python $t.py >/dev/null 2>&1 && echo OK || echo "❌ YIQILDI"; done
```

Kutiladi: sakkiztasi ham `OK`. Oxirgi commit `8cf88b3`.

**⛔️ TO'XTA:** biror test yiqilsa — sababini aniqlang va xabar bering,
o'zingiz tuzatmang.

> **Lokal botni polling bilan ishga TUSHIRMANG** — produksiya bilan
> to'qnashadi (Telegram 409 xatosi).
> Testlar jonli `attendance.db` ga tegmaydi, hammasi vaqtinchalik bazada.

---

## 2. Lokal kod server bilan bir xilmi

```bash
cd ~/Desktop/attendance_bot && ./deploy.sh check 2>&1 | grep -v '\._'
```

Kutiladi: `≠ FARQ:` qatori **umuman bo'lmasin**.

> `grep -v '\._'` nima uchun: serverda `._bot.py`, `._database.py` kabi ~25 ta
> fayl bor. Bular macOS'ning AppleDouble metama'lumot axlati, eski tar orqali
> tushib qolgan — kod emas, hech qayerda import qilinmaydi. Ular tufayli
> `check` doim ogohlantirish beradi. **O'chirmang**, shunchaki e'tiborsiz
> qoldiring (tozalash foydalanuvchi qaroriga havola qilingan).

---

## 3. Server sog'ligi

```bash
ssh root@45.138.158.174 "systemctl is-active davomat; /opt/davomat/venv/bin/python -c \"import sqlite3;print(sqlite3.connect('/opt/davomat/attendance.db').execute(\\\"SELECT name FROM sqlite_master WHERE name='calendar_days'\\\").fetchall())\"; tail -n 25 /var/log/davomat.log"
```

Kutiladi: `active`, `[('calendar_days',)]`, logda **Traceback yo'q**, va
oxirgi ishga tushishda `🤖 Bot ishga tushdi: @Sfatshop_Xodimlar_bot` hamda
`🔔 Eslatmalar sikli ishga tushdi (har 60s)` qatorlari bor.

---

## 4. ⭐️ Bayram haqqi haqiqatan qo'shilganmi (eng muhim bosqich)

Bu yerda hiyla bor: bayram summasi **hech qayerda alohida yozilmaydi**, u
jimgina «Asosiy ish haqqi» ichiga qo'shilib ketadi va «Ishlagan kunlar» soni
o'zgarmaydi. Shuning uchun hisobotga qarab turib uni ko'rib bo'lmaydi —
faqat hisoblab tekshirish mumkin.

Usul: har bir xodim uchun davomatdan kelib chiqadigan summani mustaqil
hisoblab, hisobotdagi `base` dan ayiramiz. Farq aynan bir kunlik stavkaga
teng bo'lishi kerak (avgustda bitta bayram — `2026-08-31`).

```bash
ssh root@45.138.158.174 "cd /opt/davomat && ./venv/bin/python - <<'PY'
import database as db
Y, M = 2026, 8
for e in db.get_all_employees(active_only=True):
    if e['role'] != 'employee' or not e['daily_rate']:
        continue
    i = e['id']; rate = e['daily_rate']
    norm = db.get_effective_shift_norm(i, Y, M)
    att = 0
    for r in db.get_monthly_attendance(i, Y, M):
        if not r['first_in'] or not r['last_out']:
            continue
        ih, im, _ = map(int, r['first_in'].split(':'))
        oh, om, _ = map(int, r['last_out'].split(':'))
        w = (oh * 60 + om) - (ih * 60 + im)
        if w > 0:
            att += int(min(w, 720) / norm * rate)
    base = db.get_monthly_base_salary(i, Y, M)
    hpay = db.get_monthly_holiday_pay(i, Y, M)
    ok = 'OK' if base - att == hpay else 'XATO'
    print(f\"{ok:5} {e['full_name'][:24]:26} base-davomat={base-att:>8}  bayram={hpay:>8}\")
PY"
```

Kutilgan natija — har qatorda `OK`, va farq stavkaga teng:

| Xodim | base − davomat | Kunlik stavka |
|---|---|---|
| Kodirova Manzura | 150 000 | 150 000 |
| Kuchkeldiyeva Maftuna | 150 000 | 150 000 |
| Niyatqobilov Fayozbek | 230 000 | 230 000 |
| Qosimova Nodira | 150 000 | 150 000 |
| Shavkatova Feruza | 130 000 | 130 000 |
| Xushmatov Jahongir | 150 000 | 150 000 |

**⛔️ TO'XTA:** birorta `XATO` chiqsa — bu haqiqiy nosozlik. Qaysi xodim,
qanday farq ekanini yozing va to'xtang.

> Eslatma: `2026-08-31` bayram bo'lgani bilan xodimlar o'sha kuni ishga
> kelgan, shuning uchun ular o'sha kun uchun **ham ishlagan vaqtini, ham
> to'liq stavkani** oladi. Qoida shunday kelishilgan.

### 4b. Bayram summasi hisobotlarda KO'RINADIMI

Bu 2026-09-01 da qo'shildi: ilgari summa jimgina «Asosiy ish haqqi» ichida
edi, endi alohida ko'rsatiladi.

```bash
ssh root@45.138.158.174 "cd /opt/davomat && ./venv/bin/python - <<'PY'
import sys, types, io
f = types.ModuleType('face_recognition'); f.face_encodings = lambda *a, **k: []
sys.modules.setdefault('face_recognition', f)
from openpyxl import load_workbook
from handlers.emp_data import _build_emp_excel
ws = load_workbook(io.BytesIO(_build_emp_excel(7, 2026, 8))).active
for row in ws.iter_rows(values_only=True):
    vals = [str(v) for v in row if v is not None]
    if vals:
        print(' | '.join(vals))
PY"
```

Kutiladi (Kuchkeldiyeva Maftuna, avgust):

| Qator | Ko'rinishi |
|---|---|
| `30.08.2026` | `🏖 Dam olish` — ilgari qizil «kelmagan» edi |
| `31.08.2026` | `🎉 Bayram kuni` va summa ustunida `150000` |
| Xulosa | `💵 Asosiy ish haqqi: 3333879`, ostida `🎉 Shundan bayram (1 kun): 150000` |

Xodimning o'z profilida ham xuddi shu qator chiqadi:

```bash
ssh root@45.138.158.174 "cd /opt/davomat && ./venv/bin/python - <<'PY'
import sys, types
f = types.ModuleType('face_recognition'); f.face_encodings = lambda *a, **k: []
sys.modules.setdefault('face_recognition', f)
import database as db
from handlers.profile import _salary_view
print(_salary_view(db.get_employee_by_id(7), 2026, 8)[:420])
PY"
```

Kutiladi: `🕐 Asosiy ish haqqi: +3,333,879 so'm` qatoridan keyin
`🎉 Shundan bayram (1 kun): 150,000 so'm`.

Qo'shimcha: kalendar yozuvlarini ko'rish (avgustda 5 ta dam olish yakshanbasi
va 1 ta bayram bo'lishi kerak):

```bash
ssh root@45.138.158.174 "cd /opt/davomat && ./venv/bin/python -c \"import database as db; print(db.get_calendar_month(2026, 8))\""
```

---

## 5. Ish haqqi Excelida faqat oddiy xodimlar

Haqiqiy Excel faylni serverda yaratib, ichidagi qatorlarni o'qiymiz:

```bash
ssh root@45.138.158.174 "cd /opt/davomat && ./venv/bin/python - <<'PY'
import sys, types, io
f = types.ModuleType('face_recognition'); f.face_encodings = lambda *a, **k: []
sys.modules.setdefault('face_recognition', f)
from handlers.admin import _generate_salary_excel
from openpyxl import load_workbook
ws = load_workbook(io.BytesIO(_generate_salary_excel(2026, 8))).active
for r in ws.iter_rows(min_row=3, max_row=ws.max_row, values_only=True):
    if r[1]:
        print(r[0], '|', str(r[1])[:26], '| ASOSIY:', r[5], '| BAYRAM:', r[12])
PY"
```

Kutiladi: **aynan 6 qator** — Manzura, Maftuna, Fayozbek, Nodira, Feruza,
Jahongir. Ro'yxatda **Jaloliddin, Azizjon, Kamron BO'LMASLIGI kerak**.
Oxirgi (13-) ustun `🎉 Shundan bayram` — har birida o'z kunlik stavkasi.

> 13-ustun ataylab eng oxirida: bayram summasi «Asosiy ish haqqi» ICHIDA,
> shuning uchun `JAMI` formulasi (`=SUM(F:K)`) unga tegmasligi kerak. Agar u
> yig'indiga kirib qolsa — summa ikki marta hisoblanadi.

Xuddi shu filtr «barcha xodimlar» Excelida ham amal qiladi:

```bash
ssh root@45.138.158.174 "cd /opt/davomat && ./venv/bin/python - <<'PY'
import sys, types, io
f = types.ModuleType('face_recognition'); f.face_encodings = lambda *a, **k: []
sys.modules.setdefault('face_recognition', f)
from openpyxl import load_workbook
from handlers.emp_data import _build_all_emp_excel
print(load_workbook(io.BytesIO(_build_all_emp_excel(2026, 8))).sheetnames)
PY"
```

Kutiladi: 6 ta sheet, rahbariyat yo'q.

Filtr qoidasi: `database.py` → `get_payroll_employees()` — `boss` va
`bosh_admin` rollarini chiqarib tashlaydi. `admin` roli **qoladi**: u
haqiqiy, ish haqqi oladigan xodim bo'lishi mumkin. Rollarni ko'rish:

```bash
ssh root@45.138.158.174 "cd /opt/davomat && ./venv/bin/python -c \"import database as db; [print(e['id'], e['role'], e['full_name'][:26]) for e in db.get_all_employees(active_only=True)]\""
```

---

## 6. Telegramda qo'lda tekshirish

Botda Boss yoki Bosh Admin hisobi bilan:

1. `/start` → **💰 Moliya bo'limi** → pastda **🔔 Bildirishnomalar** turibdimi?
2. **📅 Eslatma kunlari** → kunni bosganda ✅ ⇄ ⬜ almashadimi, xabar
   darhol yangilanadimi?
3. **🎉 Bayram kunlari** → kalendar chiqadimi; kun bosilganda `🎉` paydo
   bo'ladimi; ◀️ ▶️ oyni almashtiradimi; qayta bosilganda belgi ketadimi?
4. **🏖 Dam olish kunlari** → xuddi shunday, `🏖` belgisi bilan.
   Avgustda 2, 9, 16, 23, 30-kunlar `🏖`, 31-kun `🎉` bo'lib turishi kerak.
5. **⬅️ Moliya bo'limiga** → Moliya menyusiga qaytaradimi?
6. **Ish haqqi → Excel hisobot (Avgust 2026)** → faylda 6 ta xodim,
   rahbariyat yo'q (5-bosqich natijasi bilan bir xil bo'lishi kerak), oxirgi
   ustunda `🎉 Shundan bayram`.
7. Xodim hisobi bilan **💰 Ish haqqim** → «Asosiy ish haqqi» ostida
   `🎉 Shundan bayram (1 kun): 150,000 so'm` qatori bormi?
8. **Xodimlar ma'lumoti → Excel** → 31.08 qatori `🎉 Bayram kuni` va summa
   bilan, 30.08 esa `🏖 Dam olish` (qizil «kelmagan» emas).

> Kalendar tugmalari faqat Boss va Bosh Admin uchun ishlaydi — oddiy xodim
> bosganda hech nima o'zgarmasligi kerak (bu holat testda ham qoplangan).

---

## 7. Ma'lum kamchiliklar — bular nosozlik EMAS

Bularni «xato topdim» deb yozmang, ular ataylab shunday qoldirilgan va
foydalanuvchi qaroriga havola qilingan:

| Holat | Izoh |
|---|---|
| Jaloliddin va Azizjon profilida bayram haqqi 0 | Ularda `daily_rate = 0` va lavozim yo'q. Kunlik stavkasi yo'q xodimga bayram haqqi yozilmaydi — kodda ataylab shunday. |
| Bayram kunida ishga kelgan xodimga ikki xil to'lov | Ishlagan vaqti + to'liq stavka. Qoida shunday kelishilgan, xato emas. Xodim Excelida bunday kun `9s 15d + 🎉 bayram` deb belgilanadi. |
| Kamron (`boss`, demo hisob) profilida bayram haqqi bor | Uning `daily_rate = 150 000`. Excelga endi kirmaydi, lekin o'z profilida summa ko'rinadi. Hisobni o'chirish/faolsizlantirish taklif qilingan. |
| Serverdagi `._*` fayllar | macOS metama'lumot axlati, kod emas. |

---

## 8. Rollback (faqat jiddiy nosozlikda, foydalanuvchi ruxsati bilan)

```bash
ssh root@45.138.158.174 "cd /opt/davomat && ls -t backups | head -3"
```

```bash
ssh root@45.138.158.174 "cd /opt/davomat && tar xzf backups/<ENG_YANGI>.tgz && systemctl restart davomat && sleep 4 && systemctl is-active davomat"
```

Baza migratsiyasini qaytarish shart emas: eski kod `calendar_days` jadvalini
ishlatmaydi, u shunchaki bo'sh turadi.

---

## 9. Hisobot shakli

Tekshiruv tugagach quyidagilarni yozing:

1. 1-bosqich: nechta test o'tdi (`8/8` kutiladi).
2. 2-bosqich: sinxronmi.
3. 3-bosqich: servis holati, `calendar_days` bormi, logda Traceback bormi.
4. **4-bosqich: har bir xodim uchun `OK`/`XATO` va farq raqamlari** — bu eng
   muhimi, raqamlarni to'liq keltiring.
   4b: bayram qatori Excelda va profilda ko'rindimi.
5. 5-bosqich: Excelda nechta qator, rahbariyat bormi.
6. 6-bosqich: Telegramdagi qaysi qadam ishladi/ishlamadi.
7. Nomuvofiqlik topilsa — kutilgan va haqiqiy natijani yonma-yon yozing.
