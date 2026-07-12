"""Bot konfiguratsiyasi"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent

# Render persistent disk: /data/attendance.db
# Local: ./attendance.db
DB_PATH = Path(os.getenv("DB_PATH", BASE_DIR / "attendance.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Bot token va birinchi admin Telegram ID si
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
INITIAL_ADMIN_ID = int(os.getenv("INITIAL_ADMIN_ID", "0"))

# === Public IP tekshirish (Render uchun) ===
# Vergul bilan ajratilgan IP ro'yxati. Masalan: "213.230.74.56,213.230.74.57"
_office_ips_raw = os.getenv("OFFICE_PUBLIC_IPS", "")
OFFICE_PUBLIC_IPS = [ip.strip() for ip in _office_ips_raw.split(",") if ip.strip()]

# === Web server sozlamalari ===
# Render PORT ni avtomatik beradi (https://render.com/docs/web-services#port-binding)
WEB_PORT = int(os.getenv("PORT", "9090"))
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
# Render: public URL (masalan https://attendance-bot.onrender.com)
# Local: http://192.168.0.195:9090
PUBLIC_URL = os.getenv("PUBLIC_URL", "")

# Standart sozlamalar (admin keyinroq o'zgartirishi mumkin)
DEFAULT_OFFICE_LAT = float(os.getenv("OFFICE_LAT", "41.311081"))   # Toshkent markazi
DEFAULT_OFFICE_LON = float(os.getenv("OFFICE_LON", "69.240562"))
DEFAULT_OFFICE_RADIUS_M = float(os.getenv("OFFICE_RADIUS", "50"))  # metr
DEFAULT_WORK_START = os.getenv("WORK_START", "09:00")
DEFAULT_WORK_END = os.getenv("WORK_END", "18:00")
DEFAULT_OFFICE_WIFI = os.getenv("OFFICE_WIFI", "Office_WiFi")

# === Web dashboard ===
# Maxfiy kalit bo'sh bo'lsa dashboard butunlay o'chiq (barcha so'rovlar 403)
DASHBOARD_API_KEY = os.getenv("DASHBOARD_API_KEY", "")
# CORS: sfatshop sahifasi fetch qilishi uchun ruxsat etilgan origin
# (masalan https://api.sfatshop.uz). Bo'sh bo'lsa CORS header qo'yilmaydi.
DASHBOARD_ALLOWED_ORIGIN = os.getenv("DASHBOARD_ALLOWED_ORIGIN", "")

# Yuz tanish: 0.0 (eng qattiq) — 1.0 (eng yumshoq). Tavsiya: 0.50
FACE_MATCH_TOLERANCE = float(os.getenv("FACE_TOLERANCE", "0.50"))

# Maksimal xodimlar soni (limit)
MAX_EMPLOYEES = 15

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN .env faylida ko'rsatilmagan!")
