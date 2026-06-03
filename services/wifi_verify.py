"""
Wi-Fi tekshiruv + Selfi + Yuz tanish — bitta qadamda.
Xodim havolani ochadi → kamera ochiladi → selfi oladi → yuz tekshiriladi.
Sahifa faqat ofis Wi-Fi'ida ochiladi (lokal server).
"""
import asyncio
import hashlib
import io
import socket
import time
import uuid
import logging
from aiohttp import web
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import texts

logger = logging.getLogger(__name__)

# Tokenlar
_pending: dict = {}
TOKEN_EXPIRY = 300  # 5 daqiqa

# Ofis IP belgilash tokenlari (admin "joriy IP qo'shish" oqimi)
_setip_pending: dict = {}

# Bot obyekti (server ichidan Telegram xabar yuborish uchun) — start_verify_server o'rnatadi
_bot = None

# Bir xil "yangi IP" ogohlantirishini qayta-qayta yubormaslik uchun (ip -> oxirgi vaqt)
_notified_ips: dict = {}
NOTIFY_COOLDOWN = 3600  # bir xil IP uchun soatiga 1 marta

# ===== HTML sahifa: kamera + yuklash =====

def _build_camera_html(token: str, employee_name: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Davomat</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    font-family: -apple-system, system-ui, sans-serif;
    background: #f0f4f8; min-height: 100vh;
    display: flex; flex-direction: column; align-items: center;
    padding: 20px;
}}
.card {{
    background: #fff; border-radius: 16px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    padding: 28px 20px; width: 100%; max-width: 400px;
    text-align: center; margin-top: 20px;
}}
.wifi-badge {{
    display: inline-block; background: #e8f5e9; color: #2e7d32;
    padding: 8px 16px; border-radius: 20px; font-size: 14px;
    font-weight: 600; margin-bottom: 16px;
}}
h2 {{ color: #1a1a2e; margin-bottom: 8px; font-size: 22px; }}
.subtitle {{ color: #666; font-size: 14px; margin-bottom: 24px; }}
.name {{ color: #1a73e8; font-weight: 700; }}
#cameraInput {{ display: none; }}
.btn {{
    display: inline-flex; align-items: center; justify-content: center;
    gap: 8px; width: 100%; padding: 16px;
    border: none; border-radius: 12px; font-size: 17px;
    font-weight: 600; cursor: pointer; transition: all 0.2s;
}}
.btn-primary {{ background: #1a73e8; color: #fff; }}
.btn-primary:active {{ background: #1557b0; transform: scale(0.98); }}
.btn-retry {{ background: #ff5252; color: #fff; margin-top: 12px; }}
.preview {{ width: 200px; height: 200px; border-radius: 50%;
    object-fit: cover; margin: 16px auto; display: none;
    border: 4px solid #e0e0e0; }}
.loading {{ display: none; margin: 20px auto; }}
.loading.show {{ display: block; }}
.spinner {{
    width: 48px; height: 48px; border: 4px solid #e0e0e0;
    border-top-color: #1a73e8; border-radius: 50%;
    animation: spin 0.8s linear infinite; margin: 0 auto 12px;
}}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
.result {{ display: none; margin-top: 20px; padding: 20px;
    border-radius: 12px; font-size: 16px; }}
.result.success {{ display: block; background: #e8f5e9; color: #2e7d32; }}
.result.error {{ display: block; background: #fce4ec; color: #c62828; }}
.result .icon {{ font-size: 48px; margin-bottom: 12px; }}
.hint {{ margin-top: 16px; padding: 12px; background: #fff3e0;
    border-radius: 8px; font-size: 13px; color: #e65100; }}
.back-hint {{ margin-top: 20px; padding: 16px; background: #e3f2fd;
    border-radius: 12px; color: #1565c0; font-weight: 600; }}
</style>
</head>
<body>

<div class="card">
    <div class="wifi-badge">📶 Wi-Fi tasdiqlandi</div>
    <h2>📸 Selfi oling</h2>
    <p class="subtitle">Salom, <span class="name">{employee_name}</span></p>

    <input type="file" id="cameraInput" accept="image/*" capture="user">
    <img id="preview" class="preview" alt="Selfi">

    <div id="captureSection">
        <button class="btn btn-primary" onclick="openCamera()">
            📸 Kamerani ochish
        </button>
        <div class="hint">
            ⚠️ Faqat hozir olingan selfi qabul qilinadi.<br>
            Galereyadan rasm tanlamang.
        </div>
    </div>

    <div id="loadingSection" class="loading">
        <div class="spinner"></div>
        <p style="color:#666;">Yuzingiz tekshirilmoqda...</p>
    </div>

    <div id="successResult" class="result">
        <div class="icon">✅</div>
        <strong>Tasdiqlandi!</strong>
        <p style="margin-top:8px;">Yuzingiz muvaffaqiyatli tekshirildi.</p>
        <div class="back-hint">
            📱 Endi <strong>Telegram</strong>ga qayting<br>
            va <strong>«✅ Tasdiqladim»</strong> tugmasini bosing.
        </div>
    </div>

    <div id="errorResult" class="result">
        <div class="icon">❌</div>
        <strong id="errorText">Xatolik</strong>
        <button class="btn btn-retry" onclick="retry()">🔄 Qayta urinish</button>
    </div>
</div>

<script>
const TOKEN = "{token}";
const MAX_AGE_SEC = 60;

function openCamera() {{
    document.getElementById('cameraInput').click();
}}

function retry() {{
    document.getElementById('errorResult').className = 'result';
    document.getElementById('captureSection').style.display = 'block';
    document.getElementById('preview').style.display = 'none';
    document.getElementById('cameraInput').value = '';
}}

document.getElementById('cameraInput').addEventListener('change', async (e) => {{
    const file = e.target.files[0];
    if (!file) return;

    // Vaqt tekshiruvi — eski rasm bo'lsa rad etish
    const fileAge = (Date.now() - file.lastModified) / 1000;
    if (fileAge > MAX_AGE_SEC) {{
        showError("Bu rasm " + Math.round(fileAge/60) + " daqiqa oldin olingan. Faqat hozir olingan selfi qabul qilinadi.");
        return;
    }}

    // Preview ko'rsatish
    const preview = document.getElementById('preview');
    preview.src = URL.createObjectURL(file);
    preview.style.display = 'block';

    // Loading
    document.getElementById('captureSection').style.display = 'none';
    document.getElementById('loadingSection').className = 'loading show';

    // Serverga yuklash
    try {{
        const formData = new FormData();
        formData.append('photo', file);

        const resp = await fetch('/verify/' + TOKEN + '/upload', {{
            method: 'POST',
            body: formData,
        }});

        const data = await resp.json();
        document.getElementById('loadingSection').className = 'loading';

        if (data.success) {{
            document.getElementById('successResult').className = 'result success';
        }} else {{
            showError(data.error || "Noma'lum xatolik");
        }}
    }} catch (err) {{
        document.getElementById('loadingSection').className = 'loading';
        showError("Tarmoq xatosi. Qayta urinib ko'ring.");
    }}
}});

function showError(msg) {{
    document.getElementById('errorText').textContent = msg;
    document.getElementById('errorResult').className = 'result error';
    document.getElementById('captureSection').style.display = 'none';
    document.getElementById('loadingSection').className = 'loading';
}}
</script>
</body>
</html>"""


EXPIRED_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Muddati o'tgan</title>
<style>body{font-family:-apple-system,sans-serif;text-align:center;padding:60px 20px;background:#fff3e0;}</style>
</head><body>
<div style="font-size:60px;">⏰</div>
<h2 style="color:#e65100;">Havola muddati o'tgan</h2>
<p style="color:#666;">Botda qaytadan «Keldim» bosing.</p>
</body></html>"""


NOT_OFFICE_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ofis tarmog'ida emas</title>
<style>body{font-family:-apple-system,sans-serif;text-align:center;padding:60px 20px;background:#ffebee;}</style>
</head><body>
<div style="font-size:60px;">📡</div>
<h2 style="color:#c62828;">Ofis Wi-Fi'sida emassiz</h2>
<p style="color:#666;font-size:16px;margin-top:12px;">
Davomatni tasdiqlash uchun <b>ofis Wi-Fi</b>'siga ulaning va qaytadan urinib ko'ring.
</p>
<p style="color:#999;font-size:13px;margin-top:20px;">
Mobil internet yoki boshqa Wi-Fi orqali bo'lmaydi.
</p>
</body></html>"""


SETIP_OK_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ofis IP qo'shildi</title>
<style>body{font-family:-apple-system,sans-serif;text-align:center;padding:60px 20px;background:#e8f5e9;}</style>
</head><body>
<div style="font-size:60px;">✅</div>
<h2 style="color:#2e7d32;">Ofis IP qo'shildi</h2>
<p style="color:#444;font-size:18px;margin-top:12px;"><b>{ip}</b></p>
<p style="color:#666;font-size:15px;margin-top:12px;">
Bu IP endi ofis Wi-Fi'si sifatida tan olinadi. Botga qaytishingiz mumkin.
</p>
<p style="color:#999;font-size:13px;margin-top:20px;">
Eslatma: bu sahifani ofis Wi-Fi'sida ochgan bo'lsangizgina IP to'g'ri bo'ladi.
</p>
</body></html>"""


# ===== Token boshqaruvi =====

def create_token(employee_id: int, employee_name: str) -> str:
    _cleanup_expired()
    token = uuid.uuid4().hex[:16]
    _pending[token] = {
        "employee_id": employee_id,
        "employee_name": employee_name,
        "wifi_verified": False,
        "face_matched": False,
        "face_score": 0.0,
        "photo_hash": None,
        "created_at": time.time(),
    }
    return token


def get_token_data(token: str) -> dict | None:
    entry = _pending.get(token)
    if entry and time.time() - entry["created_at"] <= TOKEN_EXPIRY:
        return entry
    return None


def is_fully_verified(token: str) -> bool:
    entry = get_token_data(token)
    return entry is not None and entry["wifi_verified"] and entry["face_matched"]


def cleanup_token(token: str):
    _pending.pop(token, None)


def _cleanup_expired():
    now = time.time()
    expired = [t for t, v in _pending.items() if now - v["created_at"] > TOKEN_EXPIRY]
    for t in expired:
        _pending.pop(t, None)


# ===== Ofis IP belgilash (admin "joriy IP qo'shish") =====

def create_setip_token(admin_id: int) -> str:
    """Admin uchun bir martalik IP-belgilash tokeni."""
    now = time.time()
    expired = [t for t, v in _setip_pending.items() if now - v["created_at"] > TOKEN_EXPIRY]
    for t in expired:
        _setip_pending.pop(t, None)
    token = "ip" + uuid.uuid4().hex[:14]
    _setip_pending[token] = {"admin_id": admin_id, "created_at": now}
    return token


async def _notify_ip_changed(client_ip: str, employee_name: str):
    """Ro'yxatdagi xodim noma'lum IP'dan urinса — Bosh Adminni xabardor qilish."""
    if _bot is None:
        return
    now = time.time()
    if now - _notified_ips.get(client_ip, 0) < NOTIFY_COOLDOWN:
        return
    _notified_ips[client_ip] = now
    try:
        from database import get_bosh_admin
        ba = get_bosh_admin()
        if not ba:
            return
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Ofis IP'si — qo'sh",
                                  callback_data=f"ipadd:{client_ip}")],
            [InlineKeyboardButton(text="❌ Yo'q, e'tiborsiz",
                                  callback_data=f"ipign:{client_ip}")],
        ])
        await _bot.send_message(
            ba["telegram_id"],
            texts.IP_CHANGED_ALERT.format(name=employee_name, ip=client_ip),
            reply_markup=markup,
        )
    except Exception:
        logger.exception("IP o'zgarishi haqida ogohlantirishda xato")


def _get_client_ip(request: web.Request) -> str:
    """Render orqasidan kelgan haqiqiy client IP'ni olish"""
    # Render load balancer X-Forwarded-For sarlavhasini qo'shadi
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        # Eng chap IP — haqiqiy mijoz IP'si
        return xff.split(",")[0].strip()
    # Local rejim — to'g'ridan-to'g'ri ulanish
    return request.remote or "unknown"


def _is_office_ip(client_ip: str) -> bool:
    """Mijoz IP'si ofis IP'lariga mosligini tekshirish (baza orqali — dinamik).

    IP'lar endi `office_ips` jadvalida saqlanadi va admin tomonidan runtime'da
    yangilanadi (Render env'iga tegmasdan). Ro'yxat bo'sh bo'lsa — local rejim,
    hamma ruxsat etiladi.
    """
    from database import get_office_ips
    ips = get_office_ips()
    if not ips:
        return True
    return client_ip in ips


# ===== Web handlerlar =====

async def _page_handler(request: web.Request) -> web.Response:
    """Kamera sahifasini ko'rsatish — sahifa ochilishi = Wi-Fi tasdiqlangan"""
    token = request.match_info.get("token", "")
    entry = _pending.get(token)

    if not entry or time.time() - entry["created_at"] > TOKEN_EXPIRY:
        cleanup_token(token)
        return web.Response(text=EXPIRED_HTML, content_type="text/html")

    # Public IP tekshiruvi (Render rejimida)
    client_ip = _get_client_ip(request)
    if not _is_office_ip(client_ip):
        logger.warning("Office IP'si emas: %s (xodim=%s)", client_ip, entry["employee_name"])
        await _notify_ip_changed(client_ip, entry["employee_name"])
        return web.Response(text=NOT_OFFICE_HTML, content_type="text/html")

    # Wi-Fi tasdiqlandi (sahifa ochildi = ofis tarmoqda)
    entry["wifi_verified"] = True
    entry["client_ip"] = client_ip
    logger.info("Wi-Fi verified: employee=%s token=%s ip=%s",
                entry["employee_name"], token[:8], client_ip)

    html = _build_camera_html(token, entry["employee_name"])
    return web.Response(text=html, content_type="text/html")


async def _upload_handler(request: web.Request) -> web.Response:
    """Selfi yuklash va yuz tanish"""
    token = request.match_info.get("token", "")
    entry = _pending.get(token)

    if not entry or time.time() - entry["created_at"] > TOKEN_EXPIRY:
        return web.json_response({"success": False, "error": "Havola muddati o'tgan"})

    # Xavfsizlik: upload ham faqat ofis IP'sidan
    client_ip = _get_client_ip(request)
    if not _is_office_ip(client_ip):
        logger.warning("Upload ofis IP'sidan emas: %s", client_ip)
        return web.json_response({"success": False, "error": "Ofis Wi-Fi'sida emassiz"})

    if entry["face_matched"]:
        return web.json_response({"success": True, "error": "Allaqachon tasdiqlangan"})

    try:
        # Rasmni o'qish
        reader = await request.multipart()
        field = await reader.next()
        if not field or field.name != "photo":
            return web.json_response({"success": False, "error": "Rasm topilmadi"})

        photo_bytes = await field.read()  # rasm baytlari
        if len(photo_bytes) < 1000:
            return web.json_response({"success": False, "error": "Rasm juda kichik"})

        # Rasm hashini hisoblash (takrorlanishni tekshirish uchun)
        photo_hash = hashlib.sha256(photo_bytes).hexdigest()

        # Rasm takrorlanishini tekshirish
        from database import is_photo_used_recently, record_photo_used
        if is_photo_used_recently(photo_hash, days=30):
            return web.json_response({
                "success": False,
                "error": "Bu rasm avval ishlatilgan! Yangi selfi oling."
            })

        # Xodim yuz kodini olish
        from database import get_employee_by_id
        employee = get_employee_by_id(entry["employee_id"])
        if not employee:
            return web.json_response({"success": False, "error": "Xodim topilmadi"})

        # Yuz tanish (CPU-intensive — alohida thread'da)
        from services.face_service import compare_faces
        is_match, similarity, err = await asyncio.to_thread(
            compare_faces, employee["face_encoding"], photo_bytes
        )

        if err == "no_face":
            return web.json_response({
                "success": False,
                "error": "Rasmda yuz topilmadi. Yuzingiz aniq ko'rinsin."
            })
        if err == "multiple_faces":
            return web.json_response({
                "success": False,
                "error": "Rasmda bir nechta yuz bor. Faqat o'zingiz ko'rining."
            })
        if err:
            return web.json_response({"success": False, "error": f"Xatolik: {err}"})

        if not is_match:
            logger.warning("Face mismatch: employee=%s score=%.2f", entry["employee_name"], similarity)
            return web.json_response({
                "success": False,
                "error": "Yuz mos kelmadi. O'zingizning aniq selfingizni oling."
            })

        # Muvaffaqiyat!
        entry["face_matched"] = True
        entry["face_score"] = similarity
        entry["photo_hash"] = photo_hash

        # Rasmni "ishlatilgan" deb belgilash
        record_photo_used(photo_hash, entry["employee_id"])

        logger.info("Face verified: employee=%s score=%.2f", entry["employee_name"], similarity)
        return web.json_response({"success": True, "score": round(similarity, 3)})

    except Exception as e:
        logger.exception("Upload error")
        return web.json_response({"success": False, "error": "Server xatosi. Qayta urinib ko'ring."})


async def _setip_handler(request: web.Request) -> web.Response:
    """Admin ofis Wi-Fi'sida turib ochadi → joriy public IP ofis IP sifatida qo'shiladi."""
    token = request.match_info.get("token", "")
    entry = _setip_pending.get(token)
    if not entry or time.time() - entry["created_at"] > TOKEN_EXPIRY:
        _setip_pending.pop(token, None)
        return web.Response(text=EXPIRED_HTML, content_type="text/html")

    _setip_pending.pop(token, None)  # bir martalik
    client_ip = _get_client_ip(request)

    from database import add_office_ip, office_ip_exists
    already = office_ip_exists(client_ip)
    add_office_ip(client_ip, label="admin orqali", added_by=entry["admin_id"])
    logger.info("Ofis IP belgilandi: %s (admin=%s, already=%s)",
                client_ip, entry["admin_id"], already)

    # Adminni Telegram orqali xabardor qilish (+ tezkor o'chirish tugmasi)
    if _bot is not None:
        try:
            txt = (texts.SETIP_ALREADY if already else texts.SETIP_ADDED).format(ip=client_ip)
            del_kb = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🗑 Bu IP'ni o'chirish",
                                     callback_data=f"ipdel:{client_ip}")
            ]])
            await _bot.send_message(entry["admin_id"], txt, reply_markup=del_kb)
        except Exception:
            logger.exception("setip xabar yuborishda xato")

    return web.Response(text=SETIP_OK_HTML.replace("{ip}", client_ip),
                        content_type="text/html")


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "192.168.1.1"


async def start_verify_server(bot=None, port: int = None) -> web.AppRunner:
    """Web serverni ishga tushirish (Render: PORT env var, local: 9090)"""
    from config import WEB_PORT, WEB_HOST, PUBLIC_URL

    global _bot
    _bot = bot  # server handlerlari Telegram xabar yubora olishi uchun

    app = web.Application(client_max_size=10 * 1024 * 1024)  # 10MB limit
    app.router.add_get("/verify/{token}", _page_handler)
    app.router.add_post("/verify/{token}/upload", _upload_handler)
    app.router.add_get("/setip/{token}", _setip_handler)
    # Sog'liq tekshiruvi (Render uchun)
    app.router.add_get("/health", lambda r: web.Response(text="OK"))

    actual_port = port if port is not None else WEB_PORT
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEB_HOST, actual_port)
    await site.start()

    if PUBLIC_URL:
        from database import get_office_ips
        logger.info("Web server tayyor: %s (Render rejimida)", PUBLIC_URL)
        logger.info("Ofis IP filtri (bazadan): %s", get_office_ips() or "yo'q (hamma ruxsat)")
    else:
        local_ip = get_local_ip()
        logger.info("Web server tayyor: http://%s:%d (Local rejim)", local_ip, actual_port)
    return runner
