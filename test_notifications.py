"""Bildirishnomalar bo'limi testi — vaqtinchalik bazada, jonli baza tegilmaydi.

Tekshiriladi: calendar_days jadvali, bayram/dam olish toggle mantig'i,
eslatma hafta kunlari sozlamasi, bayram kunidagi to'liq stavka va
klaviaturalar/menyu reyestri.

Ishga tushirish: ./venv/bin/python test_notifications.py
"""
import os
import tempfile

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "notify_test.db")
os.environ.setdefault("BOT_TOKEN", "test:token")

import database as db          # noqa: E402
import keyboards as kb         # noqa: E402
import texts                   # noqa: E402

Y, M = 2026, 9   # test oyi (jonli ma'lumotdan mustaqil)


def _mk_employee(tg: int, name: str, pos_id: int, rate: int,
                 active: int = 1, registered: str = "2020-01-01 00:00:00") -> int:
    with db.get_db() as conn:
        cur = conn.execute(
            """INSERT INTO employees (telegram_id, full_name, phone, position,
               face_encoding, role, is_admin, is_active, position_id, daily_rate,
               registered_at)
               VALUES (?,?,?,?,x'00','employee',0,?,?,?,?)""",
            (tg, name, f"+9989{tg}", "TestLavozim", active, pos_id, rate, registered)
        )
        return cur.lastrowid


def _add_day(emp_id: int, day: int, hours: float):
    """Mahalliy 08:00 dan `hours` soat (bazada UTC — 03:00 dan)."""
    out_h = 3 + int(hours)
    out_m = int(round((hours % 1) * 60))
    with db.get_db() as conn:
        conn.execute("INSERT INTO attendance (employee_id, check_type, timestamp) VALUES (?,'in',?)",
                     (emp_id, f"{Y:04d}-{M:02d}-{day:02d} 03:00:00"))
        conn.execute("INSERT INTO attendance (employee_id, check_type, timestamp) VALUES (?,'out',?)",
                     (emp_id, f"{Y:04d}-{M:02d}-{day:02d} {out_h:02d}:{out_m:02d}:00"))


def test_calendar_crud():
    d1, d2 = f"{Y}-{M:02d}-01", f"{Y}-{M:02d}-02"

    assert db.get_calendar_day_type(d1) is None
    assert db.is_non_working_day(d1) is False

    # bo'sh -> bayram
    assert db.toggle_calendar_day(d1, db.HOLIDAY, 1) == db.HOLIDAY
    assert db.get_calendar_day_type(d1) == db.HOLIDAY
    assert db.is_non_working_day(d1) is True

    # bayram -> bo'sh (o'sha tugma qayta bosildi)
    assert db.toggle_calendar_day(d1, db.HOLIDAY, 1) is None
    assert db.get_calendar_day_type(d1) is None

    # bo'sh -> dam olish -> bayramga almashtirish
    assert db.toggle_calendar_day(d1, db.DAYOFF, 1) == db.DAYOFF
    assert db.toggle_calendar_day(d1, db.HOLIDAY, 1) == db.HOLIDAY, \
        "boshqa turdagi kun bosilganda tur almashishi kerak"

    db.set_calendar_day(d2, db.DAYOFF, 1)
    month = db.get_calendar_month(Y, M)
    assert month == {d1: db.HOLIDAY, d2: db.DAYOFF}, month
    assert db.get_calendar_days_by_type(Y, M, db.HOLIDAY) == [d1]
    assert db.get_calendar_days_by_type(Y, M, db.DAYOFF) == [d2]
    # boshqa oy toza
    assert db.get_calendar_month(Y, M + 1) == {}

    try:
        db.set_calendar_day(d1, "boshqa")
        raise AssertionError("noma'lum tur qabul qilindi")
    except ValueError:
        pass

    assert db.clear_calendar_day(d2) == 1
    assert db.clear_calendar_day(d2) == 0
    db.clear_calendar_day(d1)
    assert db.get_calendar_month(Y, M) == {}, "test oyidan keyin kalendar toza bo'lsin"
    print("✅ kalendar CRUD va toggle")


