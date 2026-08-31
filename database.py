"""SQLite ma'lumotlar bazasi - barcha funksiyalar"""
import json
import re
import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Optional
from config import DB_PATH, DEFAULT_OFFICE_LAT, DEFAULT_OFFICE_LON, \
    DEFAULT_OFFICE_RADIUS_M, DEFAULT_WORK_START, DEFAULT_WORK_END, \
    DEFAULT_OFFICE_WIFI, INITIAL_ADMIN_ID


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Bazani yaratish va boshlang'ich sozlamalarni o'rnatish"""
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            position TEXT NOT NULL,
            face_encoding BLOB NOT NULL,
            is_admin INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            role TEXT DEFAULT 'employee',
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            check_type TEXT NOT NULL CHECK(check_type IN ('in', 'out')),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            latitude REAL,
            longitude REAL,
            distance_meters REAL,
            wifi_name TEXT,
            wifi_match INTEGER DEFAULT 0,
            face_match_score REAL,
            photo_file_id TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_attendance_employee ON attendance(employee_id);
        CREATE INDEX IF NOT EXISTS idx_attendance_timestamp ON attendance(timestamp);

        CREATE TABLE IF NOT EXISTS used_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_unique_id TEXT NOT NULL,
            employee_id INTEGER NOT NULL,
            used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_used_photos_fuid ON used_photos(file_unique_id);

        CREATE TABLE IF NOT EXISTS salary_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            entry_type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            reason TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT (datetime('now')),
            cancelled INTEGER DEFAULT 0,
            cancelled_by INTEGER,
            cancelled_at TIMESTAMP,
            cancel_reason TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_salary_employee ON salary_entries(employee_id);
        CREATE INDEX IF NOT EXISTS idx_salary_created_at ON salary_entries(created_at);

        CREATE TABLE IF NOT EXISTS closed_months (
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            closed_by INTEGER,
            closed_at TIMESTAMP DEFAULT (datetime('now')),
            PRIMARY KEY (year, month)
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            assigned_to INTEGER NOT NULL,
            assigned_by INTEGER NOT NULL,
            deadline TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'open',
            created_at TIMESTAMP DEFAULT (datetime('now')),
            completed_at TIMESTAMP,
            FOREIGN KEY (assigned_to) REFERENCES employees (id) ON DELETE CASCADE,
            FOREIGN KEY (assigned_by) REFERENCES employees (id) ON DELETE SET NULL
        );
        CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON tasks(assigned_to);
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);

        CREATE TABLE IF NOT EXISTS task_skips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            skipped_at TIMESTAMP DEFAULT (datetime('now')),
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_task_skips_task ON task_skips(task_id);

        CREATE TABLE IF NOT EXISTS finance_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            entry_type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount INTEGER NOT NULL,
            note TEXT,
            linked_employee_id INTEGER,
            entry_date TIMESTAMP DEFAULT (datetime('now')),
            FOREIGN KEY (owner_id) REFERENCES employees (id) ON DELETE CASCADE,
            FOREIGN KEY (linked_employee_id) REFERENCES employees (id) ON DELETE SET NULL
        );
        CREATE INDEX IF NOT EXISTS idx_finance_owner_date
            ON finance_entries(owner_id, entry_date);

        CREATE TABLE IF NOT EXISTS office_ips (
            ip TEXT PRIMARY KEY,
            label TEXT DEFAULT '',
            added_by INTEGER,
            added_at TIMESTAMP DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS personal_finance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            entry_type TEXT NOT NULL CHECK(entry_type IN ('income','expense')),
            category TEXT NOT NULL,
            amount INTEGER NOT NULL,
            note TEXT DEFAULT '',
            entry_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT (datetime('now')),
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS broadcasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_emp_id INTEGER NOT NULL,
            target_type TEXT NOT NULL,
            target_id INTEGER,
            content_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT (datetime('now')),
            FOREIGN KEY (sender_emp_id) REFERENCES employees(id)
        );

        CREATE TABLE IF NOT EXISTS broadcast_reactions (
            broadcast_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            reaction TEXT NOT NULL,
            reacted_at TIMESTAMP DEFAULT (datetime('now')),
            PRIMARY KEY (broadcast_id, employee_id),
            FOREIGN KEY (broadcast_id) REFERENCES broadcasts(id) ON DELETE CASCADE,
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS broadcast_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            broadcast_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            comment TEXT NOT NULL,
            commented_at TIMESTAMP DEFAULT (datetime('now')),
            FOREIGN KEY (broadcast_id) REFERENCES broadcasts(id) ON DELETE CASCADE,
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS attendance_fix_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            target_date TEXT NOT NULL,
            request_type TEXT NOT NULL CHECK(request_type IN ('in','out','both')),
            proposed_in TEXT,
            proposed_out TEXT,
            reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending'
                CHECK(status IN ('pending','approved','rejected')),
            reviewed_by INTEGER,
            review_comment TEXT,
            created_at TIMESTAMP DEFAULT (datetime('now')),
            reviewed_at TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_fix_requests_status
            ON attendance_fix_requests(status);

        CREATE TABLE IF NOT EXISTS reminder_log (
            employee_id INTEGER NOT NULL,
            reminder_type TEXT NOT NULL,
            sent_date TEXT NOT NULL,
            PRIMARY KEY (employee_id, reminder_type, sent_date)
        );

        -- Menyu tugmalari joylashuvi (Bosh Admin bot ichidan tahrirlaydi).
        -- Yozuv yo'q = keyboards.py MENU_REGISTRY dagi standart tartib.
        CREATE TABLE IF NOT EXISTS menu_layouts (
            menu_key    TEXT PRIMARY KEY,
            layout_json TEXT NOT NULL,
            updated_at  TIMESTAMP DEFAULT (datetime('now'))
        );

        -- Kalendar kunlari (Bosh Admin/Boss belgilaydi):
        --   'holiday' = Bayram kuni  -> eslatma yo'q + to'liq stavka yoziladi
        --   'dayoff'  = Dam olish    -> eslatma yo'q, stavka hisoblanmaydi
        CREATE TABLE IF NOT EXISTS calendar_days (
            day_date   TEXT PRIMARY KEY,
            day_type   TEXT NOT NULL CHECK(day_type IN ('holiday', 'dayoff')),
            title      TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT (datetime('now'))
        );
        """)

        # Migratsiya: hourly_rate ustunini employees jadvaliga qo'shish
        cursor = conn.execute("PRAGMA table_info(employees)")
        columns = [row[1] for row in cursor.fetchall()]
        if "hourly_rate" not in columns:
            conn.execute("ALTER TABLE employees ADD COLUMN hourly_rate INTEGER DEFAULT 0")

        # Migratsiya: role ustunini employees jadvaliga qo'shish
        # (employee | admin | boss | bosh_admin)
        if "role" not in columns:
            conn.execute(
                "ALTER TABLE employees ADD COLUMN role TEXT DEFAULT 'employee'"
            )
            # Eski adminlar -> 'admin'
            conn.execute(
                "UPDATE employees SET role = 'admin' WHERE is_admin = 1"
            )
            # INITIAL_ADMIN_ID -> 'bosh_admin' (faqat bittagina)
            if INITIAL_ADMIN_ID:
                conn.execute(
                    "UPDATE employees SET role = 'bosh_admin' WHERE telegram_id = ?",
                    (INITIAL_ADMIN_ID,)
                )

        # Migratsiya (Phase 4): plastik karta ustunlari
        if "card_number" not in columns:
            conn.execute(
                "ALTER TABLE employees ADD COLUMN card_number TEXT DEFAULT ''"
            )
        if "card_holder_name" not in columns:
            conn.execute(
                "ALTER TABLE employees ADD COLUMN card_holder_name TEXT DEFAULT ''"
            )

        # Migratsiya: shaxsiy moliya bo'limiga kirish huquqi (0/1)
        if "pf_access" not in columns:
            conn.execute(
                "ALTER TABLE employees ADD COLUMN pf_access INTEGER DEFAULT 0"
            )

        # Migratsiya: linked_employee_id ustuni yo'q bo'lsa qo'shish
        fe_cols = [row[1] for row in conn.execute("PRAGMA table_info(finance_entries)").fetchall()]
        if "linked_employee_id" not in fe_cols:
            conn.execute(
                "ALTER TABLE finance_entries ADD COLUMN linked_employee_id INTEGER"
            )

        # Migratsiya: salary_entries.for_ym — yozuv qaysi oyga tegishli ("YYYY-MM").
        # Bo'sh (eski yozuvlar) bo'lsa created_at oyidan hisoblanadi.
        se_cols = [row[1] for row in conn.execute("PRAGMA table_info(salary_entries)").fetchall()]
        if "for_ym" not in se_cols:
            conn.execute("ALTER TABLE salary_entries ADD COLUMN for_ym TEXT")

    # Lavozimlar tizimini yaratish
    init_positions()

    # Smena normasi tarixi tizimini yaratish
    init_shift_norms()

    # Moliya turkumlari tizimini yaratish
    init_finance_categories()

    # Shaxsiy moliya (PF) turkumlari tizimini yaratish
    init_pf_categories()

    # Referens qurilmalar (beacon) tizimini yaratish
    init_beacon_devices()

    # Boshlang'ich sozlamalar
    defaults = {
        "office_lat": str(DEFAULT_OFFICE_LAT),
        "office_lon": str(DEFAULT_OFFICE_LON),
        "office_radius": str(DEFAULT_OFFICE_RADIUS_M),
        "work_start": DEFAULT_WORK_START,
        "work_end": DEFAULT_WORK_END,
        "office_wifi": DEFAULT_OFFICE_WIFI,
    }
    for key, value in defaults.items():
        if get_setting(key) is None:
            set_setting(key, value)

    # Ofis IP'larini env'dan bazaga ko'chirish — FAQAT jadval bo'sh bo'lganda.
    # Shundan keyin IP'lar bazada boshqariladi (admin tugmasi orqali yangilanadi),
    # Render env'iga tegmasdan. Mavjud IP'lar yo'qolib qolmasligi uchun shu seed bor.
    from config import OFFICE_PUBLIC_IPS
    with get_db() as conn:
        cnt = conn.execute("SELECT COUNT(*) FROM office_ips").fetchone()[0]
        if cnt == 0 and OFFICE_PUBLIC_IPS:
            for ip in OFFICE_PUBLIC_IPS:
                conn.execute(
                    "INSERT OR IGNORE INTO office_ips (ip, label) VALUES (?, ?)",
                    (ip, "env'dan ko'chirildi"),
                )


# ===== Sozlamalar =====

def get_setting(key: str, default=None):
    with get_db() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default


def set_setting(key: str, value: str):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, str(value))
        )


def get_office_config():
    return {
        "lat": float(get_setting("office_lat", DEFAULT_OFFICE_LAT)),
        "lon": float(get_setting("office_lon", DEFAULT_OFFICE_LON)),
        "radius": float(get_setting("office_radius", DEFAULT_OFFICE_RADIUS_M)),
        "wifi": get_setting("office_wifi", DEFAULT_OFFICE_WIFI),
        "work_start": get_setting("work_start", DEFAULT_WORK_START),
        "work_end": get_setting("work_end", DEFAULT_WORK_END),
    }


# ===== Ofis IP'lari (dinamik whitelist) =====

