"""Menyu tartibi muharriri uchun o'z-o'zini tekshiruv.
Jonli bazaga TEGMAYDI — vaqtinchalik baza ustida ishlaydi."""
import os
import shutil
import sys
import tempfile

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp()
os.environ["DB_PATH"] = os.path.join(TMP, "menu_test.db")
sys.path.insert(0, BOT_DIR)

import database as db                                    # noqa: E402
db.init_db()
db.init_db()                                             # idempotent bo'lsin
import texts                                             # noqa: E402
import keyboards as kb                                   # noqa: E402
from handlers.menu_editor import _scheme_text                # noqa: E402
from services.menu_editor_web import _reachable, ROOT_MENUS   # noqa: E402


def rows_of(k):
    return [[b.text for b in r] for r in k.keyboard]


# 1) Standart tartib — refaktordan keyin hech narsa o'zgarmagan
#    (to'liq solishtiruv alohida parity testida; bu yerda default==qurilgan)
for menu_key, reg in kb.MENU_REGISTRY.items():
    assert kb.get_layout(menu_key) == kb.normalize_layout(menu_key, reg["default"]), menu_key
    built = rows_of(kb.build_menu_kb(menu_key))
    expected = [[reg["buttons"][k] for k in row] for row in reg["default"]]
    assert built == expected, (menu_key, built, expected)
print("✅ 1) Barcha menyularda standart tartib default bilan bir xil")

# 2-3) Surish/birlashtirish mantig'i endi Mini App JS'ida — brauzerda sinaladi
# (test_menu_webapp.py izohiga qarang). Bu yerda baza + normalizatsiya qatlami.
db.set_menu_layout("finance_menu", [["expense", "income"], ["summary"]])
assert kb.get_layout("finance_menu")[0] == ["expense", "income"]
built = rows_of(kb.finance_menu_kb())
assert built[0] == [texts.BTN_FINANCE_EXPENSE, texts.BTN_FINANCE_INCOME], built
db.reset_menu_layout("finance_menu")
print("✅ 2) Saqlangan joylashuv menyuda qo'llanadi")

# Navigatsiya grafi: har target reyestrda mavjudmi va hamma menyu ochiladimi
roots = [k for k, _ in ROOT_MENUS]
for mk, reg in kb.MENU_REGISTRY.items():
    for bk, tgt in reg.get("targets", {}).items():
        assert bk in reg["buttons"], (mk, bk)
        assert tgt == "back" or tgt in kb.MENU_REGISTRY, (mk, bk, tgt)
ochiladi = _reachable(kb.MENU_REGISTRY, roots)
yetim = [k for k in kb.MENU_REGISTRY if k not in ochiladi]
# Yetimlar yo'qolib ketmasligi kerak — ular sahifada alohida ro'yxatda chiqadi
assert set(yetim) == {"boss_panel", "grp_finance"}, yetim
for kerak in ("finance_menu", "pf_menu", "admin_panel_bosh", "grp_control",
              "ip_menu", "admin_settings", "admin_panel"):
    assert kerak in ochiladi, kerak
print(f"✅ 3) Navigatsiya grafi butun; yetim menyular: {yetim} (alohida ro'yxatda)")

# 4) Standartga qaytarish — bazadan yozuv o'chadi
db.set_menu_layout("finance_menu", [["back"], ["income"]])
assert db.get_menu_layout("finance_menu") is not None
db.reset_menu_layout("finance_menu")
assert db.get_menu_layout("finance_menu") is None, "yozuv o'chmadi"
assert kb.get_layout("finance_menu") == kb.MENU_REGISTRY["finance_menu"]["default"]
print("✅ 4) Standartga qaytarish ishlaydi")

# 5) Shartli tugmalar — joylashuv qanday bo'lishidan qat'i nazar filtrlanadi
db.set_menu_layout("main_employee",
                   [["admin", "personal_finance"], ["attendance"],
                    ["profile", "stats"], ["tasks", "salary"]])
plain = rows_of(kb.main_menu_kb())
assert texts.BTN_ADMIN not in [b for r in plain for b in r], plain
assert texts.BTN_PERSONAL_FINANCE not in [b for r in plain for b in r], plain
assert plain[0] == [texts.BTN_ATTENDANCE], "bo'sh qator tushmadi"
withboth = [b for r in rows_of(kb.main_menu_kb(is_admin=True, has_pf=True)) for b in r]
assert texts.BTN_ADMIN in withboth and texts.BTN_PERSONAL_FINANCE in withboth
# faqat bittasi ko'rinsa — qator bir tugmali bo'lib qoladi
only_pf = rows_of(kb.main_menu_kb(has_pf=True))
assert only_pf[0] == [texts.BTN_PERSONAL_FINANCE], only_pf
db.reset_menu_layout("main_employee")
print("✅ 5) Shartli tugmalar layoutdan qat'i nazar to'g'ri filtrlanadi")

# 6) Normalizatsiya: yangi tugma qo'shilsa eski layoutda oxirida paydo bo'ladi
db.set_menu_layout("pf_menu", [["income", "expense"], ["back"]])
kb.MENU_REGISTRY["pf_menu"]["buttons"]["soxta_yangi"] = "🆕 Soxta tugma"
try:
    layout = kb.get_layout("pf_menu")
    flat = [k for r in layout for k in r]
    # eski layoutda yo'q tugmalar oxiriga qo'shilgan, birinchilari joyida
    assert flat[:3] == ["income", "expense", "back"], flat
    assert "soxta_yangi" in flat and flat[-1] == "soxta_yangi", flat
    assert "summary" in flat and "archive" in flat, flat
    built = rows_of(kb.pf_menu_kb())            # bot yiqilmasligi kerak
    assert "🆕 Soxta tugma" in [b for r in built for b in r]
    assert _scheme_text("pf_menu")              # muharrir sxemasi ham ishlaydi
finally:
    del kb.MENU_REGISTRY["pf_menu"]["buttons"]["soxta_yangi"]
    db.reset_menu_layout("pf_menu")
print("✅ 6) Normalizatsiya: yangi tugma oxirida paydo bo'ladi, bot yiqilmaydi")

# Buzuq/notanish ma'lumot ham botni yiqitmasin
db.set_menu_layout("pf_menu", [["yoq_kalit"], ["income", "income", "expense"], []])
layout = kb.get_layout("pf_menu")
assert all(len(r) <= 2 for r in layout) and all(r for r in layout), layout
flat = [k for r in layout for k in r]
assert flat.count("income") == 1 and "yoq_kalit" not in flat, flat
assert set(flat) == set(kb.MENU_REGISTRY["pf_menu"]["buttons"]), flat
db.reset_menu_layout("pf_menu")
with db.get_db() as conn:                       # butunlay buzuq JSON
    conn.execute("INSERT INTO menu_layouts (menu_key, layout_json) VALUES (?, ?)",
                 ("pf_menu", "{buzuq json"))
assert db.get_menu_layout("pf_menu") is None, "buzuq JSON None qaytarishi kerak"
assert rows_of(kb.pf_menu_kb()), "buzuq yozuvda menyu qurilmadi"
db.reset_menu_layout("pf_menu")
print("✅    Buzuq/takroriy/notanish ma'lumot botni yiqitmaydi")

shutil.rmtree(TMP)
print("\n✅✅ HAMMASI O'TDI — jonli attendance.db tegilmadi")
