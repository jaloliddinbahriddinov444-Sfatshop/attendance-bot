"""Web admin dashboard — jonli "kim ishda" ko'rinishi.

Mavjud aiohttp serverga (wifi_verify.start_verify_server) qo'shiladi:
  GET /dashboard?key=API_KEY              — to'liq HTML sahifa
  GET /api/dashboard/today?key=API_KEY    — bugungi holat (JSON)
  GET /api/dashboard/month?key=&year=&month= — oylik jamlanma (JSON)

Xavfsizlik: DASHBOARD_API_KEY bo'sh bo'lsa hamma so'rov 403.
Kalit query-param (?key=) yoki X-Api-Key header orqali.
CORS: DASHBOARD_ALLOWED_ORIGIN sozlangan bo'lsagina JSON endpointlarga qo'yiladi.
Barcha vaqtlar javobda Toshkent (UTC+5) vaqtida.
"""
import hmac
import logging
import re

from aiohttp import web

from config import DASHBOARD_API_KEY, DASHBOARD_ALLOWED_ORIGIN
from database import (
    get_dashboard_today, get_dashboard_month, get_office_config,
    get_employees_admin, get_all_positions, get_position,
    get_employee_by_id, update_employee_profile, update_employee_card,
    set_hourly_rate, set_employee_position, set_employee_daily_rate,
    deactivate_employee, reactivate_employee,
)
from tzutil import now as tz_now

logger = logging.getLogger(__name__)


# ---------- Yordamchilar ----------

def _authorized(request: web.Request) -> bool:
    """Kalit tekshiruvi (constant-time). Kalit sozlanmagan bo'lsa — doim rad."""
    if not DASHBOARD_API_KEY:
        return False
    supplied = request.query.get("key") or request.headers.get("X-Api-Key", "")
    return hmac.compare_digest(supplied, DASHBOARD_API_KEY)


def _cors(resp: web.StreamResponse) -> web.StreamResponse:
    if DASHBOARD_ALLOWED_ORIGIN:
        resp.headers["Access-Control-Allow-Origin"] = DASHBOARD_ALLOWED_ORIGIN
        resp.headers["Vary"] = "Origin"
    return resp


def _forbidden_json() -> web.Response:
    return _cors(web.json_response({"error": "forbidden"}, status=403))


def _parse_hhmm(value: str, fallback: tuple) -> tuple:
    """'HH:MM' -> (h, m); buzilgan bo'lsa fallback."""
    try:
        h, m = map(int, str(value).split(":")[:2])
        return h, m
    except Exception:
        return fallback


def _time_to_minutes(hhmm: str):
    """'HH:MM[:SS]' -> kun boshidan daqiqa (None bo'lsa None)."""
    if not hhmm:
        return None
    try:
        h, m = map(int, hhmm.split(":")[:2])
        return h * 60 + m
    except Exception:
        return None


def _today_payload() -> dict:
    """Bugungi holat: har faol xodim (boss'siz) uchun status/late/worked."""
    cfg = get_office_config()
    ws_h, ws_m = _parse_hhmm(cfg["work_start"], (9, 0))
    start_min = ws_h * 60 + ws_m

    now = tz_now()
    now_min = now.hour * 60 + now.minute

    employees = []
    counts = {"in": 0, "out": 0, "absent": 0}
    for row in get_dashboard_today():
        last_type = row["last_type"]
        status = "absent" if last_type is None else last_type
        counts[status] += 1

        first_in = (row["first_in"] or "")[:5] or None
        last_out = (row["last_out"] or "")[:5] or None

        late_minutes = 0
        in_min = _time_to_minutes(first_in)
        if in_min is not None:
            late_minutes = max(0, in_min - start_min)

        worked_minutes = 0
        if in_min is not None:
            if status == "in":
                worked_minutes = max(0, now_min - in_min)
            else:
                out_min = _time_to_minutes(last_out)
                if out_min is not None:
                    worked_minutes = max(0, out_min - in_min)

        employees.append({
            "id": row["id"],
            "full_name": row["full_name"],
            "position": row["position"] or "",
            "status": status,
            "first_in": first_in,
            "last_out": last_out,
            "late_minutes": late_minutes,
            "worked_minutes": worked_minutes,
        })

    return {
        "date": now.strftime("%Y-%m-%d"),
        "work_start": cfg["work_start"],
        "work_end": cfg["work_end"],
        "counts": counts,
        "employees": employees,
    }


