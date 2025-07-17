import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import calendar
from io import BytesIO
import re
import pytz

# --- Page Configuration ---
st.set_page_config(
    page_title="🌍 INTERSOFT Global Task Tracker",
    layout="wide",
    page_icon="🌐",
    initial_sidebar_state="expanded"
)

# --- Dark Theme Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        background: linear-gradient(135deg, #1f2937, #111827);
        color: #e5e7eb;
    }

    .sidebar .sidebar-content {
        background: #111827;
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
    }

    .sidebar .stButton>button {
        width: 100%;
        background: #2dd4bf;
        color: #ffffff;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .sidebar .stButton>button:hover {
        background: #26a69a;
        transform: translateY(-2px);
    }

    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background: #374151;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        border-radius: 12px;
        margin: 1rem;
    }

    .company {
        font-size: 1.4rem;
        font-weight: 700;
        color: #e5e7eb;
    }

    .greeting {
        font-size: 1rem;
        font-weight: 500;
        color: #2dd4bf;
        text-align: right;
    }

    .date-box {
        font-size: 0.9rem;
        font-weight: 500;
        color: #ffffff;
        background: #2dd4bf;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 1rem auto;
        display: inline-block;
    }

    .overview-box {
        background: #374151;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .overview-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    }

    .overview-box span {
        font-size: 2rem;
        font-weight: 600;
        color: #2dd4bf;
    }

    .stButton>button {
        background: #2dd4bf;
        color: #ffffff;
        font-weight: 500;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        border: none;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background: #26a69a;
        transform: scale(1.05);
    }

    .stForm {
        background: #374151;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        margin: 1rem 0;
    }

    .stTextInput>div>input, .stSelectbox>div>select {
        background: #4b5563;
        color: #e5e7eb;
        border: 1px solid #6b7280;
        border-radius: 8px;
        padding: 0.5rem;
    }

    .stTextInput>label, .stSelectbox>label {
        color: #e5e7eb;
        font-weight: 500;
    }

    .stTabs [role="tab"] {
        background: #374151;
        color: #e5e7eb;
        border-radius: 8px 8px 0 0;
        padding: 0.8rem 1.2rem;
        margin-right: 0.5rem;
        transition: all 0.3s ease;
    }

    .stTabs [role="tab"][aria-selected="true"] {
        background: #2dd4bf;
        color: #ffffff;
    }

    footer {
        text-align: center;
        color: #9ca3af;
        padding: 2rem 0;
        font-size: 0.9rem;
    }

    .footer-links a {
        color: #2dd4bf;
        text-decoration: none;
        margin: 0 1rem;
        font-weight: 500;
    }

    .footer-links a:hover {
        text-decoration: underline;
    }

    .profile-img {
        border-radius: 50%;
        width: 100px;
        height: 100px;
        object-fit: cover;
        margin-bottom: 1rem;
        border: 2px solid #2dd4bf;
    }
    </style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.users = {
        "Yaman": {"password": "YAMAN1", "role": "Employee", "email": "yaman@intersoft.com", "full_name": "Yaman Ali", "phone": "+1234567890", "department": "FLM", "profile_picture": "https://via.placeholder.com/100", "timezone": "UTC"},
        "Hatem": {"password": "HATEM2", "role": "Employee", "email": "hatem@intersoft.com", "full_name": "Hatem Mohamed", "phone": "+1234567891", "department": "Tech Support", "profile_picture": "https://via.placeholder.com/100", "timezone": "UTC"},
        "Mahmoud": {"password": "MAHMOUD3", "role": "Employee", "email": "mahmoud@intersoft.com", "full_name": "Mahmoud Ahmed", "phone": "+1234567892", "department": "CRM", "profile_picture": "https://via.placeholder.com/100", "timezone": "UTC"},
        "Qusai": {"password": "QUSAI4", "role": "Manager", "email": "qusai@intersoft.com", "full_name": "Qusai Hassan", "phone": "+1234567893", "department": "FLM", "profile_picture": "https://via.placeholder.com/100", "timezone": "UTC"}
    }
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "Login"
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

# --- Constants ---
SHIFTS = ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"]
CATEGORIES = ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM", "📅 Meetings", "💻 TOMS"]
PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]
ROLES = ["Employee", "Manager"]
DEPARTMENTS = ["FLM", "Tech Support", "CRM"]
TIMEZONES = ["UTC", "America/New_York", "Europe/London", "Asia/Dubai", "Asia/Tokyo"]