def get_office_ips() -> list:
    """Ofis public IP'lari ro'yxati (faqat IP satrlari)."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT ip FROM office_ips ORDER BY added_at"
        ).fetchall()
        return [r["ip"] for r in rows]


def get_office_ips_detailed() -> list:
    """Ofis IP'lari (ip, label, added_at bilan) — ro'yxat ko'rsatish uchun."""
    with get_db() as conn:
        return conn.execute(
            "SELECT ip, label, added_at FROM office_ips ORDER BY added_at"
        ).fetchall()


def add_office_ip(ip: str, label: str = "", added_by: int = None) -> bool:
    """Ofis IP qo'shish. Yangi qo'shilsa True, allaqachon bor bo'lsa False."""
    ip = (ip or "").strip()
    if not ip:
        return False
    with get_db() as conn:
        cur = conn.execute(
            "INSERT OR IGNORE INTO office_ips (ip, label, added_by) VALUES (?, ?, ?)",
            (ip, label, added_by),
        )
        return cur.rowcount > 0


def remove_office_ip(ip: str) -> int:
    """Ofis IP o'chirish. O'chirilgan qatorlar soni qaytadi."""
    with get_db() as conn:
        cur = conn.execute(
            "DELETE FROM office_ips WHERE ip = ?", ((ip or "").strip(),)
        )
        return cur.rowcount


def office_ip_exists(ip: str) -> bool:
    with get_db() as conn:
        row = conn.execute(
            "SELECT 1 FROM office_ips WHERE ip = ?", ((ip or "").strip(),)
        ).fetchone()
        return row is not None


# ===== Ofis beacon (referens qurilma) =====
# Ofis WiFi'sidagi doim yoqilgan qurilma vaqti-vaqti bilan /beacon URL'ini ochib
# turadi. Server o'sha paytdagi public IP'ni "ofisning joriy IP'si" sifatida yozadi.
# Provayder IP'ni o'zgartirsa — qurilma keyingi signalda avtomatik yangilab qo'yadi.

def set_office_beacon(ip: str, net: str, at: float):
    """Referens qurilma bergan joriy ofis IP'sini (va /24 diapazonini) saqlash."""
    set_setting("beacon_ip", (ip or "").strip())
    set_setting("beacon_net", (net or "").strip())
    set_setting("beacon_at", str(int(at)))


def get_office_beacon() -> dict:
    """Oxirgi beacon holati: {ip, net, at (unix sekund)}."""
    at = get_setting("beacon_at", "")
    return {
        "ip": get_setting("beacon_ip", "") or "",
        "net": get_setting("beacon_net", "") or "",
        "at": int(at) if at and str(at).isdigit() else 0,
    }


def get_beacon_secret() -> str:
    """Referens qurilma URL'idagi maxfiy token (sozlanmagan bo'lsa bo'sh satr)."""
    return get_setting("beacon_secret", "") or ""


def set_beacon_secret(secret: str):
    set_setting("beacon_secret", secret)


# ===== Referens qurilmalar (bir nechta beacon qurilma) =====

def init_beacon_devices():
    """`beacon_devices` jadvalini yaratish + eski bitta-secret beacon'ni ko'chirish."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS beacon_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL DEFAULT '',
                secret TEXT NOT NULL UNIQUE,
                last_ip TEXT DEFAULT '',
                last_net TEXT DEFAULT '',
                last_at INTEGER DEFAULT 0,
                is_primary INTEGER DEFAULT 0,
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT (datetime('now'))
            )
        """)
        # Migratsiya: eski `settings.beacon_secret` bo'lsa — uni qurilma sifatida ko'chiramiz
        legacy = conn.execute(
            "SELECT value FROM settings WHERE key='beacon_secret'"
        ).fetchone()
        if legacy and legacy["value"]:
            sec = legacy["value"]
            exists = conn.execute(
                "SELECT 1 FROM beacon_devices WHERE secret=?", (sec,)
            ).fetchone()
            if not exists:
                def _s(k):
                    r = conn.execute("SELECT value FROM settings WHERE key=?", (k,)).fetchone()
                    return r["value"] if r else ""
                ip, net, at = _s("beacon_ip"), _s("beacon_net"), _s("beacon_at")
                at = int(at) if at and str(at).isdigit() else 0
                conn.execute(
                    "INSERT INTO beacon_devices "
                    "(label, secret, last_ip, last_net, last_at, is_primary) "
                    "VALUES (?, ?, ?, ?, ?, 1)",
                    ("💻 Mac", sec, ip, net, at),
                )


def add_beacon_device(label: str, secret: str, added_by: int = None,
                      is_primary: bool = False) -> int:
    with get_db() as conn:
        if is_primary:
            conn.execute("UPDATE beacon_devices SET is_primary=0")
        cur = conn.execute(
            "INSERT INTO beacon_devices (label, secret, is_primary, added_by) "
            "VALUES (?, ?, ?, ?)",
            (label, secret, 1 if is_primary else 0, added_by),
        )
        return cur.lastrowid


def get_beacon_devices() -> list:
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM beacon_devices ORDER BY is_primary DESC, added_at"
        ).fetchall()


def get_beacon_device(dev_id: int):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM beacon_devices WHERE id=?", (dev_id,)
        ).fetchone()


def get_beacon_device_by_secret(secret: str):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM beacon_devices WHERE secret=?", ((secret or "").strip(),)
        ).fetchone()


def update_beacon_device_ping(secret: str, ip: str, net: str, at: float):
    with get_db() as conn:
        conn.execute(
            "UPDATE beacon_devices SET last_ip=?, last_net=?, last_at=? WHERE secret=?",
            ((ip or "").strip(), (net or "").strip(), int(at), (secret or "").strip()),
        )


def remove_beacon_device(dev_id: int) -> int:
    with get_db() as conn:
        cur = conn.execute("DELETE FROM beacon_devices WHERE id=?", (dev_id,))
        return cur.rowcount


def set_primary_beacon_device(dev_id: int):
    with get_db() as conn:
        conn.execute("UPDATE beacon_devices SET is_primary=0")
        conn.execute("UPDATE beacon_devices SET is_primary=1 WHERE id=?", (dev_id,))


def get_active_beacon_nets(valid_sec: int) -> list:
    """Oxirgi `valid_sec` sekund ichida signal bergan qurilmalar diapazonlari."""
    import time as _t
    cutoff = int(_t.time()) - int(valid_sec)
    with get_db() as conn:
        rows = conn.execute(
            "SELECT DISTINCT last_net FROM beacon_devices "
            "WHERE last_net != '' AND last_at >= ?",
            (cutoff,),
        ).fetchall()
        return [r["last_net"] for r in rows]


# ===== Xodimlar =====

def get_employee_by_telegram_id(telegram_id: int) -> Optional[sqlite3.Row]:
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM employees WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()


def get_employee_by_id(employee_id: int) -> Optional[sqlite3.Row]:
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM employees WHERE id = ?", (employee_id,)
        ).fetchone()


def get_active_employees_count() -> int:
    with get_db() as conn:
        row = conn.execute("SELECT COUNT(*) as cnt FROM employees WHERE is_active = 1").fetchone()
        return row["cnt"]


def create_employee(telegram_id: int, full_name: str, phone: str,
                    position: str, face_encoding: bytes) -> int:
    is_admin = 1 if telegram_id == INITIAL_ADMIN_ID else 0
    # Birinchi admin (INITIAL_ADMIN_ID) avtomatik Bosh Admin bo'ladi
    role = "bosh_admin" if telegram_id == INITIAL_ADMIN_ID else "employee"
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO employees (telegram_id, full_name, phone, position, "
            "face_encoding, is_admin, role) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (telegram_id, full_name, phone, position, face_encoding, is_admin, role)
        )
        return cursor.lastrowid


# ===== Phase 4: Admin-led ro'yxat + plastik karta =====

def phone_key(s: str) -> str:
    """Telefonni solishtirish uchun kalit: faqat raqamlar, oxirgi 9 ta
    (O'zbek mobil raqami). Turli format (+998..., 998..., 90...) bir xil bo'ladi."""
    return re.sub(r"\D", "", s or "")[-9:]


def create_pending_employee(full_name: str, phone: str, position: str) -> int:
    """Admin oldindan qo'shadigan 'pending' xodim. Telegram ID hali yo'q —
    kanonik holat: telegram_id = -id (manfiy, har doim noyob). Xodim /start
    berib telefoni orqali aniqlangach, telegram_id haqiqiy qiymatga o'tadi."""
    import random
    with get_db() as conn:
        last_err = None
        for _ in range(8):
            placeholder = -random.randint(10 ** 8, 10 ** 9 - 1)
            try:
                cur = conn.execute(
                    "INSERT INTO employees (telegram_id, full_name, phone, "
                    "position, face_encoding) VALUES (?, ?, ?, ?, ?)",
                    (placeholder, full_name, phone, position, b"")
                )
                new_id = cur.lastrowid
                # Kanonik: telegram_id = -id (noyob va aniqlanadigan)
                conn.execute(
                    "UPDATE employees SET telegram_id = ? WHERE id = ?",
                    (-new_id, new_id)
                )
                return new_id
            except sqlite3.IntegrityError as e:
                last_err = e
                continue
        raise RuntimeError(f"placeholder allocation failed: {last_err}")


def find_employee_by_phone(phone: str, only_pending: bool = False,
                           include_inactive: bool = True):
    """Telefon (oxirgi 9 raqam) bo'yicha xodimni topish.
    only_pending=True  -> faqat hali bog'lanmagan (telegram_id < 0).
    include_inactive=False -> faqat is_active=1.
    """
    key = phone_key(phone)
    if not key:
        return None
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM employees").fetchall()
    for r in rows:
        if phone_key(r["phone"]) != key:
            continue
        if only_pending and r["telegram_id"] >= 0:
            continue
        if not include_inactive and not r["is_active"]:
            continue
        return r
    return None


def link_pending_to_telegram(employee_id: int, telegram_id: int,
                             face_encoding: bytes):
    """Pending yozuvni haqiqiy Telegram ID va yuz kodi bilan bog'lash."""
    with get_db() as conn:
        conn.execute(
            "UPDATE employees SET telegram_id = ?, face_encoding = ?, "
            "is_active = 1 WHERE id = ?",
            (telegram_id, face_encoding, employee_id)
        )


def update_employee_card(employee_id: int, card_number: str,
                         card_holder_name: str):
    """Karta raqami (16 raqam, probelsiz) va egasi ismini saqlash."""
    with get_db() as conn:
        conn.execute(
            "UPDATE employees SET card_number = ?, card_holder_name = ? "
            "WHERE id = ?",
            (card_number, card_holder_name, employee_id)
        )


def update_employee_profile(employee_id: int, full_name: str = None,
                            position: str = None):
    """Admin xodimni qayta qo'shganda ism/lavozimni yangilash."""
    sets, params = [], []
    if full_name is not None:
        sets.append("full_name = ?")
        params.append(full_name)
    if position is not None:
        sets.append("position = ?")
        params.append(position)
    if not sets:
        return
    params.append(employee_id)
    with get_db() as conn:
        conn.execute(
            f"UPDATE employees SET {', '.join(sets)} WHERE id = ?", params
        )


def get_all_employees(active_only=True):
    with get_db() as conn:
        if active_only:
            return conn.execute(
                "SELECT * FROM employees WHERE is_active = 1 ORDER BY full_name"
            ).fetchall()
        return conn.execute("SELECT * FROM employees ORDER BY full_name").fetchall()


# ===== Menyu joylashuvi =====