def test_reminder_days():
    assert db.get_reminder_days() == {0, 1, 2, 3, 4, 5, 6}, "standart — hamma kun"

    assert db.toggle_reminder_day(6) is False
    assert db.get_reminder_days() == {0, 1, 2, 3, 4, 5}
    assert db.toggle_reminder_day(6) is True
    assert 6 in db.get_reminder_days()

    db.set_reminder_days({0, 2, 4})
    assert db.get_setting(db.REMINDER_DAYS_KEY) == "1010100"
    assert db.get_reminder_days() == {0, 2, 4}

    db.set_reminder_days(set())
    assert db.get_reminder_days() == set(), "hamma kun o'chirilishi mumkin"

    # buzuq qiymat botni yiqitmasin — standartga qaytadi
    db.set_setting(db.REMINDER_DAYS_KEY, "buzuq")
    assert db.get_reminder_days() == {0, 1, 2, 3, 4, 5, 6}

    for bad in (-1, 7):
        try:
            db.toggle_reminder_day(bad)
            raise AssertionError("noto'g'ri indeks qabul qilindi")
        except ValueError:
            pass
    db.set_reminder_days({0, 1, 2, 3, 4, 5, 6})
    print("✅ eslatma hafta kunlari")


def test_holiday_salary():
    pos_id = db.create_position("TestLavozim", 9, 100000, 500000)
    rate = 200000
    emp = _mk_employee(7001, "Bayram Test", pos_id, rate)
    off = _mk_employee(7002, "Faolsiz Test", pos_id, rate, active=0)
    late = _mk_employee(7003, "Keyin kelgan", pos_id, rate,
                        registered=f"{Y}-{M:02d}-20 00:00:00")

    # 2 kun to'liq ishlagan (9 soat = norma)
    _add_day(emp, 10, 9)
    _add_day(emp, 11, 9)
    base = db.get_monthly_base_salary(emp, Y, M)
    assert base == 2 * rate, base

    # Bayram kuni: kelmagan bo'lsa ham to'liq stavka QO'SHILADI
    db.set_calendar_day(f"{Y}-{M:02d}-15", db.HOLIDAY, 1)
    assert db.get_monthly_base_salary(emp, Y, M) == 3 * rate

    # Bayram kuni ishga kelsa — ishlagani ham ustiga qo'shiladi
    _add_day(emp, 15, 9)
    assert db.get_monthly_base_salary(emp, Y, M) == 4 * rate, \
        "bayram kuni ishlagan xodimga stavka + ishlagani qo'shilishi kerak"

    # Dam olish kuni ish haqqiga TA'SIR QILMAYDI
    before = db.get_monthly_base_salary(emp, Y, M)
    db.set_calendar_day(f"{Y}-{M:02d}-16", db.DAYOFF, 1)
    assert db.get_monthly_base_salary(emp, Y, M) == before

    # Faolsiz xodimga bayram stavkasi avtomatik yozilmaydi
    assert db.get_monthly_holiday_pay(off, Y, M) == 0
    assert db.get_monthly_base_salary(off, Y, M) == 0

    # Bayramdan KEYIN ro'yxatdan o'tgan xodimga o'sha bayram hisoblanmaydi
    assert db.get_monthly_holiday_pay(late, Y, M) == 0

    # Boshqa oyga ta'sir qilmaydi
    assert db.get_monthly_base_salary(emp, Y, M + 1) == 0

    db.clear_calendar_day(f"{Y}-{M:02d}-15")
    db.clear_calendar_day(f"{Y}-{M:02d}-16")
    assert db.get_monthly_base_salary(emp, Y, M) == 3 * rate, \
        "belgi olib tashlangach eski hisob qaytishi kerak"
    print("✅ bayram kunida to'liq stavka")


