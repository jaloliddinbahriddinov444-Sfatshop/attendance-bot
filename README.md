# 📋 Davomat Bot

Telegram bot — kichik jamoa (15 xodimgacha) uchun ish davomatini avtomatik qayd qiluvchi tizim.

## ✨ Imkoniyatlar

- ✅ Xodimlarni o'z-o'zidan ro'yxatdan o'tkazish (F.I.Sh, telefon, lavozim, boshlang'ich selfi)
- 📍 **GPS lokatsiya** orqali ishxonada ekanligini tekshirish
- 📶 **Wi-Fi nomi** orqali qo'shimcha tekshiruv (mos kelmasa admin ogohlantirish oladi)
- 🤳 **Yuz tanish** (`face_recognition`) — boshqa odam rasmini yuborolmaydi
- 📊 Shaxsiy oylik statistika (kelgan kunlar, kechikishlar, ish vaqti)
- ⚙️ Admin panel:
  - Xodimlar ro'yxati
  - Xodim o'chirish/qayta tiklash
  - Admin tayinlash
  - Bugungi davomat hisoboti
  - Ishxona koordinatalari, radius, Wi-Fi, ish vaqtini sozlash
  - **Excel hisobot** (oylik)
- 🚨 Avtomatik xabarlar:
  - Wi-Fi mos kelmaganda → adminlarga
  - Yuz mos kelmaganda → adminlarga

## 🛠 Texnologiyalar

- Python 3.11+
- aiogram 3.x (Telegram Bot framework)
- SQLite (kichik jamoa uchun ideal)
- face_recognition (dlib asosida)
- openpyxl (Excel eksport)

## 📦 O'rnatish

### 1. Botni Telegram'da yarating
1. Telegramda [@BotFather](https://t.me/BotFather) ga kiring
2. `/newbot` buyrug'ini bering
3. Bot nomi va @username ni belgilang
4. Sizga berilgan **TOKEN** ni saqlab qo'ying

### 2. O'z Telegram ID ingizni oling
1. [@userinfobot](https://t.me/userinfobot) ga `/start` yuboring
2. Sizning `id` raqamingizni ko'rsatadi (masalan `123456789`)
3. Bu raqam **birinchi admin** sifatida ishlatiladi

### 3. Tizim talablari (Linux/Ubuntu)

`face_recognition` kutubxonasi `dlib` ga asoslangan — kompilyatsiya uchun:

```bash
sudo apt update
sudo apt install -y python3-pip python3-dev cmake build-essential \
                    libboost-all-dev libopenblas-dev liblapack-dev libx11-dev
```

**Windows** uchun: [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) o'rnatish kerak (C++ rivojlantirish to'plami bilan).

**macOS** uchun: `brew install cmake`

### 4. Loyihani yuklash va kutubxonalarni o'rnatish

```bash
# Loyiha ichiga kiring
cd attendance_bot

# Virtual muhit yaratish (tavsiya etiladi)
python3 -m venv venv
source venv/bin/activate          # Linux/macOS
# venv\Scripts\activate           # Windows

# Kutubxonalarni o'rnatish
pip install -r requirements.txt
```

> ⏳ `face-recognition` o'rnatilishi 5-15 daqiqa olishi mumkin (dlib kompilyatsiya qilinadi).

### 5. Sozlash

```bash
cp .env.example .env
```

`.env` faylni oching va to'ldiring:

```
BOT_TOKEN=8123:AAH...          # @BotFather dan olgan token
INITIAL_ADMIN_ID=123456789     # sizning Telegram ID
OFFICE_LAT=41.311081           # ishxona koordinatasi (keyinroq botda o'zgartirsa bo'ladi)
OFFICE_LON=69.240562
OFFICE_RADIUS=50               # metrda
OFFICE_WIFI=Office_WiFi        # ishxona Wi-Fi nomi
WORK_START=09:00
WORK_END=18:00
```

### 6. Ishga tushirish

```bash
python bot.py
```

Konsolda `Bot ishga tushdi: @your_bot_username` xabari chiqsa — tayyor!

## 🚀 Birinchi foydalanish

1. Botingizga `/start` yuboring
2. F.I.Sh, telefon, lavozim, selfini yuboring
3. `INITIAL_ADMIN_ID` to'g'ri kiritilgan bo'lsa, siz **avtomatik admin** bo'lasiz
4. **⚙️ Admin panel** orqali ishxona sozlamalarini to'g'rilang:
   - Koordinatalar (ishxonangizdan turib lokatsiya yuboring)
   - Radius (masalan, 50m)
   - Wi-Fi nomi
   - Ish vaqti
5. Endi havolani xodimlarga yuboring va ular ro'yxatdan o'tsin

## 🏗 Loyiha tuzilishi

```
attendance_bot/
├── bot.py                  # Asosiy ishga tushirish fayli
├── config.py               # .env va konstantalar
├── database.py             # SQLite va barcha so'rovlar
├── keyboards.py            # Tugmalar
├── states.py               # FSM holatlari
├── texts.py                # Barcha O'zbek matnlar
├── requirements.txt        # Kutubxonalar
├── .env.example            # Sozlamalar namunasi
├── handlers/
│   ├── common.py           # /start, /cancel, fallback
│   ├── registration.py     # Ro'yxatdan o'tish oqimi
│   ├── attendance.py       # Keldim/Ketdim oqimi
│   ├── profile.py          # Profil va statistika
│   └── admin.py            # Admin panel
└── services/
    ├── face_service.py     # face_recognition wrapper
    └── location_service.py # GPS masofa hisoblash
```

## 🔒 Xavfsizlik haqida muhim eslatma

**Wi-Fi cheklov:** Telegram bot foydalanuvchi qaysi Wi-Fi'ga ulanganini avtomatik tekshira olmaydi (iOS/Android xavfsizlik cheklovi). Shuning uchun xodim Wi-Fi nomini qo'lda kiritadi. Bu **mutlaq himoya emas**, lekin **GPS + yuz tanish** kombinatsiyasi bilan amaliy aldovni juda qiyinlashtiradi:

| Tekshiruv | Ishonchlik |
|-----------|------------|
| 📍 GPS lokatsiya | ✅ Yuqori (faqat fake GPS app bilan aldash mumkin) |
| 📶 Wi-Fi nomi (qo'lda) | ⚠️ Past (oson aldash mumkin) — ogohlantirish vositasi |
| 🤳 Yuz tanish | ✅ Juda yuqori (boshqa odam rasmi rad etiladi) |

**Selfi cheklov:** Telegram'da rasmni faqat kameradan olishni majburiy qilib bo'lmaydi. Lekin yuz tanish va vaqt tekshiruvi bilan amaliy aldov juda qiyin.

## 🌐 Server (24/7 ishlash) uchun

### Eng oddiy variant: VPS yoki home server

```bash
# systemd service yaratish
sudo nano /etc/systemd/system/davomat-bot.service
```

```ini
[Unit]
Description=Davomat Telegram Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/attendance_bot
ExecStart=/home/youruser/attendance_bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable davomat-bot
sudo systemctl start davomat-bot
sudo systemctl status davomat-bot
```

### Render.com (bepul plan)
1. GitHub'ga loyihani yuklang
2. Render'da yangi **Background Worker** yarating
3. Build command: `apt-get update && apt-get install -y cmake && pip install -r requirements.txt`
4. Start command: `python bot.py`
5. Environment variables: `BOT_TOKEN`, `INITIAL_ADMIN_ID` va boshqalarni qo'shing

### Railway.app
Render kabi, lekin `railway.json` bilan sozlash mumkin.

## 🖥 Web Dashboard (jonli "kim ishda" ko'rinishi)

Bot ichidagi aiohttp serverda (9090-port) uchta yangi endpoint bor:

| Endpoint | Tavsif |
|---|---|
| `GET /dashboard?key=API_KEY` | To'liq HTML sahifa (60s da avto-yangilanadi) |
| `GET /api/dashboard/today?key=API_KEY` | Bugungi holat (JSON) |
| `GET /api/dashboard/month?key=API_KEY&year=2026&month=7` | Oylik jamlanma (JSON) |

**Xavfsizlik:**
- `.env`da `DASHBOARD_API_KEY` sozlanadi (bo'sh bo'lsa dashboard butunlay o'chiq — hamma so'rov 403).
  Kuchli kalit yaratish: `openssl rand -hex 24`
- Kalit `?key=` query-param yoki `X-Api-Key` header orqali yuboriladi.
- **HTTPS majburiy** — kalit URL ichida ketadi, oddiy HTTP'da ochiq ko'rinadi.
- Bosh Admin botdagi **⚙️ Boshqaruv → 🖥 Web Dashboard** tugmasi orqali tayyor havolani oladi.

**nginx reverse proxy** (serverdagi konfiguratsiyaga qo'shiladi, `/verify/` bloklari yoniga):

```nginx
location /dashboard {
    proxy_pass http://127.0.0.1:9090;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
location /api/dashboard/ {
    proxy_pass http://127.0.0.1:9090;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

So'ng: `nginx -t && systemctl reload nginx`

### Sfatshop sahifasiga biriktirish

**(a) iframe varianti** — eng oson:

```html
<iframe
  src="https://api.sfatshop.uz/dashboard?key=SIZNING_KALIT"
  style="width:100%; height:700px; border:none; border-radius:12px;"
  title="Davomat dashboard">
</iframe>
```

**(b) API + o'z dizayni** — sahifa o'zi fetch qiladi. Buning uchun `.env`da
`DASHBOARD_ALLOWED_ORIGIN` ga sfatshop sahifasi origin'i yoziladi
(masalan `https://api.sfatshop.uz`), shunda JSON endpointlarga CORS header qo'yiladi.
Kalitni query-param bilan yuboring (preflight'siz oddiy GET):

```js
const KEY = "SIZNING_KALIT";
const res = await fetch(`https://api.sfatshop.uz/api/dashboard/today?key=${KEY}`);
const data = await res.json();
```

`/api/dashboard/today` javobi:

```json
{
  "date": "2026-07-12",
  "work_start": "09:00",
  "work_end": "18:00",
  "counts": {"in": 5, "out": 2, "absent": 1},
  "employees": [
    {
      "id": 3,
      "full_name": "Aliyev Vali",
      "position": "Sotuvchi",
      "status": "in",
      "first_in": "08:55",
      "last_out": null,
      "late_minutes": 0,
      "worked_minutes": 312
    }
  ]
}
```

Maydonlar: `status` — `"in"` (ishda) / `"out"` (ketgan) / `"absent"` (kelmagan);
`late_minutes` — ish boshlanishidan kechikish (daqiqa); `worked_minutes` — ishlagan
vaqt (ishda bo'lsa hozirgacha); vaqtlar Toshkent (UTC+5).

`/api/dashboard/month?year=&month=` javobi:

```json
{
  "year": 2026,
  "month": 7,
  "employees": [
    {"id": 3, "full_name": "Aliyev Vali", "position": "Sotuvchi",
     "days": 22, "late_count": 3, "worked_hours": 176.5}
  ]
}
```

## 💾 Ma'lumotlar zaxirasi

SQLite bazasi `attendance.db` faylida saqlanadi. Vaqti-vaqti bilan nusxa olib qo'ying:

```bash
cp attendance.db backups/attendance_$(date +%Y%m%d).db
```

## 🐛 Muammolarni hal qilish

### `face_recognition` o'rnatilmadi
- `cmake` o'rnatilganligini tekshiring: `cmake --version`
- Ubuntu: `sudo apt install python3-dev libboost-all-dev`
- Xotira yetmasa, swap qo'shing (kompilyatsiya ~2GB RAM talab qiladi)

### "BOT_TOKEN .env faylida ko'rsatilmagan"
- `.env` fayl bot.py bilan bir papkada bo'lishi kerak
- `BOT_TOKEN=...` qatorida `=` atrofida bo'sh joy bo'lmasin

### Yuz tanmayapti
- `FACE_TOLERANCE` ni `.env` da kattalashtiring: `0.6` yoki `0.65`
- Yorug'lik yaxshi bo'lsin, niqob/ko'zoynak bo'lmasin

### Lokatsiya har doim "uzoq"
- `OFFICE_RADIUS` ni kattalashtiring (masalan, `100`)
- Aniq koordinatalarni admin paneli orqali yangidan belgilang

## 🔄 Kelajak uchun g'oyalar

- 🔔 Avtomatik eslatma (ish boshidan oldin)
- 🏖️ Ta'til/kasallik so'rovi
- 📈 Top xodimlar reytingi
- 🏢 Bir nechta filial
- 🌐 Web admin panel
- 📲 Bir xodim — bitta qurilma cheklovi

---

Savol yoki yordam kerak bo'lsa — admin bilan bog'laning. 🚀
