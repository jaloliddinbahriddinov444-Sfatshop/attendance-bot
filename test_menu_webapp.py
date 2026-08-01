"""Mini App menyu muharriri uchun o'z-o'zini tekshiruv.
Jonli bazaga TEGMAYDI — vaqtinchalik baza ustida ishlaydi."""
import asyncio
import json
import os
import shutil
import sys
import tempfile

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp()
os.environ["DB_PATH"] = os.path.join(TMP, "webapp_test.db")
sys.path.insert(0, BOT_DIR)

import database as db                                      # noqa: E402
db.init_db()
import texts                                               # noqa: E402
import keyboards as kb                                     # noqa: E402


# Test xodimlari: 1 — Bosh Admin, 2 — oddiy xodim
with db.get_db() as conn:
    for tg_id, nom, lavozim, adm, rol in [
        (111, "Bosh Admin", "admin", 1, "bosh_admin"),
        (222, "Oddiy Xodim", "dizayner", 0, "employee"),
    ]:
        conn.execute(
            "INSERT INTO employees (telegram_id, full_name, phone, position, "
            "face_encoding, is_admin, role) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (tg_id, nom, f"+9989000000{tg_id}", lavozim, b"", adm, rol)
        )


# ─── Soxta aiogram obyektlari ───────────────────────────────────────────────

class FakeState:
    async def clear(self):
        pass


class FakeMessage:
    def __init__(self, user_id, data):
        self.from_user = type("U", (), {"id": user_id})()
        self.web_app_data = type("W", (), {"data": data})() if data is not None else None
        self.replies = []

    async def answer(self, text, reply_markup=None, **kw):
        self.replies.append(text)


async def send(user_id, payload):
    """Mini App'dan kelgan ma'lumotni handlerga uzatadi."""
    from handlers.menu_editor import menu_layout_webapp_save
    raw = payload if isinstance(payload, str) else json.dumps(payload)
    msg = FakeMessage(user_id, raw)
    await menu_layout_webapp_save(msg, FakeState())
    return msg.replies


# ─── 2) Web sahifa: 200 / 404 / ma'lumot inyeksiyasi ────────────────────────

async def test_web():
    from aiohttp import web, ClientSession
    from services.menu_editor_web import setup_menu_editor_routes

    app = web.Application()
    setup_menu_editor_routes(app)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = runner.addresses[0][1]
    base = f"http://127.0.0.1:{port}/dashboard/menu-editor"

    async with ClientSession() as s:
        async with s.get(base) as r:                 # endi menu parametrisiz
            assert r.status == 200, r.status
            html = await r.text()

    await runner.cleanup()

    assert "__DATA__" not in html, "ma'lumot sahifaga joylanmagan"
    assert "telegram-web-app.js" in html
    assert "sendData" in html and "pointerdown" in html
    # HTML5 draggable ishlatilmasligi kerak (mobil brauzerlarda ishlamaydi).
    # Izohlarda so'z uchrashi mumkin — atribut/xossa sifatida yo'qligini tekshiramiz
    for taqiq in ['draggable="true"', "draggable=true", ".draggable =",
                  "ondragstart", "dataTransfer"]:
        assert taqiq not in html, taqiq
    # Inyeksiya qilingan JSON o'qiladimi
    start = html.index("var DATA = ") + len("var DATA = ")
    end = html.index(";\n", start)
    data = json.loads(html[start:end])
    # BARCHA menyular bitta sahifaga joylanadi
    assert set(data["menus"]) == set(kb.MENU_REGISTRY), data["menus"].keys()
    fm = data["menus"]["finance_menu"]
    assert fm["layout"] == kb.get_layout("finance_menu")
    assert fm["buttons"]["income"] == texts.BTN_FINANCE_INCOME
    assert fm["targets"]["personal_finance"] == "pf_menu"
    assert fm["targets"]["back"] == "back"
    assert data["menus"]["main_employee"]["conditional"] == ["admin", "personal_finance"]
    assert [r[0] for r in data["roots"]] == ["main_employee", "main_boss", "main_bosh_admin"]
    assert set(data["orphans"]) == {"boss_panel", "grp_finance"}, data["orphans"]
    assert data["maxRow"] == kb.MAX_ROW_BUTTONS
    assert "BackButton" in html and "roles" in html
    print("✅ 2) GET /dashboard/menu-editor: 200, BARCHA menyu + target + rol joylangan")