def _month_payload(year: int, month: int) -> dict:
    """Oylik jamlanma: kelgan kunlar, kechikishlar soni, jami ishlangan soat."""
    cfg = get_office_config()
    ws_h, ws_m = _parse_hhmm(cfg["work_start"], (9, 0))
    start_min = ws_h * 60 + ws_m

    agg = {}
    for row in get_dashboard_month(year, month):
        emp = agg.setdefault(row["id"], {
            "id": row["id"],
            "full_name": row["full_name"],
            "position": row["position"] or "",
            "days": 0,
            "late_count": 0,
            "worked_minutes": 0,
        })
        if row["day"] is None or not row["first_in"]:
            continue
        emp["days"] += 1
        in_min = _time_to_minutes(row["first_in"])
        if in_min is not None and in_min > start_min:
            emp["late_count"] += 1
        out_min = _time_to_minutes(row["last_out"])
        if in_min is not None and out_min is not None and out_min > in_min:
            emp["worked_minutes"] += out_min - in_min

    employees = []
    for emp in agg.values():
        emp["worked_hours"] = round(emp["worked_minutes"] / 60, 1)
        employees.append(emp)

    return {"year": year, "month": month, "employees": employees}


# ---------- Handlerlar ----------

async def _api_today(request: web.Request) -> web.Response:
    if not _authorized(request):
        return _forbidden_json()
    return _cors(web.json_response(_today_payload()))


async def _api_month(request: web.Request) -> web.Response:
    if not _authorized(request):
        return _forbidden_json()
    now = tz_now()
    try:
        year = int(request.query.get("year", now.year))
        month = int(request.query.get("month", now.month))
    except ValueError:
        return _cors(web.json_response({"error": "year/month butun son bo'lishi kerak"}, status=400))
    if not (2000 <= year <= 2100 and 1 <= month <= 12):
        return _cors(web.json_response({"error": "year/month qiymati noto'g'ri"}, status=400))
    return _cors(web.json_response(_month_payload(year, month)))


async def _options_handler(request: web.Request) -> web.Response:
    """CORS preflight (X-Api-Key header ishlatilganda kerak bo'ladi)."""
    resp = web.Response(status=204)
    if DASHBOARD_ALLOWED_ORIGIN:
        resp.headers["Access-Control-Allow-Origin"] = DASHBOARD_ALLOWED_ORIGIN
        resp.headers["Access-Control-Allow-Methods"] = "GET, PATCH, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "X-Api-Key, Content-Type"
        resp.headers["Vary"] = "Origin"
    return resp


# ---------- Hodimlar ma'lumotlari (ko'rish/tahrirlash) ----------

async def _api_employees(request: web.Request) -> web.Response:
    if not _authorized(request):
        return _forbidden_json()
    employees = [{
        "id": r["id"],
        "full_name": r["full_name"],
        "phone": r["phone"],
        "position_text": r["position"] or "",
        "position_id": r["position_id"],
        "position_name": r["position_name"],
        "work_hours": r["work_hours"],
        "role": r["role"] or "employee",
        "is_active": bool(r["is_active"]),
        "hourly_rate": r["hourly_rate"] or 0,
        "daily_rate": r["daily_rate"] or 0,
        "card_number": r["card_number"] or "",
        "card_holder_name": r["card_holder_name"] or "",
        "registered_at": (r["registered_at"] or "")[:16],
    } for r in get_employees_admin()]
    return _cors(web.json_response({"employees": employees}))


async def _api_positions(request: web.Request) -> web.Response:
    if not _authorized(request):
        return _forbidden_json()
    positions = [{
        "id": p["id"],
        "name": p["name"],
        "work_hours": p["work_hours"],
        "min_rate": p["min_rate"],
        "max_rate": p["max_rate"],
    } for p in get_all_positions()]
    return _cors(web.json_response({"positions": positions}))


def _bad(msg: str) -> web.Response:
    return _cors(web.json_response({"error": msg}, status=400))


