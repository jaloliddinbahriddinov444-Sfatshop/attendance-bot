"""Menyu tartibi muharriri — Telegram Mini App (navigatsiya + drag-and-drop).

Yo'l ATAYIN /dashboard/ ostida: serverdagi nginx'da faqat sanab o'tilgan
yo'llar 9090-portga (botga) yuboriladi, qolgani sfatshop backendiga ketadi.
`location /dashboard` prefiks bo'yicha ishlagani uchun bu sahifa nginx'ga
tegmasdan ochiladi.

Sahifa ochiq (kalitsiz), lekin faqat tugma YORLIQLARINI ko'rsatadi — ular
botning o'zida ham ko'rinadi, maxfiy ma'lumot yo'q. Saqlash esa Telegram
imzolagan web_app_data orqali va faqat Bosh Adminga ruxsat etilgan
(handlers/menu_editor.py).
"""
import json
import logging

from aiohttp import web

logger = logging.getLogger(__name__)

# Rol almashtirgichdagi asosiy menyu variantlari (registry kalitlari)
ROOT_MENUS = [
    ("main_employee", "Xodim"),
    ("main_boss", "Boss"),
    ("main_bosh_admin", "Bosh Admin"),
]


def _reachable(registry, roots):
    """Navigatsiya grafi bo'ylab ochib bo'ladigan menyular to'plami."""
    seen, stack = set(roots), list(roots)
    while stack:
        cur = stack.pop()
        for target in registry[cur].get("targets", {}).values():
            if target != "back" and target in registry and target not in seen:
                seen.add(target)
                stack.append(target)
    return seen