def test_keyboards():
    # Moliya menyusida yangi tugma bor va oxirida (Ortga dan oldin)
    rows = [[b.text for b in r] for r in kb.finance_menu_kb().keyboard]
    flat = [t for r in rows for t in r]
    assert texts.BTN_NOTIFICATIONS in flat, rows
    assert flat.index(texts.BTN_NOTIFICATIONS) == len(flat) - 2, rows

    notify = [[b.text for b in r] for r in kb.notify_menu_kb().keyboard]
    assert notify == [[texts.BTN_REMIND_DAYS], [texts.BTN_HOLIDAYS],
                      [texts.BTN_DAYOFFS], [texts.BTN_NOTIFY_BACK]], notify

    # Menyu reyestri butunligi (muharrir grafi buzilmasin)
    assert "notify_menu" in kb.MENU_REGISTRY
    assert kb.MENU_REGISTRY["finance_menu"]["targets"]["notifications"] == "notify_menu"
    for key, reg in kb.MENU_REGISTRY.items():
        for btn, target in reg.get("targets", {}).items():
            assert btn in reg["buttons"], f"{key}: {btn} tugmasi yo'q"
            assert target == "back" or target in kb.MENU_REGISTRY, f"{key}: {target}"

    # Tugma matnlari takrorlanmasin (handler filtrlari chalkashmasligi uchun)
    for menu in ("finance_menu", "notify_menu", "pf_menu"):
        vals = list(kb.MENU_REGISTRY[menu]["buttons"].values())
        assert len(vals) == len(set(vals)), menu
    assert texts.BTN_NOTIFY_BACK != texts.BTN_PF_BACK_FINANCE, \
        "ortga tugmalari matni bir xil bo'lsa router chalkashadi"

    # Kalendar: belgilangan kun emoji bilan chiqadi
    db.set_calendar_day(f"{Y}-{M:02d}-15", db.HOLIDAY, 1)
    labels = [b.text for row in kb.calendar_kb("h", Y, M).inline_keyboard for b in row]
    assert "🎉15" in labels, labels
    assert "14" in labels
    db.clear_calendar_day(f"{Y}-{M:02d}-15")

    # Callback uzunligi Telegram chegarasidan (64 bayt) kichik
    for row in kb.calendar_kb("o", Y, M).inline_keyboard:
        for b in row:
            assert len(b.callback_data.encode()) <= 64, b.callback_data

    # Hafta kunlari klaviaturasi holatni ko'rsatadi
    db.set_reminder_days({0, 1, 2, 3, 4})
    labels = [r[0].text for r in kb.remind_days_kb().inline_keyboard[:7]]
    assert labels[0].startswith("✅") and labels[6].startswith("⬜"), labels
    db.set_reminder_days({0, 1, 2, 3, 4, 5, 6})
    print("✅ klaviaturalar va menyu reyestri")


def test_reminders_gate():
    """Eslatma sikli bayram/dam olish va hafta kuni jadvaliga bo'ysunadimi."""
    import asyncio
    from datetime import datetime
    import services.reminders as rem

    assert not hasattr(rem, "WEEKEND_DAYS"), "eski WEEKEND_DAYS qolib ketgan"

    run = asyncio.run
    reached = {"n": 0}

    def _boom():
        reached["n"] += 1
        return []

    real_now, real_dash = rem.tz_now, rem.get_dashboard_today
    rem.get_dashboard_today = _boom
    # Ish boshlanishidan 15 daqiqa oldin (09:00 → 08:45), payshanba
    rem.tz_now = lambda: datetime(Y, M, 17, 8, 45)
    try:
        db.set_reminder_days({0, 1, 2, 3, 4, 5, 6})
        db.clear_calendar_day(f"{Y}-{M:02d}-17")
        run(rem._tick(None))
        assert reached["n"] == 1, "oddiy kunda eslatma tekshiruvi ishlashi kerak"

        # Bayram kuni — umuman tekshirilmaydi
        db.set_calendar_day(f"{Y}-{M:02d}-17", db.HOLIDAY, 1)
        run(rem._tick(None))
        assert reached["n"] == 1, "bayram kunida eslatma yuborilmasligi kerak"

        # Dam olish kuni — ham yuborilmaydi
        db.set_calendar_day(f"{Y}-{M:02d}-17", db.DAYOFF, 1)
        run(rem._tick(None))
        assert reached["n"] == 1, "dam olish kunida eslatma yuborilmasligi kerak"

        # Hafta kuni o'chirilgan bo'lsa — yuborilmaydi
        db.clear_calendar_day(f"{Y}-{M:02d}-17")
        db.set_reminder_days({0, 1, 2, 4, 5, 6})   # payshanba (3) o'chiq
        run(rem._tick(None))
        assert reached["n"] == 1, "o'chirilgan hafta kunida yuborilmasligi kerak"

        # Umumiy o'chirgich ham ishlaydi
        db.set_reminder_days({0, 1, 2, 3, 4, 5, 6})
        db.set_setting("reminders_enabled", "0")
        run(rem._tick(None))
        assert reached["n"] == 1
        db.set_setting("reminders_enabled", "1")
        run(rem._tick(None))
        assert reached["n"] == 2, "qayta yoqilganda ishlashi kerak"
    finally:
        rem.tz_now, rem.get_dashboard_today = real_now, real_dash
    print("✅ eslatmalar sikli: bayram / dam olish / hafta kuni jadvali")