async def _api_employee_patch(request: web.Request) -> web.Response:
    """Hodim ma'lumotini tahrirlash — botdagi bilan bir xil qoidalar.
    Ruxsat etilgan maydonlar: full_name, position_id(+daily_rate),
    daily_rate, hourly_rate, card_number+card_holder_name, is_active.
    Rol va telefon bu yerdan o'zgartirilmaydi (botda ham yo'q)."""
    if not _authorized(request):
        return _forbidden_json()
    try:
        emp_id = int(request.match_info["id"])
    except (KeyError, ValueError):
        return _bad("noto'g'ri id")
    emp = get_employee_by_id(emp_id)
    if emp is None:
        return _cors(web.json_response({"error": "hodim topilmadi"}, status=404))
    try:
        body = await request.json()
    except Exception:
        return _bad("JSON kutilgan edi")
    if not isinstance(body, dict):
        return _bad("JSON obyekt kutilgan edi")

    changes = []

    if "full_name" in body:
        name = str(body["full_name"] or "").strip()
        if len(name) < 5:
            return _bad("Ism juda qisqa (kamida 5 belgi)")
        update_employee_profile(emp_id, full_name=name)
        changes.append("full_name")

    if "position_id" in body:
        pos_id = body["position_id"]
        if pos_id in (None, 0, "0", ""):
            return _bad("Lavozim tanlanishi kerak")
        try:
            pos_id = int(pos_id)
        except (TypeError, ValueError):
            return _bad("Lavozim id noto'g'ri")
        if get_position(pos_id) is None:
            return _bad("Bunday lavozim yo'q")
        try:
            daily = int(body.get("daily_rate", emp["daily_rate"] or 0))
        except (TypeError, ValueError):
            return _bad("Kunlik stavka noto'g'ri")
        if daily <= 0 or daily > 10_000_000:
            return _bad("Kunlik stavka 1 dan 10 mln gacha bo'lishi kerak")
        set_employee_position(emp_id, pos_id, daily)
        changes.append("position")
    elif "daily_rate" in body:
        try:
            daily = int(body["daily_rate"])
        except (TypeError, ValueError):
            return _bad("Kunlik stavka noto'g'ri")
        if daily <= 0 or daily > 10_000_000:
            return _bad("Kunlik stavka 1 dan 10 mln gacha bo'lishi kerak")
        set_employee_daily_rate(emp_id, daily)
        changes.append("daily_rate")

    if "hourly_rate" in body:
        try:
            rate = int(body["hourly_rate"])
        except (TypeError, ValueError):
            return _bad("Soatlik stavka noto'g'ri")
        if rate < 0 or rate > 10_000_000:
            return _bad("Soatlik stavka 0 dan 10 mln gacha bo'lishi kerak")
        set_hourly_rate(emp_id, rate)
        changes.append("hourly_rate")

    if "card_number" in body or "card_holder_name" in body:
        card = re.sub(r"\D", "", str(body.get("card_number", emp["card_number"] or "")))
        holder = str(body.get("card_holder_name", emp["card_holder_name"] or "")).strip()
        if card and len(card) != 16:
            return _bad("Karta raqami 16 ta raqam bo'lishi kerak")
        if card and len(holder) < 3:
            return _bad("Karta egasining ismi juda qisqa")
        update_employee_card(emp_id, card, holder if card else "")
        changes.append("card")

    if "is_active" in body:
        if bool(body["is_active"]):
            reactivate_employee(emp_id)
        else:
            if (emp["role"] or "") == "bosh_admin":
                return _bad("Bosh adminni faolsizlantirib bo'lmaydi")
            deactivate_employee(emp_id)
        changes.append("is_active")

    if not changes:
        return _bad("O'zgartiriladigan maydon yo'q")

    logger.info("Panel: hodim #%s tahrirlandi (%s)", emp_id, ", ".join(changes))
    return _cors(web.json_response({"id": emp_id, "updated": changes}))


async def _page_handler(request: web.Request) -> web.Response:
    if not _authorized(request):
        return web.Response(status=403, text="403 — kalit noto'g'ri yoki dashboard o'chiq")
    return web.Response(text=DASHBOARD_HTML, content_type="text/html", charset="utf-8")


