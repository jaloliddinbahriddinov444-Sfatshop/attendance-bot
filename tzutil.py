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


def to_local(ts) -> datetime:
    """Bazadagi UTC qiymatni (str yoki datetime) Toshkent mahalliy vaqtiga aylantiradi."""
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts)
    return ts + OFFSET


def fmt(ts, pattern: str = "%H:%M") -> str:
    """UTC qiymatni mahalliy ko'rinishda formatlaydi."""
    return to_local(ts).strftime(pattern)
