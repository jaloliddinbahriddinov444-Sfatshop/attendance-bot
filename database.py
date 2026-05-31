"""SQLite ma'lumotlar bazasi - barcha funksiyalar"""
import sqlite3
from contextlib import contextmanager
from typing import Optional
from config import DB_PATH, DEFAULT_OFFICE_LAT, DEFAULT_OFFICE_LON, \
    DEFAULT_OFFICE_RADIUS_M, DEFAULT_WORK_START, DEFAULT_WORK_END, \
    DEFAULT_OFFICE_WIFI, INITIAL_ADMIN_ID


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
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


def get_all_employees(active_only=True):
    with get_db() as conn:
        if active_only:
            return conn.execute(
                "SELECT * FROM employees WHERE is_active = 1 ORDER BY full_name"
            ).fetchall()
        return conn.execute("SELECT * FROM employees ORDER BY full_name").fetchall()


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


def get_employees_by_role(role: str):
    """Berilgan roldagi barcha faol xodimlar."""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM employees WHERE role = ? AND is_active = 1 "
            "ORDER BY full_name",
            (role,)
        ).fetchall()


# ===== Davomat =====

def get_today_attendance(employee_id: int):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM attendance WHERE employee_id = ? "
            "AND date(timestamp, '+5 hours') = date('now', '+5 hours') "
            "ORDER BY timestamp",
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
            WHERE e.is_active = 1
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

def delete_today_attendance(employee_id: int) -> int:
    """Bugungi davomat yozuvlarini o'chirish"""
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM attendance WHERE employee_id = ? "
            "AND date(timestamp, '+5 hours') = date('now', '+5 hours')",
            (employee_id,)
        )
        return cursor.rowcount


def add_manual_attendance(employee_id: int, check_type: str, time_str: str):
    """Admin tomonidan qo'lda davomat qo'shish (bugungi sana, berilgan vaqt)"""
    from tzutil import now as tz_now, OFFSET
    h, m = map(int, time_str.split(":"))
    # Admin mahalliy (Toshkent) vaqt kiritadi -> bazaga UTC saqlaymiz
    ts_local = tz_now().replace(hour=h, minute=m, second=0, microsecond=0)
    ts = ts_local - OFFSET
    with get_db() as conn:
        conn.execute(
            "INSERT INTO attendance (employee_id, check_type, timestamp, "
            "wifi_name, wifi_match, face_match_score) "
            "VALUES (?, ?, ?, ?, 1, 1.0)",
            (employee_id, check_type, ts.isoformat(), "Admin qo'shdi")
        )


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
              AND strftime('%Y', created_at, '+5 hours') = ?
              AND strftime('%m', created_at, '+5 hours') = ?
              AND cancelled = 0
            GROUP BY entry_type
            """,
            (employee_id, str(year), f"{month:02d}")
        ).fetchall()
    totals = {"avans": 0, "jarima": 0, "mukofot": 0, "bonus": 0, "mahsulot": 0}
    for row in rows:
        if row["entry_type"] in totals:
            totals[row["entry_type"]] = row["total"]
    return totals


def add_salary_entry(employee_id: int, entry_type: str, amount: int, reason: str, created_by: int) -> int:
    """Yangi ish haqqi yozuvini qo'shish. ID qaytaradi."""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO salary_entries (employee_id, entry_type, amount, reason, created_by) "
            "VALUES (?, ?, ?, ?, ?)",
            (employee_id, entry_type, amount, reason, created_by)
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
    """Joriy oyning faol (bekor qilinmagan) yozuvlari"""
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM salary_entries WHERE employee_id = ? "
            "AND strftime('%Y', created_at, '+5 hours') = ? AND strftime('%m', created_at, '+5 hours') = ? "
            "AND cancelled = 0 ORDER BY created_at DESC",
            (employee_id, str(year), f"{month:02d}")
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
    """Bu oy uchun barcha xodimlarning xulosasi (Excel uchun)"""
    employees = get_all_employees(active_only=True)
    result = []
    for emp in employees:
        rate = emp["hourly_rate"] if "hourly_rate" in emp.keys() and emp["hourly_rate"] else 0
        minutes = get_monthly_worked_minutes(emp["id"], year, month)
        base = int((minutes / 60.0) * rate) if rate else 0
        totals = get_salary_totals_by_type(emp["id"], year, month)
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
