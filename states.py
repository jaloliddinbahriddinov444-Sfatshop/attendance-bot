"""FSM holatlari"""
from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    waiting_full_name = State()
    waiting_phone = State()
    waiting_position = State()
    waiting_face_photo = State()


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
