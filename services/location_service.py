"""Lokatsiya xizmati - ikki nuqta orasidagi masofa (metr)"""
from math import radians, sin, cos, asin, sqrt


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Ikki GPS nuqtasi orasidagi masofani metrlarda qaytaradi.
    Haversine formulasidan foydalanadi.
    """
    R = 6371000.0  # Yer radiusi (metr)
    lat1r, lat2r = radians(lat1), radians(lat2)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(lat1r) * cos(lat2r) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


def is_within_office(user_lat: float, user_lon: float,
                     office_lat: float, office_lon: float,
                     radius_m: float) -> tuple[bool, float]:
    """
    Foydalanuvchi ishxonada ekanligini tekshiradi.
    Qaytaradi: (mos_keladi, hisoblangan_masofa_metr)
    """
    distance = haversine_distance(user_lat, user_lon, office_lat, office_lon)
    return distance <= radius_m, distance
