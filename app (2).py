import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import calendar
from io import BytesIO
import uuid
import os
import json
from PIL import Image
import pytz

# --- Constants ---
USERS = {
    "yaman": {"pass": "YAMAN1", "role": "Admin"},
    "hatem": {"pass": "HATEM2", "role": "Supervisor"},
    "qusai": {"pass": "QUSAI4", "role": "Employee"},
}
USER_PROFILE = {
    "yaman": {"name": "Yaman", "email": "yaman@example.com", "picture": None},
    "hatem": {"name": "Hatem", "email": "hatem@example.com", "picture": None},
    "qusai": {"name": "Qusai", "email": "qusai@example.com", "picture": None},
}
EXPORT_FOLDER = "weekly_exports"
DATA_FILE = "data.json"
TASK_STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]
TASK_PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
DEPARTMENTS = ["FLM", "Tech Support", "CRM"]
CATEGORIES = ["Job Orders", "CRM", "Meetings", "Paperwork"]
SHIFTS = ["Morning", "Evening"]
ROLES = ["Admin", "Supervisor", "Employee"]

# --- Page Config ---
st.set_page_config(
    page_title="⚡ INTERSOFT Dashboard | FLM",
    layout="wide",
    page_icon="🚀"
)

# --- Embed CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: radial-gradient(circle at top left, #0f172a, #1e293b);
    color: #f8fafc;
    scroll-behavior: smooth;
}

.top-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0 2.5rem; margin: 1.5rem 0;
    animation: fadeIn 1s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}