# --- Authentication Functions ---
def check_login(username, password):
    return st.session_state.users.get(username, {}).get("password") == password

def register_user(username, password, confirm_password, role, email, full_name, phone, department, profile_picture, timezone):
    if username in st.session_state.users:
        return False, "اسم المستخدم موجود بالفعل!"
    if not all([username, password, confirm_password, role, email, full_name, phone, department, timezone]):
        return False, "جميع الحقول مطلوبة!"
    if password != confirm_password:
        return False, "كلمات المرور غير متطابقة!"
    if len(password) < 8:
        return False, "كلمة المرور يجب أن تكون 8 أحرف على الأقل!"
    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$", password):
        return False, "كلمة المرور يجب أن تحتوي على حرف كبير، حرف صغير، ورقم!"
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "صيغة البريد الإلكتروني غير صحيحة!"
    if not re.match(r"\+?\d{10,15}", phone):
        return False, "صيغة رقم الهاتف غير صحيحة (مثال: +1234567890)!"
    st.session_state.users[username] = {
        "password": password,
        "role": role,
        "email": email,
        "full_name": full_name,
        "phone": phone,
        "department": department,
        "profile_picture": profile_picture or "https://via.placeholder.com/100",
        "timezone": timezone
    }
    return True, "تم التسجيل بنجاح!"