def get_menu_layout(menu_key: str):
    """Saqlangan joylashuv (qatorlar ro'yxati) yoki None — standart ishlatiladi."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT layout_json FROM menu_layouts WHERE menu_key = ?", (menu_key,)
        ).fetchone()
    if not row:
        return None
    try:
        layout = json.loads(row["layout_json"])
    except (ValueError, TypeError):
        return None
    # Buzuq yozuv botni yiqitmasin — faqat ro'yxatlar ro'yxati qabul qilinadi
    if not isinstance(layout, list) or not all(isinstance(r, list) for r in layout):
        return None
    return layout


def set_menu_layout(menu_key: str, layout):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO menu_layouts (menu_key, layout_json, updated_at) "
            "VALUES (?, ?, datetime('now')) "
            "ON CONFLICT(menu_key) DO UPDATE SET "
            "layout_json = excluded.layout_json, updated_at = excluded.updated_at",
            (menu_key, json.dumps(layout))
        )


def reset_menu_layout(menu_key: str):
    """Saqlangan joylashuvni o'chirish — standart tartibga qaytadi."""
    with get_db() as conn:
        conn.execute("DELETE FROM menu_layouts WHERE menu_key = ?", (menu_key,))


# ===== Kalendar: bayram va dam olish kunlari =====
# HOLIDAY ('holiday') — Bayram kuni: eslatma yuborilmaydi VA o'sha kun uchun
#                       har bir xodimga to'liq kunlik stavka yoziladi.
# DAYOFF  ('dayoff')  — Dam olish kuni: eslatma yuborilmaydi, lekin ish haqqi
#                       hisoblanmaydi (xodim kelib ishlagan bo'lsa — odatdagidek).

HOLIDAY = "holiday"
DAYOFF = "dayoff"
CALENDAR_TYPES = (HOLIDAY, DAYOFF)


def get_calendar_day(day_date: str):
    """Bitta kunning yozuvi (yo'q bo'lsa None). day_date: 'YYYY-MM-DD'."""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM calendar_days WHERE day_date = ?", (day_date,)
        ).fetchone()


def get_calendar_day_type(day_date: str):
    """Kun turi: 'holiday' | 'dayoff' | None."""
    row = get_calendar_day(day_date)
    return row["day_type"] if row else None


def set_calendar_day(day_date: str, day_type: str,
                     created_by: int = None, title: str = None) -> None:
    """Kunni belgilash yoki turini almashtirish (UPSERT)."""
    if day_type not in CALENDAR_TYPES:
        raise ValueError(f"Noma'lum kun turi: {day_type}")
    with get_db() as conn:
        conn.execute(
            "INSERT INTO calendar_days (day_date, day_type, title, created_by) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(day_date) DO UPDATE SET "
            "day_type = excluded.day_type, "
            "title = excluded.title, "
            "created_by = excluded.created_by, "
            "created_at = datetime('now')",
            (day_date, day_type, title, created_by)
        )


def clear_calendar_day(day_date: str) -> int:
    """Belgini olib tashlash. Nechta qator o'chirilganini qaytaradi."""
    with get_db() as conn:
        return conn.execute(
            "DELETE FROM calendar_days WHERE day_date = ?", (day_date,)
        ).rowcount


def toggle_calendar_day(day_date: str, day_type: str,
                        created_by: int = None) -> str:
    """Kunni bosganda: bo'sh -> day_type, o'sha tur -> bo'sh, boshqa tur -> day_type.

    Yangi holatni qaytaradi ('holiday' | 'dayoff' | None).
    """
    current = get_calendar_day_type(day_date)
    if current == day_type:
        clear_calendar_day(day_date)
        return None
    set_calendar_day(day_date, day_type, created_by)
    return day_type


def get_calendar_month(year: int, month: int) -> dict:
    """Oydagi belgilangan kunlar: {'YYYY-MM-DD': 'holiday'|'dayoff'}."""
    ym = f"{year:04d}-{month:02d}"
    with get_db() as conn:
        rows = conn.execute(
            "SELECT day_date, day_type FROM calendar_days "
            "WHERE substr(day_date, 1, 7) = ? ORDER BY day_date",
            (ym,)
        ).fetchall()
    return {r["day_date"]: r["day_type"] for r in rows}


def get_calendar_days_by_type(year: int, month: int, day_type: str) -> list:
    """Oydagi berilgan turdagi kunlar ro'yxati (sanalar, o'sish tartibida)."""
    return [d for d, t in get_calendar_month(year, month).items() if t == day_type]


def is_non_working_day(day_date: str) -> bool:
    """Shu kun bayram yoki dam olish deb belgilanganmi (eslatma yuborilmaydi)."""
    return get_calendar_day_type(day_date) is not None


# ===== Eslatma yuboriladigan hafta kunlari =====
# Sozlama: settings['reminder_days'] — 7 belgili satr, indeks 0=Dushanba ...
# 6=Yakshanba; '1' = eslatma yuboriladi, '0' = yuborilmaydi.

REMINDER_DAYS_KEY = "reminder_days"
DEFAULT_REMINDER_DAYS = "1111111"


def get_reminder_days() -> set:
    """Eslatma yuboriladigan hafta kunlari to'plami (0=Dushanba ... 6=Yakshanba)."""
    raw = get_setting(REMINDER_DAYS_KEY, DEFAULT_REMINDER_DAYS) or ""
    raw = str(raw).strip()
    if len(raw) != 7 or any(ch not in "01" for ch in raw):
        raw = DEFAULT_REMINDER_DAYS  # buzuq qiymat botni to'xtatmasin
    return {i for i, ch in enumerate(raw) if ch == "1"}


def set_reminder_days(days) -> None:
    """Hafta kunlari to'plamini saqlash."""
    days = set(days)
    set_setting(REMINDER_DAYS_KEY,
                "".join("1" if i in days else "0" for i in range(7)))


def toggle_reminder_day(index: int) -> bool:
    """Bitta hafta kunini yoqish/o'chirish. Yangi holatni (True=yoqilgan) qaytaradi."""
    if not 0 <= index <= 6:
        raise ValueError("Hafta kuni indeksi 0..6 bo'lishi kerak")
    days = get_reminder_days()
    if index in days:
        days.discard(index)
        new_state = False
    else:
        days.add(index)
        new_state = True
    set_reminder_days(days)
    return new_state


def set_pf_access(employee_id: int, value: int):
    """Xodimga 'Shaxsiy xarajatlarim' bo'limini yoqish (1) yoki o'chirish (0)."""
    with get_db() as conn:
        conn.execute(
            "UPDATE employees SET pf_access = ? WHERE id = ?",
            (1 if value else 0, employee_id)
        )


def get_all_admins():
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM employees WHERE is_admin = 1 AND is_active = 1"
        ).fetchall()


def deactivate_employee(employee_id: int):
    with get_db() as conn:
        conn.execute("UPDATE employees SET is_active = 0 WHERE id = ?", (employee_id,))


def reactivate_employee(employee_id: int):
    with get_db() as conn:
        conn.execute("UPDATE employees SET is_active = 1 WHERE id = ?", (employee_id,))


def set_admin_status(employee_id: int, is_admin: bool):
    """is_admin'ni yangilash va role'ni mos ravishda sinxronlash.

    XAVFSIZLIK: Bosh Admin va Boss bu funksiya orqali pasaytirilmaydi —
    ularning roli alohida funksiyalar orqali boshqariladi (set_role).
    """
    with get_db() as conn:
        # Joriy rolni tekshirish — bosh_admin/boss'ni saqlab qolish uchun
        row = conn.execute(
            "SELECT role FROM employees WHERE id = ?", (employee_id,)
        ).fetchone()
        current_role = (row["role"] if row else None) or "employee"
        if current_role in ("bosh_admin", "boss"):
            # Bunday foydalanuvchilarni bu funksiya tegmaydi
            return
        new_role = "admin" if is_admin else "employee"
        conn.execute(
            "UPDATE employees SET is_admin = ?, role = ? WHERE id = ?",
            (1 if is_admin else 0, new_role, employee_id)
        )


# ===== Rollar (bosh_admin, boss, admin) =====

def set_role(employee_id: int, role: str):
    """Xodimning rolini to'g'ridan-to'g'ri o'rnatish va is_admin'ni sinxronlash.

    Faqat shu funksiya bosh_admin yoki boss tayinlay/olib tashlay oladi.
    """
    is_admin_flag = 1 if role in ("admin", "bosh_admin") else 0
    with get_db() as conn:
        conn.execute(
            "UPDATE employees SET role = ?, is_admin = ? WHERE id = ?",
            (role, is_admin_flag, employee_id)
        )


def get_bosh_admin():
    """Bitta Bosh Admin (yoki None)."""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM employees WHERE role = 'bosh_admin' AND is_active = 1 "
            "LIMIT 1"
        ).fetchone()


def get_boss():
    """Bitta Boss (yoki None — hali tayinlanmagan bo'lishi mumkin)."""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM employees WHERE role = 'boss' AND is_active = 1 "
            "LIMIT 1"
        ).fetchone()

def get_bosses():
    """Barcha faol Bosslar ro'yxati (bir nechta bo'lishi mumkin)."""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM employees WHERE role = 'boss' AND is_active = 1 "
            "ORDER BY full_name"
        ).fetchall()



# ===== Davomat =====

def get_today_attendance(employee_id: int):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM attendance WHERE employee_id = ? "
            "AND date(timestamp, '+5 hours') = date('now', '+5 hours') "
            "ORDER BY datetime(timestamp)",
            (employee_id,)
        ).fetchall()


def get_last_check_today(employee_id: int):
    today = get_today_attendance(employee_id)
    return today[-1] if today else None


def record_attendance(employee_id, check_type, latitude, longitude,
                       distance, wifi_name, wifi_match, face_score, photo_file_id):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO attendance (employee_id, check_type, timestamp, latitude, longitude, "
            "distance_meters, wifi_name, wifi_match, face_match_score, photo_file_id) "
            "VALUES (?, ?, datetime('now'), ?, ?, ?, ?, ?, ?, ?)",
            (employee_id, check_type, latitude, longitude, distance,
             wifi_name, 1 if wifi_match else 0, face_score, photo_file_id)
        )


def get_monthly_attendance(employee_id: int, year: int, month: int):
    with get_db() as conn:
        return conn.execute(
            """
            SELECT date(timestamp, '+5 hours') as day,
                   MIN(CASE WHEN check_type = 'in' THEN time(timestamp, '+5 hours') END) as first_in,
                   MAX(CASE WHEN check_type = 'out' THEN time(timestamp, '+5 hours') END) as last_out
            FROM attendance
            WHERE employee_id = ?
              AND strftime('%Y', timestamp, '+5 hours') = ?
              AND strftime('%m', timestamp, '+5 hours') = ?
            GROUP BY day
            ORDER BY day DESC
            """,
            (employee_id, str(year), f"{month:02d}")
        ).fetchall()


def get_today_all_attendance():
    with get_db() as conn:
        return conn.execute(
            """
            SELECT e.full_name, e.position, e.id as employee_id,
                   MIN(CASE WHEN a.check_type = 'in' THEN time(a.timestamp, '+5 hours') END) as first_in,
                   MAX(CASE WHEN a.check_type = 'out' THEN time(a.timestamp, '+5 hours') END) as last_out,
                   MAX(CASE WHEN a.wifi_match = 0 THEN 1 ELSE 0 END) as has_wifi_warning
            FROM employees e
            LEFT JOIN attendance a ON a.employee_id = e.id
                AND date(a.timestamp, '+5 hours') = date('now', '+5 hours')
            WHERE e.is_active = 1 AND e.role != 'boss'
            GROUP BY e.id
            ORDER BY e.full_name
            """
        ).fetchall()

