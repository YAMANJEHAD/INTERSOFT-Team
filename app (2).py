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

# --- Global Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        background: #f1f5f9;
        color: #1e3a8a;
    }

    .sidebar .sidebar-content {
        background: #1e3a8a;
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
    }

    .sidebar .stButton>button {
        width: 100%;
        background: #14b8a6;
        color: #ffffff;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .sidebar .stButton>button:hover {
        background: #0d9488;
        transform: translateY(-2px);
    }

    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background: #ffffff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-radius: 12px;
        margin: 1rem;
    }

    .company {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e3a8a;
    }

    .greeting {
        font-size: 1rem;
        font-weight: 500;
        color: #14b8a6;
        text-align: right;
    }

    .date-box {
        font-size: 0.9rem;
        font-weight: 500;
        color: #ffffff;
        background: #14b8a6;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin: 1rem auto;
        display: inline-block;
    }

    .overview-box {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .overview-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }

    .overview-box span {
        font-size: 2rem;
        font-weight: 600;
        color: #14b8a6;
    }

    .stButton>button {
        background: #14b8a6;
        color: #ffffff;
        font-weight: 500;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        border: none;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background: #0d9488;
        transform: scale(1.05);
    }

    .stForm {
        background: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }

    .stTextInput>div>input, .stSelectbox>div>select {
        background: #f7fafc;
        color: #1e3a8a;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.5rem;
    }

    .stTextInput>label, .stSelectbox>label {
        color: #1e3a8a;
        font-weight: 500;
    }

    .stTabs [role="tab"] {
        background: #ffffff;
        color: #1e3a8a;
        border-radius: 8px 8px 0 0;
        padding: 0.8rem 1.2rem;
        margin-right: 0.5rem;
        transition: all 0.3s ease;
    }

    .stTabs [role="tab"][aria-selected="true"] {
        background: #14b8a6;
        color: #ffffff;
    }

    footer {
        text-align: center;
        color: #64748b;
        padding: 2rem 0;
        font-size: 0.9rem;
    }

    .footer-links a {
        color: #14b8a6;
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
    st.session_state.theme = "Light"

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
        return False, "Username already exists!"
    if not all([username, password, confirm_password, role, email, full_name, phone, department, timezone]):
        return False, "All fields are required!"
    if password != confirm_password:
        return False, "Passwords do not match!"
    if len(password) < 8:
        return False, "Password must be at least 8 characters long!"
    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$", password):
        return False, "Password must contain at least one uppercase letter, one lowercase letter, and one number!"
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
        "department": department,
        "profile_picture": profile_picture or "https://via.placeholder.com/100",
        "timezone": timezone
    }
    return True, "Registration successful!"