def update_user(username, full_name, email, phone, department, profile_picture, timezone, new_password, confirm_password):
    if not all([full_name, email, phone, department, timezone]):
        return False, "جميع الحقول مطلوبة!"
    if new_password and new_password != confirm_password:
        return False, "كلمات المرور غير متطابقة!"
    if new_password and len(new_password) < 8:
        return False, "كلمة المرور الجديدة يجب أن تكون 8 أحرف على الأقل!"
    if new_password and not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$", new_password):
        return False, "كلمة المرور الجديدة يجب أن تحتوي على حرف كبير، حرف صغير، ورقم!"
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "صيغة البريد الإلكتروني غير صحيحة!"
    if not re.match(r"\+?\d{10,15}", phone):
        return False, "صيغة رقم الهاتف غير صحيحة (مثال: +1234567890)!"
    user = st.session_state.users[username]
    user["full_name"] = full_name
    user["email"] = email
    user["phone"] = phone
    user["department"] = department
    user["profile_picture"] = profile_picture or user["profile_picture"]
    user["timezone"] = timezone
    if new_password:
        user["password"] = new_password
    return True, "تم تحديث الملف الشخصي بنجاح!"

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("<div class='company'>INTERSOFT<br>Global Task Tracker</div>", unsafe_allow_html=True)
    if st.session_state.logged_in:
        user_info = st.session_state.users.get(st.session_state.user_role, {})
        st.markdown(f"<div class='greeting'>👤 {user_info.get('full_name', 'User')}</div>", unsafe_allow_html=True)
        if st.button("🏠 الرئيسية", key="nav_dashboard"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        if st.button("🔓 تسجيل الخروج", key="nav_logout"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.current_page = "Login"
            st.rerun()
    else:
        if st.button("🔐 تسجيل الدخول", key="nav_login"):
            st.session_state.current_page = "Login"
            st.rerun()
        if st.button("📝 التسجيل", key="nav_register"):
            st.session_state.current_page = "Register"
            st.rerun()

# --- Pages ---
def login_page():
    user_tz = pytz.timezone('Asia/Dubai')  # Use Asia/Dubai as requested time zone
    st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>Global Task Tracker</div><div class='greeting'>🔐 تسجيل الدخول إلى حسابك</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='date-box'>📅 {datetime.now(user_tz).strftime('%A, %B %d, %Y - %I:%M %p')}</div>", unsafe_allow_html=True)
    
    st.subheader("🔐 تسجيل الدخول")
    with st.form("login_form"):
        username = st.text_input("👤 اسم المستخدم", placeholder="أدخل اسم المستخدم")
        password = st.text_input("🔑 كلمة المرور", type="password", placeholder="أدخل كلمة المرور")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.form_submit_button("تسجيل الدخول 🚀"):
                if check_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.user_role = username
                    st.session_state.current_page = "Dashboard"
                    st.rerun()
                else:
                    st.error("❌ بيانات الاعتماد غير صحيحة")
        with col2:
            if st.form_submit_button("نسيت كلمة المرور 🔧"):
                st.info("ℹ️ تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني (محاكاة).")

def register_page():
    user_tz = pytz.timezone('Asia/Dubai')
    st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>Global Task Tracker</div><div class='greeting'>📝 إنشاء حسابك</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='date-box'>📅 {datetime.now(user_tz).strftime('%A, %B %d, %Y - %I:%M %p')}</div>", unsafe_allow_html=True)
    
    st.subheader("📝 التسجيل")
    with st.form("register_form"):
        st.markdown("### المعلومات الشخصية")
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("🧑 الاسم الكامل", placeholder="أدخل اسمك الكامل")
            email = st.text_input("📧 البريد الإلكتروني", placeholder="أدخل بريدك الإلكتروني")
            phone = st.text_input("📱 رقم الهاتف", placeholder="مثال: +1234567890")
        with col2:
            username = st.text_input("👤 اسم المستخدم", placeholder="اختر اسم مستخدم")
            role = st.selectbox("👷 الدور", ROLES, format_func=lambda x: "موظف" if x == "Employee" else "مدير")
            department = st.selectbox("🏢 القسم", DEPARTMENTS, format_func=lambda x: x)
        
        st.markdown("### أمان الحساب")
        col3, col4 = st.columns(2)
        with col3:
            password = st.text_input("🔑 كلمة المرور", type="password", placeholder="أنشئ كلمة مرور")
        with col4:
            confirm_password = st.text_input("🔑 تأكيد كلمة المرور", type="password", placeholder="أكد كلمة المرور")
        
        profile_picture = st.text_input("🖼 رابط صورة الملف الشخصي", placeholder="اختياري: أدخل رابط الصورة")
        timezone = st.selectbox("🌐 المنطقة الزمنية", TIMEZONES)
        
        col5, col6 = st.columns([1, 1])
        with col5:
            if st.form_submit_button("التسجيل 🌟"):
                success, message = register_user(
                    username, password, confirm_password, role, email, full_name, phone, department, profile_picture, timezone
                )
                if success:
                    st.success(message)
                    st.session_state.current_page = "Login"
                    st.rerun()
                else:
                    st.error(message)
        with col6:
            if st.form_submit_button("العودة إلى تسجيل الدخول 🔙"):
                st.session_state.current_page = "Login"
                st.rerun()

def dashboard_page():
    user_info = st.session_state.users.get(st.session_state.user_role, {})
    user_tz = pytz.timezone(user_info.get('timezone', 'Asia/Dubai'))
    st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>Global Task Tracker</div><div class='greeting'>👋 مرحبًا، <b>{}</b><br><small>إدارة المهام، تتبع التقدم، والبقاء منظمًا!</small></div></div>".format(user_info.get('full_name', 'User')), unsafe_allow_html=True)
    st.markdown(f"<div class='date-box'>📅 {datetime.now(user_tz).strftime('%A, %B %d, %Y - %I:%M %p')}</div>", unsafe_allow_html=True)

    # --- Dashboard Overview (Moved to Top) ---
    df = pd.DataFrame(st.session_state.timesheet)
    df_user = df[df['Employee'] == user_info.get('full_name')] if not df.empty else pd.DataFrame()
    total_tasks = len(df_user)
    completed_tasks = df_user[df_user['Status'] == '✅ Completed'].shape[0] if not df_user.empty else 0
    in_progress_tasks = df_user[df_user['Status'] == '🔄 In Progress'].shape[0] if not df_user.empty else 0
    not_started_tasks = df_user[df_user['Status'] == '⏳ Not Started'].shape[0] if not df_user.empty else 0

    st.markdown("### 📊 نظرة عامة")
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"<div class='overview-box'>إجمالي المهام<br><span>{total_tasks}</span></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='overview-box'>المهام المكتملة<br><span>{completed_tasks}</span></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='overview-box'>قيد التنفيذ<br><span>{in_progress_tasks}</span></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='overview-box'>لم تبدأ<br><span>{not_started_tasks}</span></div>", unsafe_allow_html=True)

    # --- Tabs ---
    tab1, tab2, tab3, tab4 = st.tabs(["➕ إضافة مهمة", "📈 التحليلات", "👤 الملف الشخصي", "⚙️ الإعدادات"])

    # --- Add Task ---
    with tab1:
        st.subheader("📝 إضافة مهمة جديدة")
        with st.form("task_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                shift = st.selectbox("🕒 الوردية", SHIFTS, format_func=lambda x: "الصباح (8:30 - 5:30)" if x == SHIFTS[0] else "المساء (3:00 - 11:00)")
                date = st.date_input("📅 التاريخ", value=datetime.today())
                department = st.selectbox("🏢 القسم", DEPARTMENTS, format_func=lambda x: x)
            with col2:
                cat = st.selectbox("📂 الفئة", CATEGORIES, format_func=lambda x: x[2:])
                stat = st.selectbox("📌 الحالة", STATUSES, format_func=lambda x: x[2:])
                prio = st.selectbox("⚠️ الأولوية", PRIORITIES, format_func=lambda x: x[2:])
            desc = st.text_area("🗒 وصف المهمة", height=100, placeholder="صف المهمة...")
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn1:
                submitted = st.form_submit_button("✅ إرسال المهمة")
            with col_btn2:
                clear_form = st.form_submit_button("🔄 إعادة تعيين النموذج")
            with col_btn3:
                clear_all = st.form_submit_button("🧹 مسح جميع المهام")
            if submitted:
                st.session_state.timesheet.append({
                    "Employee": user_info.get('full_name'),
                    "Date": date.strftime('%Y-%m-%d'),
                    "Day": calendar.day_name[date.weekday()],
                    "Shift": shift,
                    "Department": department,
                    "Category": cat,
                    "Status": stat,
                    "Priority": prio,
                    "Description": desc,
                    "Submitted": datetime.now(user_tz).strftime('%Y-%m-%d %H:%M:%S')
                })
                st.success("🎉 تم إضافة المهمة بنجاح!")
            if clear_form:
                st.rerun()
            if clear_all:
                if st.checkbox("تأكيد مسح جميع المهام"):
                    st.session_state.timesheet = []
                    st.warning("🧹 تم مسح جميع المهام!")
                    st.rerun()

        # --- Task Management ---
        if not df_user.empty:
            st.markdown("### 📋 إدارة المهام")
            task_filter = st.selectbox("تصفية المهام", ["الكل", "لم تبدأ", "قيد التنفيذ", "مكتملة"], format_func=lambda x: x)
            date_filter = st.date_input("تصفية حسب نطاق التاريخ", value=(datetime.today() - timedelta(days=30), datetime.today()))
            filtered_df = df_user
            if task_filter != "الكل":
                filtered_df = filtered_df[filtered_df['Status'] == f"{'⏳ Not Started' if task_filter == 'لم تبدأ' else '🔄 In Progress' if task_filter == 'قيد التنفيذ' else '✅ Completed'}"]
            filtered_df = filtered_df[(filtered_df['Date'] >= date_filter[0].strftime('%Y-%m-%d')) & (filtered_df['Date'] <= date_filter[1].strftime('%Y-%m-%d'))]
            st.dataframe(filtered_df)

            # Task Editing/Deletion
            if not filtered_df.empty:
                task_index = st.selectbox("اختر مهمة للتعديل/الحذف", filtered_df.index, format_func=lambda x: filtered_df.loc[x, 'Description'][:50])
                with st.form("edit_task_form"):
                    edit_shift = st.selectbox("🕒 الوردية", SHIFTS, index=SHIFTS.index(filtered_df.loc[task_index, 'Shift']), format_func=lambda x: "الصباح (8:30 - 5:30)" if x == SHIFTS[0] else "المساء (3:00 - 11:00)")
                    edit_date = st.date_input("📅 التاريخ", value=pd.to_datetime(filtered_df.loc[task_index, 'Date']))
                    edit_department = st.selectbox("🏢 القسم", DEPARTMENTS, index=DEPARTMENTS.index(filtered_df.loc[task_index, 'Department']), format_func=lambda x: x)
                    edit_cat = st.selectbox("📂 الفئة", CATEGORIES, index=CATEGORIES.index(filtered_df.loc[task_index, 'Category']), format_func=lambda x: x[2:])
                    edit_stat = st.selectbox("📌 الحالة", STATUSES, index=STATUSES.index(filtered_df.loc[task_index, 'Status']), format_func=lambda x: x[2:])
                    edit_prio = st.selectbox("⚠️ الأولوية", PRIORITIES, index=PRIORITIES.index(filtered_df.loc[task_index, 'Priority']), format_func=lambda x: x[2:])
                    edit_desc = st.text_area("🗒 وصف المهمة", value=filtered_df.loc[task_index, 'Description'], height=100)
                    col_edit, col_delete = st.columns(2)
                    with col_edit:
                        if st.form_submit_button("💾 تحديث المهمة"):
                            st.session_state.timesheet[task_index] = {
                                "Employee": user_info.get('full_name'),
                                "Date": edit_date.strftime('%Y-%m-%d'),
                                "Day": calendar.day_name[edit_date.weekday()],
                                "Shift": edit_shift,
                                "Department": edit_department,
                                "Category": edit_cat,
                                "Status": edit_stat,
                                "Priority": edit_prio,
                                "Description": edit_desc,
                                "Submitted": datetime.now(user_tz).strftime('%Y-%m-%d %H:%M:%S')
                            }
                            st.success("✅ تم تحديث المهمة بنجاح!")
                            st.rerun()
                    with col_delete:
                        if st.form_submit_button("🗑 حذف المهمة"):
                            st.session_state.timesheet.pop(task_index)
                            st.warning("🗑 تم حذف المهمة!")
                            st.rerun()

    # --- Analytics ---
    with tab2:
        if not df_user.empty:
            st.subheader("📊 تحليل المهام")
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                date_range = st.date_input("نطاق التاريخ", value=(datetime.today() - timedelta(days=30), datetime.today()))
            with col_filter2:
                dept_filter = st.multiselect("تصفية القسم", DEPARTMENTS, default=DEPARTMENTS, format_func=lambda x: x)
            filtered_df = df_user[
                (df_user['Date'] >= date_range[0].strftime('%Y-%m-%d')) &
                (df_user['Date'] <= date_range[1].strftime('%Y-%m-%d')) &
                (df_user['Department'].isin(dept_filter))
            ]
            if not filtered_df.empty:
                st.plotly_chart(px.histogram(filtered_df, x="Date", color="Status", barmode="group", title="المهام عبر الزمن"), use_container_width=True)
                st.plotly_chart(px.pie(filtered_df, names="Category", title="توزيع الفئات"), use_container_width=True)
                st.plotly_chart(px.bar(filtered_df, x="Priority", color="Priority", title="توزيع الأولويات"), use_container_width=True)
                st.plotly_chart(px.line(filtered_df.groupby('Date').size().reset_index(name='Count'), x="Date", y="Count", title="اتجاه المهام عبر الزمن"), use_container_width=True)

                st.markdown("### 📋 جدول المهام")
                st.dataframe(filtered_df)

                st.markdown("### 📥 تصدير إلى Excel")
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    filtered_df.to_excel(writer, index=False, sheet_name='Tasks')
                    workbook = writer.book
                    worksheet = writer.sheets['Tasks']
                    header_format = workbook.add_format({
                        'bold': True, 'font_color': 'white', 'bg_color': '#2dd4bf',
                        'font_size': 12, 'align': 'center', 'valign': 'vcenter'
                    })
                    for col_num, value in enumerate(filtered_df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                        worksheet.set_column(col_num, col_num, 18)
                st.download_button(
                    label="📥 تنزيل ملف Excel",
                    data=output.getvalue(),
                    file_name="FLM_Tasks.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("ℹ️ لا توجد مهام. أضف بعض المهام من علامة تبويب 'إضافة مهمة'.")

    # --- Profile ---
    with tab3:
        st.subheader("👤 الملف الشخصي")
        st.image(user_info.get('profile_picture', 'https://via.placeholder.com/100'), caption="صورة الملف الشخصي", width=100, use_column_width=False)
        st.markdown(f"**الاسم الكامل:** {user_info.get('full_name', 'N/A')}")
        st.markdown(f"**البريد الإلكتروني:** {user_info.get('email', 'N/A')}")
        st.markdown(f"**رقم الهاتف:** {user_info.get('phone', 'N/A')}")
        st.markdown(f"**الدور:** {user_info.get('role', 'N/A')}")
        st.markdown(f"**القسم:** {user_info.get('department', 'N/A')}")
        st.markdown(f"**المنطقة الزمنية:** {user_info.get('timezone', 'N/A')}")
        st.markdown("### 📊 ملخص النشاط")
        st.write(f"المهام التي تم إنشاؤها: {total_tasks}")
        st.write(f"المهام المكتملة: {completed_tasks}")
        if st.button("📥 تصدير تقرير الملف الشخصي"):
            output = BytesIO()
            profile_data = pd.DataFrame([{
                "الاسم الكامل": user_info.get('full_name'),
                "البريد الإلكتروني": user_info.get('email'),
                "رقم الهاتف": user_info.get('phone'),
                "الدور": user_info.get('role'),
                "القسم": user_info.get('department'),
                "المنطقة الزمنية": user_info.get('timezone'),
                "إجمالي المهام": total_tasks,
                "المهام المكتملة": completed_tasks
            }])
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                profile_data.to_excel(writer, index=False, sheet_name='Profile')
                workbook = writer.book
                worksheet = writer.sheets['Profile']
                header_format = workbook.add_format({
                    'bold': True, 'font_color': 'white', 'bg_color': '#2dd4bf',
                    'font_size': 12, 'align': 'center', 'valign': 'vcenter'
                })
                for col_num, value in enumerate(profile_data.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    worksheet.set_column(col_num, col_num, 18)
            st.download_button(
                label="📥 تنزيل تقرير الملف الشخصي",
                data=output.getvalue(),
                file_name=f"{user_info.get('full_name')}_Profile.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # --- Settings ---
    with tab4:
        st.subheader("⚙️ إعدادات الحساب")
        with st.form("settings_form"):
            st.markdown("### تحديث المعلومات الشخصية")
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("🧑 الاسم الكامل", value=user_info.get('full_name', ''), placeholder="أدخل اسمك الكامل")
                email = st.text_input("📧 البريد الإلكتروني", value=user_info.get('email', ''), placeholder="أدخل بريدك الإلكتروني")
                phone = st.text_input("📱 رقم الهاتف", value=user_info.get('phone', ''), placeholder="مثال: +1234567890")
            with col2:
                department = st.selectbox("🏢 القسم", DEPARTMENTS, index=DEPARTMENTS.index(user_info.get('department', DEPARTMENTS[0])), format_func=lambda x: x)
                profile_picture = st.text_input("🖼 رابط صورة الملف الشخصي", value=user_info.get('profile_picture', ''), placeholder="اختياري: أدخل رابط الصورة")
                timezone = st.selectbox("🌐 المنطقة الزمنية", TIMEZONES, index=TIMEZONES.index(user_info.get('timezone', TIMEZONES[0])))
            
            st.markdown("### تحديث كلمة المرور (اختياري)")
            col3, col4 = st.columns(2)
            with col3:
                new_password = st.text_input("🔑 كلمة المرور الجديدة", type="password", placeholder="أدخل كلمة المرور الجديدة")
            with col4:
                confirm_password = st.text_input("🔑 تأكيد كلمة المرور الجديدة", type="password", placeholder="أكد كلمة المرور الجديدة")
            
            st.markdown("### التفضيلات")
            theme = st.selectbox("🎨 الثيم", ["Dark"], index=0)  # Dark theme enforced
            notifications = st.checkbox("🔔 تفعيل إشعارات البريد الإلكتروني", value=True)
            
            if st.form_submit_button("💾 حفظ التغييرات"):
                success, message = update_user(
                    st.session_state.user_role, full_name, email, phone, department, profile_picture, timezone, new_password, confirm_password
                )
                if success:
                    st.session_state.theme = theme
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    # --- Footer ---
    st.markdown(f"""
        <footer>
            <div>🌍 INTERSOFT Global Task Tracker • {datetime.now(user_tz).strftime('%Y-%m-%d %I:%M %p')}</div>
            <div class='footer-links'>
                <a href='#'>حول</a>
                <a href='#'>الدعم</a>
                <a href='#'>سياسة الخصوصية</a>
            </div>
        </footer>
    """, unsafe_allow_html=True)

# --- Page Navigation ---
if st.session_state.current_page == "Login":
    login_page()
elif st.session_state.current_page == "Register":
    register_page()
elif st.session_state.current_page == "Dashboard" and st.session_state.logged_in:
    dashboard_page()
else:
    st.session_state.current_page = "Login"
    login_page()
