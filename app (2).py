import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import calendar
from io import BytesIO
import uuid

# --- Page Configuration ---
st.set_page_config(
    page_title="⚡ INTERSOFT Dashboard | FLM",
    layout="wide",
    page_icon="🚀"
)

# --- Beautiful Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background: radial-gradient(circle at top left, #0f172a, #1e293b);
        color: #f8fafc;
    }

    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 2rem;
        margin-top: 1rem;
    }

    .greeting {
        font-size: 1rem;
        font-weight: 500;
        color: #fcd34d;
        text-align: right;
    }

    .company {
        font-size: 1.2rem;
        font-weight: 600;
        color: #60a5fa;
    }

    .date-box {
        font-size: 1rem;
        font-weight: 500;
        color: #f8fafc;
        text-align: center;
        background: #1e293b;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        margin-bottom: 1.5rem;
        display: inline-block;
    }

    .overview-box {
        background: linear-gradient(to bottom right, #1e3a8a, #3b82f6);
        padding: 1.5rem;
        border-radius: 18px;
        text-align: center;
        margin: 1rem 0;
        transition: 0.4s ease;
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }

    .overview-box:hover {
        transform: translateY(-5px) scale(1.02);
    }
    .overview-box span {
        font-size: 2.2rem;
        font-weight: 800;
        color: #fcd34d;
    }

    .stButton>button {
        background: linear-gradient(135deg, #4f46e5, #9333ea);
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        box-shadow: 0 6px 25px rgba(0,0,0,0.3);
        transition: all 0.3s ease-in-out;
    }

    .stButton>button:hover {
        transform: scale(1.05);
    }

    footer {
        text-align: center;
        color: #94a3b8;
        padding-top: 2rem;
    }

    .stTextInput>div>input, .stSelectbox>div>select {
        background: #1e293b;
        color: #f8fafc;
        border: 1px solid #4b5e8e;
        border-radius: 8px;
        padding: 0.5rem;
    }

    .stTextInput>label, .stSelectbox>label {
        color: #f8fafc;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.users = {
        "Yaman": {"password": "YAMAN1", "role": "Employee"},
        "Hatem": {"password": "HATEM2", "role": "Employee"},
        "Mahmoud": {"password": "MAHMOUD3", "role": "Employee"},
        "Qusai": {"password": "QUSAI4", "role": "Employee"}
    }
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "Login"

# --- Constants ---
SHIFTS = ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"]
CATEGORIES = ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM", "📅 Meetings", "💻 TOMS"]
PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]
ROLES = ["Employee", "Manager"]

# --- Authentication Functions ---
def check_login(username, password):
    return st.session_state.users.get(username, {}).get("password") == password

def register_user(username, password, role, email, full_name):
    if username in st.session_state.users:
        return False, "Username already exists!"
    if not username or not password or not role or not email or not full_name:
        return False, "All fields are required!"
    if "@" not in email or "." not in email:
        return False, "Invalid email format!"
    st.session_state.users[username] = {
        "password": password,
        "role": role,
        "email": email,
        "full_name": full_name
    }
    return True, "Registration successful!"

# --- Pages ---
def login_page():
    st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>🔐 INTERSOFT Task Tracker</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='date-box'>📅 {}</div>".format(datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')), unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🔐 Login")
        with st.form("login_form"):
            username = st.text_input("👤 Username")
            password = st.text_input("🔑 Password", type="password")
            if st.form_submit_button("Login 🚀"):
                if check_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.user_role = st.session_state.users[username]["full_name"]
                    st.session_state.current_page = "Dashboard"
                    st.r rer()
                else:
                    st.error("❌ Invalid credentials")
    
    with col2:
        st.subheader("📝 Register")
        with st.form("register_form"):
            new_username = st.text_input("

👤 New Username")
            new_password = st.text_input("🔑 New Password", type="password")
            role = st.selectbox("👷 Role", ROLES)
            email = st.text_input("📧 Email")
            full_name = st.text_input("🧑 Full Name")
            if st.form_submit_button("Register 🌟"):
                success, message = register_user(new_username, new_password, role, email, full_name)
                if success:
                    st.success(message)
                else:
                    st.error(message)

def dashboard_page():
    # --- Top Info Header ---
    st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>👋 Welcome <b>{}</b><br><small>Start tracking tasks, boost your day, and monitor progress like a pro!</small></div></div!".format(st.session_state.user_role), unsafe_allow_html=True)
    st.markdown(f"<div class='date-box'>📅 {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}</div>", unsafe_allow_html=True)

    # --- Dashboard Overview ---
    df = pd.DataFrame(st.session_state.timesheet)
    df_user = df[df['Employee'] == st.session_state.user_role] if not df.empty else pd.DataFrame()
    total_tasks = len(df_user)
    completed_tasks = df_user[df_user['Status'] == '✅ Completed'].shape[0] if not df_user.empty else 0
    in_progress_tasks = df_user[df_user['Status'] == '🔄 In Progress'].shape[0] if not df_user.empty else 0
    not_started_tasks = df_user[df_user['Status'] == '⏳ Not Started'].shape[0] if not df_user.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"<div class='overview-box'>Total Tasks<br><span>{total_tasks}</span></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='overview-box'>Completed<br><span>{completed_tasks}</span></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='overview-box'>In Progress<br><span>{in_progress_tasks}</span></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='overview-box'>Not Started<br><span>{not_started_tasks}</span></div>", unsafe_allow_html=True)

    # --- Tabs ---
    tab1, tab2, tab3 = st.tabs(["➕ Add Task", "📈 Analytics", "👤 Profile"])

    # --- Add Task ---
    with tab1:
        with st.form("task_form", clear_on_submit=True):
            st.subheader("📝 Add New Task")
            col1, col2 = st.columns(2)
            with col1:
                shift = st.selectbox("🕒 Shift", SHIFTS)
                date = st.date_input("📅 Date", value=datetime.today())
                department = st.selectbox("🏢 Department", ["FLM", "Tech Support", "CRM"])
            with col2:
                cat = st.selectbox("📂 Category", CATEGORIES)
                stat = st.selectbox("📌 Status", STATUSES)
                prio = st.selectbox("⚠️ Priority", PRIORITIES)
            desc = st.text_area("🗒 Task Description", height=100)
            btn1, btn2 = st.columns([1, 1])
            with btn1:
                submitted = st.form_submit_button("✅ Submit Task")
            with btn2:
                clear = st.form_submit_button("🧹 Clear All Tasks")
            if submitted:
                st.session_state.timesheet.append({
                    "Employee": st.session_state.user_role,
                    "Date": date.strftime('%Y-%m-%d'),
                    "Day": calendar.day_name[date.weekday()],
                    "Shift": shift,
                    "Department": department,
                    "Category": cat,
                    "Status": stat,
                    "Priority": prio,
                    "Description": desc,
                    "Submitted": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                st.success("🎉 Task added successfully!")
            if clear:
                st.session_state.timesheet = []
                st.warning("🧹 All tasks cleared!")

    # --- Analytics ---
    with tab2:
        if not df_user.empty:
            st.subheader("📊 Task Analysis")
            st.plotly_chart(px.histogram(df_user, x="Date", color="Status", barmode="group", title="Tasks Over Time"), use_container_width=True)
            st.plotly_chart(px.pie(df_user, names="Category", title="Category Breakdown"), use_container_width=True)
            st.plotly_chart(px.bar(df_user, x="Priority", color="Priority", title="Priority Distribution"), use_container_width=True)

            st.markdown("### 📋 Task Table")
            st.dataframe(df_user)

            st.markdown("### 📥 Export to Excel")
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_user.to_excel(writer, index=False, sheet_name='Tasks')
                workbook = writer.book
                worksheet = writer.sheets['Tasks']
                header_format = workbook.add_format({
                    'bold': True, 'font_color': 'white', 'bg_color': '#4f81bd',
                    'font_size': 12, 'align': 'center', 'valign': 'vcenter'
                })
                for col_num, value in enumerate(df_user.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    worksheet.set_column(col_num, col_num, 18)
            st.download_button(
                label="📥 Download Excel File",
                data=output.getvalue(),
                file_name="FLM_Tasks.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("ℹ️ No tasks found. Add some from the 'Add Task' tab.")

    # --- Profile ---
    with tab3:
        st.subheader("👤 User Profile")
        user_info = st.session_state.users.get(st.session_state.user_role, {})
        st.markdown(f"**Full Name:** {user_info.get('full_name', 'N/A')}")
        st.markdown(f"**Email:** {user_info.get('email', 'N/A')}")
        st.markdown(f"**Role:** {user_info.get('role', 'N/A')}")
        if st.button("🔓 Logout"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.current_page = "Login"
            st.rerun()

    # --- Footer ---
    st.markdown(f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</footer>", unsafe_allow_html=True)

# --- Page Navigation ---
if st.session_state.logged_in:
    dashboard_page()
else:
    login_page()
