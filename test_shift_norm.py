"""Smena normasi (ish vaqti) o'zgarishini tekshirish — vaqtinchalik bazada, jonli baza tegilmaydi.

Ishga tushirish: ./venv/bin/python test_shift_norm.py
"""
import os
import tempfile

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "shift_norm_test.db")

import database as db  # noqa: E402  (DB_PATH dan keyin import qilinishi shart)


def _add_day(emp_id: int, year: int, month: int, day: int, hours: float):
    """Mahalliy 08:00 dan boshlab `hours` soat ishlagan kun (bazada UTC saqlanadi)."""
    out_h = 3 + int(hours)
    out_m = int(round((hours % 1) * 60))
    with db.get_db() as conn:
        conn.execute("INSERT INTO attendance (employee_id, check_type, timestamp) VALUES (?,'in',?)",
                     (emp_id, f"{year:04d}-{month:02d}-{day:02d} 03:00:00"))
        conn.execute("INSERT INTO attendance (employee_id, check_type, timestamp) VALUES (?,'out',?)",
                     (emp_id, f"{year:04d}-{month:02d}-{day:02d} {out_h:02d}:{out_m:02d}:00"))


def main():
    db.init_db()
    db.init_db()  # idempotentlik: ikkinchi marta ham xato bermasin

    # Norma 10 soat, kunlik stavka 230 000 so'm
    pos_id = db.create_position("TestNorma", 10, 100000, 300000)
    with db.get_db() as conn:
        for tg, name in ((9001, "Test A"), (9002, "Test B")):
            conn.execute(
                """INSERT INTO employees (telegram_id, full_name, phone, position, face_encoding,
                   role, is_admin, is_active, position_id, daily_rate)
                   VALUES (?,?,?,?,x'00','employee',0,1,?,230000)""",
                (tg, name, f"+9989{tg}", "TestNorma", pos_id)
            )
    emp_a, emp_b = 1, 2

    # Ikkala xodim ham iyun/iyul/avgustda 2 kun, 9.5 soat ishlagan (normadan 0.5 soat kam)
    for emp_id in (emp_a, emp_b):
        for month in (6, 7, 8):
            for day in (5, 10):
                _add_day(emp_id, 2026, month, day, 9.5)

    partial = db.get_monthly_base_salary(emp_a, 2026, 7)   # 10 soat normada — kam to'lanadi
    full = 2 * 230000                                       # 9.5 soat normada — to'liq
    assert partial < full, f"boshlang'ich holat kutilganidek emas: {partial}"

    # Xodim darajasida: 2026-07 dan norma 10 -> 9.5 soat
    db.set_shift_norm("employee", emp_a, "2026-07", 570, reason="test", created_by=None)

    assert db.get_monthly_base_salary(emp_a, 2026, 6) == partial, "amal oyidan oldingi oy o'zgarmasligi kerak"
    assert db.get_monthly_base_salary(emp_a, 2026, 7) == full, "amal oyida to'liq haq to'lanishi kerak"
    assert db.get_monthly_base_salary(emp_a, 2026, 8) == full, "keyingi oylarga ham amal qilishi kerak"
    assert db.get_monthly_base_salary(emp_b, 2026, 7) == partial, "boshqa xodim o'zgarmasligi kerak"
    print("✅ 1) Xodim darajasidagi norma: oldingi oy o'zgarmadi, amal oyi va keyingisi to'liq")

    # Lavozim darajasida: shaxsiy normasi yo'q xodim lavozim normasini olsin
    db.set_shift_norm("position", pos_id, "2026-07", 570, reason="test pos", created_by=None)
    assert db.get_monthly_base_salary(emp_b, 2026, 7) == full, "lavozim normasi qo'llanishi kerak"
    assert db.get_monthly_base_salary(emp_b, 2026, 6) == partial, "lavozim normasi oldingi oyga tegmasin"
    print("✅ 2) Lavozim darajasidagi norma qo'llandi")

    # Ustuvorlik: xodimning shaxsiy normasi lavozim normasidan ustun
    db.set_shift_norm("position", pos_id, "2026-07", 480, reason="8 soat", created_by=None)
    assert db.get_effective_shift_norm(emp_a, 2026, 7) == 570, "shaxsiy norma ustun bo'lishi kerak"
    assert db.get_effective_shift_norm(emp_b, 2026, 7) == 480, "shaxsiy normasi yo'q — lavozimdan olsin"
    print("✅ 3) Ustuvorlik: xodim normasi > lavozim normasi > positions.work_hours")

    # UPSERT: bir oyga ikkinchi marta yozilsa yangilanadi, dublikat yaratmaydi
    db.set_shift_norm("employee", emp_a, "2026-07", 540, reason="qayta", created_by=None)
    history = db.get_shift_norm_history("employee", emp_a)
    assert len(history) == 1, f"dublikat yozuv paydo bo'ldi: {len(history)}"
    assert history[0]["norm_minutes"] == 540, "UPSERT qiymatni yangilamadi"
    print("✅ 4) UPSERT: bir oyga bitta yozuv, qiymat yangilanadi")

    # Ko'rsatish uchun soat formati ('9.5' / '10' — ".0" chiqmasin)
    assert db.get_effective_shift_hours(emp_a, 2026, 7) == "9", "540 daqiqa '9' bo'lishi kerak"
    assert db.get_effective_shift_hours(emp_b, 2026, 7) == "8", "480 daqiqa '8' bo'lishi kerak"
    db.set_shift_norm("employee", emp_a, "2026-07", 570, reason="9.5", created_by=None)
    assert db.get_effective_shift_hours(emp_a, 2026, 7) == "9.5", "570 daqiqa '9.5' bo'lishi kerak"
    print("✅ 5) Ko'rsatish formati: 540->'9', 570->'9.5'")

    # Norma yo'q xodim uchun positions.work_hours default bo'lib qolishi kerak
    for row in db.get_shift_norm_history("employee", emp_a):
        db.delete_shift_norm(row["id"])
    assert db.get_effective_shift_norm(emp_a, 2026, 6) == 10 * 60, "default positions.work_hours bo'lishi kerak"
    print("✅ 6) O'chirilgach positions.work_hours defaultga qaytadi")

    print("\n✅✅ HAMMASI O'TDI — jonli attendance.db tegilmadi")


if __name__ == "__main__":
    main()