asyncio.run(test_web())


# ─── 3) Saqlash oqimi ───────────────────────────────────────────────────────

async def test_save():
    yangi = [["expense", "income"], ["summary"], ["excel"], ["delete"],
             ["archive"], ["categories"], ["personal_finance"], ["back"]]
    pf_yangi = [["expense", "income"], ["summary", "excel"], ["delete"],
                ["archive"], ["categories"], ["back"]]
    # IKKI menyu birdaniga (yangi format)
    replies = await send(111, {"layouts": {"finance_menu": yangi, "pf_menu": pf_yangi}})
    assert db.get_menu_layout("finance_menu") == yangi, db.get_menu_layout("finance_menu")
    assert db.get_menu_layout("pf_menu") == pf_yangi, db.get_menu_layout("pf_menu")
    assert any("2 ta menyu saqlandi" in r for r in replies), replies
    built = [[b.text for b in r] for r in kb.finance_menu_kb().keyboard]
    assert built[0] == [texts.BTN_FINANCE_EXPENSE, texts.BTN_FINANCE_INCOME], built[0]
    pfb = [[b.text for b in r] for r in kb.pf_menu_kb().keyboard]
    assert pfb[0] == [texts.BTN_PF_EXPENSE, texts.BTN_PF_INCOME], pfb[0]
    db.reset_menu_layout("pf_menu")
    print("✅ 3) Bir yuborishda IKKI menyu saqlandi va ikkalasi menyuda ko'rindi")

    # Standartga qaytarilsa — bazadan yozuv O'CHADI (kod standarti muzlab qolmasin)
    await send(111, {"layouts": {"finance_menu":
                     kb.MENU_REGISTRY["finance_menu"]["default"]}})
    assert db.get_menu_layout("finance_menu") is None, "standartda yozuv qolib ketdi"
    await send(111, {"layouts": {"finance_menu": yangi}})
    print("✅    Standartga qaytarish bazadan yozuvni o'chiradi")

    # 4) Qatorda 3 ta tugma — bot tomonda ham rad etiladi
    await send(111, {"layouts": {"finance_menu":
                     [["income", "expense", "summary"], ["back"]]}})
    saqlangan = db.get_menu_layout("finance_menu")
    assert all(len(r) <= kb.MAX_ROW_BUTTONS for r in saqlangan), saqlangan
    assert ["income", "expense"] in saqlangan and ["summary"] in saqlangan, saqlangan
    print("✅ 4) Qatorda 3-tugma bot validatsiyasida ham rad etiladi")

    # 5) Bosh Admin bo'lmagan foydalanuvchi
    db.reset_menu_layout("finance_menu")
    replies = await send(222, {"layouts": {"finance_menu": [["back"]]}})
    assert db.get_menu_layout("finance_menu") is None, "ruxsatsiz saqlab yubordi!"
    assert texts.NO_PERMISSION in replies, replies
    replies = await send(999, {"layouts": {"finance_menu": [["back"]]}})   # notanish
    assert db.get_menu_layout("finance_menu") is None
    print("✅ 5) Bosh Admin bo'lmagan (va notanish) foydalanuvchi rad etiladi")

    # 6) Buzuq / soxta ma'lumot — bot yiqilmaydi
    for buzuq in ["{buzuq json", "[]", '{"layouts":{}}', '{"layouts":"matn"}',
                  '{"menu":"finance_menu","layout":[["back"]]}',   # ESKI format
                  '{"layouts":{"yoq_menyu":[["back"]]}}',
                  '{"layouts":{"finance_menu":"matn"}}',
                  '{"layouts":{"finance_menu":[]}}',
                  '{"layouts":{"finance_menu":[[],[]]}}']:
        replies = await send(111, buzuq)
        assert replies and replies[0].startswith("❌"), (buzuq, replies)
        assert db.get_menu_layout("finance_menu") is None, buzuq
    # notanish kalitlar tashlanadi, mavjudlari saqlanadi
    await send(111, {"layouts": {"pf_menu":
                     [["yoq_kalit"], ["back"], ["income", "income"]]}})
    saqlangan = db.get_menu_layout("pf_menu")
    tekis = [k for r in saqlangan for k in r]
    assert "yoq_kalit" not in tekis and tekis.count("income") == 1, saqlangan
    assert set(tekis) == set(kb.MENU_REGISTRY["pf_menu"]["buttons"]), saqlangan
    assert tekis[0] == "back", "mavjud tartib saqlanmadi"
    db.reset_menu_layout("pf_menu")
    print("✅ 6) Buzuq/soxta JSON botni yiqitmaydi, xato xabari beriladi")


