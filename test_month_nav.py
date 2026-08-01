"""Oy navigatsiyasi (◀️ ▶️) testi — vaqtinchalik bazada, jonli baza tegilmaydi.

Ishga tushirish: ./venv/bin/python test_month_nav.py
"""
import os
import tempfile

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "month_nav_test.db")

import tzutil as tz  # noqa: E402
import keyboards as kb  # noqa: E402


def main():
    # ─ Oy arifmetikasi ─
    assert tz.prev_month(2026, 1) == (2025, 12)
    assert tz.prev_month(2026, 8) == (2026, 7)
    assert tz.next_month(2026, 12) == (2027, 1)
    assert tz.next_month(2026, 7) == (2026, 8)
    assert tz.months_back(2026, 8, 6) == (2026, 2)
    assert tz.months_back(2026, 3, 6) == (2025, 9)
    assert tz.months_back(2026, 8, 0) == (2026, 8)

    # ─ nav_ym: parse + chegara ─
    d = tz.now()
    y, m = d.year, d.month
    assert tz.nav_ym(f"x:{y}:{m}") == (y, m)
    py, pm = tz.prev_month(y, m)
    assert tz.nav_ym(f"x:{py}:{pm}") == (py, pm)
    oy6 = tz.months_back(y, m, 6)
    assert tz.nav_ym(f"x:{oy6[0]}:{oy6[1]}") == oy6  # chegaraning o'zi ruxsat
    # Kelajak, juda eski va buzuq callbacklar → joriy oy
    ny, nm = tz.next_month(y, m)
    assert tz.nav_ym(f"x:{ny}:{nm}") == (y, m)
    oy7 = tz.months_back(y, m, 7)
    assert tz.nav_ym(f"x:{oy7[0]}:{oy7[1]}") == (y, m)
    assert tz.nav_ym("buzuq") == (y, m)
    assert tz.nav_ym("x:abc:def") == (y, m)
    assert tz.nav_ym(f"x:{y}:13") == (y, m)

    # ─ month_nav_kb: tugma chegaralari ─
    def flat(markup):
        return [b for row in markup.inline_keyboard for b in row]

    # Joriy oy: faqat ◀️ (kelajak tugmasi yo'q)
    btns = flat(kb.month_nav_kb("t", y, m))
    assert len(btns) == 1 and btns[0].callback_data == f"t:{py}:{pm}"
    assert btns[0].text.startswith("◀️")
    # Eng eski ruxsat etilgan oy: faqat ▶️
    btns = flat(kb.month_nav_kb("t", *oy6))
    nxt = tz.next_month(*oy6)
    assert len(btns) == 1 and btns[0].callback_data == f"t:{nxt[0]}:{nxt[1]}"
    assert btns[0].text.endswith("▶️")
    # O'rtadagi oy: ikkala tugma
    mid = tz.months_back(y, m, 3)
    assert len(flat(kb.month_nav_kb("t", *mid))) == 2

    # ─ month_excel_kb: yuklab olish tugmasi + nav ─
    btns = flat(kb.month_excel_kb("finxl", y, m))
    assert btns[0].callback_data == f"finxldl:{y}:{m}"

    # ─ month_close_pick_kb: holat belgilari ─
    months = [(2026, 8, False), (2026, 7, True), (2026, 6, False)]
    btns = flat(kb.month_close_pick_kb(months))
    assert btns[0].callback_data == "mclose:2026:8" and "🔒" not in btns[0].text
    assert btns[1].callback_data == "mclose:2026:7" and btns[1].text.startswith("🔒")

    # ─ salary_month_pick_kb: prefiks va bekor tugmasi ─
    btns = flat(kb.salary_month_pick_kb("sal_month", months))
    assert btns[0].callback_data == "sal_month:2026:8"
    assert btns[-1].callback_data == "sal_month:cancel"

    # ─ for_ym: yozuv tanlangan oyga tushishi ─
    import database as db
    db.init_db()
    with db.get_db() as conn:
        conn.execute(
            "INSERT INTO employees (telegram_id, full_name, phone, position, face_encoding) "
            "VALUES (1001, 'Test Xodim', '+998', 'X', x'00')"
        )
        emp_id = conn.execute(
            "SELECT id FROM employees WHERE telegram_id=1001"
        ).fetchone()["id"]

    py, pm = tz.prev_month(y, m)
    db.add_salary_entry(emp_id, "bonus", 50000, "o'tgan oy bonusi", 0,
                        for_ym=f"{py:04d}-{pm:02d}")
    db.add_salary_entry(emp_id, "jarima", 20000, "joriy jarima", 0)  # for_ym yo'q

    prev_tot = db.get_salary_totals_by_type(emp_id, py, pm)
    cur_tot = db.get_salary_totals_by_type(emp_id, y, m)
    assert prev_tot["bonus"] == 50000 and prev_tot["jarima"] == 0
    assert cur_tot["jarima"] == 20000 and cur_tot["bonus"] == 0
    assert len(db.get_active_salary_entries(emp_id, py, pm)) == 1
    assert len(db.get_active_salary_entries(emp_id, y, m)) == 1

    # Bekor qilingandan keyin hisobdan chiqadi
    prev_entry = db.get_active_salary_entries(emp_id, py, pm)[0]
    db.cancel_salary_entry(prev_entry["id"], 0, "xato yozildi")
    assert db.get_salary_totals_by_type(emp_id, py, pm)["bonus"] == 0
    assert len(db.get_active_salary_entries(emp_id, py, pm)) == 0

    print("✅ test_month_nav: hammasi o'tdi")


if __name__ == "__main__":
    main()
