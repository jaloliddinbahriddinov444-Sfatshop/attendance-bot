"""Turkum kalitlarini (standart + maxsus 'c{id}') emoji/nomga yechish."""
import re

import texts
from database import get_custom_category_by_id

_CUSTOM_RE = re.compile(r"^c(\d+)$")


def custom_id(key) -> int | None:
    """'c7' -> 7, aks holda None."""
    m = _CUSTOM_RE.match(key or "")
    return int(m.group(1)) if m else None


def resolve_category(key: str, scope: str = "fin") -> tuple:
    """(emoji, nom) qaytaradi.

    scope: 'fin' -> texts.FINANCE_CATEGORIES, 'pf' -> texts.PF_ALL_CATS.
    Standart lug'atda topilmasa 'c{id}' bo'yicha custom_categories'dan
    (is_active'dan qat'i nazar — eski yozuvlar nomi saqlanishi uchun),
    u ham topilmasa ("📋", key).
    """
    cats = texts.FINANCE_CATEGORIES if scope == "fin" else texts.PF_ALL_CATS
    if key in cats:
        return cats[key]
    cid = custom_id(key)
    if cid is not None:
        row = get_custom_category_by_id(cid)
        if row:
            return (row["emoji"] or "🏷", row["name"])
    return ("📋", key)