# ===== Rasm takrorlanishini bloklash =====

def is_photo_used_recently(file_unique_id: str, days: int = 30) -> bool:
    """Rasm oxirgi N kunda ishlatilganmi?"""
    with get_db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM used_photos "
            "WHERE file_unique_id = ? AND used_at > datetime('now', ?)",
            (file_unique_id, f"-{days} days")
        ).fetchone()
        return row["cnt"] > 0


def record_photo_used(file_unique_id: str, employee_id: int):
    """Ishlatilgan rasmni qayd qilish"""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO used_photos (file_unique_id, employee_id) VALUES (?, ?)",
            (file_unique_id, employee_id)
        )


# ===== Admin davomat tahrirlash =====

def get_day_attendance(employee_id: int, date_local: str):
    """Berilgan mahalliy kun (YYYY-MM-DD, Toshkent vaqti) uchun barcha
    davomat yozuvlari (eski → yangi tartibda)."""
    with get_db() as conn:
        return conn.execute(
            "SELECT id, check_type, timestamp FROM attendance "
            "WHERE employee_id = ? "
            "AND date(timestamp, '+5 hours') = ? "
            "ORDER BY datetime(timestamp) ASC",
            (employee_id, date_local)
        ).fetchall()


def delete_day_attendance(employee_id: int, date_local: str) -> int:
    """Berilgan mahalliy kun davomat yozuvlarini o'chirish.
    date_local: 'YYYY-MM-DD' (Toshkent vaqti)."""
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM attendance WHERE employee_id = ? "
            "AND date(timestamp, '+5 hours') = ?",
            (employee_id, date_local)
        )
        return cursor.rowcount


def add_manual_attendance(employee_id: int, check_type: str, time_str: str,
                          date_local: str = None):
    """Admin tomonidan qo'lda davomat qo'shish.
    date_local: 'YYYY-MM-DD' mahalliy sana (None bo'lsa — bugun)."""
    from datetime import datetime as _dt
    from tzutil import now as tz_now, OFFSET
    h, m = map(int, time_str.split(":"))
    if date_local:
        y, mo, d = map(int, date_local.split("-"))
        ts_local = _dt(y, mo, d, h, m, 0)
    else:
        ts_local = tz_now().replace(hour=h, minute=m, second=0, microsecond=0)
    # Admin mahalliy (Toshkent) vaqt kiritadi -> bazaga UTC saqlaymiz
    ts = ts_local - OFFSET
    with get_db() as conn:
        conn.execute(
            "INSERT INTO attendance (employee_id, check_type, timestamp, "
            "wifi_name, wifi_match, face_match_score) "
            "VALUES (?, ?, ?, ?, 1, 1.0)",
            (employee_id, check_type, ts.isoformat(sep=' '), "Admin qo'shdi")
        )


def delete_day_attendance_by_type(employee_id: int, date_local: str,
                                  check_type: str) -> int:
    """Berilgan mahalliy kunning faqat bitta turdagi ('in' yoki 'out')
    yozuvlarini o'chirish. date_local: 'YYYY-MM-DD' (Toshkent vaqti)."""
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM attendance WHERE employee_id = ? "
            "AND date(timestamp, '+5 hours') = ? AND check_type = ?",
            (employee_id, date_local, check_type)
        )
        return cursor.rowcount


# ===== Web dashboard =====

def get_dashboard_today():
    """Bugungi holat (barcha faol xodimlar, boss'siz): first_in/last_out
    Toshkent vaqtida + kunning oxirgi yozuv turi (holatni aniqlash uchun)."""
    with get_db() as conn:
        return conn.execute(
            """
            SELECT e.id, e.telegram_id, e.full_name, e.position,
                   MIN(CASE WHEN a.check_type = 'in' THEN time(a.timestamp, '+5 hours') END) as first_in,
                   MAX(CASE WHEN a.check_type = 'out' THEN time(a.timestamp, '+5 hours') END) as last_out,
                   (SELECT a2.check_type FROM attendance a2
                     WHERE a2.employee_id = e.id
                       AND date(a2.timestamp, '+5 hours') = date('now', '+5 hours')
                     ORDER BY datetime(a2.timestamp) DESC LIMIT 1) as last_type
            FROM employees e
            LEFT JOIN attendance a ON a.employee_id = e.id
                AND date(a.timestamp, '+5 hours') = date('now', '+5 hours')
            WHERE e.is_active = 1 AND e.role != 'boss'
            GROUP BY e.id
            ORDER BY e.full_name
            """
        ).fetchall()


def get_dashboard_month(year: int, month: int):
    """Oylik jamlanma uchun xom qatorlar: har faol xodim (boss'siz) uchun
    kunma-kun first_in/last_out (Toshkent vaqtida). Kelmagan xodim ham
    ro'yxatda chiqadi (day NULL)."""
    with get_db() as conn:
        return conn.execute(
            """
            SELECT e.id, e.full_name, e.position, d.day, d.first_in, d.last_out
            FROM employees e
            LEFT JOIN (
                SELECT employee_id, date(timestamp, '+5 hours') as day,
                       MIN(CASE WHEN check_type = 'in' THEN time(timestamp, '+5 hours') END) as first_in,
                       MAX(CASE WHEN check_type = 'out' THEN time(timestamp, '+5 hours') END) as last_out
                FROM attendance
                WHERE strftime('%Y', timestamp, '+5 hours') = ?
                  AND strftime('%m', timestamp, '+5 hours') = ?
                GROUP BY employee_id, day
            ) d ON d.employee_id = e.id
            WHERE e.is_active = 1 AND e.role != 'boss'
            ORDER BY e.full_name, d.day
            """,
            (str(year), f"{month:02d}")
        ).fetchall()


def get_employees_admin():
    """Web panel uchun to'liq hodimlar ro'yxati (faol+nofaol, lavozim bilan)."""
    with get_db() as conn:
        return conn.execute(
            """
            SELECT e.id, e.telegram_id, e.full_name, e.phone, e.position,
                   e.role, e.is_active, e.hourly_rate, e.daily_rate,
                   e.card_number, e.card_holder_name,
                   datetime(e.registered_at, '+5 hours') as registered_at,
                   e.position_id, p.name as position_name, p.work_hours
            FROM employees e
            LEFT JOIN positions p ON p.id = e.position_id
            ORDER BY e.is_active DESC, e.full_name
            """
        ).fetchall()


# ===== Davomat tuzatish so'rovlari =====

def create_fix_request(employee_id: int, target_date: str, request_type: str,
                       proposed_in, proposed_out, reason: str) -> int:
    """Yangi tuzatish so'rovi. Yangi yozuv id'si qaytadi."""
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO attendance_fix_requests "
            "(employee_id, target_date, request_type, proposed_in, proposed_out, reason) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (employee_id, target_date, request_type, proposed_in, proposed_out, reason)
        )
        return cur.lastrowid


def has_pending_fix_request(employee_id: int, target_date: str) -> bool:
    """Shu kun uchun kutilayotgan so'rov bormi?"""
    with get_db() as conn:
        row = conn.execute(
            "SELECT 1 FROM attendance_fix_requests "
            "WHERE employee_id = ? AND target_date = ? AND status = 'pending' LIMIT 1",
            (employee_id, target_date)
        ).fetchone()
        return row is not None


def count_fix_requests_today(employee_id: int) -> int:
    """Xodim bugun (Toshkent kuni) nechta so'rov yuborgan."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM attendance_fix_requests "
            "WHERE employee_id = ? "
            "AND date(created_at, '+5 hours') = date('now', '+5 hours')",
            (employee_id,)
        ).fetchone()
        return row["cnt"]


def get_fix_request(req_id: int):
    """Bitta so'rov (xodim ma'lumotlari bilan)."""
    with get_db() as conn:
        return conn.execute(
            "SELECT r.*, e.full_name, e.telegram_id FROM attendance_fix_requests r "
            "JOIN employees e ON e.id = r.employee_id WHERE r.id = ?",
            (req_id,)
        ).fetchone()


def get_pending_fix_requests():
    """Barcha kutilayotgan so'rovlar (eski → yangi)."""
    with get_db() as conn:
        return conn.execute(
            "SELECT r.*, e.full_name, e.telegram_id FROM attendance_fix_requests r "
            "JOIN employees e ON e.id = r.employee_id "
            "WHERE r.status = 'pending' ORDER BY datetime(r.created_at)"
        ).fetchall()


def claim_fix_request(req_id: int, status: str, reviewed_by: int,
                      comment: str = None) -> bool:
    """So'rovni atomik yakunlash. Ikki admin bir vaqtda bossagina bittasi
    yutadi (WHERE status='pending'). Muvaffaqiyatda True."""
    with get_db() as conn:
        cur = conn.execute(
            "UPDATE attendance_fix_requests "
            "SET status = ?, reviewed_by = ?, review_comment = ?, "
            "reviewed_at = datetime('now') "
            "WHERE id = ? AND status = 'pending'",
            (status, reviewed_by, comment, req_id)
        )
        return cur.rowcount == 1


# ===== Eslatmalar jurnali =====

def try_mark_reminder(employee_id: int, reminder_type: str, sent_date: str) -> bool:
    """Eslatmani atomik band qilish: birinchi urinishda True, takrorda False.
    Restart'da ham takrorlanmaydi (bazada saqlanadi)."""
    with get_db() as conn:
        cur = conn.execute(
            "INSERT OR IGNORE INTO reminder_log (employee_id, reminder_type, sent_date) "
            "VALUES (?, ?, ?)",
            (employee_id, reminder_type, sent_date)
        )
        return cur.rowcount == 1


# ===== Ish haqqi =====

def set_hourly_rate(employee_id: int, rate: int):
    """Xodimga soatbay stavka belgilash"""
    with get_db() as conn:
        conn.execute(
            "UPDATE employees SET hourly_rate = ? WHERE id = ?",
            (rate, employee_id)
        )