.greeting {
    font-size: 1.1rem; font-weight: 600; color: #fcd34d;
    text-align: right; line-height: 1.4;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

.company {
    font-size: 1.4rem; font-weight: 700; color: #ffffff; letter-spacing: 0.5px;
}

.date-box {
    font-size: 1.1rem; font-weight: 600; color: #f8fafc; text-align: center;
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
    padding: 0.75rem 1.5rem; border-radius: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    margin-bottom: 1rem; display: inline-block;
    animation: fadeIn 0.6s ease-in-out;
}

.nav-buttons {
    display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center;
    margin: 1.5rem 0; padding: 1rem;
}

.stButton>button {
    background: linear-gradient(135deg, #4f46e5, #9333ea);
    color: white; font-weight: 600; font-size: 1rem;
    border-radius: 12px; padding: 0.7rem 1.5rem;
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    transition: all 0.3s ease-in-out; border: none;
    cursor: pointer; text-align: center; min-width: 150px;
    animation: slideIn 0.4s ease-in-out;
}

.stButton>button:hover {
    transform: scale(1.06); box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    background: linear-gradient(135deg, #6b7280, #9ca3af);
}

.stButton>button:active {
    transform: scale(0.94); box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.stButton>button.selected {
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
    transform: scale(1.03);
    box-shadow: 0 8px 25px rgba(0,0,0,0.4);
}

@keyframes slideIn {
    from { transform: translateY(10px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

.stButton>button.delete-button {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
}

.overview-box {
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
    padding: 1rem; border-radius: 15px; text-align: center;
    margin: 0.5rem 0; transition: transform 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    animation: zoomIn 0.6s ease-in-out;
}

.overview-box:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 12px 30px rgba(0,0,0,0.4);
}

@keyframes zoomIn {
    from { transform: scale(0.95); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}

.overview-box span {
    font-size: 1.5rem; font-weight: 800; color: #fcd34d;
    display: block;
}

.overview-box small {
    font-size: 0.8rem; color: #e2e8f0;
}

.edit-section {
    background: #1e293b; padding: 2rem; border-radius: 16px; margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    animation: fadeIn 0.5s ease-in-out;
}

.alert-box {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    padding: 1.2rem; border-radius: 14px; color: white;
    margin-bottom: 1.5rem; font-weight: 600;
    animation: shake 0.5s ease-in-out;
}

@keyframes shake {
    0% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    50% { transform: translateX(5px); }
    75% { transform: translateX(-5px); }
    100% { transform: translateX(0); }
}

.stDataFrame table {
    width: 100%; border-collapse: collapse;
    background: #1e293b; border-radius: 12px; overflow: hidden;
}

.stDataFrame th {
    background-color: #4f81bd; color: white; font-weight: 700;
    padding: 10px; font-size: 1.1rem;
}

.stDataFrame td {
    font-weight: 600; color: #f8fafc; padding: 10px;
    border-bottom: 1px solid #334155; font-size: 1rem;
}

footer {
    text-align: center; color: #94a3b8; padding: 2.5rem 0;
    font-size: 1rem; font-weight: 500;
    animation: fadeIn 1s ease-in-out;
}

.profile-picture {
    border-radius: 50%; width: 100px; height: 100px; object-fit: cover;
    border: 2px solid #60a5fa; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

# --- Persistent Storage ---
def save_data():
    try:
        data = {
            "timesheet": st.session_state.timesheet,
            "reminders": st.session_state.reminders,
            "user_profile": {
                k: {"name": v["name"], "email": v["email"], "picture": None}
                for k, v in USER_PROFILE.items()
            },
            "users": USERS,
            "login_log": st.session_state.login_log
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"⚠️ Failed to save data: {e}")

def load_data():
    global USERS, USER_PROFILE
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                st.session_state.timesheet = data.get("timesheet", [])
                st.session_state.reminders = data.get("reminders", [])
                st.session_state.login_log = data.get("login_log", [])
                USERS.update(data.get("users", {}))
                for user, profile in data.get("user_profile", {}).items():
                    if user in USER_PROFILE:
                        USER_PROFILE[user]["name"] = profile.get("name", USER_PROFILE[user]["name"])
                        USER_PROFILE[user]["email"] = profile.get("email", USER_PROFILE[user]["email"])
                    else:
                        USER_PROFILE[user] = {"name": profile.get("name", ""), "email": profile.get("email", ""), "picture": None}
    except Exception as e:
        st.error(f"⚠️ Failed to load data: {e}")

# --- Session Initialization ---
def initialize_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_role_type = None
        st.session_state.timesheet = []
        st.session_state.login_log = []
        st.session_state.reminders = []
        st.session_state.selected_tab = "Dashboard"
    if "reminders" not in st.session_state:
        st.session_state.reminders = []
    if "selected_tab" not in st.session_state:
        st.session_state.selected_tab = "Dashboard"
    load_data()

# --- Authentication ---
def authenticate_user():
    if not st.session_state.logged_in:
        st.title("🔐 Login to INTERSOFT Dashboard")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = USERS.get(username.lower())
            if user and user["pass"] == password:
                st.session_state.logged_in = True
                st.session_state.user_role = username.lower()
                st.session_state.user_role_type = user["role"]
                st.session_state.login_log.append({
                    "Username": username.lower(),
                    "Login Time": datetime.now(pytz.timezone("Asia/Riyadh")).strftime('%Y-%m-%d %H:%M:%S'),
                    "Role": user["role"]
                })
                save_data()
                st.session_state.selected_tab = "Dashboard"
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
        st.stop()

# --- Excel Export Function ---
def export_to_excel(df, sheet_name, file_name):
    output = BytesIO()
    try:
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            header_format = workbook.add_format({
                'bold': True, 'font_color': 'white', 'bg_color': '#4f81bd',
                'font_size': 12, 'align': 'center', 'valign': 'vcenter'
            })
            cell_format = workbook.add_format({
                'font_color': '#000000', 'align': 'left', 'valign': 'vcenter'
            })
            for col_num, col in enumerate(df.columns):
                worksheet.write(0, col_num, col, header_format)
                max_len = max(
                    df[col].astype(str).map(len).max() if not df[col].empty else 10,
                    len(col)
                )
                worksheet.set_column(col_num, col_num, max_len + 2)
            for row_num in range(1, len(df) + 1):
                for col_num in range(len(df.columns)):
                    worksheet.write(row_num, col_num, df.iloc[row_num-1, col_num], cell_format)
        return output.getvalue(), file_name
    except Exception as e:
        st.error(f"⚠️ Failed to export to Excel: {e}")
        return None, file_name

# --- Auto Weekly Export ---
def auto_export_weekly():
    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    now = datetime.now(pytz.timezone("Asia/Riyadh"))
    if now.weekday() == 6:  # Sunday
        filename = os.path.join(EXPORT_FOLDER, f"flm_tasks_week_{now.strftime('%Y_%U')}.csv")
        if not os.path.exists(filename):
            df_export = pd.DataFrame(st.session_state.timesheet)
            if not df_export.empty:
                try:
                    df_export.to_csv(filename, index=False)
                    st.info(f"✅ Auto-exported weekly tasks to {filename}")
                except Exception as e:
                    st.error(f"⚠️ Failed to export tasks: {e}")

# --- Settings Popup ---
def render_settings():
    with st.expander("⚙️ User Settings", expanded=False):
        st.subheader("User Profile")
        user = st.session_state.user_role
        current_profile = USER_PROFILE.get(user, {"name": "", "email": "", "picture": None})
        
        # Display Profile Picture
        if current_profile["picture"]:
            st.image(current_profile["picture"], width=100, caption="Profile Picture", output_format="PNG")
        
        # Edit Profile
        with st.form("profile_form"):
            name = st.text_input("Name", value=current_profile["name"], key="profile_name")
            email = st.text_input("Email", value=current_profile["email"], key="profile_email")
            picture = st.file_uploader("Upload Profile Picture", type=["png", "jpg", "jpeg"], key="profile_picture")
            submitted = st.form_submit_button("💾 Save Profile")
            if submitted:
                USER_PROFILE[user]["name"] = name
                USER_PROFILE[user]["email"] = email
                if picture:
                    img = Image.open(picture)
                    img = img.resize((100, 100))
                    USER_PROFILE[user]["picture"] = img
                save_data()
                st.success("✅ Profile updated successfully!")
                st.rerun()

        # Change Password
        st.subheader("🔑 Change Password")
        with st.form("password_form"):
            current_password = st.text_input("Current Password", type="password", key="current_password")
            new_password = st.text_input("New Password", type="password", key="new_password")
            confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_password")
            submitted = st.form_submit_button("🔄 Change Password")
            if submitted:
                if current_password == USERS[user]["pass"]:
                    if new_password == confirm_password and new_password:
                        USERS[user]["pass"] = new_password
                        save_data()
                        st.success("✅ Password changed successfully!")
                        st.rerun()
                    else:
                        st.error("⚠️ New password and confirmation do not match or are empty!")
                else:
                    st.error("⚠️ Current password is incorrect!")

# --- Download Tasks ---
def render_download_tasks():
    current_user = st.session_state.user_role
    user_tasks = df_all[df_all['Employee'] == current_user] if not df_all.empty and 'Employee' in df_all.columns else pd.DataFrame()
    if not user_tasks.empty:
        data, file_name = export_to_excel(user_tasks, f"{current_user}_Tasks", f"{current_user}_tasks.xlsx")
        if data:
            st.download_button(
                label="⬇️ Download My Tasks",
                data=data,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("⚠️ Failed to generate Excel file.")
    else:
        st.info("ℹ️ No tasks available for your account.")

# --- Admin Download Other Users' Tasks ---
def render_admin_download_tasks():
    if st.session_state.user_role_type == "Admin":
        st.markdown("### 🛠 Admin Panel: Download Employee Tasks")
        df_all = pd.DataFrame(st.session_state.timesheet)
        if not df_all.empty and 'Employee' in df_all.columns:
            employees = df_all['Employee'].unique().tolist()
            if employees:
                selected_employee = st.selectbox("Select Employee", employees, key="admin_download_employee")
                emp_tasks = df_all[df_all['Employee'] == selected_employee]
                if not emp_tasks.empty:
                    data, file_name = export_to_excel(emp_tasks, f"{selected_employee}_Tasks", f"{selected_employee}_tasks.xlsx")
                    if data:
                        st.download_button(
                            label=f"⬇️ Download {selected_employee.capitalize()} Tasks",
                            data=data,
                            file_name=file_name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.error("⚠️ Failed to generate Excel file.")
                else:
                    st.info(f"ℹ️ No tasks found for {selected_employee}.")
            else:
                st.info("ℹ️ No employees with tasks found.")
        else:
            st.info("ℹ️ No tasks recorded yet.")

# --- Render Header ---
def render_header():
    tz = pytz.timezone("Asia/Riyadh")
    current_time = datetime.now(tz).strftime('%I:%M %p')
    st.markdown(
        f"""
        <div class='top-header'>
            <div class='company'>INTERSOFT<br>International Software Company</div>
            <div class='greeting'>👋 Welcome <b>{st.session_state.user_role.capitalize()} ({st.session_state.user_role_type})</b><br>
            <small>Today is {datetime.now(tz).strftime('%A, %B %d, %Y')}</small></div>
        </div>
        <div class='date-box'>🕒 {current_time} (+03)</div>
        """,
        unsafe_allow_html=True
    )

    # Ensure selected_tab is initialized
    if "selected_tab" not in st.session_state:
        st.session_state.selected_tab = "Dashboard"

    # Navigation Buttons
    st.markdown("<div class='nav-buttons'>", unsafe_allow_html=True)
    tabs = [
        ("Dashboard", "🏠 Dashboard"),
        ("Add Task", "➕ Add Task"),
        ("Edit/Delete Task", "✏️ Edit/Delete Task"),
        ("Analytics", "📈 Analytics"),
        ("Employee Work", "👥 Employee Work")
    ]
    if st.session_state.user_role_type == "Admin":
        tabs.append(("Admin Panel", "🛠 Admin Panel"))
    tabs.append(("Settings", "⚙️ Settings"))
    tabs.append(("Download Tasks", "⬇️ Download My Tasks"))

    cols = st.columns(len(tabs))
    for idx, (tab_key, tab_label) in enumerate(tabs):
        with cols[idx]:
            button_class = "selected" if st.session_state.selected_tab == tab_key else ""
            if st.button(tab_label, key=f"nav_{tab_key.lower().replace(' ', '_')}", help=tab_label, use_container_width=True):
                st.session_state.selected_tab = tab_key
                st.rerun()
            st.markdown(f"""
                <script>
                    document.querySelectorAll('.stButton>button').forEach((btn, index) => {{
                        if (index === {idx} && "{st.session_state.selected_tab}" === "{tab_key}") {{
                            btn.classList.add('selected');
                        }} else {{
                            btn.classList.remove('selected');
                        }}
                    }});
                </script>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Render Sidebar Stats ---
def render_sidebar_stats():
    tz = pytz.timezone("Asia/Riyadh")
    today_str = datetime.now(tz).strftime('%Y-%m-%d')
    st.sidebar.markdown(f"### 👥 Today's Employee Statistics ({today_str})")
    df_all = pd.DataFrame(st.session_state.timesheet)
    if not df_all.empty and 'Employee' in df_all.columns:
        today_df = df_all[df_all['Date'] == today_str]
        employees = sorted(today_df['Employee'].unique()) if not today_df.empty else []
        if employees:
            for employee in employees:
                emp_df = today_df[today_df['Employee'] == employee]
                emp_total = len(emp_df)
                emp_completed = emp_df[emp_df['Status'] == '✅ Completed'].shape[0]
                emp_in_progress = emp_df[emp_df['Status'] == '🔄 In Progress'].shape[0]
                emp_not_started = emp_df[emp_df['Status'] == '⏳ Not Started'].shape[0]
                st.sidebar.markdown(
                    f"""
                    <div class='overview-box'>
                        <div>{employee.capitalize()}</div>
                        <span>{emp_total}</span>
                        <small>Completed: {emp_completed} | In Progress: {emp_in_progress} | Not Started: {emp_not_started}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.sidebar.info(f"ℹ️ No tasks recorded for today ({today_str}).")
    else:
        st.sidebar.info("ℹ️ No tasks recorded yet.")

# --- Render Dashboard Stats ---
def render_dashboard_stats(display_df):
    total_tasks = len(display_df)
    completed_tasks = display_df[display_df['Status'] == '✅ Completed'].shape[0] if not display_df.empty else 0
    in_progress_tasks = display_df[display_df['Status'] == '🔄 In Progress'].shape[0] if not display_df.empty else 0
    not_started_tasks = display_df[display_df['Status'] == '⏳ Not Started'].shape[0] if not display_df.empty else 0

    st.markdown("### 📊 Overall Task Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"<div class='overview-box'>Total Tasks<br><span>{total_tasks}</span></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='overview-box'>Completed<br><span>{completed_tasks}</span></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='overview-box'>In Progress<br><span>{in_progress_tasks}</span></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='overview-box'>Not Started<br><span>{not_started_tasks}</span></div>", unsafe_allow_html=True)

# --- Render Alerts ---
def render_alerts(df_user, df_all):
    tz = pytz.timezone("Asia/Riyadh")
    today_str = datetime.now(tz).strftime('%Y-%m-%d')
    if st.session_state.user_role_type == "Employee" and (df_user.empty or today_str not in df_user['Date'].values):
        st.markdown(f"<div class='alert-box'>⚠️ You haven't submitted any tasks for today!</div>", unsafe_allow_html=True)
    
    if st.session_state.user_role_type in ["Admin", "Supervisor"]:
        users = list(set(df_all['Employee'].unique()) if not df_all.empty and 'Employee' in df_all.columns else [])
        for user in USERS.keys():
            if user.lower() not in users or not any(df_all[df_all['Employee'] == user.lower()]['Date'] == today_str):
                st.markdown(f"<div class='alert-box'>🔔 Alert: <b>{user.capitalize()}</b> has not submitted a task today!</div>", unsafe_allow_html=True)

    # Render Reminders
    try:
        reminders = st.session_state.reminders
    except AttributeError:
        st.session_state.reminders = []
        reminders = st.session_state.reminders
    for reminder in reminders:
        if reminder["user"] == st.session_state.user_role and reminder["date"] == today_str:
            st.markdown(f"<div class='alert-box'>🔔 Reminder: Task '{reminder['task_desc'][:30]}...' is still Not Started! Due: {reminder['due_date']}</div>", unsafe_allow_html=True)

# --- Add Task ---
def render_add_task():
    tz = pytz.timezone("Asia/Riyadh")
    st.header("➕ Add New Task")
    with st.form("task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            shift = st.selectbox("🕒 Shift", SHIFTS, key="add_shift")
            date_selected = st.date_input("📅 Date", value=datetime.now(tz), key="add_date")
            department = st.selectbox("🏢 Department", DEPARTMENTS, key="add_dept")
        with col2:
            category = st.selectbox("📂 Category", CATEGORIES, key="add_cat")
            status = st.selectbox("📌 Status", TASK_STATUSES, key="add_stat")
            priority = st.selectbox("⚠️ Priority", TASK_PRIORITIES, key="add_prio")
        description = st.text_area("🗒 Description", height=120, key="add_desc")
        set_reminder = st.checkbox("🔔 Set Reminder for Not Started Task", key="add_reminder") if status == "⏳ Not Started" else False
        reminder_date = st.date_input("📅 Reminder Due Date", value=datetime.now(tz) + timedelta(days=1), key="add_reminder_date") if set_reminder else None
        
        submitted = st.form_submit_button("✅ Submit Task")
        
        if submitted:
            if description.strip():
                task = {
                    "TaskID": str(uuid.uuid4()),
                    "Employee": st.session_state.user_role,
                    "Date": date_selected.strftime('%Y-%m-%d'),
                    "Day": calendar.day_name[date_selected.weekday()],
                    "Shift": shift,
                    "Department": department,
                    "Category": category,
                    "Status": status,
                    "Priority": priority,
                    "Description": description,
                    "Submitted": datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
                }
                st.session_state.timesheet.append(task)
                if set_reminder and status == "⏳ Not Started":
                    st.session_state.reminders.append({
                        "user": st.session_state.user_role,
                        "task_id": task["TaskID"],
                        "task_desc": task["Description"],
                        "date": datetime.now(tz).strftime('%Y-%m-%d'),
                        "due_date": reminder_date.strftime('%Y-%m-%d')
                    })
                save_data()
                st.success("🎉 Task added successfully!")
                st.rerun()
            else:
                st.error("⚠️ Description cannot be empty!")

# --- Edit/Delete Task ---
def render_edit_delete_task(display_df):
    tz = pytz.timezone("Asia/Riyadh")
    st.header("✏️ Edit/Delete Task")
    if not display_df.empty:
        st.markdown("<div class='edit-section'>", unsafe_allow_html=True)
        task_dict = {f"{row['Description'][:30]}... ({row['Date']} | {row['Category']} | {row['Status']} | {row['Employee'].capitalize()})": row["TaskID"] for _, row in display_df.iterrows()}
        selected_label = st.selectbox("📋 Select Task", list(task_dict.keys()), key="select_task")
        selected_id = task_dict[selected_label]
        selected_task = display_df[display_df["TaskID"] == selected_id].iloc[0]

        # Edit Form
        with st.form("edit_form"):
            col1, col2 = st.columns(2)
            with col1:
                shift = st.selectbox("🕒 Shift", SHIFTS, index=SHIFTS.index(selected_task["Shift"]), key="edit_shift")
                date = st.date_input("📅 Date", datetime.strptime(selected_task["Date"], '%Y-%m-%d'), key="edit_date")
                dept = st.selectbox("🏢 Department", DEPARTMENTS, index=DEPARTMENTS.index(selected_task["Department"]), key="edit_dept")
            with col2:
                cat = st.selectbox("📂 Category", CATEGORIES, index=CATEGORIES.index(selected_task["Category"]), key="edit_cat")
                stat = st.selectbox("📌 Status", TASK_STATUSES, index=TASK_STATUSES.index(selected_task["Status"]), key="edit_stat")
                prio = st.selectbox("⚠️ Priority", TASK_PRIORITIES, index=TASK_PRIORITIES.index(selected_task["Priority"]), key="edit_prio")
            desc = st.text_area("🗒 Description", selected_task["Description"], height=120, key="edit_desc")
            set_reminder = st.checkbox("🔔 Set Reminder for Not Started Task", key="edit_reminder") if stat == "⏳ Not Started" else False
            reminder_date = st.date_input("📅 Reminder Due Date", value=datetime.now(tz) + timedelta(days=1), key="edit_reminder_date") if set_reminder else None

            submitted = st.form_submit_button("💾 Save Changes")
            if submitted:
                if desc.strip():
                    for i, t in enumerate(st.session_state.timesheet):
                        if t["TaskID"] == selected_id:
                            st.session_state.timesheet[i] = {
                                "TaskID": selected_id,
                                "Employee": selected_task["Employee"],
                                "Date": date.strftime('%Y-%m-%d'),
                                "Day": calendar.day_name[date.weekday()],
                                "Shift": shift,
                                "Department": dept,
                                "Category": cat,
                                "Status": stat,
                                "Priority": prio,
                                "Description": desc,
                                "Submitted": datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
                            }
                            if set_reminder and stat == "⏳ Not Started":
                                st.session_state.reminders = [r for r in st.session_state.reminders if r["task_id"] != selected_id]
                                st.session_state.reminders.append({
                                    "user": st.session_state.user_role,
                                    "task_id": selected_id,
                                    "task_desc": desc,
                                    "date": datetime.now(tz).strftime('%Y-%m-%d'),
                                    "due_date": reminder_date.strftime('%Y-%m-%d')
                                })
                            save_data()
                            st.success("✅ Task updated successfully!")
                            st.rerun()
                else:
                    st.error("⚠️ Description cannot be empty!")

        # Delete Form (Admin Only)
        if st.session_state.user_role_type == "Admin":
            with st.form("delete_form"):
                st.warning("⚠️ This action cannot be undone!")
                delete_confirmed = st.checkbox("I confirm I want to delete this task", key="confirm_delete")
                submitted_delete = st.form_submit_button("🗑 Delete Task")
                if submitted_delete and delete_confirmed:
                    st.session_state.timesheet = [t for t in st.session_state.timesheet if t["TaskID"] != selected_id]
                    st.session_state.reminders = [r for r in st.session_state.reminders if r["task_id"] != selected_id]
                    save_data()
                    st.warning("🗑 Task deleted successfully!")
                    st.rerun()
        else:
            st.info("ℹ️ Task deletion is restricted to Admins only.")

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("ℹ️ No tasks available to edit.")

# --- Analytics ---
def render_analytics(display_df):
    st.header("📈 Analytics")
    if display_df.empty:
        st.info("ℹ️ No tasks yet.")
    else:
        st.plotly_chart(px.histogram(display_df, x="Date", color="Status", title="Tasks Over Time", color_discrete_sequence=px.colors.qualitative.Plotly), use_container_width=True)
        st.plotly_chart(px.pie(display_df, names="Category", title="Category Distribution", color_discrete_sequence=px.colors.qualitative.Plotly), use_container_width=True)
        st.plotly_chart(px.bar(display_df, x="Priority", color="Priority", title="Priority Levels", color_discrete_sequence=px.colors.qualitative.Plotly), use_container_width=True)
        
        st.markdown("### 📋 Task Table")
        st.dataframe(display_df)

        st.markdown("### 📥 Download Tasks")
        data, file_name = export_to_excel(display_df, "Tasks", "tasks_export.xlsx")
        if data:
            st.download_button("📥 Download Excel", data=data, file_name=file_name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.error("⚠️ Failed to generate Excel file.")

# --- Employee Work Tab ---
def render_employee_work():
    tz = pytz.timezone("Asia/Riyadh")
    st.header("👥 Employee Work")
    df_all = pd.DataFrame(st.session_state.timesheet)
    if not df_all.empty and 'Employee' in df_all.columns:
        # Filter Tasks
        st.markdown("### 📅 View Employee Tasks")
        col1, col2 = st.columns(2)
        with col1:
            users = df_all['Employee'].unique().tolist()
            selected_user = st.selectbox("Employee", options=["All"] + users, key="employee_work_filter")
        with col2:
            start = st.date_input("Start Date", value=datetime.now(tz) - timedelta(days=7), key="employee_work_start")
            end = st.date_input("End Date", value=datetime.now(tz), key="employee_work_end")
        filtered_df = df_all
        if selected_user != "All":
            filtered_df = filtered_df[filtered_df['Employee'] == selected_user]
        filtered_df = filtered_df[(filtered_df['Date'] >= start.strftime('%Y-%m-%d')) & (filtered_df['Date'] <= end.strftime('%Y-%m-%d'))]
        st.dataframe(filtered_df)
    else:
        st.info("ℹ️ No tasks recorded yet.")

# --- Admin Panel ---
def render_admin_panel():
    tz = pytz.timezone("Asia/Riyadh")
    if st.session_state.user_role_type == "Admin":
        st.header("🛠 Admin Panel")
        df_all = pd.DataFrame(st.session_state.timesheet)
        
        # User Management
        st.markdown("### 👤 Manage Users")
        st.markdown("<div class='edit-section'>", unsafe_allow_html=True)
        
        # Add New User
        st.subheader("Add New User")
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("Username", key="new_username")
                new_password = st.text_input("Password", type="password", key="new_password")
                new_role = st.selectbox("Role", ROLES, key="new_role")
            with col2:
                new_name = st.text_input("Name", key="new_name")
                new_email = st.text_input("Email", key="new_email")
            submitted = st.form_submit_button("➕ Add User")
            if submitted:
                if new_username.lower() in USERS:
                    st.error("⚠️ Username already exists!")
                elif not all([new_username, new_password, new_name, new_email]):
                    st.error("⚠️ All fields are required!")
                else:
                    USERS[new_username.lower()] = {"pass": new_password, "role": new_role}
                    USER_PROFILE[new_username.lower()] = {"name": new_name, "email": new_email, "picture": None}
                    save_data()
                    st.success(f"✅ User {new_username} added successfully!")
                    st.rerun()

        # Delete User
        st.subheader("Delete User")
        with st.form("delete_user_form"):
            users = [u for u in USERS.keys() if u != st.session_state.user_role]
            selected_user = st.selectbox("Select User to Delete", users, key="delete_user_select")
            delete_confirmed = st.checkbox("I confirm I want to delete this user", key="confirm_user_delete")
            submitted_delete = st.form_submit_button("🗑 Delete User")
            if submitted_delete and delete_confirmed:
                if selected_user == st.session_state.user_role:
                    st.error("⚠️ Cannot delete your own account!")
                else:
                    del USERS[selected_user]
                    del USER_PROFILE[selected_user]
                    st.session_state.timesheet = [t for t in st.session_state.timesheet if t["Employee"] != selected_user]
                    st.session_state.reminders = [r for r in st.session_state.reminders if r["user"] != selected_user]
                    save_data()
                    st.warning(f"🗑 User {selected_user} deleted successfully!")
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Filter Tasks
        if not df_all.empty and 'Employee' in df_all.columns:
            st.markdown("### 📅 View and Filter Tasks")
            col1, col2 = st.columns(2)
            with col1:
                users = df_all['Employee'].unique().tolist()
                selected_user = st.selectbox("Employee", options=["All"] + users, key="filter_employee")
            with col2:
                start = st.date_input("Start Date", value=datetime.now(tz) - timedelta(days=7), key="filter_start")
                end = st.date_input("End Date", value=datetime.now(tz), key="filter_end")
            filtered_df = df_all
            if selected_user != "All":
                filtered_df = filtered_df[filtered_df['Employee'] == selected_user]
            filtered_df = filtered_df[(filtered_df['Date'] >= start.strftime('%Y-%m-%d')) & (filtered_df['Date'] <= end.strftime('%Y-%m-%d'))]
            st.dataframe(filtered_df)

            # Edit Any Task
            st.markdown("### ✏️ Edit Any Task")
            st.markdown("<div class='edit-section'>", unsafe_allow_html=True)
            task_dict = {f"{row['Description'][:30]}... ({row['Date']} | {row['Category']} | {row['Status']} | {row['Employee'].capitalize()})": row["TaskID"] for _, row in df_all.iterrows()}
            selected_label = st.selectbox("📋 Select Task to Edit", list(task_dict.keys()), key="admin_select_task")
            selected_id = task_dict[selected_label]
            selected_task = df_all[df_all["TaskID"] == selected_id].iloc[0]

            with st.form("admin_edit_form"):
                col1, col2 = st.columns(2)
                with col1:
                    shift = st.selectbox("🕒 Shift", SHIFTS, index=SHIFTS.index(selected_task["Shift"]), key="admin_edit_shift")
                    date = st.date_input("📅 Date", datetime.strptime(selected_task["Date"], '%Y-%m-%d'), key="admin_edit_date")
                    dept = st.selectbox("🏢 Department", DEPARTMENTS, index=DEPARTMENTS.index(selected_task["Department"]), key="admin_edit_dept")
                with col2:
                    cat = st.selectbox("📂 Category", CATEGORIES, index=CATEGORIES.index(selected_task["Category"]), key="admin_edit_cat")
                    stat = st.selectbox("📌 Status", TASK_STATUSES, index=TASK_STATUSES.index(selected_task["Status"]), key="admin_edit_stat")
                    prio = st.selectbox("⚠️ Priority", TASK_PRIORITIES, index=TASK_PRIORITIES.index(selected_task["Priority"]), key="admin_edit_prio")
                desc = st.text_area("🗒 Description", selected_task["Description"], height=120, key="admin_edit_desc")
                set_reminder = st.checkbox("🔔 Set Reminder for Not Started Task", key="admin_edit_reminder") if stat == "⏳ Not Started" else False
                reminder_date = st.date_input("📅 Reminder Due Date", value=datetime.now(tz) + timedelta(days=1), key="admin_edit_reminder_date") if set_reminder else None

                submitted = st.form_submit_button("💾 Save Changes")
                if submitted:
                    if desc.strip():
                        for i, t in enumerate(st.session_state.timesheet):
                            if t["TaskID"] == selected_id:
                                st.session_state.timesheet[i] = {
                                    "TaskID": selected_id,
                                    "Employee": selected_task["Employee"],
                                    "Date": date.strftime('%Y-%m-%d'),
                                    "Day": calendar.day_name[date.weekday()],
                                    "Shift": shift,
                                    "Department": dept,
                                    "Category": cat,
                                    "Status": stat,
                                    "Priority": prio,
                                    "Description": desc,
                                    "Submitted": datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
                                }
                                if set_reminder and stat == "⏳ Not Started":
                                    st.session_state.reminders = [r for r in st.session_state.reminders if r["task_id"] != selected_id]
                                    st.session_state.reminders.append({
                                        "user": selected_task["Employee"],
                                        "task_id": selected_id,
                                        "task_desc": desc,
                                        "date": datetime.now(tz).strftime('%Y-%m-%d'),
                                        "due_date": reminder_date.strftime('%Y-%m-%d')
                                    })
                                save_data()
                                st.success("✅ Task updated successfully!")
                                st.rerun()
                    else:
                        st.error("⚠️ Description cannot be empty!")
            st.markdown("</div>", unsafe_allow_html=True)

            # Login Activity Log
            st.markdown("### 📜 Login Activity Log")
            st.dataframe(pd.DataFrame(st.session_state.login_log))

            # Employee Statistics
            st.markdown("### 📊 Employee Statistics")
            stats_df = df_all.groupby('Employee').agg({
                'TaskID': 'count',
                'Status': lambda x: (x == '✅ Completed').sum()
            }).rename(columns={'TaskID': 'Total Tasks', 'Status': 'Completed Tasks'})
            stats_df['Completion Rate'] = (stats_df['Completed Tasks'] / stats_df['Total Tasks'] * 100).round(2)
            st.dataframe(stats_df)

            # Export All Tasks
            st.markdown("### 📥 Export All Tasks")
            data, file_name = export_to_excel(df_all, "All_Tasks", "all_tasks_export.xlsx")
            if data:
                st.download_button("📥 Download All Tasks", data=data, file_name=file_name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.error("⚠️ Failed to generate Excel file.")
        else:
            st.info("ℹ️ No tasks recorded yet.")

# --- Main App Logic ---
if __name__ == "__main__":
    initialize_session()
    authenticate_user()

    # Sidebar
    st.sidebar.title("🔒 Session")
    if st.sidebar.button("Logout", key="logout_button"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_role_type = None
        st.session_state.reminders = []
        st.session_state.selected_tab = "Dashboard"
        save_data()
        st.rerun()

    # Render Sidebar Stats
    render_sidebar_stats()

    # Data Setup
    df_all = pd.DataFrame(st.session_state.timesheet)
    df_user = df_all[df_all['Employee'] == st.session_state.user_role] if not df_all.empty and 'Employee' in df_all.columns else pd.DataFrame()
    display_df = df_user if st.session_state.user_role_type == "Employee" else df_all

    # Render Header with Navigation
    render_header()

    # Render Content Based on Selected Tab
    if st.session_state.selected_tab == "Dashboard":
        st.header("🏠 Dashboard")
        render_dashboard_stats(display_df)
        render_alerts(df_user, df_all)
        render_admin_download_tasks()
        auto_export_weekly()
    elif st.session_state.selected_tab == "Add Task":
        render_add_task()
    elif st.session_state.selected_tab == "Edit/Delete Task":
        render_edit_delete_task(display_df)
    elif st.session_state.selected_tab == "Analytics":
        render_analytics(display_df)
    elif st.session_state.selected_tab == "Employee Work":
        render_employee_work()
    elif st.session_state.selected_tab == "Admin Panel":
        if st.session_state.user_role_type == "Admin":
            render_admin_panel()
        else:
            st.error("🚫 Access restricted to Admins only.")
            st.session_state.selected_tab = "Dashboard"
            st.rerun()
    elif st.session_state.selected_tab == "Settings":
        render_settings()
    elif st.session_state.selected_tab == "Download Tasks":
        render_download_tasks()

    # Footer
    st.markdown(
        f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now(pytz.timezone('Asia/Riyadh')).strftime('%A, %B %d, %Y - %I:%M %p')}</footer>",
        unsafe_allow_html=True
    )
