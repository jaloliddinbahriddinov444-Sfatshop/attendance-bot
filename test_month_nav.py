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

    print("✅ test_month_nav: hammasi o'tdi")


if __name__ == "__main__":
    main()