def test_handlers():
    """Handlerlarni soxta Message/CallbackQuery bilan chaqirib tekshirish."""
    import sys, types, asyncio
    fake = types.ModuleType("face_recognition")
    fake.face_encodings = lambda *a, **k: []
    sys.modules.setdefault("face_recognition", fake)
    from handlers import notifications as nt

    boss_tg = 7777
    with db.get_db() as conn:
        conn.execute(
            """INSERT INTO employees (telegram_id, full_name, phone, position,
               face_encoding, role, is_admin, is_active)
               VALUES (?,?,?,?,x'00','bosh_admin',1,1)""",
            (boss_tg, "Rahbar", "+998900000000", "Rahbar")
        )

    class User:
        def __init__(self, tg): self.id = tg

    class Msg:
        def __init__(self, tg):
            self.from_user, self.sent, self.deleted = User(tg), [], False
        async def answer(self, text, reply_markup=None):
            self.sent.append((text, reply_markup))
        async def edit_text(self, text, reply_markup=None):
            self.sent.append((text, reply_markup))
        async def delete(self): self.deleted = True

    class Call:
        def __init__(self, tg, data):
            self.from_user, self.data = User(tg), data
            self.message, self.answers = Msg(tg), []
        async def answer(self, text=None, show_alert=False):
            self.answers.append(text)

    class St:
        async def clear(self): pass

    run = asyncio.run

    # Ruxsatsiz foydalanuvchi hech narsa o'zgartira olmasin
    other = Call(4242, f"cal:h:{Y}-{M:02d}-05")
    run(nt.calendar_pick(other))
    assert db.get_calendar_day_type(f"{Y}-{M:02d}-05") is None, "ruxsatsiz belgilab yubordi!"

    # Bo'lim menyusi ochiladi
    m = Msg(boss_tg); run(nt.notify_open(m, St()))
    assert m.sent and texts.BTN_HOLIDAYS in str(m.sent[0][1]), m.sent

    # Bayram kunini belgilash / bekor qilish
    c = Call(boss_tg, f"cal:h:{Y}-{M:02d}-05")
    run(nt.calendar_pick(c))
    assert db.get_calendar_day_type(f"{Y}-{M:02d}-05") == db.HOLIDAY
    assert "bayram" in c.answers[0]
    c = Call(boss_tg, f"cal:h:{Y}-{M:02d}-05")
    run(nt.calendar_pick(c))
    assert db.get_calendar_day_type(f"{Y}-{M:02d}-05") is None

    # Buzuq sana / notanish rejim botni yiqitmasin
    for bad in (f"cal:h:{Y}-{M:02d}-99", "cal:x:2026-09-05", "cal:h:salom", "cal:h"):
        run(nt.calendar_pick(Call(boss_tg, bad)))

    # Chegaradan tashqari oy rad etiladi
    c = Call(boss_tg, "cal:h:2000-01-01"); run(nt.calendar_pick(c))
    assert db.get_calendar_day_type("2000-01-01") is None
    assert c.answers and texts.CAL_LIMIT in c.answers[0]

    # Oy navigatsiyasi
    c = Call(boss_tg, f"caln:o:{Y}:{M}"); run(nt.calendar_nav(c))
    assert c.message.sent, "kalendar yangilanmadi"

    # Hafta kuni toggle
    before = db.get_reminder_days()
    c = Call(boss_tg, "rday:6"); run(nt.remind_day_toggle(c))
    assert (6 in db.get_reminder_days()) != (6 in before)
    run(nt.remind_day_toggle(Call(boss_tg, "rday:6")))
    assert db.get_reminder_days() == before
    run(nt.remind_day_toggle(Call(boss_tg, "rday:99")))
    run(nt.remind_day_toggle(Call(boss_tg, "rday:xato")))
    assert db.get_reminder_days() == before, "buzuq indeks holatni o'zgartirdi"

    with db.get_db() as conn:
        conn.execute("DELETE FROM employees WHERE telegram_id = ?", (boss_tg,))
    print("✅ handlerlar: ruxsat, belgilash, navigatsiya, buzuq ma'lumot")


def main():
    db.init_db()
    db.init_db()   # idempotentlik
    test_calendar_crud()
    test_reminder_days()
    test_holiday_salary()
    test_keyboards()
    test_reminders_gate()
    test_handlers()
    print("\n🎉 Barcha testlar o'tdi")


if __name__ == "__main__":
    main()