def get_monthly_worked_minutes(employee_id: int, year: int, month: int) -> int:
    """Oyda ishlangan umumiy daqiqalar (Keldim-Ketdim juftliklari asosida)"""
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT date(timestamp, '+5 hours') as day,
                   MIN(CASE WHEN check_type = 'in' THEN time(timestamp, '+5 hours') END) as first_in,
                   MAX(CASE WHEN check_type = 'out' THEN time(timestamp, '+5 hours') END) as last_out
            FROM attendance
            WHERE employee_id = ?
              AND strftime('%Y', timestamp, '+5 hours') = ?
              AND strftime('%m', timestamp, '+5 hours') = ?
            GROUP BY day
            """,
            (employee_id, str(year), f"{month:02d}")
        ).fetchall()

    total = 0
    for row in rows:
        if row["first_in"] and row["last_out"]:
            try:
                ih, im, _ = map(int, row["first_in"].split(":"))
                oh, om, _ = map(int, row["last_out"].split(":"))
                minutes = (oh * 60 + om) - (ih * 60 + im)
                if minutes > 0:
                    total += minutes
            except Exception:
                pass
    return total


def get_monthly_salary_entries(employee_id: int, year: int, month: int):
    """Oyda barcha ish haqqi yozuvlarini olish (faol va bekor qilinmagan)"""
    with get_db() as conn:
        return conn.execute(
            """
            SELECT * FROM salary_entries
            WHERE employee_id = ?
              AND strftime('%Y', created_at, '+5 hours') = ?
              AND strftime('%m', created_at, '+5 hours') = ?
              AND cancelled = 0
            ORDER BY created_at DESC
            """,
            (employee_id, str(year), f"{month:02d}")
        ).fetchall()


def get_salary_totals_by_type(employee_id: int, year: int, month: int) -> dict:
    """Har bir kategoriya bo'yicha jami summa"""
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT entry_type, SUM(amount) as total
            FROM salary_entries
            WHERE employee_id = ?
              AND COALESCE(for_ym, strftime('%Y-%m', created_at, '+5 hours')) = ?
              AND cancelled = 0
            GROUP BY entry_type
            """,
            (employee_id, f"{year:04d}-{month:02d}")
        ).fetchall()
    totals = {"avans": 0, "jarima": 0, "mukofot": 0, "bonus": 0, "mahsulot": 0}
    for row in rows:
        if row["entry_type"] in totals:
            totals[row["entry_type"]] = row["total"]
    return totals


def add_salary_entry(employee_id: int, entry_type: str, amount: int, reason: str,
                     created_by: int, for_ym: str | None = None) -> int:
    """Yangi ish haqqi yozuvini qo'shish. ID qaytaradi.

    for_ym — yozuv qaysi oyga tegishli ("YYYY-MM"); None bo'lsa created_at oyi.
    """
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO salary_entries (employee_id, entry_type, amount, reason, created_by, for_ym) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (employee_id, entry_type, amount, reason, created_by, for_ym)
        )
        return cursor.lastrowid


def cancel_salary_entry(entry_id: int, cancelled_by: int, cancel_reason: str):
    """Yozuvni bekor qilish (tarix saqlanadi)"""
    with get_db() as conn:
        conn.execute(
            "UPDATE salary_entries SET cancelled = 1, cancelled_by = ?, "
            "cancelled_at = datetime('now'), cancel_reason = ? "
            "WHERE id = ?",
            (cancelled_by, cancel_reason, entry_id)
        )


def get_salary_entry(entry_id: int):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM salary_entries WHERE id = ?", (entry_id,)
        ).fetchone()


def get_active_salary_entries(employee_id: int, year: int, month: int):
    """Berilgan oyning faol (bekor qilinmagan) yozuvlari — for_ym yoki created_at oyi bo'yicha"""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM salary_entries WHERE employee_id = ? "
            "AND COALESCE(for_ym, strftime('%Y-%m', created_at, '+5 hours')) = ? "
            "AND cancelled = 0 ORDER BY created_at DESC",
            (employee_id, f"{year:04d}-{month:02d}")
        ).fetchall()


# ===== Oy yopish =====

def is_month_closed(year: int, month: int) -> bool:
    with get_db() as conn:
        row = conn.execute(
            "SELECT 1 FROM closed_months WHERE year = ? AND month = ?",
            (year, month)
        ).fetchone()
        return bool(row)


def close_month(year: int, month: int, closed_by: int):
    with get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO closed_months (year, month, closed_by, closed_at) "
            "VALUES (?, ?, ?, datetime('now'))",
            (year, month, closed_by)
        )


def reopen_month(year: int, month: int):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM closed_months WHERE year = ? AND month = ?",
            (year, month)
        )


def get_closed_months(limit: int = 10):
    """Oxirgi yopilgan oylar (eng yangisi birinchi). Arxiv uchun."""
    with get_db() as conn:
        return conn.execute(
            "SELECT year, month, closed_at FROM closed_months "
            "ORDER BY year DESC, month DESC LIMIT ?",
            (limit,)
        ).fetchall()


# ===== Audit =====

def get_audit_entries(year: int, month: int, limit: int = 30):
    """Audit tarixi: kim qo'shgan/bekor qilgan ma'lumotlari bilan"""
    with get_db() as conn:
        return conn.execute(
            """
            SELECT se.*,
                   e.full_name AS employee_name,
                   creator.full_name AS creator_name,
                   canceller.full_name AS canceller_name
            FROM salary_entries se
            LEFT JOIN employees e ON se.employee_id = e.id
            LEFT JOIN employees creator ON se.created_by = creator.id
            LEFT JOIN employees canceller ON se.cancelled_by = canceller.id
            WHERE strftime('%Y', se.created_at, '+5 hours') = ?
              AND strftime('%m', se.created_at, '+5 hours') = ?
            ORDER BY se.created_at DESC
            LIMIT ?
            """,
            (str(year), f"{month:02d}", limit)
        ).fetchall()


def get_all_employees_salary_summary(year: int, month: int):
    """Bu oy uchun barcha xodimlarning xulosasi (Excel uchun).

    O'chirilgan (faolsiz) xodimlar ham — agar shu oyda faoliyati (ishlangan vaqt
    yoki ish haqqi yozuvi) bo'lsa — kiritiladi. Shunday qilib xodim o'chirilgandan
    keyin ham o'sha oygi ma'lumotlari hisobotda saqlanib qoladi.
    Asosiy ish haqqi kunbay (lavozim/kunlik stavka) bo'yicha hisoblanadi.
    """
    employees = get_all_employees(active_only=False)
    result = []
    for emp in employees:
        minutes = get_monthly_worked_minutes(emp["id"], year, month)
        totals = get_salary_totals_by_type(emp["id"], year, month)
        base = get_monthly_base_salary(emp["id"], year, month)

        # Faolsiz (o'chirilgan) xodim faqat shu oyda faoliyati bo'lsa ko'rsatiladi
        has_activity = bool(minutes) or bool(base) or any(totals.values())
        is_active = bool(emp["is_active"]) if "is_active" in emp.keys() else True
        if not is_active and not has_activity:
            continue

        # Ko'rsatiladigan stavka: kunlik stavka (bo'lmasa — eski soatbay)
        daily = emp["daily_rate"] if "daily_rate" in emp.keys() and emp["daily_rate"] else 0
        hourly = emp["hourly_rate"] if "hourly_rate" in emp.keys() and emp["hourly_rate"] else 0
        rate = daily if daily else hourly

        total = (base - totals["avans"] - totals["jarima"]
                 + totals["mukofot"] + totals["bonus"] - totals["mahsulot"])
        result.append({
            "employee": emp,
            "rate": rate,
            "minutes": minutes,
            "base": base,
            "totals": totals,
            "total": total,
        })
    return result


# ===== Vazifalar (Tasks) =====

def create_task(title: str, description: str, assigned_to: int,
                assigned_by: int, deadline: str = None) -> int:
    """Yangi vazifa yaratish. deadline — ISO format yoki None."""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title, description, assigned_to, assigned_by, deadline) "
            "VALUES (?, ?, ?, ?, ?)",
            (title.strip(), (description or None), assigned_to, assigned_by, deadline)
        )
        return cursor.lastrowid


def get_task(task_id: int):
    """Bitta vazifa + tayinlovchi va xodim ismlari bilan."""
    with get_db() as conn:
        return conn.execute(
            """
            SELECT t.*,
                   emp.full_name AS assigned_to_name,
                   emp.telegram_id AS assigned_to_tg,
                   bys.full_name AS assigned_by_name,
                   bys.telegram_id AS assigned_by_tg
            FROM tasks t
            LEFT JOIN employees emp ON t.assigned_to = emp.id
            LEFT JOIN employees bys ON t.assigned_by = bys.id
            WHERE t.id = ?
            """,
            (task_id,)
        ).fetchone()


def get_open_tasks(employee_id: int):
    """Xodimning hozirgi ochiq vazifalari."""
    with get_db() as conn:
        return conn.execute(
            """
            SELECT t.*, bys.full_name AS assigned_by_name
            FROM tasks t
            LEFT JOIN employees bys ON t.assigned_by = bys.id
            WHERE t.assigned_to = ? AND t.status = 'open'
            ORDER BY t.created_at DESC
            """,
            (employee_id,)
        ).fetchall()


def get_recent_tasks_for_employee(employee_id: int, limit: int = 20):
    """Xodimning so'nggi vazifalari (har qanday holatda)."""
    with get_db() as conn:
        return conn.execute(
            """
            SELECT t.*, bys.full_name AS assigned_by_name
            FROM tasks t
            LEFT JOIN employees bys ON t.assigned_by = bys.id
            WHERE t.assigned_to = ?
            ORDER BY (t.status='open') DESC, t.created_at DESC
            LIMIT ?
            """,
            (employee_id, limit)
        ).fetchall()


def complete_task(task_id: int):
    """Vazifani tugatilgan deb belgilash."""
    with get_db() as conn:
        conn.execute(
            "UPDATE tasks SET status='completed', completed_at=datetime('now') "
            "WHERE id = ? AND status='open'",
            (task_id,)
        )


def cancel_task(task_id: int):
    """Vazifani bekor qilish (admin/boss tomonidan)."""
    with get_db() as conn:
        conn.execute(
            "UPDATE tasks SET status='cancelled' WHERE id = ? AND status='open'",
            (task_id,)
        )


def skip_task(task_id: int):
    """Vazifa Ketdim chog'ida tugatilmagan deb belgilangani — log yozuvi."""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO task_skips (task_id) VALUES (?)", (task_id,)
        )


def get_skip_history(task_id: int):
    """Vazifa qachon-qachon o'tkazib yuborilgan."""
    with get_db() as conn:
        return conn.execute(
            "SELECT skipped_at FROM task_skips WHERE task_id = ? ORDER BY skipped_at DESC",
            (task_id,)
        ).fetchall()


def get_open_tasks_with_skips(employee_id: int):
    """Tugatilmagan vazifalar va har birining o'tkazib yuborilgan kunlari soni.
    Admin/Boss xodim profilini ko'rganda foydalaniladi.
    """
    with get_db() as conn:
        return conn.execute(
            """
            SELECT t.*,
                   bys.full_name AS assigned_by_name,
                   (SELECT COUNT(*) FROM task_skips ts WHERE ts.task_id = t.id) AS skip_count,
                   (SELECT MAX(skipped_at) FROM task_skips ts WHERE ts.task_id = t.id) AS last_skipped_at
            FROM tasks t
            LEFT JOIN employees bys ON t.assigned_by = bys.id
            WHERE t.assigned_to = ? AND t.status = 'open'
            ORDER BY t.created_at DESC
            """,
            (employee_id,)
        ).fetchall()


# ===== Moliya bo'limi (Phase 4) =====
# Konventsiya: har Boss/Bosh Admin uchun alohida daftar (owner_id orqali ajratiladi).

def create_finance_entry(owner_id: int, entry_type: str, category: str,
                         amount: int, note: str = None,
                         linked_employee_id: int = None,
                         entry_date_utc: str = None) -> int:
    """Kirim yoki chiqim yozuvi qo'shish.
    entry_type: 'income' yoki 'expense'.
    linked_employee_id: Avans uchun xodim ID (ixtiyoriy).
    entry_date_utc: 'YYYY-MM-DD HH:MM:SS' (UTC). None bo'lsa — hozirgi vaqt.
    """
    with get_db() as conn:
        if entry_date_utc:
            cursor = conn.execute(
                "INSERT INTO finance_entries "
                "(owner_id, entry_type, category, amount, note, linked_employee_id, entry_date) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (owner_id, entry_type, category, amount,
                 (note or None), linked_employee_id or None, entry_date_utc)
            )
        else:
            cursor = conn.execute(
                "INSERT INTO finance_entries "
                "(owner_id, entry_type, category, amount, note, linked_employee_id) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (owner_id, entry_type, category, amount,
                 (note or None), linked_employee_id or None)
            )
        return cursor.lastrowid