async def _menu_editor_page(request: web.Request) -> web.Response:
    # Import shu yerda — keyboards.py aylanma importga tushmasligi uchun
    import keyboards as kb

    roots = [k for k, _ in ROOT_MENUS]
    reachable = _reachable(kb.MENU_REGISTRY, roots)

    menus = {}
    for key, reg in kb.MENU_REGISTRY.items():
        menus[key] = {
            "title": reg["title"],
            "buttons": reg["buttons"],
            "targets": reg.get("targets", {}),
            "conditional": sorted(reg.get("conditional", ())),
            "layout": kb.get_layout(key),
            "default": kb.normalize_layout(key, reg["default"]),
        }

    data = {
        "menus": menus,
        "roots": ROOT_MENUS,
        # Navigatsiya orqali ochilmaydigan menyular (masalan Boss panel —
        # uning tugmasi hech qaysi klaviaturada yo'q) alohida ro'yxatda chiqadi,
        # aks holda ular tahrirlab bo'lmas bo'lib qolardi
        "orphans": sorted(k for k in kb.MENU_REGISTRY if k not in reachable),
        "maxRow": kb.MAX_ROW_BUTTONS,
    }
    html = MENU_EDITOR_HTML.replace(
        "__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    )
    return web.Response(text=html, content_type="text/html", charset="utf-8")


def setup_menu_editor_routes(app: web.Application):
    app.router.add_get("/dashboard/menu-editor", _menu_editor_page)
    logger.info("Menyu muharriri endpointi ulandi: /dashboard/menu-editor")


# ---------- Sahifa (bitta fayl, tashqi kutubxonasiz, vanilla JS) ----------

MENU_EDITOR_HTML = """<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Menyu tartibi</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
  :root {
    --bg: #ffffff; --text: #000000; --hint: #999999;
    --btn: #2481cc; --btn-text: #ffffff; --secondary-bg: #f1f1f1;
  }
  * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
  body {
    margin: 0; padding: 12px 12px 92px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg); color: var(--text);
    -webkit-user-select: none; user-select: none; overflow-x: hidden;
  }

  /* Rol almashtirgich */
  #roles { display: flex; gap: 4px; padding: 3px; margin-bottom: 12px;
           background: var(--secondary-bg); border-radius: 10px; }
  #roles button {
    flex: 1; padding: 8px 4px; border: 0; border-radius: 8px;
    background: transparent; color: var(--text); font-size: 13px;
    font-family: inherit; transition: background .15s ease;
  }
  #roles button.on { background: var(--bg); font-weight: 600; }

  /* Sarlavha + orqaga */
  #head { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
  #back {
    display: none; border: 0; background: transparent; color: var(--btn);
    font-size: 22px; padding: 0 4px; font-family: inherit;
  }
  #head.deep #back { display: block; }
  h1 { font-size: 17px; margin: 0; font-weight: 600; }
  #crumbs { font-size: 12px; color: var(--hint); margin: 0 0 10px; min-height: 15px; }
  .hint { font-size: 12px; color: var(--hint); margin: 0 0 14px; line-height: 1.45; }

  /* Menyu maydoni */
  #rows { position: relative; }
  #rows.slide-in  { animation: sin .22s ease; }
  #rows.slide-out { animation: sout .22s ease; }
  @keyframes sin  { from { transform: translateX(28px); opacity: .3 } to { transform: none; opacity: 1 } }
  @keyframes sout { from { transform: translateX(-28px); opacity: .3 } to { transform: none; opacity: 1 } }
  .row { display: flex; gap: 8px; margin-bottom: 8px; transition: transform .18s ease; }
  .row.merge-ok  { outline: 2px solid var(--btn); outline-offset: 3px; border-radius: 12px; }
  .row.merge-bad { outline: 2px solid #e0483e; outline-offset: 3px; border-radius: 12px; }
  .btn {
    position: relative; flex: 1 1 0; min-width: 0;
    padding: 14px 10px; border-radius: 10px;
    background: var(--secondary-bg); color: var(--text);
    font-size: 15px; text-align: center;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    transition: transform .18s ease, box-shadow .18s ease, opacity .18s ease;
    touch-action: pan-y;
  }
  .btn.nav::after { content: "›"; position: absolute; right: 10px; color: var(--hint); }
  .btn.cond { opacity: .62; }
  .btn.cond::before {
    content: "◌"; position: absolute; left: 9px; font-size: 12px; color: var(--hint);
  }
  .btn.placeholder { opacity: .28; }
  .ghost {
    position: fixed; z-index: 50; pointer-events: none;
    border-radius: 10px; padding: 14px 10px;
    background: var(--secondary-bg); color: var(--text);
    font-size: 15px; text-align: center;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    box-shadow: 0 10px 24px rgba(0,0,0,.28); transform: scale(1.06); opacity: .96;
  }
  .gapline { height: 3px; border-radius: 2px; background: var(--btn); margin: -5px 0 2px; }

  /* Yetim menyular */
  #orphans { margin-top: 22px; }
  #orphans h2 { font-size: 13px; color: var(--hint); font-weight: 500; margin: 0 0 8px; }
  #orphans .chip {
    display: inline-block; padding: 8px 12px; margin: 0 6px 6px 0;
    border-radius: 8px; background: var(--secondary-bg); font-size: 13px;
  }

  /* Toast */
  #toast {
    position: fixed; left: 50%; bottom: 110px; transform: translateX(-50%);
    background: rgba(0,0,0,.82); color: #fff; padding: 9px 14px;
    border-radius: 9px; font-size: 13px; max-width: 86%; text-align: center;
    opacity: 0; pointer-events: none; transition: opacity .2s ease; z-index: 60;
  }
  #toast.on { opacity: 1; }

  /* Pastki panel */
  #bar {
    position: fixed; left: 0; right: 0; bottom: 0;
    padding: 10px 12px calc(10px + env(safe-area-inset-bottom));
    background: var(--bg); border-top: 1px solid var(--secondary-bg);
    display: flex; gap: 8px;
  }
  #bar button {
    padding: 14px 8px; border: 0; border-radius: 10px;
    font-size: 14px; font-weight: 500; font-family: inherit;
  }
  #reset { flex: 1.15; background: var(--secondary-bg); color: var(--text); }
  #save  { flex: 1; background: var(--btn); color: var(--btn-text); }
  #save:disabled { opacity: .45; }
</style>
</head>
<body>

<div id="roles"></div>
<div id="head"><button id="back" type="button">‹</button><h1 id="title"></h1></div>
<p id="crumbs"></p>
<p class="hint">
  Tugmani <b>bosib ushlab</b> turing — surib joylashtirasiz.
  Oddiy bosish esa bo'limni ochadi (<b>›</b> belgili tugmalar).<br>
  <b>◌</b> — shartli tugma: botda faqat huquqi bor xodimga ko'rinadi.
</p>

<div id="rows"></div>
<div id="orphans"></div>
<div id="toast"></div>

<div id="bar">
  <button id="reset" type="button">♻️ Shu menyuni standartga</button>
  <button id="save" type="button" disabled>💾 Saqlash</button>
</div>

<script>
(function () {
  "use strict";
  var DATA = __DATA__;
  var tg = window.Telegram && window.Telegram.WebApp;

  if (tg) {
    tg.ready();
    tg.expand();
    var tp = tg.themeParams || {};
    var css = document.documentElement.style;
    var map = { bg_color:"--bg", text_color:"--text", hint_color:"--hint",
                button_color:"--btn", button_text_color:"--btn-text",
                secondary_bg_color:"--secondary-bg" };
    Object.keys(map).forEach(function (k) { if (tp[k]) css.setProperty(map[k], tp[k]); });
  }

  // ---- Holat ----
  // work[menuKey] — tahrirlanayotgan joylashuv (faqat o'zgargani saqlanadi)
  var work = {};
  var role = DATA.roots[0][0];
  var stack = [role];                       // navigatsiya steki
  var rowsEl = document.getElementById("rows");
  var toastEl = document.getElementById("toast");
  var saveBtn = document.getElementById("save");

  function cur() { return stack[stack.length - 1]; }
  function layoutOf(key) { return work[key] || DATA.menus[key].layout; }
  function changed() { return Object.keys(work); }

  function sameLayout(a, b) { return JSON.stringify(a) === JSON.stringify(b); }

  function setLayout(key, rows) {
    if (sameLayout(rows, DATA.menus[key].layout)) delete work[key];
    else work[key] = rows;
    refreshBar();
  }

  function refreshBar() {
    var n = changed().length;
    saveBtn.disabled = n === 0;
    saveBtn.textContent = n ? "💾 Saqlash (" + n + ")" : "💾 Saqlash";
  }

  var toastTimer = null;
  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add("on");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("on"); }, 1400);
  }

  // ---- Rol almashtirgich ----
  var rolesEl = document.getElementById("roles");
  DATA.roots.forEach(function (r) {
    var b = document.createElement("button");
    b.type = "button";
    b.textContent = r[1];
    b.dataset.key = r[0];
    b.addEventListener("click", function () {
      role = r[0];
      stack = [role];
      render("in");
    });
    rolesEl.appendChild(b);
  });

  // ---- Navigatsiya ----
  function go(key) {
    stack.push(key);
    render("in");
  }
  function back() {
    if (stack.length > 1) { stack.pop(); render("out"); }
  }
  document.getElementById("back").addEventListener("click", back);
  if (tg && tg.BackButton) {
    tg.BackButton.onClick(back);
  }

  function render(dir) {
    var key = cur();
    var menu = DATA.menus[key];
    var deep = stack.length > 1;

    document.getElementById("title").textContent = menu.title;
    document.getElementById("head").classList.toggle("deep", deep);
    document.getElementById("crumbs").textContent =
      stack.map(function (k) { return DATA.menus[k].title; }).join("  ›  ");
    document.getElementById("roles").style.display = deep ? "none" : "flex";
    Array.prototype.forEach.call(rolesEl.children, function (b) {
      b.classList.toggle("on", b.dataset.key === role);
    });
    if (tg && tg.BackButton) { deep ? tg.BackButton.show() : tg.BackButton.hide(); }

    rowsEl.innerHTML = "";
    layoutOf(key).forEach(function (row) {
      var r = document.createElement("div");
      r.className = "row";
      row.forEach(function (bk) {
        var b = document.createElement("div");
        b.className = "btn";
        if (menu.targets[bk]) b.classList.add("nav");
        if (menu.conditional.indexOf(bk) >= 0) b.classList.add("cond");
        b.dataset.key = bk;
        b.textContent = menu.buttons[bk] || bk;
        r.appendChild(b);
      });
      rowsEl.appendChild(r);
    });

    if (dir) {
      rowsEl.classList.remove("slide-in", "slide-out");
      void rowsEl.offsetWidth;                       // animatsiyani qayta ishga tushirish
      rowsEl.classList.add(dir === "out" ? "slide-out" : "slide-in");
    }
    renderOrphans(deep);
  }

  // Navigatsiya orqali ochilmaydigan menyular — faqat ildiz oynada
  function renderOrphans(deep) {
    var box = document.getElementById("orphans");
    box.innerHTML = "";
    if (deep || !DATA.orphans.length) return;
    var h = document.createElement("h2");
    h.textContent = "Alohida menyular (tugmasi boshqa menyuda yo'q)";
    box.appendChild(h);
    DATA.orphans.forEach(function (k) {
      var c = document.createElement("div");
      c.className = "chip";
      c.textContent = DATA.menus[k].title;
      c.addEventListener("click", function () { go(k); });
      box.appendChild(c);
    });
  }

  // ---- Joylashuvni o'zgartirish ----
  function applyDrop(key, btnKey, target) {
    // Tugmani chiqarib olamiz, bo'sh qatorlarni SAQLAYMIZ — indekslar surilmasin
    var rows = layoutOf(key).map(function (r) {
      return r.filter(function (k) { return k !== btnKey; });
    });
    if (target.type === "merge") {
      if (rows[target.index].length >= DATA.maxRow) return false;
      rows[target.index].push(btnKey);
    } else {
      rows.splice(target.index, 0, [btnKey]);
    }
    setLayout(key, rows.filter(function (r) { return r.length; }));
    return true;
  }

  // ---- Bosib-ushlab surish (Pointer Events) ----
  var HOLD_MS = 300, MOVE_TOL = 8;
  var timer = null, dragging = false, ghost = null, gapline = null;
  var srcBtn = null, srcKey = null, startX = 0, startY = 0, offX = 0, offY = 0;
  var target = null, moved = false;

  rowsEl.addEventListener("pointerdown", function (e) {
    var btn = e.target.closest(".btn");
    if (!btn || dragging) return;
    srcBtn = btn; srcKey = btn.dataset.key; moved = false;
    startX = e.clientX; startY = e.clientY;
    var rect = btn.getBoundingClientRect();
    offX = e.clientX - rect.left; offY = e.clientY - rect.top;
    timer = setTimeout(function () { startDrag(rect, e.pointerId); }, HOLD_MS);
  });

  function startDrag(rect, pointerId) {
    dragging = true; timer = null;
    if (tg && tg.HapticFeedback) tg.HapticFeedback.impactOccurred("medium");
    else if (navigator.vibrate) navigator.vibrate(10);
    document.body.style.touchAction = "none";
    document.body.style.overflow = "hidden";
    ghost = document.createElement("div");
    ghost.className = "ghost";
    ghost.textContent = srcBtn.textContent;
    ghost.style.width = rect.width + "px";
    ghost.style.left = rect.left + "px";
    ghost.style.top = rect.top + "px";
    document.body.appendChild(ghost);
    srcBtn.classList.add("placeholder");
    try { srcBtn.setPointerCapture(pointerId); } catch (err) {}
  }

  function clearMarks() {
    Array.prototype.forEach.call(rowsEl.querySelectorAll(".row"), function (r) {
      r.classList.remove("merge-ok", "merge-bad");
    });
    if (gapline) { gapline.remove(); gapline = null; }
  }

  function findTarget(y) {
    var rows = rowsEl.querySelectorAll(".row");
    for (var i = 0; i < rows.length; i++) {
      var r = rows[i].getBoundingClientRect();
      if (y < r.top) return { type: "gap", index: i };
      if (y <= r.bottom) {
        var edge = r.height * 0.25;
        if (y < r.top + edge) return { type: "gap", index: i };
        if (y > r.bottom - edge) return { type: "gap", index: i + 1 };
        return { type: "merge", index: i };
      }
    }
    return { type: "gap", index: rows.length };
  }

  function showTarget(t) {
    clearMarks();
    var rows = rowsEl.querySelectorAll(".row");
    if (t.type === "merge") {
      var row = rows[t.index];
      var busy = row.querySelectorAll(".btn:not(.placeholder)").length;
      row.classList.add(busy >= DATA.maxRow ? "merge-bad" : "merge-ok");
    } else {
      gapline = document.createElement("div");
      gapline.className = "gapline";
      if (t.index >= rows.length) rowsEl.appendChild(gapline);
      else rowsEl.insertBefore(gapline, rows[t.index]);
    }
  }

  document.addEventListener("pointermove", function (e) {
    if (timer && (Math.abs(e.clientX - startX) > MOVE_TOL ||
                  Math.abs(e.clientY - startY) > MOVE_TOL)) {
      clearTimeout(timer); timer = null; moved = true;   // skroll — surish emas
      return;
    }
    if (!dragging) return;
    e.preventDefault();
    ghost.style.left = (e.clientX - offX) + "px";
    ghost.style.top = (e.clientY - offY) + "px";
    target = findTarget(e.clientY);
    showTarget(target);
  }, { passive: false });

  function endDrag() {
    if (timer) { clearTimeout(timer); timer = null; }
    if (!dragging) {
      // Ushlab turilmadi va surilmadi => ODDIY BOSISH = navigatsiya
      if (srcBtn && !moved) {
        var menu = DATA.menus[cur()];
        var t = menu.targets[srcKey];
        if (t === "back") back();
        else if (t) go(t);
        else toast("Bu tugma bo'lim ochmaydi — surish uchun bosib ushlab turing");
      }
      srcBtn = null; srcKey = null;
      return;
    }
    dragging = false;
    document.body.style.touchAction = "";
    document.body.style.overflow = "";
    if (ghost) { ghost.remove(); ghost = null; }
    clearMarks();
    if (target) {
      var ok = applyDrop(cur(), srcKey, target);
      if (tg && tg.HapticFeedback) {
        tg.HapticFeedback.notificationOccurred(ok ? "success" : "error");
      }
      if (!ok) toast("Bir qatorda ko'pi bilan " + DATA.maxRow + " ta tugma");
    }
    target = null; srcBtn = null; srcKey = null;
    render();
  }

  document.addEventListener("pointerup", endDrag);
  document.addEventListener("pointercancel", endDrag);

  // ---- Pastki panel ----
  document.getElementById("reset").addEventListener("click", function () {
    var key = cur();
    setLayout(key, JSON.parse(JSON.stringify(DATA.menus[key].default)));
    render();
    toast("Standart tartib qaytarildi (saqlash uchun 💾 bosing)");
  });

  saveBtn.addEventListener("click", function () {
    var keys = changed();
    if (!keys.length) return;
    if (!tg || !tg.sendData) {
      alert("Bu sahifani Telegram bot menyusidagi tugma orqali oching.");
      return;
    }
    var payload = { layouts: {} };
    keys.forEach(function (k) { payload.layouts[k] = work[k]; });
    // Faqat kalitlar yuboriladi — yorliqlar emas (sendData chegarasi 4096 bayt)
    tg.sendData(JSON.stringify(payload));
  });

  render();
  refreshBar();
})();
</script>
</body>
</html>
"""