def update_user(username, full_name, email, phone, department, profile_picture, timezone, new_password, confirm_password):
    if not all([full_name, email, phone, department, timezone]):
        return False, "All fields are required!"
    if new_password and new_password != confirm_password:
        return False, "Passwords do not match!"
    if new_password and len(new_password) < 8:
        return False, "New password must be at least 8 characters long!"
    if new_password and not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$", new_password):
        return False, "New password must contain at least one uppercase letter, one lowercase letter, and one number!"
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email format!"
    if not re.match(r"\+?\d{10,15}", phone):
        return False, "Invalid phone number format (e.g., +1234567890)!"
    user = st.session_state.users[username]
    user["full_name"] = full_name
    user["email"] = email
    user["phone"] = phone
    user["department"] = department
    user["profile_picture"] = profile_picture or user["profile_picture"]
    user["timezone"] = timezone
    if new_password:
        user["password"] = new_password
    return True, "Profile updated successfully!"

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("<div class='company'>INTERSOFT<br>Global Task Tracker</div>", unsafe_allow_html=True)
    if st.session_state.logged_in:
        user_info = st.session_state.users.get(st.session_state.user_role, {})
        st.markdown(f"<div class='greeting'>👤 {user_info.get('full_name', 'User')}</div>", unsafe_allow_html=True)
        if st.button("🏠 Dashboard", key="nav_dashboard"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        if st.button("🔓 Logout", key="nav_logout"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.current_page = "Login"
            st.rerun()
    else:
        if st.button("🔐 Login", key="nav_login"):
            st.session_state.current_page = "Login"
            st.rerun()
        if st.button("📝 Register", key="nav_register"):
            st.session_state.current_page = "Register"
            st.rerun()

# --- Pages ---
def login_page():
    st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>Global Task Tracker</div><div class='greeting'>🔐 Sign In to Your Account</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='date-box'>📅 {datetime.now(pytz.timezone('UTC')).strftime('%A, %B %d, %Y - %I:%M %p')}</div>", unsafe_allow_html=True)
    
    st.subheader("🔐 Login")
    with st.form("login_form"):
        username = st.text_input("👤 Username", placeholder="Enter your username")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
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
            if st.form_submit_button("Forgot Password 🔧"):
                st.info("ℹ️ Password reset link sent to your email (simulated).")

def register_page():
    st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>Global Task Tracker</div><div class='greeting'>📝 Create Your Account</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='date-box'>📅 {datetime.now(pytz.timezone('UTC')).strftime('%A, %B %d, %Y - %I:%M %p')}</div>", unsafe_allow_html=True)
    
    st.subheader("📝 Register")
    with st.form("register_form"):
        st.markdown("### Personal Information")
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("🧑 Full Name", placeholder="Enter your full name")
            email = st.text_input("📧 Email", placeholder="Enter your email")
            phone = st.text_input("📱 Phone Number", placeholder="e.g., +1234567890")
        with col2:
            username = st.text_input("👤 Username", placeholder="Choose a username")
            role = st.selectbox("👷 Role", ROLES)
            department = st.selectbox("🏢 Department", DEPARTMENTS)
        
        st.markdown("### Account Security")
        col3, col4 = st.columns(2)
        with col3:
            password = st.text_input("🔑 Password", type="password", placeholder="Create a password")
        with col4:
            confirm_password = st.text_input("🔑 Confirm Password", type="password", placeholder="Confirm your password")
        
        profile_picture = st.text_input("🖼 Profile Picture URL", placeholder="Optional: Enter image URL")
        timezone = st.selectbox("🌐 Time Zone", TIMEZONES)
        
        col5, col6 = st.columns([1, 1])
        with col5:
            if st.form_submit_button("Register 🌟"):
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
            if st.form_submit_button("Back to Login 🔙"):
                st.session_state.current_page = "Login"
                st.rerun()

def dashboard_page():
    user_info = st.session_state.users.get(st.session_state.user_role, {})
    user_tz = pytz.timezone(user_info.get('timezone', 'UTC'))
    st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>Global Task Tracker</div><div class='greeting'>👋 Welcome, <b>{}</b><br><small>Manage tasks, track progress, and stay organized!</small></div></div>".format(user_info.get('full_name', 'User')), unsafe_allow_html=True)
    st.markdown(f"<div class='date-box'>📅 {datetime.now(user_tz).strftime('%A, %B %d, %Y - %I:%M %p')}</div>", unsafe_allow_html=True)

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
        st.subheader("📝 Add New Task")
        with st.form("task_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                shift = st.selectbox("🕒 Shift", SHIFTS)
                date = st.date_input("📅 Date", value=datetime.today())
                department = st.selectbox("🏢 Department", DEPARTMENTS)
            with col2:
                cat = st.selectbox("📂 Category", CATEGORIES)
                stat = st.selectbox("📌 Status", STATUSES)
                prio = st.selectbox("⚠️ Priority", PRIORITIES)
            desc = st.text_area("🗒 Task Description", height=100, placeholder="Describe the task...")
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn1:
                submitted = st.form_submit_button("✅ Submit Task")
            with col_btn2:
                clear_form = st.form_submit_button("🔄 Reset Form")
            with col_btn3:
                clear_all = st.form_submit_button("🧹 Clear All Tasks")
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
                st.success("🎉 Task added successfully!")
            if clear_form:
                st.rerun()
            if clear_all:
                if st.checkbox("Confirm Clear All Tasks"):
                    st.session_state.timesheet = []
                    st.warning("🧹 All tasks cleared!")
                    st.rerun()

        # --- Task Management ---
        if not df_user.empty:
            st.markdown("### 📋 Manage Tasks")
            task_filter = st.selectbox("Filter Tasks", ["All", "Not Started", "In Progress", "Completed"])
            date_filter = st.date_input("Filter by Date Range", value=(datetime.today() - timedelta(days=30), datetime.today()))
            filtered_df = df_user
            if task_filter != "All":
                filtered_df = filtered_df[filtered_df['Status'] == f"{'⏳ Not Started' if task_filter == 'Not Started' else '🔄 In Progress' if task_filter == 'In Progress' else '✅ Completed'}"]
            filtered_df = filtered_df[(filtered_df['Date'] >= date_filter[0].strftime('%Y-%m-%d')) & (filtered_df['Date'] <= date_filter[1].strftime('%Y-%m-%d'))]
            st.dataframe(filtered_df)

            # Task Editing/Deletion
            if not filtered_df.empty:
                task_index = st.selectbox("Select Task to Edit/Delete", filtered_df.index, format_func=lambda x: filtered_df.loc[x, 'Description'][:50])
                with st.form("edit_task_form"):
                    edit_shift = st.selectbox("🕒 Shift", SHIFTS, index=SHIFTS.index(filtered_df.loc[task_index, 'Shift']))
                    edit_date = st.date_input("📅 Date", value=pd.to_datetime(filtered_df.loc[task_index, 'Date']))
                    edit_department = st.selectbox("🏢 Department", DEPARTMENTS, index=DEPARTMENTS.index(filtered_df.loc[task_index, 'Department']))
                    edit_cat = st.selectbox("📂 Category", CATEGORIES, index=CATEGORIES.index(filtered_df.loc[task_index, 'Category']))
                    edit_stat = st.selectbox("📌 Status", STATUSES, index=STATUSES.index(filtered_df.loc[task_index, 'Status']))
                    edit_prio = st.selectbox("⚠️ Priority", PRIORITIES, index=PRIORITIES.index(filtered_df.loc[task_index, 'Priority']))
                    edit_desc = st.text_area("🗒 Task Description", value=filtered_df.loc[task_index, 'Description'], height=100)
                    col_edit, col_delete = st.columns(2)
                    with col_edit:
                        if st.form_submit_button("💾 Update Task"):
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
                            st.success("✅ Task updated successfully!")
                            st.rerun()
                    with col_delete:
                        if st.form_submit_button("🗑 Delete Task"):
                            st.session_state.timesheet.pop(task_index)
                            st.warning("🗑 Task deleted!")
                            st.rerun()

    # --- Analytics ---
    with tab2:
        if not df_user.empty:
            st.subheader("📊 Task Analysis")
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                date_range = st.date_input("Date Range", value=(datetime.today() - timedelta(days=30), datetime.today()))
            with col_filter2:
                dept_filter = st.multiselect("Department Filter", DEPARTMENTS, default=DEPARTMENTS)
            filtered_df = df_user[
                (df_user['Date'] >= date_range[0].strftime('%Y-%m-%d')) &
                (df_user['Date'] <= date_range[1].strftime('%Y-%m-%d')) &
                (df_user['Department'].isin(dept_filter))
            ]
            if not filtered_df.empty:
                st.plotly_chart(px.histogram(filtered_df, x="Date", color="Status", barmode="group", title="Tasks Over Time"), use_container_width=True)
                st.plotly_chart(px.pie(filtered_df, names="Category", title="Category Breakdown"), use_container_width=True)
                st.plotly_chart(px.bar(filtered_df, x="Priority", color="Priority", title="Priority Distribution"), use_container_width=True)
                st.plotly_chart(px.line(filtered_df.groupby('Date').size().reset_index(name='Count'), x="Date", y="Count", title="Task Trend Over Time"), use_container_width=True)

                st.markdown("### 📋 Task Table")
                st.dataframe(filtered_df)

                st.markdown("### 📥 Export to Excel")
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    filtered_df.to_excel(writer, index=False, sheet_name='Tasks')
                    workbook = writer.book
                    worksheet = writer.sheets['Tasks']
                    header_format = workbook.add_format({
                        'bold': True, 'font_color': 'white', 'bg_color': '#14b8a6',
                        'font_size': 12, 'align': 'center', 'valign': 'vcenter'
                    })
                    for col_num, value in enumerate(filtered_df.columns.values):
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
        st.image(user_info.get('profile_picture', 'https://via.placeholder.com/100'), caption="Profile Picture", width=100, use_column_width=False)
        st.markdown(f"**Full Name:** {user_info.get('full_name', 'N/A')}")
        st.markdown(f"**Email:** {user_info.get('email', 'N/A')}")
        st.markdown(f"**Phone:** {user_info.get('phone', 'N/A')}")
        st.markdown(f"**Role:** {user_info.get('role', 'N/A')}")
        st.markdown(f"**Department:** {user_info.get('department', 'N/A')}")
        st.markdown(f"**Time Zone:** {user_info.get('timezone', 'N/A')}")
        st.markdown("### 📊 Activity Summary")
        st.write(f"Tasks Created: {total_tasks}")
        st.write(f"Tasks Completed: {completed_tasks}")
        if st.button("📥 Export Profile Report"):
            output = BytesIO()
            profile_data = pd.DataFrame([{
                "Full Name": user_info.get('full_name'),
                "Email": user_info.get('email'),
                "Phone": user_info.get('phone'),
                "Role": user_info.get('role'),
                "Department": user_info.get('department'),
                "Time Zone": user_info.get('timezone'),
                "Total Tasks": total_tasks,
                "Completed Tasks": completed_tasks
            }])
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                profile_data.to_excel(writer, index=False, sheet_name='Profile')
                workbook = writer.book
                worksheet = writer.sheets['Profile']
                header_format = workbook.add_format({
                    'bold': True, 'font_color': 'white', 'bg_color': '#14b8a6',
                    'font_size': 12, 'align': 'center', 'valign': 'vcenter'
                })
                for col_num, value in enumerate(profile_data.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    worksheet.set_column(col_num, col_num, 18)
            st.download_button(
                label="📥 Download Profile Report",
                data=output.getvalue(),
                file_name=f"{user_info.get('full_name')}_Profile.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # --- Settings ---
    with tab4:
        st.subheader("⚙️ Account Settings")
        with st.form("settings_form"):
            st.markdown("### Update Personal Information")
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("🧑 Full Name", value=user_info.get('full_name', ''), placeholder="Enter your full name")
                email = st.text_input("📧 Email", value=user_info.get('email', ''), placeholder="Enter your email")
                phone = st.text_input("📱 Phone Number", value=user_info.get('phone', ''), placeholder="e.g., +1234567890")
            with col2:
                department = st.selectbox("🏢 Department", DEPARTMENTS, index=DEPARTMENTS.index(user_info.get('department', DEPARTMENTS[0])))
                profile_picture = st.text_input("🖼 Profile Picture URL", value=user_info.get('profile_picture', ''), placeholder="Optional: Enter image URL")
                timezone = st.selectbox("🌐 Time Zone", TIMEZONES, index=TIMEZONES.index(user_info.get('timezone', TIMEZONES[0])))
            
            st.markdown("### Update Password (Optional)")
            col3, col4 = st.columns(2)
            with col3:
                new_password = st.text_input("🔑 New Password", type="password", placeholder="Enter new password")
            with col4:
                confirm_password = st.text_input("🔑 Confirm New Password", type="password", placeholder="Confirm new password")
            
            st.markdown("### Preferences")
            theme = st.selectbox("🎨 Theme", ["Light", "Dark"], index=0 if st.session_state.theme == "Light" else 1)
            notifications = st.checkbox("🔔 Enable Email Notifications", value=True)
            
            if st.form_submit_button("💾 Save Changes"):
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
                <a href='#'>About</a>
                <a href='#'>Support</a>
                <a href='#'>Privacy Policy</a>
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
