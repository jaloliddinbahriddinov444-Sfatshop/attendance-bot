"""FSM holatlari"""
from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    waiting_full_name = State()
    waiting_phone = State()
    waiting_position = State()
    waiting_face_photo = State()
    # Phase 4 — admin oldindan qo'shgan xodimni bog'lash (stranger kontakt kutish)
    linking_phone = State()
    # Phase 4 — ro'yxatdan o'tish oxirida karta ma'lumotlari
    waiting_card_number = State()
    waiting_card_holder_name = State()


class AdminAddEmployee(StatesGroup):
    """Admin/Bosh Admin tomonidan xodimni oldindan qo'shish (Phase 4)."""
    waiting_name = State()
    waiting_phone = State()
    waiting_position = State()
    waiting_confirm = State()


class CardUpdate(StatesGroup):
    """Profil orqali karta ma'lumotlarini yangilash (Phase 4)."""
    waiting_number = State()
    waiting_holder_name = State()


class Attendance(StatesGroup):
    waiting_check_type = State()
    waiting_wifi_confirm = State()  # Wi-Fi havolasi tasdiqlashni kutish
    waiting_selfie = State()


class AdminPanel(StatesGroup):
    waiting_remove_choice = State()
    waiting_promote_choice = State()
    waiting_office_lat = State()
    waiting_office_lon = State()
    waiting_office_radius = State()
    waiting_office_wifi = State()
    waiting_work_start = State()
    waiting_work_end = State()
    waiting_att_time = State()
    waiting_hourly_rate = State()


class AdminSalary(StatesGroup):
    """Ish haqqi yozuvlarini boshqarish"""
    add_amount = State()
    add_reason = State()
    cancel_reason = State()


class TaskCreate(StatesGroup):
    """Admin/Boss tomonidan vazifa yaratish."""
    choosing_employee = State()
    entering_title = State()
    entering_description = State()
    entering_deadline = State()


class FinanceEntry(StatesGroup):
    """Boss/Bosh Admin moliya yozuvi."""
    entering_other_category = State()
    entering_amount = State()
    entering_note = State()
