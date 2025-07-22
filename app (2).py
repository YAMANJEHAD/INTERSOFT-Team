import streamlit as st
import base64
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
import numpy as np

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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif;
    box-sizing: border-box;
}

body {
    background: #0f172a;
    color: #e2e8f0;
    margin: 0;
    padding: 0;
}

.main-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem;
    background: #1e293b;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.company-logo {
    font-size: 1.8rem;
    font-weight: 700;
    color: #60a5fa;
}

.user-info {
    text-align: right;
    font-size: 1rem;
    color: #94a3b8;
}

.user-info b {
    color: #f8fafc;
    font-weight: 600;
}

.nav-bar {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}

.nav-button {
    background: #1e3a8a;
    color: #f8fafc;
    padding: 0.8rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
}

.nav-button:hover, .nav-button.active {
    background: #3b82f6;
    box-shadow: 0 4px 12px rgba(59,130,246,0.3);
}

.card {
    background: #1e293b;
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    transition: transform 0.3s ease;
}

.card:hover {
    transform: translateY(-4px);
}

.card-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #60a5fa;
    margin-bottom: 1rem;
}

.stat-card {
    text-align: center;
    padding: 1rem;
    background: #1e3a8a;
    border-radius: 8px;
    color: #f8fafc;
}

.stat-card span {
    font-size: 2rem;
    font-weight: 700;
    color: #fcd34d;
    display: block;
    margin-bottom: 0.5rem;
}

.alert {
    background: #b91c1c;
    color: #f8fafc;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    font-weight: 500;
}

.alert.reminder {
    background: #eab308;
}

.stButton>button {
    background: #1e3a8a;
    color: #f8fafc;
    border-radius: 8px;
    padding: 0.8rem 1.5rem;
    font-weight: 600;
    border: none;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background: #3b82f6;
    box-shadow: 0 4px 12px rgba(59,130,246,0.3);
}

.stButton>button.delete-button {
    background: #b91c1c;
}

.stButton>button.delete-button:hover {
    background: #dc2626;
}

.stSelectbox, .stTextInput, .stTextArea, .stDateInput {
    background: #334155;
    color: #f8fafc;
    border-radius: 8px;
    padding: 0.5rem;
}

.stDataFrame table {
    background: #1e293b;
    border-radius: 8px;
    color: #f8fafc;
}

.stDataFrame th {
    background: #1e3a8a;
    color: #f8fafc;
    font-weight: 600;
}

.stDataFrame td {
    border-bottom: 1px solid #334155;
}

.chart-container {
    padding: 1rem;
    background: #1e293b;
    border-radius: 12px;
    margin-bottom: 1.5rem;
}

.profile-picture {
    border-radius: 50%;
    width: 80px;
    height: 80px;
    object-fit: cover;
    border: 2px solid #60a5fa;
}

