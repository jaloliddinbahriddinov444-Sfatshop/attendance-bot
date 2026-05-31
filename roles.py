"""Foydalanuvchi rollari va asosiy predicatelar.

Konventsiya:
  - employee  : oddiy xodim
  - admin     : admin (kundalik boshqaruv)
  - boss      : Boss (operativ qarorlar, Bosh Admin tasdig'i bilan)
  - bosh_admin: Bosh Admin (egasi, oxirgi tasdiqlovchi). Faqat 1 ta bo'ladi.

Eski 'is_admin' DB ustuni mosligi: rollar tizimi joriy etilgandan keyin ham
saqlanadi (admin va bosh_admin uchun is_admin=1). Shu sabab eski kod buzilmaydi.
"""

ROLE_EMPLOYEE   = "employee"
ROLE_ADMIN      = "admin"
ROLE_BOSS       = "boss"
ROLE_BOSH_ADMIN = "bosh_admin"

ALL_ROLES = (ROLE_EMPLOYEE, ROLE_ADMIN, ROLE_BOSS, ROLE_BOSH_ADMIN)


def get_role(employee) -> str:
    """Xodim obyektidan rolni xavfsiz olish (eski yozuvlar uchun ham)."""
    if employee is None:
        return ROLE_EMPLOYEE
    try:
        role = employee["role"]
    except (KeyError, IndexError):
        role = None
    return role if role else ROLE_EMPLOYEE


def is_bosh_admin(employee) -> bool:
    return get_role(employee) == ROLE_BOSH_ADMIN


def is_boss(employee) -> bool:
    return get_role(employee) == ROLE_BOSS


def is_admin(employee) -> bool:
    """Admin yoki Bosh Admin (admin-darajadagi huquqlar)."""
    return get_role(employee) in (ROLE_ADMIN, ROLE_BOSH_ADMIN)


def can_assign_tasks(employee) -> bool:
    """Vazifa bera oladigan rollar: Bosh Admin, Boss, Admin."""
    return get_role(employee) in (ROLE_ADMIN, ROLE_BOSS, ROLE_BOSH_ADMIN)


def is_elevated(employee) -> bool:
    """Xodimdan boshqa har qanday rol."""
    return get_role(employee) != ROLE_EMPLOYEE
