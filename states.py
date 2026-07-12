"""FSM holatlari"""
from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    waiting_full_name = State()
    waiting_phone = State()
    waiting_position = State()
    waiting_face_photo = State()
    linking_phone = State()
    waiting_card_number = State()
    waiting_card_holder_name = State()


class AdminAddEmployee(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_position = State()
    waiting_confirm = State()


class CardUpdate(StatesGroup):
    waiting_number = State()
    waiting_holder_name = State()


class Attendance(StatesGroup):
    waiting_check_type = State()
    waiting_wifi_confirm = State()
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
    add_amount = State()
    add_reason = State()
    cancel_reason = State()


class TaskCreate(StatesGroup):
    choosing_employee = State()
    entering_title = State()
    entering_description = State()
    entering_deadline = State()


class FinanceEntry(StatesGroup):
    """Boss/Bosh Admin moliya yozuvi."""
    entering_other_category = State()
    selecting_employee = State()   # Avans uchun xodim tanlash (YANGI)
    entering_amount = State()
    entering_note = State()
    entering_date = State()        # Sana tanlash: bugun yoki qo'lda


class FinanceDelete(StatesGroup):
    """Moliya yozuvini sana orqali o'chirish."""
    entering_date = State()


class PositionManage(StatesGroup):
    waiting_name = State()
    waiting_work_hours = State()
    waiting_min_rate = State()
    waiting_max_rate = State()
    edit_choose_field = State()
    edit_value = State()


class EmployeePositionSet(StatesGroup):
    choose_employee = State()
    choose_position = State()
    enter_daily_rate = State()


class EmpRateChange(StatesGroup):
    enter_rate = State()


class PersonalFinance(StatesGroup):
    choosing_category = State()
    entering_amount = State()
    entering_note = State()
    entering_date = State()
    deleting = State()


class CategoryManage(StatesGroup):
    entering_name = State()


class Broadcast(StatesGroup):
    target = State()
    choosing_employee = State()
    content_type = State()
    entering_text = State()
    waiting_media = State()
    poll_question = State()
    poll_options = State()
    confirming = State()
    setup_chat = State()