footer {
    text-align: center;
    color: #94a3b8;
    padding: 2rem 0;
    font-size: 0.9rem;
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
                timesheet = data.get("timesheet", [])
                valid_timesheet = []
                for task in timesheet:
                    try:
                        pd.to_datetime(task["Submitted"], format='%Y-%m-%d %H:%M:%S')
                        valid_timesheet.append(task)
                    except (ValueError, TypeError):
                        st.warning(f"Invalid timestamp in task {task.get('TaskID', 'Unknown')}")
                st.session_state.timesheet = valid_timesheet
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

# --- Authentication ---
def authenticate_user():
    if not st.session_state.logged_in:
        st.markdown("<div class='card'><h2 class='card-title'>🔐 Login</h2>", unsafe_allow_html=True)
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
                st.rerun()
            else:
                st.error("❌ Invalid credentials")
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

# --- Excel Export Function ---
def export_to_excel(df, sheet_name, file_name):
    output = BytesIO()
    try:
        df_clean = df.drop(columns=['TaskID', 'Attachment'], errors='ignore')
        df_clean = df_clean.replace([np.nan, np.inf, -np.inf], '')
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df_clean.to_excel(writer, index=False, sheet_name=sheet_name)
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            header_format = workbook.add_format({
                'bold': True, 'font_color': 'white', 'bg_color': '#1e3a8a',
                'align': 'center'
            })
            for col_num, col in enumerate(df_clean.columns):
                worksheet.write(0, col_num, col, header_format)
                worksheet.set_column(col_num, col_num, max(len(str(col)), 10) + 2)
        return output.getvalue(), file_name
    except Exception as e:
        st.error(f"⚠️ Failed to export: {e}")
        return None, file_name

# --- Auto Weekly Export ---
def auto_export_weekly():
    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    now = datetime.now(pytz.timezone("Asia/Riyadh"))
    if now.weekday() == 6:
        filename = os.path.join(EXPORT_FOLDER, f"flm_tasks_week_{now.strftime('%Y_%U')}.csv")
        if not os.path.exists(filename):
            df_export = pd.DataFrame(st.session_state.timesheet)
            if not df_export.empty:
                try:
                    df_export = df_export.drop(columns=['TaskID', 'Attachment'], errors='ignore')
                    df_export.to_csv(filename, index=False)
                    st.info(f"✅ Auto-exported to {filename}")
                except Exception as e:
                    st.error(f"⚠️ Export failed: {e}")

# --- Dashboard Stats ---
def render_dashboard_stats(display_df, date_str):
    total_tasks = len(display_df)
    completed_tasks = display_df[display_df['Status'] == '✅ Completed'].shape[0]
    in_progress_tasks = display_df[display_df['Status'] == '🔄 In Progress'].shape[0]
    not_started_tasks = display_df[display_df['Status'] == '⏳ Not Started'].shape[0]

    st.markdown(f"<div class='card'><h3 class='card-title'>📊 Stats for {date_str}</h3>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='stat-card'>Total<br><span>{total_tasks}</span></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='stat-card'>Completed<br><span>{completed_tasks}</span></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='stat-card'>In Progress<br><span>{in_progress_tasks}</span></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='stat-card'>Not Started<br><span>{not_started_tasks}</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Render Analytics ---
def render_analytics(display_df):
    if not display_df.empty:
        st.markdown("<div class='card'><h2 class='card-title'>📈 Task Analytics</h2>", unsafe_allow_html=True)
        unique_dates = sorted(display_df['Date'].unique(), reverse=True)
        for date_str in unique_dates[:3]:  # Limit to recent 3 days
            date_df = display_df[display_df['Date'] == date_str]
            render_dashboard_stats(date_df, date_str)
            col1, col2 = st.columns(2)
            with col1:
                fig = px.histogram(
                    date_df, x="Status", title="Task Status",
                    color="Status", template="plotly_dark",
                    height=300
                )
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with col2:
                fig = px.pie(
                    date_df, names="Category", title="Category Distribution",
                    template="plotly_dark", height=300
                )
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            st.dataframe(date_df.drop(columns=['TaskID', 'Attachment'], errors='ignore'))
            data, file_name = export_to_excel(date_df, f"Tasks_{date_str}", f"tasks_{date_str}.xlsx")
            if data:
                st.download_button(f"⬇️ Download {date_str} Tasks", data, file_name, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("ℹ️ No tasks available.")

# --- Render Uploaded Files ---
def render_all_uploaded_files(df_all):
    st.markdown("<div class='card'><h2 class='card-title'>📎 Uploaded Files</h2>", unsafe_allow_html=True)
    if not df_all.empty and 'Attachment' in df_all.columns:
        attachments = [
            {
                "File Name": row["Attachment"].get("name", "Unknown"),
                "File Type": row["Attachment"].get("type", "Unknown"),
                "Employee": row["Employee"].capitalize(),
                "Task Date": row["Date"],
                "Data": row["Attachment"].get("data"),
                "TaskID": row["TaskID"]
            }
            for _, row in df_all.iterrows() if isinstance(row.get("Attachment"), dict)
        ]
        if attachments:
            for att in attachments:
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                col1.write(att["File Name"])
                col2.write(att["File Type"])
                col3.write(att["Employee"])
                col4.download_button("⬇️", base64.b64decode(att["Data"]), att["File Name"], att["File Type"], key=f"download_{att['TaskID']}")
        else:
            st.info("ℹ️ No files uploaded.")
    else:
        st.info("ℹ️ No attachments found.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Settings ---
def render_settings():
    st.markdown("<div class='card'><h2 class='card-title'>⚙️ Settings</h2>", unsafe_allow_html=True)
    user = st.session_state.user_role
    profile = USER_PROFILE.get(user, {"name": "", "email": "", "picture": None})
    
    with st.form("profile_form"):
        st.markdown("<h3>👤 Profile</h3>", unsafe_allow_html=True)
        name = st.text_input("Name", profile["name"])
        email = st.text_input("Email", profile["email"])
        picture = st.file_uploader("Profile Picture", type=["png", "jpg", "jpeg"])
        if st.form_submit_button("💾 Save"):
            USER_PROFILE[user]["name"] = name
            USER_PROFILE[user]["email"] = email
            if picture:
                img = Image.open(picture).resize((80, 80))
                USER_PROFILE[user]["picture"] = img
            save_data()
            st.success("✅ Profile updated!")
            st.rerun()
    
    with st.form("password_form"):
        st.markdown("<h3>🔑 Password</h3>", unsafe_allow_html=True)
        current = st.text_input("Current Password", type="password")
        new = st.text_input("New Password", type="password")
        confirm = st.text_input("Confirm New Password", type="password")
        if st.form_submit_button("🔄 Change"):
            if current == USERS[user]["pass"] and new == confirm and new:
                USERS[user]["pass"] = new
                save_data()
                st.success("✅ Password changed!")
                st.rerun()
            else:
                st.error("⚠️ Password mismatch or incorrect!")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Download Tasks ---
def render_download_tasks():
    st.markdown("<div class='card'><h2 class='card-title'>⬇️ Download Tasks</h2>", unsafe_allow_html=True)
    user = st.session_state.user_role
    df_user = pd.DataFrame(st.session_state.timesheet)
    df_user = df_user[df_user['Employee'] == user] if not df_user.empty else pd.DataFrame()
    
    if not df_user.empty:
        tz = pytz.timezone("Asia/Riyadh")
        col1, col2, col3 = st.columns(3)
        with col1:
            start = st.date_input("Start Date", datetime.now(tz) - timedelta(days=7))
        with col2:
            end = st.date_input("End Date", datetime.now(tz))
        with col3:
            category = st.selectbox("Category", ["All"] + CATEGORIES)
        priority = st.selectbox("Priority", ["All"] + TASK_PRIORITIES)
        
        filtered_df = df_user
        if category != "All":
            filtered_df = filtered_df[filtered_df['Category'] == category]
        if priority != "All":
            filtered_df = filtered_df[filtered_df['Priority'] == priority]
        filtered_df = filtered_df[(filtered_df['Date'] >= start.strftime('%Y-%m-%d')) & (filtered_df['Date'] <= end.strftime('%Y-%m-%d'))]
        
        st.dataframe(filtered_df.drop(columns=['TaskID', 'Attachment'], errors='ignore'))
        file_name = f"{user}_tasks_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.xlsx"
        data, file_name = export_to_excel(filtered_df, f"{user}_Tasks", file_name)
        if data:
            st.download_button("⬇️ Download", data, file_name, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("ℹ️ No tasks available.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Admin Download Tasks ---
def render_admin_download_tasks():
    if st.session_state.user_role_type == "Admin":
        st.markdown("<div class='card'><h2 class='card-title'>🛠 Admin: Download Tasks</h2>", unsafe_allow_html=True)
        df_all = pd.DataFrame(st.session_state.timesheet)
        if not df_all.empty:
            employees = df_all['Employee'].unique().tolist()
            selected = st.selectbox("Employee", employees)
            emp_tasks = df_all[df_all['Employee'] == selected]
            if not emp_tasks.empty:
                data, file_name = export_to_excel(emp_tasks, f"{selected}_Tasks", f"{selected}_tasks.xlsx")
                if data:
                    st.download_button(f"⬇️ Download {selected.capitalize()} Tasks", data, file_name, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.info(f"ℹ️ No tasks for {selected}.")
        else:
            st.info("ℹ️ No tasks recorded.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- Header ---
def render_header():
    tz = pytz.timezone("Asia/Riyadh")
    st.markdown(f"""
        <div class='header'>
            <div class='company-logo'>INTERSOFT Dashboard</div>
            <div class='user-info'>
                👋 {st.session_state.user_role.capitalize()} ({st.session_state.user_role_type})<br>
                <small>{datetime.now(tz).strftime('%A, %B %d, %Y - %I:%M %p')}</small>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    tabs = ["Dashboard", "Add Task", "Edit/Delete Task", "Employee Work", "Settings", "Download Tasks"]
    if st.session_state.user_role_type == "Admin":
        tabs.append("Admin Panel")
    
    st.markdown("<div class='nav-bar'>", unsafe_allow_html=True)
    cols = st.columns(len(tabs))
    for idx, tab in enumerate(tabs):
        with cols[idx]:
            if st.button(tab, key=f"nav_{tab}", type="primary" if st.session_state.selected_tab == tab else "secondary"):
                st.session_state.selected_tab = tab
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- Sidebar Stats ---
def render_sidebar_stats():
    tz = pytz.timezone("Asia/Riyadh")
    today_str = datetime.now(tz).strftime('%Y-%m-%d')
    st.sidebar.markdown(f"<h3>📊 Today's Stats ({today_str})</h3>", unsafe_allow_html=True)
    df_all = pd.DataFrame(st.session_state.timesheet)
    if not df_all.empty:
        today_df = df_all[df_all['Date'] == today_str]
        for employee in sorted(today_df['Employee'].unique()):
            emp_df = today_df[today_df['Employee'] == employee]
            total = len(emp_df)
            completed = emp_df[emp_df['Status'] == '✅ Completed'].shape[0]
            st.sidebar.markdown(f"""
                <div class='stat-card'>
                    {employee.capitalize()}<br>
                    <span>{total}</span>
                    <small>Completed: {completed}</small>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.info("ℹ️ No tasks today.")

# --- Alerts ---
def render_alerts(df_user, df_all):
    tz = pytz.timezone("Asia/Riyadh")
    today_str = datetime.now(tz).strftime('%Y-%m-%d')
    if st.session_state.user_role_type != "Admin":
        if df_user.empty or today_str not in df_user['Date'].values:
            st.sidebar.markdown("<div class='alert'>⚠️ No tasks submitted today!</div>", unsafe_allow_html=True)
        if st.session_state.user_role_type == "Supervisor":
            for user in USERS.keys():
                if USERS[user]["role"] != "Admin" and (user not in df_all['Employee'].unique() or today_str not in df_all[df_all['Employee'] == user]['Date'].values):
                    st.sidebar.markdown(f"<div class='alert'>🔔 {user.capitalize()} has no tasks today!</div>", unsafe_allow_html=True)
        for reminder in st.session_state.reminders:
            if reminder["user"] == st.session_state.user_role and reminder["date"] == today_str:
                st.sidebar.markdown(f"<div class='alert reminder'>🔔 Reminder: {reminder['task_desc'][:20]}... Due: {reminder['due_date']}</div>", unsafe_allow_html=True)

# --- Add Task ---
def render_add_task():
    st.markdown("<div class='card'><h2 class='card-title'>➕ Add Task</h2>", unsafe_allow_html=True)
    tz = pytz.timezone("Asia/Riyadh")
    with st.form("task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            shift = st.selectbox("Shift", SHIFTS)
            date = st.date_input("Date", datetime.now(tz))
            dept = st.selectbox("Department", DEPARTMENTS)
        with col2:
            category = st.selectbox("Category", CATEGORIES)
            status = st.selectbox("Status", TASK_STATUSES)
            priority = st.selectbox("Priority", TASK_PRIORITIES)
        desc = st.text_area("Description", height=100)
        attachment = st.file_uploader("Attachment (Optional)", type=["png", "jpg", "jpeg", "pdf", "xlsx"])
        set_reminder = st.checkbox("Set Reminder") if status == "⏳ Not Started" else False
        reminder_date = st.date_input("Reminder Due Date", datetime.now(tz) + timedelta(days=1)) if set_reminder else None
        
        if st.form_submit_button("✅ Submit"):
            if desc.strip():
                task = {
                    "TaskID": str(uuid.uuid4()),
                    "Employee": st.session_state.user_role,
                    "Date": date.strftime('%Y-%m-%d'),
                    "Day": calendar.day_name[date.weekday()],
                    "Shift": shift,
                    "Department": dept,
                    "Category": category,
                    "Status": status,
                    "Priority": priority,
                    "Description": desc,
                    "Submitted": datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'),
                    "Attachment": None
                }
                if attachment and attachment.size <= 5 * 1024 * 1024:
                    task["Attachment"] = {
                        "name": attachment.name,
                        "data": base64.b64encode(attachment.read()).decode('utf-8'),
                        "type": attachment.type
                    }
                st.session_state.timesheet.append(task)
                if set_reminder and status == "⏳ Not Started":
                    st.session_state.reminders.append({
                        "user": st.session_state.user_role,
                        "task_id": task["TaskID"],
                        "task_desc": desc,
                        "date": datetime.now(tz).strftime('%Y-%m-%d'),
                        "due_date": reminder_date.strftime('%Y-%m-%d')
                    })
                save_data()
                st.success("🎉 Task added!")
                st.rerun()
            else:
                st.error("⚠️ Description required!")
        st.markdown("</div>", unsafe_allow_html=True)

# --- Edit/Delete Task ---
def render_edit_delete_task(display_df):
    st.markdown("<div class='card'><h2 class='card-title'>✏️ Edit/Delete Task</h2>", unsafe_allow_html=True)
    if not display_df.empty:
        task_dict = {f"{row['Description'][:20]}... ({row['Date']} | {row['Category']})": row["TaskID"] for _, row in display_df.iterrows()}
        selected_id = st.selectbox("Select Task", list(task_dict.keys()))
        selected_id = task_dict[selected_id]
        task = display_df[display_df["TaskID"] == selected_id].iloc[0]
        
        if isinstance(task.get("Attachment"), dict):
            st.markdown(f"<p>File: {task['Attachment']['name']}</p>", unsafe_allow_html=True)
            if task['Attachment']['type'].startswith("image/"):
                st.image(base64.b64decode(task['Attachment']['data']), width=150)
            st.download_button("⬇️ Download", base64.b64decode(task['Attachment']['data']), task['Attachment']['name'], task['Attachment']['type'])
        
        with st.form("edit_form"):
            col1, col2 = st.columns(2)
            with col1:
                shift = st.selectbox("Shift", SHIFTS, index=SHIFTS.index(task["Shift"]))
                date = st.date_input("Date", datetime.strptime(task["Date"], '%Y-%m-%d'))
                dept = st.selectbox("Department", DEPARTMENTS, index=DEPARTMENTS.index(task["Department"]))
            with col2:
                category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(task["Category"]))
                status = st.selectbox("Status", TASK_STATUSES, index=TASK_STATUSES.index(task["Status"]))
                priority = st.selectbox("Priority", TASK_PRIORITIES, index=TASK_PRIORITIES.index(task["Priority"]))
            desc = st.text_area("Description", task["Description"], height=100)
            attachment = st.file_uploader("New Attachment", type=["png", "jpg", "jpeg", "pdf", "xlsx"])
            set_reminder = st.checkbox("Set Reminder") if status == "⏳ Not Started" else False
            reminder_date = st.date_input("Reminder Due Date", datetime.now(pytz.timezone("Asia/Riyadh")) + timedelta(days=1)) if set_reminder else None
            
            if st.form_submit_button("💾 Save"):
                if desc.strip():
                    for i, t in enumerate(st.session_state.timesheet):
                        if t["TaskID"] == selected_id:
                            st.session_state.timesheet[i] = {
                                "TaskID": selected_id,
                                "Employee": task["Employee"],
                                "Date": date.strftime('%Y-%m-%d'),
                                "Day": calendar.day_name[date.weekday()],
                                "Shift": shift,
                                "Department": dept,
                                "Category": category,
                                "Status": status,
                                "Priority": priority,
                                "Description": desc,
                                "Submitted": datetime.now(pytz.timezone("Asia/Riyadh")).strftime('%Y-%m-%d %H:%M:%S'),
                                "Attachment": t.get("Attachment")
                            }
                            if attachment and attachment.size <= 5 * 1024 * 1024:
                                st.session_state.timesheet[i]["Attachment"] = {
                                    "name": attachment.name,
                                    "data": base64.b64encode(attachment.read()).decode('utf-8'),
                                    "type": attachment.type
                                }
                            if set_reminder and status == "⏳ Not Started":
                                st.session_state.reminders = [r for r in st.session_state.reminders if r["task_id"] != selected_id]
                                st.session_state.reminders.append({
                                    "user": task["Employee"],
                                    "task_id": selected_id,
                                    "task_desc": desc,
                                    "date": datetime.now(pytz.timezone("Asia/Riyadh")).strftime('%Y-%m-%d'),
                                    "due_date": reminder_date.strftime('%Y-%m-%d')
                                })
                    save_data()
                    st.success("✅ Task updated!")
                    st.rerun()
                else:
                    st.error("⚠️ Description required!")
        
        with st.form("delete_form"):
            st.warning("⚠️ This action is permanent!")
            if st.checkbox("Confirm Delete") and st.form_submit_button("🗑 Delete", type="primary"):
                if task["Employee"] == st.session_state.user_role or st.session_state.user_role_type == "Admin":
                    st.session_state.timesheet = [t for t in st.session_state.timesheet if t["TaskID"] != selected_id]
                    st.session_state.reminders = [r for r in st.session_state.reminders if r["task_id"] != selected_id]
                    save_data()
                    st.warning("🗑 Task deleted!")
                    st.rerun()
                else:
                    st.error("⚠️ Permission denied!")
    else:
        st.info("ℹ️ No tasks to edit.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Employee Work ---
def render_employee_work():
    st.markdown("<div class='card'><h2 class='card-title'>👥 Employee Work</h2>", unsafe_allow_html=True)
    df_all = pd.DataFrame(st.session_state.timesheet)
    if not df_all.empty:
        tz = pytz.timezone("Asia/Riyadh")
        col1, col2 = st.columns(2)
        with col1:
            user = st.selectbox("Employee", ["All"] + df_all['Employee'].unique().tolist())
        with col2:
            start = st.date_input("Start Date", datetime.now(tz) - timedelta(days=7))
            end = st.date_input("End Date", datetime.now(tz))
        filtered_df = df_all
        if user != "All":
            filtered_df = filtered_df[filtered_df['Employee'] == user]
        filtered_df = filtered_df[(filtered_df['Date'] >= start.strftime('%Y-%m-%d')) & (filtered_df['Date'] <= end.strftime('%Y-%m-%d'))]
        st.dataframe(filtered_df.drop(columns=['TaskID', 'Attachment'], errors='ignore'))
    else:
        st.info("ℹ️ No tasks recorded.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Admin Panel ---
def render_admin_panel():
    if st.session_state.user_role_type == "Admin":
        st.markdown("<div class='card'><h2 class='card-title'>🛠 Admin Panel</h2>", unsafe_allow_html=True)
        with st.expander("👤 Manage Users"):
            with st.form("add_user_form"):
                col1, col2 = st.columns(2)
                with col1:
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    role = st.selectbox("Role", ROLES)
                with col2:
                    name = st.text_input("Name")
                    email = st.text_input("Email")
                if st.form_submit_button("➕ Add"):
                    if username.lower() in USERS:
                        st.error("⚠️ Username exists!")
                    elif all([username, password, name, email]):
                        USERS[username.lower()] = {"pass": password, "role": role}
                        USER_PROFILE[username.lower()] = {"name": name, "email": email, "picture": None}
                        save_data()
                        st.success(f"✅ User {username} added!")
                        st.rerun()
                    else:
                        st.error("⚠️ All fields required!")
            
            with st.form("change_role_form"):
                user = st.selectbox("User", [u for u in USERS.keys() if u != st.session_state.user_role])
                new_role = st.selectbox("New Role", ROLES)
                if st.checkbox("Confirm Role Change") and st.form_submit_button("🔄 Change"):
                    USERS[user]["role"] = new_role
                    save_data()
                    st.success(f"✅ Role for {user} changed!")
                    st.rerun()
            
            with st.form("delete_user_form"):
                user = st.selectbox("User to Delete", [u for u in USERS.keys() if u != st.session_state.user_role])
                if st.checkbox("Confirm Delete") and st.form_submit_button("🗑 Delete", type="primary"):
                    del USERS[user]
                    del USER_PROFILE[user]
                    st.session_state.timesheet = [t for t in st.session_state.timesheet if t["Employee"] != user]
                    st.session_state.reminders = [r for r in st.session_state.reminders if r["user"] != user]
                    save_data()
                    st.warning(f"🗑 User {user} deleted!")
                    st.rerun()
        
        with st.expander("📅 Task Management"):
            df_all = pd.DataFrame(st.session_state.timesheet)
            if not df_all.empty:
                tz = pytz.timezone("Asia/Riyadh")
                col1, col2, col3 = st.columns(3)
                with col1:
                    user = st.selectbox("Employee", ["All"] + df_all['Employee'].unique().tolist())
                with col2:
                    start = st.date_input("Start Date", datetime.now(tz) - timedelta(days=7))
                with col3:
                    end = st.date_input("End Date", datetime.now(tz))
                filtered_df = df_all
                if user != "All":
                    filtered_df = filtered_df[filtered_df['Employee'] == user]
                filtered_df = filtered_df[(filtered_df['Date'] >= start.strftime('%Y-%m-%d')) & (filtered_df['Date'] <= end.strftime('%Y-%m-%d'))]
                st.dataframe(filtered_df.drop(columns=['TaskID', 'Attachment'], errors='ignore'))
                data, file_name = export_to_excel(filtered_df, "Filtered_Tasks", f"tasks_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.xlsx")
                if data:
                    st.download_button("⬇️ Download", data, file_name, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                
                st.markdown("<h3>✏️ Edit Task</h3>", unsafe_allow_html=True)
                task_dict = {f"{row['Description'][:20]}... ({row['Date']} | {row['Category']})": row["TaskID"] for _, row in df_all.iterrows()}
                selected_id = st.selectbox("Select Task", list(task_dict.keys()))
                task = df_all[df_all["TaskID"] == task_dict[selected_id]].iloc[0]
                
                if isinstance(task.get("Attachment"), dict):
                    st.markdown(f"<p>File: {task['Attachment']['name']}</p>", unsafe_allow_html=True)
                    if task['Attachment']['type'].startswith("image/"):
                        st.image(base64.b64decode(task['Attachment']['data']), width=150)
                    st.download_button("⬇️ Download", base64.b64decode(task['Attachment']['data']), task['Attachment']['name'], task['Attachment']['type'])
                
                with st.form("admin_edit_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        shift = st.selectbox("Shift", SHIFTS, index=SHIFTS.index(task["Shift"]))
                        date = st.date_input("Date", datetime.strptime(task["Date"], '%Y-%m-%d'))
                        dept = st.selectbox("Department", DEPARTMENTS, index=DEPARTMENTS.index(task["Department"]))
                    with col2:
                        category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(task["Category"]))
                        status = st.selectbox("Status", TASK_STATUSES, index=TASK_STATUSES.index(task["Status"]))
                        priority = st.selectbox("Priority", TASK_PRIORITIES, index=TASK_PRIORITIES.index(task["Priority"]))
                    desc = st.text_area("Description", task["Description"], height=100)
                    attachment = st.file_uploader("New Attachment", type=["png", "jpg", "jpeg", "pdf", "xlsx"])
                    set_reminder = st.checkbox("Set Reminder") if status == "⏳ Not Started" else False
                    reminder_date = st.date_input("Reminder Due Date", datetime.now(tz) + timedelta(days=1)) if set_reminder else None
                    
                    if st.form_submit_button("💾 Save"):
                        if desc.strip():
                            for i, t in enumerate(st.session_state.timesheet):
                                if t["TaskID"] == task["TaskID"]:
                                    st.session_state.timesheet[i] = {
                                        "TaskID": task["TaskID"],
                                        "Employee": task["Employee"],
                                        "Date": date.strftime('%Y-%m-%d'),
                                        "Day": calendar.day_name[date.weekday()],
                                        "Shift": shift,
                                        "Department": dept,
                                        "Category": category,
                                        "Status": status,
                                        "Priority": priority,
                                        "Description": desc,
                                        "Submitted": datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'),
                                        "Attachment": t.get("Attachment")
                                    }
                                    if attachment and attachment.size <= 5 * 1024 * 1024:
                                        st.session_state.timesheet[i]["Attachment"] = {
                                            "name": attachment.name,
                                            "data": base64.b64encode(attachment.read()).decode('utf-8'),
                                            "type": attachment.type
                                        }
                                    if set_reminder and status == "⏳ Not Started":
                                        st.session_state.reminders = [r for r in st.session_state.reminders if r["task_id"] != task["TaskID"]]
                                        st.session_state.reminders.append({
                                            "user": task["Employee"],
                                            "task_id": task["TaskID"],
                                            "task_desc": desc,
                                            "date": datetime.now(tz).strftime('%Y-%m-%d'),
                                            "due_date": reminder_date.strftime('%Y-%m-%d')
                                        })
                            save_data()
                            st.success("✅ Task updated!")
                            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- Main App ---
if __name__ == "__main__":
    initialize_session()
    authenticate_user()
    
    st.sidebar.title("🔒 Session")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_role_type = None
        st.session_state.reminders = []
        st.session_state.selected_tab = "Dashboard"
        save_data()
        st.rerun()
    
    if st.session_state.logged_in:
        st.markdown("<div class='main-container'>", unsafe_allow_html=True)
        df_all = pd.DataFrame(st.session_state.timesheet)
        df_user = df_all[df_all['Employee'] == st.session_state.user_role] if not df_all.empty else pd.DataFrame()
        render_alerts(df_user, df_all)
        render_sidebar_stats()
        display_df = df_user if st.session_state.user_role_type == "Employee" else df_all
        render_header()
        
        if st.session_state.selected_tab == "Dashboard":
            render_analytics(display_df)
            render_all_uploaded_files(df_all)
            render_admin_download_tasks()
            auto_export_weekly()
        elif st.session_state.selected_tab == "Add Task":
            render_add_task()
        elif st.session_state.selected_tab == "Edit/Delete Task":
            render_edit_delete_task(display_df)
        elif st.session_state.selected_tab == "Employee Work":
            render_employee_work()
        elif st.session_state.selected_tab == "Settings":
            render_settings()
        elif st.session_state.selected_tab == "Download Tasks":
            render_download_tasks()
        elif st.session_state.selected_tab == "Admin Panel":
            render_admin_panel()
        
        st.markdown(f"<footer>© INTERSOFT {datetime.now(pytz.timezone('Asia/Riyadh')).strftime('%Y')}</footer>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