asyncio.run(test_save())


# ─── 7) Shartli tugmalar — layoutdan qat'i nazar ────────────────────────────

db.set_menu_layout("main_employee",
                   [["admin", "personal_finance"], ["attendance"],
                    ["profile", "stats"], ["tasks", "salary"]])
oddiy = [b for r in kb.main_menu_kb().keyboard for b in r]
assert texts.BTN_ADMIN not in [b.text for b in oddiy]
assert texts.BTN_PERSONAL_FINANCE not in [b.text for b in oddiy]
db.reset_menu_layout("main_employee")
print("✅ 7) Shartli tugmalar layoutdan qat'i nazar filtrlanadi")


# ─── 8) Normalizatsiya: yangi kalit oxirida paydo bo'ladi ───────────────────

db.set_menu_layout("pf_menu", [["income", "expense"], ["back"]])
kb.MENU_REGISTRY["pf_menu"]["buttons"]["soxta_yangi"] = "🆕 Soxta"
try:
    tekis = [k for r in kb.get_layout("pf_menu") for k in r]
    assert tekis[:3] == ["income", "expense", "back"], tekis
    assert tekis[-1] == "soxta_yangi", tekis
    assert kb.pf_menu_kb(), "menyu qurilmadi"
finally:
    del kb.MENU_REGISTRY["pf_menu"]["buttons"]["soxta_yangi"]
    db.reset_menu_layout("pf_menu")
print("✅ 8) Yangi kalit eski layoutda oxirida paydo bo'ladi")


# ─── Mini App klaviaturasi ─────────────────────────────────────────────────

k = kb.menu_editor_webapp_kb("https://api.sfatshop.uz")
wb = k.keyboard[0][0]
assert wb.web_app is not None, "web_app KeyboardButton bo'lishi kerak (inline emas)"
assert wb.web_app.url == "https://api.sfatshop.uz/dashboard/menu-editor"
assert k.keyboard[1][0].text == texts.BTN_CANCEL
print("✅    Mini App KeyboardButton(web_app=...) — /dashboard/ ostida (nginx tayyor)")

# sendData hajmi 4096 baytdan oshmasin (eng katta menyu)
# Eng yomon holat: BARCHA menyu birdaniga o'zgargan
hammasi = {"layouts": {m: kb.get_layout(m) for m in kb.MENU_REGISTRY}}
hajm = len(json.dumps(hammasi).encode())
assert hajm < 4096, f"sendData chegarasidan oshdi: {hajm}"
print(f"✅    Barcha menyu birdaniga: {hajm} bayt (chegara 4096)")

shutil.rmtree(TMP)
print("\n✅✅ HAMMASI O'TDI — jonli attendance.db tegilmadi")
