import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import calendar
from io import BytesIO
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="⚡ INTERSOFT Dashboard | FLM",
    layout="wide",
    page_icon="🚀"
)

# --- Modern SaaS Styling with Animations and Dark Mode Toggle ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f9fafb;
        color: #1f2937;
        transition: all 0.3s ease-in-out;
    }

    .dark-mode html, .dark-mode body, .dark-mode [class*="css"] {
        background-color: #1e293b !important;
        color: #f8fafc !important;
    }

    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background-color: #ffffff;
        border-radius: 10px;
        border-bottom: 1px solid #e5e7eb;
        transition: all 0.3s ease-in-out;
    }

    .dark-mode .top-header {
        background-color: #334155;
        border-color: #475569;
    }

    .greeting {
        font-size: 1.1rem;
        font-weight: 600;
        color: #6366f1;
        text-align: right;
    }

    .company {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1d4ed8;
    }

    .dark-mode .greeting, .dark-mode .company {
        color: #facc15;
    }

    .date-box {
        font-size: 1rem;
        font-weight: 500;
        color: #334155;
        text-align: center;
        background: #e0f2fe;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        display: inline-block;
        margin: 1rem 0;
        transition: background 0.3s;
    }

    .dark-mode .date-box {
        background: #475569;
        color: #f8fafc;
    }

    .overview-box {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #e5e7eb;
        transition: 0.3s;
        transform: scale(1);
    }

    .overview-box:hover {
        transform: scale(1.02);
    }

    .dark-mode .overview-box {
        background: #334155;
        border-color: #475569;
    }

    .overview-box span {
        font-size: 2.2rem;
        font-weight: 800;
        color: #2563eb;
    }

    .dark-mode .overview-box span {
        color: #fcd34d;
    }

    .stButton>button {
        background: linear-gradient(135deg, #3b82f6, #6366f1);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        transition: all 0.3s ease-in-out;
    }

    .stButton>button:hover {
        transform: scale(1.05);
        background: linear-gradient(135deg, #2563eb, #4f46e5);
    }

    .stTextInput>div>input, .stSelectbox>div>select {
        background: #ffffff;
        color: #111827;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 0.5rem;
    }

    .dark-mode .stTextInput>div>input, .dark-mode .stSelectbox>div>select {
        background: #1e293b;
        color: #f8fafc;
        border-color: #475569;
    }

    .stTextInput>label, .stSelectbox>label {
        color: #1f2937;
        font-weight: 600;
    }

    .dark-mode .stTextInput>label, .dark-mode .stSelectbox>label {
        color: #f1f5f9;
    }

    .stForm {
        background: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
    }

    .dark-mode .stForm {
        background: #1e293b;
        border-color: #475569;
    }

    footer {
        text-align: center;
        color: #9ca3af;
        padding-top: 2rem;
        font-size: 0.9rem;
    }

    .dark-mode footer {
        color: #94a3b8;
    }
    </style>
""", unsafe_allow_html=True)

# --- Dark Mode Toggle Script ---
st.markdown("""
    <script>
    const root = window.parent.document.documentElement;
    const darkModeToggle = document.createElement('button');
    darkModeToggle.innerText = '🌓';
    darkModeToggle.style.position = 'fixed';
    darkModeToggle.style.top = '10px';
    darkModeToggle.style.right = '10px';
    darkModeToggle.style.zIndex = '1000';
    darkModeToggle.style.border = 'none';
    darkModeToggle.style.background = '#e2e8f0';
    darkModeToggle.style.color = '#1e293b';
    darkModeToggle.style.padding = '10px';
    darkModeToggle.style.borderRadius = '50%';
    darkModeToggle.style.boxShadow = '0 2px 10px rgba(0,0,0,0.15)';
    darkModeToggle.style.cursor = 'pointer';
    darkModeToggle.onclick = () => {
        root.classList.toggle('dark-mode');
    }
    window.addEventListener('DOMContentLoaded', () => {
        if (!document.body.contains(darkModeToggle)) {
            document.body.appendChild(darkModeToggle);
        }
    });
    </script>
""", unsafe_allow_html=True)
# --- Initialize Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.users = {
        "Yaman": {"password": "YAMAN1", "role": "Employee", "email": "yaman@intersoft.com", "full_name": "Yaman Ali", "phone": "+1234567890", "department": "FLM"},
        "Hatem": {"password": "HATEM2", "role": "Employee", "email": "hatem@intersoft.com", "full_name": "Hatem Mohamed", "phone": "+1234567891", "department": "Tech Support"},
        "Mahmoud": {"password": "MAHMOUD3", "role": "Employee", "email": "mahmoud@intersoft.com", "full_name": "Mahmoud Ahmed", "phone": "+1234567892", "department": "CRM"},
        "Qusai": {"password": "QUSAI4", "role": "Employee", "email": "qusai@intersoft.com", "full_name": "Qusai Hassan", "phone": "+1234567893", "department": "FLM"}
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
DEPARTMENTS = ["FLM", "Tech Support", "CRM"]

# --- Authentication Functions ---
def check_login(username, password):
    return st.session_state.users.get(username, {}).get("password") == password

def register_user(username, password, confirm_password, role, email, full_name, phone, department):
    if username in st.session_state.users:
        return False, "Username already exists!"
    if not all([username, password, confirm_password, role, email, full_name, phone, department]):
        return False, "All fields are required!"
    if password != confirm_password:
        return False, "Passwords do not match!"
    if len(password) < 6:
        return False, "Password must be at least 6 characters long!"
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email format!"
    if not re.match(r"\+?\d{10,15}", phone):
        return False, "Invalid phone number format (e.g., +1234567890)!"
    st.session_state.users[username] = {
        "password": password,
        "role": role,
        "email": email,
        "full_name": full_name,
        "phone": phone,
        "department": department
    }
    return True, "Registration successful!"

def update_user(username, full_name, email, phone, department, new_password, confirm_password):
    if not all([full_name, email, phone, department]):
        return False, "All fields are required!"
    if new_password and new_password != confirm_password:
        return False, "Passwords do not match!"
    if new_password and len(new_password) < 6:
        return False, "New password must be at least 6 characters long!"
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email format!"
    if not re.match(r"\+?\d{10,15}", phone):
        return False, "Invalid phone number format (e.g., +1234567890)!"
    user = st.session_state.users[username]
    user["full_name"] = full_name
    user["email"] = email
    user["phone"] = phone
    user["department"] = department
    if new_password:
        user["password"] = new_password
    return True, "Profile updated successfully!"

# --- Pages ---
def login_page():
    st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>🔐 INTERSOFT Task Tracker</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='date-box'>📅 {}</div>".format(datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')), unsafe_allow_html=True)
    
    st.subheader("🔐 Login")
    with st.form("login_form"):
        username = st.text_input("👤 Username")
        password = st.text_input("🔑 Password", type="password")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.form_submit_button("Login 🚀"):
                if check_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.user_role = username
                    st.session_state.current_page = "Dashboard"
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        with col2:
            if st.form_submit_button("Go to Register 🌟"):
                st.session_state.current_page = "Register"
                st.rerun()

def register_page():
    st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>📝 Register for INTERSOFT Task Tracker</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='date-box'>📅 {}</div>".format(datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')), unsafe_allow_html=True)
    
    st.subheader("📝 Create Your Account")
    with st.form("register_form"):
        st.markdown("### Personal Information")
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("🧑 Full Name")
            email = st.text_input("📧 Email")
            phone = st.text_input("📱 Phone Number (e.g., +1234567890)")
        with col2:
            username = st.text_input("👤 Username")
            role = st.selectbox("👷 Role", ROLES)
            department = st.selectbox("🏢 Department", DEPARTMENTS)
        
        st.markdown("### Account Security")
        col3, col4 = st.columns(2)
        with col3:
            password = st.text_input("🔑 Password", type="password")
        with col4:
            confirm_password = st.text_input("🔑 Confirm Password", type="password")
        
        col5, col6 = st.columns([1, 1])
        with col5:
            if st.form_submit_button("Register 🌟"):
                success, message = register_user(
                    username, password, confirm_password, role, email, full_name, phone, department
                )
                if success:
                    st.success(message)
                    st.session_state.current_page = "Login"
                    st.rerun()
                else:
                    st.error(message)
        with col6:
            if st.form_submit_button("Back to Login 🔙"):
                st.session_state.current_page = "Login"
                st.rerun()

def dashboard_page():
    # --- Top Info Header ---
    user_info = st.session_state.users.get(st.session_state.user_role, {})
    st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>👋 Welcome <b>{}</b><br><small>Start tracking tasks, boost your day, and monitor progress like a pro!</small></div></div!".format(user_info.get('full_name', 'User')), unsafe_allow_html=True)
    st.markdown(f"<div class='date-box'>📅 {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}</div>", unsafe_allow_html=True)

    # --- Dashboard Overview ---
    df = pd.DataFrame(st.session_state.timesheet)
    df_user = df[df['Employee'] == user_info.get('full_name')] if not df.empty else pd.DataFrame()
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
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Task", "📈 Analytics", "👤 Profile", "⚙️ Settings"])

    # --- Add Task ---
    with tab1:
        with st.form("task_form", clear_on_submit=True):
            st.subheader("📝 Add New Task")
            col1, col2 = st.columns(2)
            with col1:
                shift = st.selectbox("🕒 Shift", SHIFTS)
                date = st.date_input("📅 Date", value=datetime.today())
                department = st.selectbox("🏢 Department", DEPARTMENTS)
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
                    "Employee": user_info.get('full_name'),
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
        st.markdown(f"**Full Name:** {user_info.get('full_name', 'N/A')}")
        st.markdown(f"**Email:** {user_info.get('email', 'N/A')}")
        st.markdown(f"**Phone:** {user_info.get('phone', 'N/A')}")
        st.markdown(f"**Role:** {user_info.get('role', 'N/A')}")
        st.markdown(f"**Department:** {user_info.get('department', 'N/A')}")
        if st.button("🔓 Logout"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.current_page = "Login"
            st.rerun()

    # --- Settings ---
    with tab4:
        st.subheader("⚙️ Account Settings")
        with st.form("settings_form"):
            st.markdown("### Update Personal Information")
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("🧑 Full Name", value=user_info.get('full_name', ''))
                email = st.text_input("📧 Email", value=user_info.get('email', ''))
                phone = st.text_input("📱 Phone Number (e.g., +1234567890)", value=user_info.get('phone', ''))
            with col2:
                department = st.selectbox("🏢 Department", DEPARTMENTS, index=DEPARTMENTS.index(user_info.get('department', DEPARTMENTS[0])))
            
            st.markdown("### Update Password (Optional)")
            col3, col4 = st.columns(2)
            with col3:
                new_password = st.text_input("🔑 New Password", type="password")
            with col4:
                confirm_password = st.text_input("🔑 Confirm New Password", type="password")
            
            if st.form_submit_button("💾 Save Changes"):
                success, message = update_user(
                    st.session_state.user_role, full_name, email, phone, department, new_password, confirm_password
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    # --- Footer ---
    st.markdown(f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</footer>", unsafe_allow_html=True)

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