def get_finance_entry(entry_id: int, owner_id: int):
    """Bitta yozuv (faqat egasiniki)."""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM finance_entries WHERE id = ? AND owner_id = ?",
            (entry_id, owner_id)
        ).fetchone()


def get_finance_entries_by_date(owner_id: int, date_str: str):
    """Berilgan kun (Toshkent vaqti, 'YYYY-MM-DD') bo'yicha yozuvlar."""
    with get_db() as conn:
        return conn.execute(
            """
            SELECT *
            FROM finance_entries
            WHERE owner_id = ?
              AND date(entry_date, '+5 hours') = ?
            ORDER BY entry_date ASC
            """,
            (owner_id, date_str)
        ).fetchall()


def delete_finance_entry(entry_id: int, owner_id: int) -> bool:
    """Yozuvni o'chirish (faqat egasi). True — o'chirildi."""
    with get_db() as conn:
        cur = conn.execute(
            "DELETE FROM finance_entries WHERE id = ? AND owner_id = ?",
            (entry_id, owner_id)
        )
        return cur.rowcount > 0


def get_finance_balance(owner_id: int) -> int:
    """Umumiy qoldiq: barcha kirimlar − barcha chiqimlar."""
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(SUM(CASE WHEN entry_type='income' THEN amount
                                     ELSE -amount END), 0) AS bal
            FROM finance_entries WHERE owner_id = ?
            """,
            (owner_id,)
        ).fetchone()
        return row["bal"] or 0


def get_finance_balance_before(owner_id: int, year: int, month: int) -> int:
    """Berilgan oy boshigacha (Toshkent vaqti) yig'ilgan qoldiq."""
    first_day = f"{year:04d}-{month:02d}-01"
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(SUM(CASE WHEN entry_type='income' THEN amount
                                     ELSE -amount END), 0) AS bal
            FROM finance_entries
            WHERE owner_id = ?
              AND date(entry_date, '+5 hours') < ?
            """,
            (owner_id, first_day)
        ).fetchone()
        return row["bal"] or 0


def get_monthly_finance_entries(owner_id: int, year: int, month: int):
    """Berilgan oydagi barcha yozuvlar (Toshkent vaqtiga ko'ra)."""
    ystr = f"{year:04d}"
    mstr = f"{month:02d}"
    with get_db() as conn:
        return conn.execute(
            """
            SELECT *
            FROM finance_entries
            WHERE owner_id = ?
              AND strftime('%Y', entry_date, '+5 hours') = ?
              AND strftime('%m', entry_date, '+5 hours') = ?
            ORDER BY entry_date ASC
            """,
            (owner_id, ystr, mstr)
        ).fetchall()


def get_monthly_finance_summary(owner_id: int, year: int, month: int):
    """Oylik xulosa: kirim/chiqim turkumlar bo'yicha."""
    ystr = f"{year:04d}"
    mstr = f"{month:02d}"
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT entry_type, category, SUM(amount) AS total, COUNT(*) AS cnt
            FROM finance_entries
            WHERE owner_id = ?
              AND strftime('%Y', entry_date, '+5 hours') = ?
              AND strftime('%m', entry_date, '+5 hours') = ?
            GROUP BY entry_type, category
            ORDER BY entry_type, total DESC
            """,
            (owner_id, ystr, mstr)
        ).fetchall()
    income_total = 0
    expense_total = 0
    by_cat = {"income": [], "expense": []}
    for r in rows:
        if r["entry_type"] == "income":
            income_total += r["total"]
        else:
            expense_total += r["total"]
        by_cat[r["entry_type"]].append(dict(r))
    return {
        "income_total": income_total,
        "expense_total": expense_total,
        "net": income_total - expense_total,
        "by_category": by_cat,
    }


def get_today_finance_summary(owner_id: int, date_str: str) -> dict:
    """Bugungi kun xulosasi (Toshkent vaqti, 'YYYY-MM-DD')."""
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT entry_type, category, SUM(amount) AS total, COUNT(*) AS cnt
            FROM finance_entries
            WHERE owner_id = ?
              AND date(entry_date, '+5 hours') = ?
            GROUP BY entry_type, category
            ORDER BY entry_type, total DESC
            """,
            (owner_id, date_str)
        ).fetchall()
    income_total = 0
    expense_total = 0
    expense_cnt = 0
    cnt = 0
    by_cat = {"income": [], "expense": []}
    for r in rows:
        cnt += r["cnt"]
        if r["entry_type"] == "income":
            income_total += r["total"]
        else:
            expense_total += r["total"]
            expense_cnt += r["cnt"]
        by_cat[r["entry_type"]].append(dict(r))
    return {
        "income_total": income_total,
        "expense_total": expense_total,
        "expense_cnt": expense_cnt,
        "cnt": cnt,
        "by_category": by_cat,
    }


# ===== Moliya turkumlari (kategoriya) tizimi =====

# Seed: (entry_type, ckey, emoji, name, protected, is_personal)
_FINANCE_CATEGORY_SEED = [
    # Chiqim (expense)
    ("expense", "food",      "🍽", "Ovqat",                 0, 0),
    ("expense", "transport", "🚌", "Yo'lkira",              0, 0),
    ("expense", "supply",    "📦", "Ta'minot",              0, 0),
    ("expense", "expense",   "💸", "Xarajat",               0, 0),
    ("expense", "advance",   "👤", "Hodimlar uchun Avans",  1, 0),
    ("expense", "salary",    "💼", "Ish haqqi",             0, 0),
    ("expense", "personal",  "🛍", "Shaxsiy xarajatlarim",  1, 0),
    ("expense", "other",     "📝", "Boshqa",                0, 0),
    # Shaxsiy ichki turkumlar (expense, is_personal=1, himoyalangan)
    ("expense", "p_transport", "🚌", "Shaxsiy: Yo'lkira",   1, 1),
    ("expense", "p_food",      "🍽", "Shaxsiy: Ovqat",      1, 1),
    ("expense", "p_rent",      "🏠", "Shaxsiy: Ijara",      1, 1),
    ("expense", "p_saving",    "💰", "Shaxsiy: Jamg'arma",  1, 1),
    ("expense", "p_debt",      "💳", "Shaxsiy: Qarz",       1, 1),
    ("expense", "p_other",     "📝", "Shaxsiy: Boshqa",     1, 1),
    # Kirim (income)
    ("income", "podachot", "📊", "Podachot",         0, 0),
    ("income", "sales",    "💵", "Sotuvdan tushum",  0, 0),
    ("income", "other",    "📝", "Boshqa",           0, 0),
]


_FINCAT_CREATE_SQL = """
    CREATE TABLE finance_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER,
        entry_type TEXT NOT NULL,
        ckey TEXT NOT NULL,
        emoji TEXT DEFAULT '🏷',
        name TEXT NOT NULL,
        protected INTEGER DEFAULT 0,
        is_personal INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT (datetime('now')),
        UNIQUE(owner_id, entry_type, ckey)
    )
"""


def _seed_owner_categories(conn, owner_id: int):
    for entry_type, ckey, emoji, name, protected, is_personal in _FINANCE_CATEGORY_SEED:
        conn.execute(
            "INSERT OR IGNORE INTO finance_categories "
            "(owner_id, entry_type, ckey, emoji, name, protected, is_personal) "
            "VALUES (?,?,?,?,?,?,?)",
            (owner_id, entry_type, ckey, emoji, name, protected, is_personal)
        )


def _finance_owner_ids(conn):
    return [r["id"] for r in conn.execute(
        "SELECT id FROM employees WHERE role IN ('boss','bosh_admin') AND is_active = 1"
    ).fetchall()]


def _migrate_fincat_per_owner(conn):
    """Eski global finance_categories -> owner_id li sxema.

    Eski (global) turkumlar bosh_admin'ga ko'chiriladi (custom'lar saqlanadi);
    bosslarga default to'plam keyin seed qilinadi.
    """
    old = conn.execute("SELECT * FROM finance_categories").fetchall()
    ba = conn.execute(
        "SELECT id FROM employees WHERE role='bosh_admin' AND is_active=1 ORDER BY id LIMIT 1"
    ).fetchone()
    ba_id = ba["id"] if ba else None
    conn.execute("ALTER TABLE finance_categories RENAME TO finance_categories_old")
    conn.execute(_FINCAT_CREATE_SQL)
    if ba_id:
        for r in old:
            conn.execute(
                "INSERT OR IGNORE INTO finance_categories "
                "(owner_id, entry_type, ckey, emoji, name, protected, is_personal, is_active) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (ba_id, r["entry_type"], r["ckey"], r["emoji"], r["name"],
                 r["protected"], r["is_personal"], r["is_active"])
            )
    conn.execute("DROP TABLE finance_categories_old")


def init_finance_categories():
    """finance_categories (owner_id li) — yaratish, migratsiya, har egaga default seed."""
    with get_db() as conn:
        exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='finance_categories'"
        ).fetchone()
        if exists:
            cols = [r[1] for r in conn.execute(
                "PRAGMA table_info(finance_categories)").fetchall()]
            if "owner_id" not in cols:
                _migrate_fincat_per_owner(conn)
        else:
            conn.execute(_FINCAT_CREATE_SQL)
        # Har bir moliya egasiga default turkumlar (idempotent)
        for oid in _finance_owner_ids(conn):
            _seed_owner_categories(conn, oid)


def ensure_owner_categories(owner_id: int):
    """Egada birorta turkum bo'lmasa — default to'plamni yaratadi (yangi boss uchun)."""
    with get_db() as conn:
        cnt = conn.execute(
            "SELECT COUNT(*) AS c FROM finance_categories WHERE owner_id = ?", (owner_id,)
        ).fetchone()["c"]
        if cnt == 0:
            _seed_owner_categories(conn, owner_id)


def get_finance_categories(entry_type: str, owner_id: int, active_only: bool = True):
    """Tanlov klaviaturasi uchun — egaga tegishli asosiy turkumlar."""
    q = ("SELECT * FROM finance_categories "
         "WHERE owner_id = ? AND entry_type = ? AND is_personal = 0")
    if active_only:
        q += " AND is_active = 1"
    q += " ORDER BY id"
    with get_db() as conn:
        return conn.execute(q, (owner_id, entry_type)).fetchall()


def get_finance_personal_categories(owner_id: int, active_only: bool = True):
    """Egaga tegishli shaxsiy xarajatlar ichki turkumlari."""
    q = "SELECT * FROM finance_categories WHERE owner_id = ? AND is_personal = 1"
    if active_only:
        q += " AND is_active = 1"
    q += " ORDER BY id"
    with get_db() as conn:
        return conn.execute(q, (owner_id,)).fetchall()


def get_all_finance_categories(owner_id: int, active_only: bool = True):
    """Boshqaruv menyusi uchun — egaga tegishli barcha turkumlar."""
    q = "SELECT * FROM finance_categories WHERE owner_id = ?"
    if active_only:
        q += " AND is_active = 1"
    q += " ORDER BY entry_type, id"
    with get_db() as conn:
        return conn.execute(q, (owner_id,)).fetchall()


def get_finance_category(cat_id: int):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM finance_categories WHERE id = ?", (cat_id,)
        ).fetchone()


