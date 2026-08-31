#!/bin/bash
# Davomat boti — lokaldan serverga deploy (/opt/davomat).
#
#   ./deploy.sh check   — server bilan solishtirish (hech nima o'zgartirmaydi)
#   ./deploy.sh push    — zaxira olib, fayllarni yuborish va botni qayta ishga tushirish
#
# Serverda git YO'Q — deploy tar orqali. Baza (attendance.db) TEGILMAYDI.

set -euo pipefail

SRV="${SRV:-root@45.138.158.174}"
REMOTE_DIR="/opt/davomat"
cd "$(dirname "$0")"

# Shu ishda o'zgargan/yangi fayllar
FILES=(
  bot.py
  database.py
  keyboards.py
  texts.py
  services/reminders.py
  handlers/notifications.py
  test_notifications.py
  test_menu_parity.py
  test_menu_webapp.py
  test_payroll_roles.py
)

md5of() { md5 -q "$1" 2>/dev/null || md5sum "$1" | cut -d' ' -f1; }

cmd_check() {
  echo "🔍 Server bilan solishtirish — barcha .py fayllar"
  local remote_md5 farq=0
  remote_md5="$(ssh "$SRV" "cd $REMOTE_DIR && find . -name '*.py' -not -path './venv/*' -not -path './__pycache__/*' -not -path './docs/*' -exec md5sum {} +")"
  while read -r rhash rpath; do
    rpath="${rpath#./}"
    if [ ! -f "$rpath" ]; then
      echo "  ➖ faqat SERVERDA: $rpath"; farq=1; continue
    fi
    if [ "$(md5of "$rpath")" != "$rhash" ]; then
      echo "  ≠  FARQ: $rpath"; farq=1
    fi
  done <<< "$remote_md5"
  [ "$farq" = 0 ] && echo "✅ Server bilan sinxron." || \
    echo "⚠️  Yuqoridagi farqlarni tekshiring — serverda boshqa chatdan yangi kod bo'lishi mumkin!"
}

cmd_push() {
  echo "💾 1/4 Zaxira olinmoqda…"
  ssh "$SRV" "cd $REMOTE_DIR && mkdir -p backups && tar czf backups/pre-deploy-\$(date +%Y%m%d-%H%M%S).tgz *.py handlers services && ls -t backups | head -1"

  echo "📤 2/4 Fayllar yuborilmoqda…"
  tar czf - "${FILES[@]}" | ssh "$SRV" "cd $REMOTE_DIR && tar xzf -"

  echo "🧪 3/4 Sintaksis tekshiruvi…"
  ssh "$SRV" "cd $REMOTE_DIR && ./venv/bin/python -m py_compile ${FILES[*]} && echo OK"

  echo "🔄 4/4 Bot qayta ishga tushirilmoqda…"
  ssh "$SRV" "systemctl restart davomat && sleep 4 && systemctl is-active davomat && tail -n 15 /var/log/davomat.log"
  echo "✅ Deploy tugadi."
}

case "${1:-check}" in
  check) cmd_check ;;
  push)  cmd_push ;;
  *) echo "Foydalanish: ./deploy.sh [check|push]"; exit 1 ;;
esac
