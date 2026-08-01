"""Arxiv + pf_access uchun o'z-o'zini tekshiruv. Jonli bazaga TEGMAYDI —
har doim vaqtinchalik nusxa/yangi baza ustida ishlaydi."""
import os, shutil, sqlite3, sys, tempfile

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
LIVE_DB = os.path.join(BOT_DIR, "attendance.db")
TMP = tempfile.mkdtemp()


def run(db_path, label):
    """Alohida jarayonda emas — modullarni qayta yuklab, DB_PATH ni almashtiramiz."""
    os.environ["DB_PATH"] = db_path
    for m in list(sys.modules):
        if m in ("config", "database", "texts", "keyboards", "tzutil") or m.startswith("handlers"):
            del sys.modules[m]
    sys.path.insert(0, BOT_DIR)

    import database as db
    import texts
    from tzutil import last_months, now as tz_now

    # 1) Migratsiya idempotent: ikki marta init_db
    db.init_db()
    db.init_db()
    cols = [r[1] for r in sqlite3.connect(db_path).execute(
        "PRAGMA table_info(employees)").fetchall()]
    assert "pf_access" in cols, f"{label}: pf_access ustuni yo'q"

    # 2) last_months — 6 ta, joriy oy birinchi, kamayuvchi, oy 1..12
    ms = last_months(6)
    n = tz_now()
    assert len(ms) == 6 and ms[0] == (n.year, n.month), f"{label}: {ms}"
    assert all(1 <= m <= 12 for _, m in ms), ms
    for i in range(5):
        assert ms[i] > ms[i + 1], ms
    # yil chegarasi: yanvardan orqaga o'tish
    assert (2026, 1) not in ms or (2025, 12) in ms

    # 3) pf_access toggle + get_all_employees pf_access qaytaradi
    emps = db.get_all_employees(active_only=True)
    if emps:
        e = emps[0]
        old = e["pf_access"]
        db.set_pf_access(e["id"], 1)
        assert db.get_employee_by_id(e["id"])["pf_access"] == 1, label
        db.set_pf_access(e["id"], 0)
        assert db.get_employee_by_id(e["id"])["pf_access"] == 0, label
        db.set_pf_access(e["id"], old)

    # 4) Arxiv xulosasi: har oy uchun chaqirilishi kerak (bo'sh oyda None/EMPTY)
    from handlers.personal_finance import _pf_summary_text, _parse_ym
    from handlers.finance import _finance_summary_text
    if emps:
        eid = emps[0]["id"]
        for y, m in ms:
            out = _pf_summary_text(eid, y, m, with_today=False)
            assert out is None or texts.MONTHS_UZ[m] in out, (label, y, m)
            fin = _finance_summary_text(eid, y, m, with_today=False)
            assert texts.MONTHS_UZ[m] in fin, (label, y, m)
            # arxivda "bugun"/balans bloklari chiqmasligi kerak
            assert "Bugun" not in fin, (label, y, m, fin)
        # joriy oy — bugungi blok bo'lishi kerak
        cur = _finance_summary_text(eid, n.year, n.month, with_today=True)
        assert "Bugun" in cur or "Balans" in cur, cur

    # 5) callback qiymatini o'qish
    assert _parse_ym("2026-07") == (2026, 7)
    assert _parse_ym("2026-13") is None
    assert _parse_ym("cancel") is None

    # 6) Klaviaturalar: has_pf, arxiv, toggle belgilari
    import keyboards as kb
    plain = [b.text for row in kb.main_menu_kb().keyboard for b in row]
    withpf = [b.text for row in kb.main_menu_kb(has_pf=True).keyboard for b in row]
    assert texts.BTN_PERSONAL_FINANCE not in plain, plain
    assert texts.BTN_PERSONAL_FINANCE in withpf, withpf
    # Bosh Admin/Boss menyulari o'zgarmagan
    for k in (kb.main_menu_kb(is_bosh_admin=True, has_pf=True),
              kb.main_menu_kb(is_boss=True, has_pf=True)):
        assert texts.BTN_PERSONAL_FINANCE not in [b.text for r in k.keyboard for b in r]

    # PF menyusi: Moliya orqali kirganda ortga tugmasi boshqacha
    pf_emp = [b.text for r in kb.pf_menu_kb().keyboard for b in r]
    pf_fin = [b.text for r in kb.pf_menu_kb(from_finance=True).keyboard for b in r]
    assert texts.BTN_BACK in pf_emp and texts.BTN_PF_BACK_FINANCE not in pf_emp, pf_emp
    assert texts.BTN_PF_BACK_FINANCE in pf_fin and texts.BTN_BACK not in pf_fin, pf_fin

    arc = kb.archive_months_kb("pf_arc", ms)
    datas = [b.callback_data for r in arc.inline_keyboard for b in r]
    assert datas[0] == f"pf_arc:{n.year}-{n.month:02d}", datas
    assert datas[-1] == "pf_arc:cancel", datas
    # prefiks to'qnashuvi yo'q: "pf_arcx:..." "pf_arc:" bilan boshlanmaydi
    assert not f"pf_arcx:{n.year}-{n.month:02d}".startswith("pf_arc:")
    assert not f"fin_arcx:{n.year}-{n.month:02d}".startswith("fin_arc:")

    fake = [{"id": 3, "full_name": "Fayozbek", "pf_access": 1},
            {"id": 4, "full_name": "Ali", "pf_access": 0}]
    acc = [b.text for r in kb.pf_access_kb(fake).inline_keyboard for b in r]
    assert acc[0].startswith("✅") and acc[1].startswith("⬜"), acc

    # 7) Menyularda arxiv tugmalari bor va matnlari to'qnashmaydi
    finm = [b.text for r in kb.finance_menu_kb().keyboard for b in r]
    assert texts.BTN_FINANCE_ARCHIVE in finm and texts.BTN_PF_ARCHIVE in pf_emp
    assert texts.BTN_FINANCE_ARCHIVE != texts.BTN_PF_ARCHIVE, "arxiv tugma matnlari bir xil!"

    print(f"✅ {label}: hamma tekshiruv o'tdi ({len(emps)} faol xodim)")


# A) Yangi (bo'sh) baza
run(os.path.join(TMP, "yangi.db"), "yangi baza")

# B) Jonli bazaning NUSXASI (eski sxema — migratsiya sinovi)
copy = os.path.join(TMP, "eski.db")
shutil.copy(LIVE_DB, copy)
sqlite3.connect(copy).close()
run(copy, "eski baza nusxasi")

shutil.rmtree(TMP)
print("✅✅ HAMMASI O'TDI — jonli attendance.db tegilmadi")