def finance_category_label(ckey: str):
    """Turkum kaliti bo'yicha (emoji, nom). O'chirilgan (faolsiz) turkumlar ham
    topiladi, shunda eski yozuvlar nomini yo'qotmaydi. Topilmasa — None."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT emoji, name FROM finance_categories WHERE ckey = ? "
            "ORDER BY is_active DESC LIMIT 1",
            (ckey,)
        ).fetchone()
    return (row["emoji"], row["name"]) if row else None


def create_finance_category(entry_type: str, emoji: str, name: str, owner_id: int) -> int:
    """Egaga yangi turkum qo'shish. Barqaror ckey = 'c{id}' beriladi."""
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO finance_categories (owner_id, entry_type, ckey, emoji, name) "
            "VALUES (?, ?, '', ?, ?)",
            (owner_id, entry_type, emoji, name)
        )
        cid = cur.lastrowid
        conn.execute(
            "UPDATE finance_categories SET ckey = ? WHERE id = ?",
            (f"c{cid}", cid)
        )
        return cid


def delete_finance_category(cat_id: int, owner_id: int) -> bool:
    """Yumshoq o'chirish (is_active=0). Faqat egasining himoyalanmagan turkumi. Tarix saqlanadi."""
    with get_db() as conn:
        cur = conn.execute(
            "UPDATE finance_categories SET is_active = 0 "
            "WHERE id = ? AND owner_id = ? AND protected = 0 AND is_active = 1",
            (cat_id, owner_id)
        )
        return cur.rowcount > 0


# ===== Shaxsiy moliya (PF) turkumlari tizimi =====
# finance_categories bilan bir xil naqsh: har egaga alohida, ckey barqaror,
# custom turkumlar ckey='c{id}', yumshoq o'chirish.

# Seed: (entry_type, ckey, emoji, name) — texts.PF_*_CATS lug'atlari asosida.
# Hech bir PF kalitiga kod mantig'i bog'lanmagan — hammasi himoyalanmagan.
_PF_CATEGORY_SEED = [
    # Chiqim (expense)
    ("expense", "subscription",  "📱", "Oylik obuna"),
    ("expense", "transport",     "🚗", "Yo'lkira"),
    ("expense", "food",          "🍽", "Ovqat"),
    ("expense", "entertainment", "🎮", "Ko'ngil ochar"),
    ("expense", "debt_pay",      "💸", "Qarz to'lash"),
    ("expense", "charity",       "🤲", "Ehson va hadiya"),
    ("expense", "clothing",      "👕", "Kiyim-kechak"),
    ("expense", "shopping",      "🛒", "Xarid"),
    ("expense", "pf_other",      "📋", "Boshqa"),
    # Kirim (income)
    ("income", "salary",       "💵", "Ish haqqi"),
    ("income", "daily_income", "📈", "Kunlik daromad"),
    ("income", "loan_in",      "🤝", "Qarz olish"),
    ("income", "pf_inc_other", "📋", "Boshqa"),
]

_PFCAT_CREATE_SQL = """
    CREATE TABLE IF NOT EXISTS pf_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER NOT NULL,
        entry_type TEXT NOT NULL,
        ckey TEXT NOT NULL,
        emoji TEXT DEFAULT '🏷',
        name TEXT NOT NULL,
        protected INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT (datetime('now')),
        UNIQUE(owner_id, entry_type, ckey)
    )
"""


def _seed_owner_pf_categories(conn, owner_id: int):
    for entry_type, ckey, emoji, name in _PF_CATEGORY_SEED:
        conn.execute(
            "INSERT OR IGNORE INTO pf_categories "
            "(owner_id, entry_type, ckey, emoji, name) "
            "VALUES (?,?,?,?,?)",
            (owner_id, entry_type, ckey, emoji, name)
        )


def init_pf_categories():
    """pf_categories — yaratish va har egaga default seed (idempotent)."""
    with get_db() as conn:
        conn.execute(_PFCAT_CREATE_SQL)
        for oid in _finance_owner_ids(conn):
            _seed_owner_pf_categories(conn, oid)


def ensure_owner_pf_categories(owner_id: int):
    """Egada birorta PF turkumi bo'lmasa — default to'plamni yaratadi."""
    with get_db() as conn:
        cnt = conn.execute(
            "SELECT COUNT(*) AS c FROM pf_categories WHERE owner_id = ?", (owner_id,)
        ).fetchone()["c"]
        if cnt == 0:
            _seed_owner_pf_categories(conn, owner_id)


def get_pf_categories(entry_type: str, owner_id: int, active_only: bool = True):
    """Tanlov klaviaturasi uchun — egaga tegishli PF turkumlari."""
    q = "SELECT * FROM pf_categories WHERE owner_id = ? AND entry_type = ?"
    if active_only:
        q += " AND is_active = 1"
    q += " ORDER BY id"
    with get_db() as conn:
        return conn.execute(q, (owner_id, entry_type)).fetchall()


def get_all_pf_categories(owner_id: int, active_only: bool = True):
    """Boshqaruv menyusi uchun — egaga tegishli barcha PF turkumlari."""
    q = "SELECT * FROM pf_categories WHERE owner_id = ?"
    if active_only:
        q += " AND is_active = 1"
    q += " ORDER BY entry_type, id"
    with get_db() as conn:
        return conn.execute(q, (owner_id,)).fetchall()


def get_pf_category(cat_id: int):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM pf_categories WHERE id = ?", (cat_id,)
        ).fetchone()


def get_pf_category_by_ckey(owner_id: int, entry_type: str, ckey: str):
    """Tanlovni tekshirish uchun — faqat egaga tegishli AKTIV turkum."""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM pf_categories "
            "WHERE owner_id = ? AND entry_type = ? AND ckey = ? AND is_active = 1",
            (owner_id, entry_type, ckey)
        ).fetchone()


def pf_category_label(ckey: str):
    """PF turkum kaliti bo'yicha (emoji, nom). Faolsizlar ham topiladi —
    eski yozuvlar nomini yo'qotmaydi. Topilmasa — None."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT emoji, name FROM pf_categories WHERE ckey = ? "
            "ORDER BY is_active DESC LIMIT 1",
            (ckey,)
        ).fetchone()
    return (row["emoji"], row["name"]) if row else None


def create_pf_category(entry_type: str, emoji: str, name: str, owner_id: int) -> int:
    """Egaga yangi PF turkumi. Barqaror ckey = 'c{id}' beriladi."""
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO pf_categories (owner_id, entry_type, ckey, emoji, name) "
            "VALUES (?, ?, '', ?, ?)",
            (owner_id, entry_type, emoji, name)
        )
        cid = cur.lastrowid
        conn.execute(
            "UPDATE pf_categories SET ckey = ? WHERE id = ?",
            (f"c{cid}", cid)
        )
        return cid


def delete_pf_category(cat_id: int, owner_id: int) -> bool:
    """Yumshoq o'chirish (is_active=0). Faqat egasining turkumi. Tarix saqlanadi."""
    with get_db() as conn:
        cur = conn.execute(
            "UPDATE pf_categories SET is_active = 0 "
            "WHERE id = ? AND owner_id = ? AND protected = 0 AND is_active = 1",
            (cat_id, owner_id)
        )
        return cur.rowcount > 0


# ===== Lavozimlar tizimi =====

def init_positions():
    """Positions jadvalini yaratish va default lavozimlarni seed qilish."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                work_hours REAL NOT NULL DEFAULT 9,
                min_rate INTEGER NOT NULL DEFAULT 0,
                max_rate INTEGER NOT NULL DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT (datetime('now'))
            )
        """)
        # Migratsiya: employees ga position_id va daily_rate
        cursor = conn.execute("PRAGMA table_info(employees)")
        cols = [r[1] for r in cursor.fetchall()]
        if "position_id" not in cols:
            conn.execute("ALTER TABLE employees ADD COLUMN position_id INTEGER REFERENCES positions(id)")
        if "daily_rate" not in cols:
            conn.execute("ALTER TABLE employees ADD COLUMN daily_rate INTEGER DEFAULT 0")

        # Seed: 3 ta asosiy lavozim
        defaults = [
            ("Upakovkachilar",  9, 120000, 150000),
            ("Grafik dizayner", 9, 150000, 200000),
            ("Ombor xodimi",   9.5, 150000, 200000),
        ]
        for name, wh, mn, mx in defaults:
            conn.execute(
                "INSERT OR IGNORE INTO positions (name, work_hours, min_rate, max_rate) VALUES (?,?,?,?)",
                (name, wh, mn, mx)
            )
        conn.execute("UPDATE positions SET work_hours=9.5 WHERE name='Ombor xodimi'")


def get_all_positions(active_only=True):
    with get_db() as conn:
        if active_only:
            return conn.execute(
                "SELECT * FROM positions WHERE is_active=1 ORDER BY name"
            ).fetchall()
        return conn.execute("SELECT * FROM positions ORDER BY name").fetchall()


def get_position(pos_id: int):
    with get_db() as conn:
        return conn.execute("SELECT * FROM positions WHERE id=?", (pos_id,)).fetchone()


def get_employees_by_position_id(position_id: int):
    """Muayyan lavozimga biriktirilgan barcha faol xodimlar."""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM employees WHERE position_id = ? AND is_active = 1 ORDER BY full_name",
            (position_id,)
        ).fetchall()


def create_position(name: str, work_hours: int, min_rate: int, max_rate: int) -> int:
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO positions (name, work_hours, min_rate, max_rate) VALUES (?,?,?,?)",
            (name, work_hours, min_rate, max_rate)
        )
        return cur.lastrowid


def update_position(pos_id: int, name: str = None, work_hours: int = None,
                    min_rate: int = None, max_rate: int = None):
    sets, params = [], []
    if name is not None:       sets.append("name=?");       params.append(name)
    if work_hours is not None: sets.append("work_hours=?"); params.append(work_hours)
    if min_rate is not None:   sets.append("min_rate=?");   params.append(min_rate)
    if max_rate is not None:   sets.append("max_rate=?");   params.append(max_rate)
    if not sets:
        return
    params.append(pos_id)
    with get_db() as conn:
        conn.execute(f"UPDATE positions SET {','.join(sets)} WHERE id=?", params)


def delete_position(pos_id: int):
    """Lavozimni o'chirish (faqat bog'langan xodim yo'q bo'lsa)."""
    with get_db() as conn:
        conn.execute("DELETE FROM positions WHERE id=?", (pos_id,))


def set_employee_position(employee_id: int, position_id: int, daily_rate: int):
    """Xodimga lavozim va kunlik stavka belgilash."""
    with get_db() as conn:
        conn.execute(
            "UPDATE employees SET position_id=?, daily_rate=? WHERE id=?",
            (position_id, daily_rate, employee_id)
        )


def set_employee_daily_rate(employee_id: int, daily_rate: int):
    """Faqat kunlik stavkani yangilash — lavozim o'zgarmaydi."""
    with get_db() as conn:
        conn.execute(
            "UPDATE employees SET daily_rate = ? WHERE id = ?",
            (daily_rate, employee_id)
        )


# ===== Smena normasi tarixi (vaqt bo'yicha amal qiluvchi) =====

def init_shift_norms() -> None:
    """Smena normasi tarixi jadvalini yaratish (idempotent)."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS shift_norms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scope TEXT NOT NULL,                -- 'employee' yoki 'position'
                target_id INTEGER NOT NULL,         -- employee_id yoki position_id
                effective_from TEXT NOT NULL,       -- 'YYYY-MM' (shu oydan boshlab amal qiladi)
                norm_minutes INTEGER NOT NULL,      -- yangi smena normasi (daqiqada)
                reason TEXT,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT (datetime('now')),
                UNIQUE(scope, target_id, effective_from)
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_shift_norms_lookup
                ON shift_norms(scope, target_id, effective_from)
        """)


