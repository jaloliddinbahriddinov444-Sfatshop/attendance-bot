"""Markaziy vaqt mintaqasi yordamchisi — O'zbekiston (Asia/Tashkent, UTC+5, DST yo'q).

KONVENTSIYA:
  - Bazada (SQLite) BARCHA vaqtlar UTC da saqlanadi (datetime('now')).
  - Ko'rsatish va oy/kun bo'yicha guruhlashda +5 soat qo'shib
    mahalliy (Toshkent) vaqtga aylantiriladi.

Shu sabab Render (UTC server) ham, Mac (mahalliy) ham bir xil natija beradi.
"""
from datetime import datetime, timedelta, timezone

# Asia/Tashkent doimiy UTC+5 (yozgi vaqt yo'q)
OFFSET = timedelta(hours=5)


def _utcnow() -> datetime:
    """Naive UTC vaqti (deprecation ogohlantirishisiz)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def now() -> datetime:
    """Hozirgi Toshkent mahalliy vaqti (naive datetime)."""
    return _utcnow() + OFFSET


def last_months(count: int = 6):
    """Oxirgi `count` oy, joriy oydan boshlab: [(yil, oy), ...] (Toshkent vaqti)."""
    d = now()
    y, m = d.year, d.month
    out = []
    for _ in range(count):
        out.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return out


def prev_month(year: int, month: int) -> tuple[int, int]:
    """Oldingi oy (yil, oy) juftligini qaytaradi."""
    return (year - 1, 12) if month == 1 else (year, month - 1)


def next_month(year: int, month: int) -> tuple[int, int]:
    """Keyingi oy (yil, oy) juftligini qaytaradi."""
    return (year + 1, 1) if month == 12 else (year, month + 1)


def months_back(year: int, month: int, n: int) -> tuple[int, int]:
    """n oy orqadagi (yil, oy)."""
    total = year * 12 + (month - 1) - n
    return total // 12, total % 12 + 1


# Hisobot navigatsiyasida orqaga ruxsat etilgan maksimal oy soni
NAV_BACK = 6


def nav_ym(data: str) -> tuple[int, int]:
    """"{prefix}:{yil}:{oy}" callbackdan (yil, oy) ni oladi.

    Xato format yoki chegaradan tashqarida (NAV_BACK oydan eski / kelajak)
    bo'lsa — jimgina joriy oy qaytariladi.
    """
    d = now()
    try:
        _, y, m = data.split(":")
        y, m = int(y), int(m)
    except ValueError:
        return d.year, d.month
    cur = d.year * 12 + d.month - 1
    v = y * 12 + m - 1
    if not (1 <= m <= 12) or not (cur - NAV_BACK <= v <= cur):
        return d.year, d.month
    return y, m


def to_local(ts) -> datetime:
    """Bazadagi UTC qiymatni (str yoki datetime) Toshkent mahalliy vaqtiga aylantiradi."""
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts)
    return ts + OFFSET


def fmt(ts, pattern: str = "%H:%M") -> str:
    """UTC qiymatni mahalliy ko'rinishda formatlaydi."""
    return to_local(ts).strftime(pattern)