def setup_dashboard_routes(app: web.Application):
    app.router.add_get("/dashboard", _page_handler)
    app.router.add_get("/api/dashboard/today", _api_today)
    app.router.add_get("/api/dashboard/month", _api_month)
    app.router.add_get("/api/dashboard/employees", _api_employees)
    app.router.add_get("/api/dashboard/positions", _api_positions)
    app.router.add_patch("/api/dashboard/employees/{id}", _api_employee_patch)
    app.router.add_route("OPTIONS", "/api/dashboard/{tail:.*}", _options_handler)
    logger.info("Dashboard endpointlari ulandi: /dashboard, /api/dashboard/*")


# ---------- HTML sahifa (bitta fayl, CDN'siz, vanilla JS) ----------

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Davomat — jonli dashboard</title>
<style>
  :root { --green:#16a34a; --red:#dc2626; --gray:#6b7280; --bg:#f5f6f8; --card:#fff; }
  * { box-sizing: border-box; margin: 0; }
  body { font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
         background: var(--bg); color: #111827; padding: 12px; }
  .wrap { max-width: 860px; margin: 0 auto; }
  h1 { font-size: 1.15rem; margin-bottom: 2px; }
  .sub { color: var(--gray); font-size: .85rem; margin-bottom: 12px; }
  .cards { display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }
  .card { flex: 1 1 100px; background: var(--card); border-radius: 10px;
          padding: 10px 12px; box-shadow: 0 1px 2px rgba(0,0,0,.06); text-align: center; }
  .card .num { font-size: 1.5rem; font-weight: 700; }
  .card .lbl { font-size: .78rem; color: var(--gray); }
  .card.c-in .num { color: var(--green); }
  .card.c-out .num { color: var(--red); }
  .card.c-abs .num { color: var(--gray); }
  .tbl-box { background: var(--card); border-radius: 10px; overflow-x: auto;
             box-shadow: 0 1px 2px rgba(0,0,0,.06); margin-bottom: 20px; }
  table { width: 100%; border-collapse: collapse; font-size: .87rem; min-width: 520px; }
  th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid #eef0f3; white-space: nowrap; }
  th { background: #fafbfc; color: var(--gray); font-weight: 600; font-size: .76rem;
       text-transform: uppercase; letter-spacing: .03em; }
  tr:last-child td { border-bottom: none; }
  .late { color: var(--red); font-weight: 600; }
  .muted { color: var(--gray); }
  h2 { font-size: 1rem; margin: 4px 0 8px; }
  select { font-size: .9rem; padding: 6px 10px; border-radius: 8px; border: 1px solid #d1d5db;
           background: var(--card); margin-bottom: 10px; }
  .err { background: #fef2f2; color: var(--red); padding: 10px 12px; border-radius: 10px;
         margin-bottom: 12px; display: none; font-size: .87rem; }
  .foot { color: var(--gray); font-size: .75rem; text-align: center; margin-top: 14px; }
</style>
</head>
<body>
<div class="wrap">
  <h1>📊 Davomat — jonli dashboard</h1>
  <div class="sub" id="subline">Yuklanmoqda...</div>
  <div class="err" id="errbox"></div>

  <div class="cards">
    <div class="card c-in"><div class="num" id="c-in">–</div><div class="lbl">🟢 Ishda</div></div>
    <div class="card c-out"><div class="num" id="c-out">–</div><div class="lbl">🔴 Ketgan</div></div>
    <div class="card c-abs"><div class="num" id="c-abs">–</div><div class="lbl">❌ Kelmagan</div></div>
  </div>

  <div class="tbl-box">
    <table>
      <thead><tr>
        <th>Xodim</th><th>Lavozim</th><th>Holat</th>
        <th>Kelgan</th><th>Kechikish</th><th>Ishlagan</th>
      </tr></thead>
      <tbody id="today-body"></tbody>
    </table>
  </div>

  <h2>🗓 Oylik jamlanma</h2>
  <select id="month-sel"></select>
  <div class="tbl-box">
    <table>
      <thead><tr>
        <th>Xodim</th><th>Lavozim</th><th>Kelgan kunlar</th>
        <th>Kechikishlar</th><th>Jami soat</th>
      </tr></thead>
      <tbody id="month-body"></tbody>
    </table>
  </div>

  <div class="foot">Har 60 soniyada avtomatik yangilanadi</div>
</div>

<script>
(function () {
  var KEY = new URLSearchParams(location.search).get('key') || '';
  var OYLAR = ['', 'Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun',
               'Iyul', 'Avgust', 'Sentyabr', 'Oktyabr', 'Noyabr', 'Dekabr'];
  var HAFTA = ['Yakshanba', 'Dushanba', 'Seshanba', 'Chorshanba',
               'Payshanba', 'Juma', 'Shanba'];
  var STATUS = {
    'in':     '🟢 ishda',
    'out':    '🔴 ketgan',
    'absent': '❌ kelmagan'
  };

  function showErr(msg) {
    var box = document.getElementById('errbox');
    box.textContent = msg;
    box.style.display = 'block';
  }
  function hideErr() {
    document.getElementById('errbox').style.display = 'none';
  }

  function fmtMin(m) {
    if (!m) return '—';
    return Math.floor(m / 60) + 's ' + (m % 60) + 'd';
  }

  function td(text, cls) {
    var el = document.createElement('td');
    el.textContent = text;
    if (cls) el.className = cls;
    return el;
  }

  function loadToday() {
    fetch('api/dashboard/today?key=' + encodeURIComponent(KEY))
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function (data) {
        hideErr();
        var d = new Date(data.date + 'T00:00:00');
        document.getElementById('subline').textContent =
          data.date + ' · ' + HAFTA[d.getDay()] + ' · ish vaqti ' +
          data.work_start + '–' + data.work_end;
        document.getElementById('c-in').textContent = data.counts['in'];
        document.getElementById('c-out').textContent = data.counts['out'];
        document.getElementById('c-abs').textContent = data.counts['absent'];

        var body = document.getElementById('today-body');
        body.textContent = '';
        data.employees.forEach(function (e) {
          var tr = document.createElement('tr');
          tr.appendChild(td(e.full_name));
          tr.appendChild(td(e.position, 'muted'));
          tr.appendChild(td(STATUS[e.status] || e.status));
          tr.appendChild(td(e.first_in || '—'));
          tr.appendChild(e.late_minutes > 0
            ? td(e.late_minutes + ' daqiqa', 'late')
            : td('—', 'muted'));
          tr.appendChild(td(fmtMin(e.worked_minutes)));
          body.appendChild(tr);
        });
      })
      .catch(function (err) {
        showErr('Yuklashda xato: ' + err.message +
                (KEY ? '' : ' (URL\\'da ?key=... yo\\'q)'));
      });
  }

  function loadMonth() {
    var val = document.getElementById('month-sel').value.split('-');
    fetch('api/dashboard/month?key=' + encodeURIComponent(KEY) +
          '&year=' + val[0] + '&month=' + val[1])
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function (data) {
        var body = document.getElementById('month-body');
        body.textContent = '';
        data.employees.forEach(function (e) {
          var tr = document.createElement('tr');
          tr.appendChild(td(e.full_name));
          tr.appendChild(td(e.position, 'muted'));
          tr.appendChild(td(String(e.days)));
          tr.appendChild(e.late_count > 0
            ? td(String(e.late_count), 'late') : td('0', 'muted'));
          tr.appendChild(td(String(e.worked_hours)));
          body.appendChild(tr);
        });
      })
      .catch(function (err) { showErr('Oylik yuklashda xato: ' + err.message); });
  }

  // Oy tanlash: joriy oydan 12 oy orqaga
  var sel = document.getElementById('month-sel');
  var now = new Date();
  for (var i = 0; i < 12; i++) {
    var dt = new Date(now.getFullYear(), now.getMonth() - i, 1);
    var opt = document.createElement('option');
    opt.value = dt.getFullYear() + '-' + (dt.getMonth() + 1);
    opt.textContent = OYLAR[dt.getMonth() + 1] + ' ' + dt.getFullYear();
    sel.appendChild(opt);
  }
  sel.addEventListener('change', loadMonth);

  loadToday();
  loadMonth();
  setInterval(loadToday, 60000);
})();
</script>
</body>
</html>
"""