def set_shift_norm(scope: str, target_id: int, effective_from: str, norm_minutes: int,
                    reason: str = None, created_by: int = None) -> None:
    """Smena normasini belgilash/yangilash (bir oyga bitta yozuv — UPSERT)."""
    with get_db() as conn:
        conn.execute("""
            INSERT INTO shift_norms (scope, target_id, effective_from, norm_minutes, reason, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(scope, target_id, effective_from) DO UPDATE SET
                norm_minutes = excluded.norm_minutes,
                reason = excluded.reason,
                created_by = excluded.created_by,
                created_at = datetime('now')
        """, (scope, target_id, effective_from, norm_minutes, reason, created_by))


def get_scope_shift_norm(scope: str, target_id: int, year: int, month: int):
    """Faqat shu scope darajasida (kaskadsiz) amaldagi normani (daqiqada) qaytaradi, topilmasa None."""
    ym = f"{year:04d}-{month:02d}"
    with get_db() as conn:
        row = conn.execute("""
            SELECT norm_minutes FROM shift_norms
            WHERE scope=? AND target_id=? AND effective_from<=?
            ORDER BY effective_from DESC LIMIT 1
        """, (scope, target_id, ym)).fetchone()
        return row["norm_minutes"] if row else None


def get_effective_shift_norm(employee_id: int, year: int, month: int) -> int:
    """Muayyan oy uchun amaldagi smena normasini (daqiqada) qaytaradi.

    Ustuvorlik: xodim darajasidagi norma -> lavozim darajasidagi norma -> positions.work_hours.
    """
    emp = get_employee_by_id(employee_id)
    if not emp:
        return 9 * 60

    minutes = get_scope_shift_norm("employee", employee_id, year, month)
    if minutes is not None:
        return minutes

    position_id = emp["position_id"] if "position_id" in emp.keys() else None
    if position_id:
        minutes = get_scope_shift_norm("position", position_id, year, month)
        if minutes is not None:
            return minutes

    pos = get_position(position_id) if position_id else None
    return int((pos["work_hours"] if pos else 9) * 60)


def get_effective_shift_hours(employee_id: int, year: int, month: int) -> str:
    """Amaldagi normani ko'rsatish uchun soatda qaytaradi ('9.5' yoki '10')."""
    hours = get_effective_shift_norm(employee_id, year, month) / 60
    return str(int(hours)) if hours == int(hours) else f"{hours:.1f}"


def delete_shift_norm(norm_id: int) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM shift_norms WHERE id=?", (norm_id,))


def get_shift_norm_history(scope: str, target_id: int) -> list:
    """Berilgan xodim/lavozim uchun norma tarixi (eng yangisi birinchi)."""
    with get_db() as conn:
        return conn.execute("""
            SELECT * FROM shift_norms WHERE scope=? AND target_id=?
            ORDER BY effective_from DESC
        """, (scope, target_id)).fetchall()


def get_monthly_holiday_pay(employee_id: int, year: int, month: int) -> int:
    """Oydagi BAYRAM kunlari uchun qo'shiladigan to'liq stavka summasi.

    Qoida (2026-08-31 da kelishilgan): bayram kuni hamma xodimga bir kunlik
    to'liq stavka yoziladi; agar xodim o'sha kuni ishga kelgan bo'lsa,
    ishlagan vaqti ham odatdagidek ustiga qo'shiladi.

    Istisnolar:
      - kunlik stavkasi yo'q (eski soatbay) xodimga qo'llanmaydi;
      - faolsiz (o'chirilgan) xodimga avtomatik yozilmaydi;
      - xodim ro'yxatdan o'tgan kundan OLDINGI bayramlar hisoblanmaydi.
    """
    emp = get_employee_by_id(employee_id)
    if not emp:
        return 0
    daily_rate = emp["daily_rate"] if "daily_rate" in emp.keys() else 0
    position_id = emp["position_id"] if "position_id" in emp.keys() else None
    if not daily_rate or not position_id:
        return 0
    is_active = bool(emp["is_active"]) if "is_active" in emp.keys() else True
    if not is_active:
        return 0

    days = get_calendar_days_by_type(year, month, HOLIDAY)
    if not days:
        return 0

    reg = emp["registered_at"] if "registered_at" in emp.keys() else None
    if reg:
        try:
            start = (datetime.fromisoformat(str(reg)) + timedelta(hours=5)).strftime("%Y-%m-%d")
            days = [d for d in days if d >= start]
        except (ValueError, TypeError):
            pass
    return len(days) * int(daily_rate)


def get_monthly_base_salary(employee_id: int, year: int, month: int) -> int:
    """Kunlik stavka asosida oylik asosiy ish haqqi hisoblash.

    Har ish kuni uchun: min(ishlangan_daqiqa, smena_daqiqa) / smena_daqiqa * kunlik_stavka
    Agar position/daily_rate yo'q bo'lsa — hourly_rate bilan fallback.
    """
    emp = get_employee_by_id(employee_id)
    if not emp:
        return 0

    daily_rate = emp["daily_rate"] if "daily_rate" in emp.keys() else 0
    position_id = emp["position_id"] if "position_id" in emp.keys() else None

    # Fallback: eski hourly_rate tizimi
    if not daily_rate or not position_id:
        rate = emp["hourly_rate"] if "hourly_rate" in emp.keys() else 0
        if not rate:
            return 0
        minutes = get_monthly_worked_minutes(employee_id, year, month)
        return int((minutes / 60.0) * rate)

    pos = get_position(position_id)
    standard_minutes = get_effective_shift_norm(employee_id, year, month)
    if standard_minutes <= 0:
        standard_minutes = int((pos["work_hours"] if pos else 9) * 60)

    rows = get_monthly_attendance(employee_id, year, month)
    total = 0
    for row in rows:
        if not row["first_in"] or not row["last_out"]:
            continue
        try:
            ih, im, _ = map(int, row["first_in"].split(":"))
            oh, om, _ = map(int, row["last_out"].split(":"))
            worked = (oh * 60 + om) - (ih * 60 + im)
            if worked <= 0:
                continue
            capped = min(worked, 12 * 60)
            total += int(capped / standard_minutes * daily_rate)
        except Exception:
            continue

    # Bayram kunlari uchun to'liq stavka (kelmagan bo'lsa ham)
    total += get_monthly_holiday_pay(employee_id, year, month)
    return total


# ===== Xabarnoma (Broadcast) =====

def create_broadcast(sender_emp_id: int, target_type: str,
                     target_id: Optional[int], content_type: str) -> int:
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO broadcasts (sender_emp_id, target_type, target_id, content_type) "
            "VALUES (?, ?, ?, ?)",
            (sender_emp_id, target_type, target_id, content_type)
        )
        return cur.lastrowid


def save_broadcast_reaction(broadcast_id: int, employee_id: int, reaction: str):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO broadcast_reactions (broadcast_id, employee_id, reaction)
               VALUES (?, ?, ?)
               ON CONFLICT(broadcast_id, employee_id)
               DO UPDATE SET reaction = excluded.reaction,
                             reacted_at = datetime('now')""",
            (broadcast_id, employee_id, reaction)
        )


def get_broadcast_sender(broadcast_id: int):
    with get_db() as conn:
        return conn.execute(
            """SELECT b.sender_emp_id, e.telegram_id AS tg_id, e.full_name
               FROM broadcasts b
               JOIN employees e ON e.id = b.sender_emp_id
               WHERE b.id = ?""",
            (broadcast_id,)
        ).fetchone()


def save_broadcast_comment(broadcast_id: int, employee_id: int, comment: str) -> int:
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO broadcast_comments (broadcast_id, employee_id, comment) "
            "VALUES (?, ?, ?)",
            (broadcast_id, employee_id, comment)
        )
        return cur.lastrowid


# ===== Shaxsiy moliya (Personal Finance) =====

def pf_add_entry(employee_id: int, entry_type: str, category: str,
                 amount: int, note: str, entry_date: str) -> int:
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO personal_finance "
            "(employee_id, entry_type, category, amount, note, entry_date) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (employee_id, entry_type, category, amount, note or "", entry_date)
        )
        return cur.lastrowid


def pf_get_monthly(employee_id: int, year: int, month: int):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM personal_finance "
            "WHERE employee_id = ? "
            "  AND strftime('%Y', entry_date) = ? "
            "  AND strftime('%m', entry_date) = ? "
            "ORDER BY entry_date DESC, id DESC",
            (employee_id, str(year), f"{month:02d}")
        ).fetchall()


def pf_get_summary(employee_id: int, year: int, month: int) -> dict:
    """Oylik kirim/chiqim jami va kategoriya bo'yicha."""
    rows = pf_get_monthly(employee_id, year, month)
    income_total = sum(r["amount"] for r in rows if r["entry_type"] == "income")
    expense_total = sum(r["amount"] for r in rows if r["entry_type"] == "expense")
    by_cat: dict = {}
    for r in rows:
        key = (r["entry_type"], r["category"])
        by_cat[key] = by_cat.get(key, 0) + r["amount"]
    return {
        "income": income_total,
        "expense": expense_total,
        "net": income_total - expense_total,
        "by_cat": by_cat,
    }


def pf_get_today_totals(employee_id: int, date_str: str) -> dict:
    """Bugungi kirim/chiqim jami (entry_date lokal 'YYYY-MM-DD' string)."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT entry_type, SUM(amount) AS total, COUNT(*) AS cnt "
            "FROM personal_finance "
            "WHERE employee_id = ? AND entry_date = ? "
            "GROUP BY entry_type",
            (employee_id, date_str)
        ).fetchall()
    result = {"income": 0, "expense": 0, "cnt": 0}
    for r in rows:
        result[r["entry_type"]] = r["total"]
        result["cnt"] += r["cnt"]
    return result


def pf_get_entry(entry_id: int, employee_id: int):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM personal_finance WHERE id = ? AND employee_id = ?",
            (entry_id, employee_id)
        ).fetchone()


def pf_delete_entry(entry_id: int, employee_id: int):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM personal_finance WHERE id = ? AND employee_id = ?",
            (entry_id, employee_id)
        )


def pf_balance_before(employee_id: int, year: int, month: int) -> int:
    """Berilgan oy boshigacha yig'ilgan shaxsiy qoldiq (kirim − chiqim).

    personal_finance.entry_date 'YYYY-MM-DD' satr sifatida saqlanadi — ISO format
    bo'lgani uchun matn taqqoslash to'g'ri ishlaydi.
    """
    first = f"{year:04d}-{month:02d}-01"
    with get_db() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(CASE WHEN entry_type='income' THEN amount "
            "ELSE -amount END), 0) AS b "
            "FROM personal_finance WHERE employee_id = ? AND entry_date < ?",
            (employee_id, first)
        ).fetchone()
        return row["b"] or 0


def pf_get_by_date(employee_id: int, date_str: str):
    """Berilgan kun ('YYYY-MM-DD') bo'yicha shaxsiy yozuvlar (eskisidan yangisiga)."""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM personal_finance "
            "WHERE employee_id = ? AND entry_date = ? ORDER BY id",
            (employee_id, date_str)
        ).fetchall()
