"""Refaktordan keyin har menyu AYNAN eski tartibda chiqayotganini tekshirish.
Kutilgan tartib qo'lda, eski koddan ko'chirilgan."""
import os, shutil, sys, tempfile
TMP = tempfile.mkdtemp(); os.environ["DB_PATH"] = os.path.join(TMP, "t.db")
sys.path.insert(0, "/Users/jb89/Desktop/attendance_bot")
import database as db; db.init_db()
import texts as t, keyboards as kb

def rows(k):
    return [[b.text for b in r] for r in k.keyboard]

KUTILGAN = {
 "main_employee(oddiy)": (kb.main_menu_kb(), [
    [t.BTN_ATTENDANCE], [t.BTN_PROFILE, t.BTN_STATS], [t.BTN_TASKS, t.BTN_SALARY]]),
 "main_employee(admin)": (kb.main_menu_kb(is_admin=True), [
    [t.BTN_ATTENDANCE], [t.BTN_PROFILE, t.BTN_STATS], [t.BTN_TASKS, t.BTN_SALARY],
    [t.BTN_ADMIN]]),
 "main_employee(pf)": (kb.main_menu_kb(has_pf=True), [
    [t.BTN_ATTENDANCE], [t.BTN_PROFILE, t.BTN_STATS], [t.BTN_TASKS, t.BTN_SALARY],
    [t.BTN_PERSONAL_FINANCE]]),
 "main_boss": (kb.main_menu_kb(is_boss=True), [
    [t.BTN_BOSS_ATTENDANCE], [t.BTN_ADMIN_TASKS, t.BTN_BOSS_FINANCE]]),
 "main_bosh_admin": (kb.main_menu_kb(is_bosh_admin=True), [
    [t.BTN_BOSS_FINANCE], [t.BTN_ATTENDANCE], [t.BTN_PROFILE, t.BTN_STATS],
    [t.BTN_TASKS, t.BTN_SALARY], [t.BTN_ADMIN]]),
 "admin_panel_bosh": (kb.admin_menu_kb(is_bosh_admin=True), [
    [t.BTN_GRP_EMPLOYEES, t.BTN_GRP_ATTENDANCE], [t.BTN_ADMIN_TASKS],
    [t.BTN_GRP_CONTROL], [t.BTN_BACK]]),
 "admin_panel": (kb.admin_menu_kb(), [
    [t.BTN_ADMIN_ADD_EMPLOYEE], [t.BTN_ADMIN_LIST, t.BTN_ADMIN_TODAY],
    [t.BTN_ADMIN_ATT_EDIT, t.BTN_ADMIN_RATES], [t.BTN_FIX_REQUESTS_ADMIN],
    [t.BTN_ADMIN_SALARY, t.BTN_ADMIN_TASKS],
    [t.BTN_ADMIN_EXPORT, t.BTN_ADMIN_EMP_EXCEL],
    [t.BTN_ADMIN_REMOVE, t.BTN_ADMIN_PROMOTE], [t.BTN_ADMIN_SETTINGS], [t.BTN_BACK]]),
 "grp_employees": (kb.grp_employees_kb(), [
    [t.BTN_ADMIN_LIST, t.BTN_ADMIN_EMP_EXCEL],
    [t.BTN_ADMIN_ADD_EMPLOYEE, t.BTN_ADMIN_REMOVE],
    [t.BTN_SET_POSITION, t.BTN_ADMIN_SALARY], [t.BTN_ADMIN_BACK]]),
 "grp_attendance": (kb.grp_attendance_kb(), [
    [t.BTN_ADMIN_TODAY], [t.BTN_ADMIN_ATT_EDIT], [t.BTN_FIX_REQUESTS_ADMIN],
    [t.BTN_ADMIN_BACK]]),
 "grp_finance": (kb.grp_finance_kb(), [[t.BTN_ADMIN_SALARY], [t.BTN_ADMIN_BACK]]),
 "grp_control": (kb.grp_control_kb(), [
    [t.BTN_ADMIN_SETTINGS], [t.BTN_WEB_DASHBOARD, t.BTN_REMINDERS],
    [t.BTN_OFFICE_IP], [t.BTN_POSITIONS, t.BTN_FINANCE_CATEGORIES],
    [t.BTN_ADMIN_PROMOTE, t.BTN_ADMIN_BOSS_ASSIGN], [t.BTN_ADMIN_PF_ACCESS],
    [t.BTN_MENU_LAYOUT], [t.BTN_BROADCAST], [t.BTN_ADMIN_BACK]]),
 "admin_settings": (kb.admin_settings_kb(), [[t.BTN_SET_HOURS], [t.BTN_BACK]]),
 "ip_menu": (kb.ip_menu_kb(), [
    [t.BTN_OFFICE_IP_ADD], [t.BTN_OFFICE_IP_LIST], [t.BTN_OFFICE_BEACON], [t.BTN_BACK]]),
 "boss_panel": (kb.boss_panel_kb(), [
    [t.BTN_BOSS_ATTENDANCE], [t.BTN_ADMIN_TASKS, t.BTN_BOSS_FINANCE],
    [t.BTN_BROADCAST], [t.BTN_BACK]]),
 "finance_menu": (kb.finance_menu_kb(), [
    [t.BTN_FINANCE_INCOME, t.BTN_FINANCE_EXPENSE],
    [t.BTN_FINANCE_SUMMARY, t.BTN_FINANCE_EXCEL], [t.BTN_FINANCE_DELETE],
    [t.BTN_FINANCE_ARCHIVE], [t.BTN_FINANCE_CATEGORIES],
    [t.BTN_PERSONAL_FINANCE], [t.BTN_BACK]]),
 "pf_menu": (kb.pf_menu_kb(), [
    [t.BTN_PF_INCOME, t.BTN_PF_EXPENSE], [t.BTN_PF_SUMMARY, t.BTN_PF_EXCEL],
    [t.BTN_PF_DELETE], [t.BTN_PF_ARCHIVE], [t.BTN_PF_CATEGORIES], [t.BTN_BACK]]),
 "pf_menu(moliyadan)": (kb.pf_menu_kb(from_finance=True), [
    [t.BTN_PF_INCOME, t.BTN_PF_EXPENSE], [t.BTN_PF_SUMMARY, t.BTN_PF_EXCEL],
    [t.BTN_PF_DELETE], [t.BTN_PF_ARCHIVE], [t.BTN_PF_CATEGORIES],
    [t.BTN_PF_BACK_FINANCE]]),
}
xato = 0
for nom, (got_kb, kutilgan) in KUTILGAN.items():
    got = rows(got_kb)
    if got == kutilgan:
        print(f"  ✅ {nom}")
    else:
        xato += 1
        print(f"  ❌ {nom}\n     olindi:   {got}\n     kutilgan: {kutilgan}")
shutil.rmtree(TMP)
print("✅ HAMMA MENYU AYNAN ESKIDEK" if not xato else f"❌ {xato} ta menyu FARQ QILDI")
sys.exit(1 if xato else 0)
