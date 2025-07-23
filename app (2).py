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
    "yaman": {"pass": "YAMAN1", "role": "Employee"},
    "hatem": {"pass": "HATEM2", "role": "Employee"},
    "qusai": {"pass": "QUSAI4", "role": "Employee"},
    "mahmoud": {"pass": "mahmoud4", "role": "Employee"},
    "mohammad aleem": {"pass": "moh00", "role": "Admin"},
}
USER_PROFILE = {
    "yaman": {"name": "Yaman", "picture": None},
    "hatem": {"name": "Hatem", "picture": None},
    "qusai": {"name": "Qusai", "picture": None},
    "mahmoud": {"name": "Mahmoud", "picture": None},
    "mohammad aleem": {"name": "Mohammad Aleem", "picture": None},
}
EXPORT_FOLDER = "weekly_exports"
DATA_FILE = "data.json"
TASK_STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]
TASK_PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
DEPARTMENTS = ["FLM", "Tech Support", "CRM"]
CATEGORIES = ["Job Orders", "CRM", "Meetings", "Paperwork"]
SHIFTS = ["Morning", "Evening"]
ROLES = ["Admin", "Supervisor", "Employee"]
TASK_COLUMNS = [
    "TaskID", "Employee", "Date", "Day", "Shift", "Department",
    "Category", "Status", "Priority", "Description", "Submitted", "Attachment"
]

# --- Page Config ---
st.set_page_config(page_title="INTERSOFT Time Sheet", page_icon="⚡", layout="wide")

# --- Embed CSS ---
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

/* Define color variables for consistency */
:root {
    --primary-blue: #1E3A8A;
    --secondary-blue: #2563EB;
    --accent-yellow: #FCD34D;
    --dark-bg: #0F172A;
    --card-bg: #1E293B;
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
}

/* Global styles */
* {
    font-family: 'Inter', sans-serif;
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

/* Main container */
.main-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 1.5rem;
    background: var(--dark-bg);
    min-height: 100vh;
}

/* Header */
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    background: var(--primary-blue);
    border-radius: 10px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}

.company-logo {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--accent-yellow);
}

.user-info {
    text-align: right;
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.user-info b {
    color: var(--text-primary);
    font-weight: 600;
}

/* Navigation bar */
.nav-bar {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: var(--card-bg);
    border-radius: 10px;
}

.nav-button {
    background: var(--primary-blue);
    color: var(--text-primary);
    padding: 0.7rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.9rem;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.nav-button:hover, .nav-button.active {
    background: var(--accent-yellow);
    color: var(--primary-blue);
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(252, 211, 77, 0.4);
}

/* Cards */
.card {
    background: var(--card-bg);
    padding: 1.5rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
    transition: transform 0.3s ease;
}

.card:hover {
    transform: translateY(-3px);
}

.card-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--accent-yellow);
    margin-bottom: 1rem;
    text-align: left;
}

/* Stat cards */
.stat-card {
    text-align: center;
    padding: 1rem;
    background: var(--primary-blue);
    border-radius: 8px;
    color: var(--text-primary);
    margin-bottom: 0.75rem;
}

.stat-card span {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent-yellow);
    display: block;
    margin-bottom: 0.3rem;
}

/* Alerts */
.alert {
    background: #7F1D1D;
    color: var(--text-primary);
    padding: 0.8rem;
    border-radius: 8px;
    margin-bottom: 0.75rem;
    font-size: 0.85rem;
    animation: slideIn 0.5s ease;
}

.alert.reminder {
    background: #D97706;
}

@keyframes slideIn {
    from { transform: translateY(-10px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

/* Streamlit button styles */
.stButton>button {
    background: var(--primary-blue);
    color: var(--text-primary);
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
    font-size: 0.9rem;
    border: none;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background: var(--accent-yellow);
    color: var(--primary-blue);
    transform: translateY(-2px);
}

.stButton>button.delete-button {
    background: #7F1D1D;
}

.stButton>button.delete-button:hover {
    background: #B91C1C;
    color: var(--text-primary);
}

/* Streamlit input styles */
.stTextInput input, .stSelectbox select, .stDateInput input {
    background: var(--primary-blue);
    color: var(--text-primary);
    border-radius: 8px;
    padding: 0.6rem;
    border: 1px solid var(--text-secondary);
}

.stTextInput input:focus, .stSelectbox select:focus, .stDateInput input:focus {
    border-color: var(--accent-yellow);
    box-shadow: 0 0 5px rgba(252, 211, 77, 0.4);
}

/* Streamlit table styles */
.stDataFrame table {
    background: var(--card-bg);
    border-radius: 8px;
    color: var(--text-primary);
}

.stDataFrame th {
    background: var(--primary-blue);
    color: var(--text-primary);
    font-weight: 600;
}

.stDataFrame td {
    border-bottom: 1px solid var(--text-secondary);
    padding: 0.8rem;
}

/* Chart container */
.chart-container {
    padding: 1rem;
    background: var(--card-bg);
    border-radius: 8px;
    margin-bottom: 1.5rem;
}

/* Profile picture */
.profile-picture {
    border-radius: 50%;
    width: 80px;
    height: 80px;
    object-fit: cover;
    border: 2px solid var(--accent-yellow);
    margin-bottom: 1rem;
}

/* Footer */
footer {
    text-align: center;
    color: var(--text-secondary);
    padding: 1.5rem 0;
    font-size: 0.85rem;
}

/* Section divider */
.section-divider {
    border-top: 1px solid var(--text-secondary);
    margin: 1.5rem 0;
}

/* Login page specific styles */
.login-wrapper {
    max-width: 800px;
    margin: 4rem auto;
    display: flex;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
}

.login-left {
    flex: 1;
    background: linear-gradient(135deg, var(--secondary-blue), var(--primary-blue));
    color: var(--text-primary);
    padding: 2rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}

.login-left svg {
    width: 60px;
    height: 60px;
    margin-bottom: 1rem;
}

.login-left h4 {
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.login-left p {
    font-size: 0.9rem;
    opacity: 0.9;
}

.login-right {
    flex: 1;
    background: rgba(17, 24, 39, 0.95);
    padding: 2rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.login-right h2 {
    font-size: 1.5rem;
    color: var(--accent-yellow);
    margin-bottom: 1rem;
    text-align: center;
}

.login-right p {
    text-align: center;
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}

.stButton>button.login-button {
    background: var(--accent-yellow);
    color: var(--primary-blue);
    font-weight: 600;
    border-radius: 8px;
    padding: 0.7rem;
    width: 100%;
}

.stButton>button.login-button:hover {
    background: #FBBF24;
    transform: scale(1.02);
}
</style>
""", unsafe_allow_html=True)

# --- Authentication ---
def authenticate_user():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_role_type = None

    if not st.session_state.logged_in:
        st.markdown("""
        <div class="login-wrapper">
            <div class="login-left">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M12 11c0 1.104-.896 2-2 2s-2-.896-2-2 2-4 2-4 2 2.896 2 4zm4 2c1.104 0 2-.896 2-2s-2-4-2-4-2 2.896-2 4 .896 2 2 2zm-8 2h8m-4 0v5"/>
                </svg>
                <h4>INTERSOFT Time Sheet</h4>
                <p>International Software Company</p>
                <p>Empowering your workflow with intelligent time tracking 🚀</p>
            </div>
            <div class="login-right">
                <h2>🔐 Login</h2>
                <p>Welcome back, let's get to work! ☕</p>
        """, unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Enter your username", key="login_username")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")

        if st.button("Login", key="login_button", type="primary"):
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

        st.markdown("</div></div>", unsafe_allow_html=True)
        st.stop()

# --- Persistent Storage ---
def save_data():
    try:
        data = {
            "timesheet": st.session_state.timesheet,
            "reminders": st.session_state.reminders,
            "user_profile": {
                k: {"name": v["name"], "picture": v["picture"] if not isinstance(v["picture"], Image.Image) else None}
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
                    if (isinstance(task, dict) and
                        all(key in task for key in ["TaskID", "Employee", "Date", "Submitted"]) and
                        isinstance(task["Date"], str) and
                        isinstance(task["Submitted"], str)):
                        try:
                            pd.to_datetime(task["Submitted"], format='%Y-%m-%d %H:%M:%S')
                            pd.to_datetime(task["Date"], format='%Y-%m-%d')
                            valid_timesheet.append(task)
                        except (ValueError, TypeError):
                            st.warning(f"Invalid timestamp in task {task.get('TaskID', 'Unknown')}")
                    else:
                        st.warning(f"Missing or invalid fields in task {task.get('TaskID', 'Unknown')}")
                st.session_state.timesheet = valid_timesheet
                st.session_state.reminders = [
                    r for r in data.get("reminders", [])
                    if isinstance(r, dict) and all(k in r for k in ["user", "task_id", "task_desc", "date", "due_date"])
                ]
                st.session_state.login_log = data.get("login_log", [])
                USERS.update(data.get("users", {}))
                for user, profile in data.get("user_profile", {}).items():
                    if user in USER_PROFILE:
                        USER_PROFILE[user]["name"] = profile.get("name", USER_PROFILE[user]["name"])
                        USER_PROFILE[user]["picture"] = profile.get("picture", None)
                    else:
                        USER_PROFILE[user] = {"name": profile.get("name", ""), "picture": None}
    except Exception as e:
        st.error(f"⚠️ Failed to load data: {e}")

# --- Session Initialization ---
def initialize_session():
    defaults = {
        "logged_in": False,
        "user_role": None,
        "user_role_type": None,
        "timesheet": [],
        "login_log": [],
        "reminders": [],
        "selected_tab": "Dashboard",
        "selected_date": datetime.now(pytz.timezone("Asia/Riyadh")).strftime('%Y-%m-%d')
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    load_data()

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
                'bold': True, 'font_color': 'white', 'bg_color': '#2d3748',
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
    high_priority = display_df[display_df['Priority'] == '🔴 High'].shape[0]
    tasks_by_dept = display_df['Department'].value_counts().to_dict()
    tasks_by_shift = display_df['Shift'].value_counts().to_dict()

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
    
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("<h4>🏬 By Department</h4>", unsafe_allow_html=True)
        for dept, count in tasks_by_dept.items():
            st.markdown(f"<div class='stat-card'>{dept}<br><span>{count}</span></div>", unsafe_allow_html=True)
    with col6:
        st.markdown("<h4>⏰ By Shift</h4>", unsafe_allow_html=True)
        for shift, count in tasks_by_shift.items():
            st.markdown(f"<div class='stat-card'>{shift}<br><span>{count}</span></div>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='stat-card'>High Priority<br><span>{high_priority}</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Render Analytics ---
def render_analytics(display_df):
    tz = pytz.timezone("Asia/Riyadh")
    today_str = datetime.now(tz).strftime('%Y-%m-%d')
    
    st.markdown("<div class='card'><h2 class='card-title'>📈 Task Analytics</h2>", unsafe_allow_html=True)
    
    # Today's Work
    st.markdown("<h3>📅 Today's Work</h3>", unsafe_allow_html=True)
    if not display_df.empty and 'Date' in display_df.columns:
        today_df = display_df[display_df['Date'] == today_str]
        if not today_df.empty:
            render_dashboard_stats(today_df, today_str)
            col1, col2, col3 = st.columns(3)
            with col1:
                fig_status = px.histogram(
                    today_df, x="Status", title="Task Status",
                    color="Status", template="plotly_dark",
                    height=300
                )
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.plotly_chart(fig_status, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with col2:
                fig_category = px.pie(
                    today_df, names="Category", title="Category Distribution",
                    template="plotly_dark", height=300
                )
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.plotly_chart(fig_category, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with col3:
                fig_priority = px.pie(
                    today_df, names="Priority", title="Priority Distribution",
                    template="plotly_dark", height=300
                )
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.plotly_chart(fig_priority, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            st.dataframe(today_df.drop(columns=['TaskID', 'Attachment'], errors='ignore'), use_container_width=True)
            with st.form(key="today_download_form"):
                if st.form_submit_button("⬇️ Download Today's Tasks"):
                    data, file_name = export_to_excel(today_df, f"Tasks_{today_str}", f"tasks_{today_str}.xlsx")
                    if data:
                        st.download_button(
                            label="⬇️ Download Now",
                            data=data,
                            file_name=file_name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_today_{today_str}"
                        )
        else:
            st.info("ℹ️ No tasks for today.")
    else:
        st.info("ℹ️ No tasks available or data is missing required fields.")
    
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    
    # All Work
    st.markdown("<h3>📚 All Work</h3>", unsafe_allow_html=True)
    if not display_df.empty and 'Date' in display_df.columns:
        unique_dates = sorted(display_df['Date'].unique(), reverse=True)
        selected_date = st.selectbox("Filter by Date", ["All"] + unique_dates, key="date_filter")
        filtered_df = display_df if selected_date == "All" else display_df[display_df['Date'] == selected_date]
        
        if not filtered_df.empty:
            render_dashboard_stats(filtered_df, selected_date if selected_date != "All" else "All Time")
            col1, col2, col3 = st.columns(3)
            with col1:
                fig_status = px.histogram(
                    filtered_df, x="Status", title="Task Status",
                    color="Status", template="plotly_dark",
                    height=300
                )
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.plotly_chart(fig_status, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with col2:
                fig_category = px.pie(
                    filtered_df, names="Category", title="Category Distribution",
                    template="plotly_dark", height=300
                )
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.plotly_chart(fig_category, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with col3:
                fig_priority = px.pie(
                    filtered_df, names="Priority", title="Priority Distribution",
                    template="plotly_dark", height=300
                )
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.plotly_chart(fig_priority, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            st.dataframe(filtered_df.drop(columns=['TaskID', 'Attachment'], errors='ignore'), use_container_width=True)
            with st.form(key="all_download_form"):
                if st.form_submit_button("⬇️ Download Tasks"):
                    data, file_name = export_to_excel(filtered_df, f"Tasks_{selected_date if selected_date != 'All' else 'All'}", f"tasks_{selected_date if selected_date != 'All' else 'all'}.xlsx")
                    if data:
                        st.download_button(
                            label="⬇️ Download Now",
                            data=data,
                            file_name=file_name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_all_{selected_date}"
                        )
        else:
            st.info("ℹ️ No tasks for selected date.")
    else:
        st.info("ℹ️ No tasks available or data is missing required fields.")
    st.markdown("</div>", unsafe_allow_html=True)

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
            for _, row in df_all.iterrows() if isinstance(row.get("Attachment"), dict) and row["Attachment"].get("data")
        ]
        if attachments:
            for att in attachments:
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                col1.write(att["File Name"])
                col2.write(att["File Type"])
                col3.write(att["Employee"])
                col4.download_button(
                    "⬇️",
                    base64.b64decode(att["Data"]),
                    att["File Name"],
                    att["File Type"],
                    key=f"download_attachment_{att['TaskID']}"
                )
        else:
            st.info("ℹ️ No files uploaded.")
    else:
        st.info("ℹ️ No attachments found.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Settings ---
def render_settings():
    st.markdown("<div class='card'><h2 class='card-title'>⚙️ Settings</h2>", unsafe_allow_html=True)
    user = st.session_state.user_role
    profile = USER_PROFILE.get(user, {"name": "", "picture": None})
    
    with st.form(key="profile_form"):
        st.markdown("<h3>👤 Profile</h3>", unsafe_allow_html=True)
        if profile["picture"]:
            st.image(base64.b64decode(profile["picture"]), width=80, caption="Profile Picture")
        name = st.text_input("Name", profile["name"], key="profile_name")
        picture = st.file_uploader("Profile Picture", type=["png", "jpg", "jpeg"], key="profile_picture")
        if st.form_submit_button("💾 Save"):
            USER_PROFILE[user]["name"] = name
            if picture:
                img = Image.open(picture).resize((80, 80))
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                USER_PROFILE[user]["picture"] = base64.b64encode(buffered.getvalue()).decode('utf-8')
            save_data()
            st.success("✅ Profile updated!")
            st.rerun()
    
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    with st.form(key="password_form"):
        st.markdown("<h3>🔑 Password</h3>", unsafe_allow_html=True)
        current = st.text_input("Current Password", type="password", key="current_password")
        new = st.text_input("New Password", type="password", key="new_password")
        confirm = st.text_input("Confirm New Password", type="password", key="confirm_password")
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
    df_user = pd.DataFrame(st.session_state.timesheet, columns=TASK_COLUMNS)
    df_user = df_user[df_user['Employee'] == user] if not df_user.empty else pd.DataFrame(columns=TASK_COLUMNS)
    
    if not df_user.empty:
        tz = pytz.timezone("Asia/Riyadh")
        filtered_df = pd.DataFrame(columns=TASK_COLUMNS)
        trigger_download = False
        file_name = None
        excel_data = None
        
        with st.form(key="download_tasks_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                start = st.date_input("Start Date", datetime.now(tz) - timedelta(days=7), key="download_start_date")
            with col2:
                end = st.date_input("End Date", datetime.now(tz), key="download_end_date")
            with col3:
                category = st.selectbox("Category", ["All"] + CATEGORIES, key="download_category")
            priority = st.selectbox("Priority", ["All"] + TASK_PRIORITIES, key="download_priority")
            
            submitted = st.form_submit_button("🔍 Filter and Download")
        
        if submitted:
            filtered_df = df_user
            if category != "All":
                filtered_df = filtered_df[filtered_df['Category'] == category]
            if priority != "All":
                filtered_df = filtered_df[filtered_df['Priority'] == priority]
            filtered_df = filtered_df[(filtered_df['Date'] >= start.strftime('%Y-%m-%d')) & (filtered_df['Date'] <= end.strftime('%Y-%m-%d'))]
            
            if not filtered_df.empty:
                st.dataframe(filtered_df.drop(columns=['TaskID', 'Attachment'], errors='ignore'), use_container_width=True)
                file_name = f"{user}_tasks_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.xlsx"
                excel_data, file_name = export_to_excel(filtered_df, f"{user}_Tasks", file_name)
                trigger_download = True
            else:
                st.info("ℹ️ No tasks match the filters.")
        
        if trigger_download and excel_data:
            st.download_button(
                label="⬇️ Download Now",
                data=excel_data,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"download_tasks_{user}_{start.strftime('%Y%m%d')}"
            )
    else:
        st.info("ℹ️ No tasks available.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Admin Download Tasks ---
def render_admin_download_tasks():
    if st.session_state.user_role_type == "Admin":
        st.markdown("<div class='card'><h2 class='card-title'>🛠 Admin: Download Tasks</h2>", unsafe_allow_html=True)
        df_all = pd.DataFrame(st.session_state.timesheet, columns=TASK_COLUMNS)
        
        if not df_all.empty:
            with st.form(key="admin_download_form"):
                employees = df_all['Employee'].unique().tolist()
                selected = st.selectbox("Employee", employees, key="admin_download_employee")
                submit_download = st.form_submit_button("🔍 Filter and Prepare Download")
            
            if submit_download:
                emp_tasks = df_all[df_all['Employee'] == selected]
                if not emp_tasks.empty:
                    data, file_name = export_to_excel(emp_tasks, f"{selected}_Tasks", f"{selected}_tasks.xlsx")
                    
                    if data and isinstance(file_name, str):
                        st.download_button(
                            label=f"⬇️ Download {selected.capitalize()} Tasks",
                            data=data,
                            file_name=file_name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"admin_download_{selected}"
                        )
                    else:
                        st.error("❌ Failed to generate file.")
                else:
                    st.info(f"ℹ️ No tasks found for {selected}.")
        else:
            st.info("ℹ️ No tasks recorded.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- Header ---
def render_header():
    tz = pytz.timezone("Asia/Riyadh")
    st.markdown(f"""
        <div class='header'>
            <div class='company-logo'>⚡ INTERSOFT Dashboard</div>
            <div class='user-info'>
                👋 {st.session_state.user_role.capitalize()} ({st.session_state.user_role_type})<br>
                <small>{datetime.now(tz).strftime('%A, %B %d, %Y - %I:%M %p')}</small>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    tabs = [
        ("Dashboard", "🏠"),
        ("Add Task", "➕"),
        ("Edit/Delete Task", "✏️"),
        ("Employee Work", "👥"),
        ("Settings", "⚙️"),
        ("Download Tasks", "⬇️")
    ]
    if st.session_state.user_role_type == "Admin":
        tabs.append(("Admin Panel", "🛠"))
    
    st.markdown("<div class='nav-bar'>", unsafe_allow_html=True)
    cols = st.columns(len(tabs))
    for idx, (tab, icon) in enumerate(tabs):
        with cols[idx]:
            if st.button(f"{icon} {tab}", key=f"nav_{tab.lower().replace(' ', '_')}", type="primary" if st.session_state.selected_tab == tab else "secondary"):
                st.session_state.selected_tab = tab
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- Sidebar Stats ---
def render_sidebar_stats():
    tz = pytz.timezone("Asia/Riyadh")
    today_str = datetime.now(tz).strftime('%Y-%m-%d')
    st.sidebar.markdown(f"<h3>📊 Today's Stats ({today_str})</h3>", unsafe_allow_html=True)
    df_all = pd.DataFrame(st.session_state.timesheet, columns=TASK_COLUMNS)
    if not df_all.empty and 'Date' in df_all.columns:
        today_df = df_all[df_all['Date'] == today_str]
        for employee in sorted(today_df['Employee'].unique()):
            emp_df = today_df[today_df['Employee'] == employee]
            total = len(emp_df)
            completed = emp_df[emp_df['Status'] == '✅ Completed'].shape[0]
            st.sidebar.markdown(
                f"""
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
        if df_user.empty or 'Date' not in df_user.columns or today_str not in df_user['Date'].values:
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
    with st.form(key="task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            shift = st.selectbox("Shift", SHIFTS, key="task_shift")
            date = st.date_input("Date", datetime.now(tz), key="task_date")
            dept = st.selectbox("Department", DEPARTMENTS, key="task_dept")
        with col2:
            category = st.selectbox("Category", CATEGORIES, key="task_category")
            status = st.selectbox("Status", TASK_STATUSES, key="task_status")
            priority = st.selectbox("Priority", TASK_PRIORITIES, key="task_priority")
        desc = st.text_area("Description", height=100, key="task_desc")
        attachment = st.file_uploader("Attachment (Optional)", type=["png", "jpg", "jpeg", "pdf", "xlsx"], key="task_attachment")
        set_reminder = st.checkbox("Set Reminder", key="task_reminder") if status == "⏳ Not Started" else False
        reminder_date = st.date_input("Reminder Due Date", datetime.now(tz) + timedelta(days=1), key="task_reminder_date") if set_reminder else None
        
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
    if not display_df.empty and 'TaskID' in display_df.columns:
        task_dict = {f"{row['Description'][:20]}... ({row['Date']} | {row['Category']})": row["TaskID"] for _, row in display_df.iterrows()}
        selected_task = st.selectbox("Select Task", list(task_dict.keys()), key="edit_task_select")
        selected_id = task_dict[selected_task]
        task = display_df[display_df["TaskID"] == selected_id].iloc[0]
        
        if isinstance(task.get("Attachment"), dict):
            st.markdown(f"<p>File: {task['Attachment']['name']}</p>", unsafe_allow_html=True)
            if task['Attachment']['type'].startswith("image/"):
                st.image(base64.b64decode(task['Attachment']['data']), width=150)
            st.download_button(
                label="⬇️ Download Attachment",
                data=base64.b64decode(task['Attachment']['data']),
                file_name=task['Attachment']['name'],
                mime=task['Attachment']['type'],
                key=f"edit_attachment_{task['TaskID']}"
            )
        
        with st.form(key=f"edit_form_{selected_id}"):
            col1, col2 = st.columns(2)
            with col1:
                shift = st.selectbox("Shift", SHIFTS, index=SHIFTS.index(task["Shift"]), key=f"edit_shift_{selected_id}")
                date = st.date_input("Date", datetime.strptime(task["Date"], '%Y-%m-%d'), key=f"edit_date_{selected_id}")
                dept = st.selectbox("Department", DEPARTMENTS, index=DEPARTMENTS.index(task["Department"]), key=f"edit_dept_{selected_id}")
            with col2:
                category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(task["Category"]), key=f"edit_category_{selected_id}")
                status = st.selectbox("Status", TASK_STATUSES, index=TASK_STATUSES.index(task["Status"]), key=f"edit_status_{selected_id}")
                priority = st.selectbox("Priority", TASK_PRIORITIES, index=TASK_PRIORITIES.index(task["Priority"]), key=f"edit_priority_{selected_id}")
            desc = st.text_area("Description", task["Description"], height=100, key=f"edit_desc_{selected_id}")
            attachment = st.file_uploader("New Attachment", type=["png", "jpg", "jpeg", "pdf", "xlsx"], key=f"edit_attachment_upload_{selected_id}")
            set_reminder = st.checkbox("Set Reminder", key=f"edit_reminder_{selected_id}") if status == "⏳ Not Started" else False
            reminder_date = st.date_input("Reminder Due Date", datetime.now(pytz.timezone("Asia/Riyadh")) + timedelta(days=1), key=f"edit_reminder_date_{selected_id}") if set_reminder else None
            
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
        
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        with st.form(key=f"delete_form_{selected_id}"):
            st.warning("⚠️ This action is permanent!")
            if st.form_submit_button("🗑 Delete", type="primary"):
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
    df_all = pd.DataFrame(st.session_state.timesheet, columns=TASK_COLUMNS)
    if not df_all.empty and 'Date' in df_all.columns:
        tz = pytz.timezone("Asia/Riyadh")
        with st.form(key="employee_work_form"):
            col1, col2 = st.columns(2)
            with col1:
                user = st.selectbox("Employee", ["All"] + df_all['Employee'].unique().tolist(), key="employee_work_user")
            with col2:
                start = st.date_input("Start Date", datetime.now(tz) - timedelta(days=7), key="employee_work_start")
                end = st.date_input("End Date", datetime.now(tz), key="employee_work_end")
            if st.form_submit_button("🔍 Filter"):
                filtered_df = df_all
                if user != "All":
                    filtered_df = filtered_df[filtered_df['Employee'] == user]
                filtered_df = filtered_df[(filtered_df['Date'] >= start.strftime('%Y-%m-%d')) & (filtered_df['Date'] <= end.strftime('%Y-%m-%d'))]
                st.dataframe(filtered_df.drop(columns=['TaskID', 'Attachment'], errors='ignore'), use_container_width=True)
    else:
        st.info("ℹ️ No tasks recorded.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Admin Panel ---
def render_admin_panel():
    if st.session_state.user_role_type == "Admin":
        st.markdown("<div class='card'><h2 class='card-title'>🛠 Admin Panel</h2>", unsafe_allow_html=True)
        
        # --- Add User ---
        with st.form(key="add_user_form"):
            st.markdown("<h3>👤 Add User</h3>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Username", key="add_user_username")
                password = st.text_input("Password", type="password", key="add_user_password")
            with col2:
                name = st.text_input("Name", key="add_user_name")
                role = st.selectbox("Role", ROLES, key="add_user_role")
            if st.form_submit_button("➕ Add"):
                if username.lower() in USERS:
                    st.error("⚠️ Username exists!")
                elif all([username, password, name]):
                    USERS[username.lower()] = {"pass": password, "role": role}
                    USER_PROFILE[username.lower()] = {"name": name, "picture": None}
                    save_data()
                    st.success(f"✅ User {username} added!")
                    st.rerun()
                else:
                    st.error("⚠️ All fields required!")
        
        # --- Change Role ---
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        with st.form(key="change_role_form"):
            st.markdown("<h3>🔄 Change Role</h3>", unsafe_allow_html=True)
            user = st.selectbox("User", [u for u in USERS.keys() if u != st.session_state.user_role], key="change_role_user")
            new_role = st.selectbox("New Role", ROLES, key="change_role_new")
            if st.form_submit_button("🔄 Change"):
                USERS[user]["role"] = new_role
                save_data()
                st.success(f"✅ Role for {user} changed!")
                st.rerun()
        
        # --- Delete User ---
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        with st.form(key="delete_user_form"):
            st.markdown("<h3>🗑 Delete User</h3>", unsafe_allow_html=True)
            user = st.selectbox("User to Delete", [u for u in USERS.keys() if u != st.session_state.user_role], key="delete_user_select")
            if st.form_submit_button("🗑 Delete", type="primary"):
                del USERS[user]
                del USER_PROFILE[user]
                st.session_state.timesheet = [t for t in st.session_state.timesheet if t["Employee"] != user]
                st.session_state.reminders = [r for r in st.session_state.reminders if r["user"] != user]
                save_data()
                st.warning(f"🗑 User {user} deleted!")
                st.rerun()
        
        # --- Task Filter ---
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        df_all = pd.DataFrame(st.session_state.timesheet, columns=TASK_COLUMNS)
        if not df_all.empty and 'Date' in df_all.columns:
            st.markdown("<h3>📅 Task Management</h3>", unsafe_allow_html=True)
            tz = pytz.timezone("Asia/Riyadh")
            filtered_df = pd.DataFrame(columns=TASK_COLUMNS)
            data, file_name = None, None
            
            with st.form(key="admin_task_form"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    user = st.selectbox("Employee", ["All"] + df_all['Employee'].unique().tolist(), key="admin_task_user")
                with col2:
                    start = st.date_input("Start Date", datetime.now(tz) - timedelta(days=7), key="admin_task_start")
                with col3:
                    end = st.date_input("End Date", datetime.now(tz), key="admin_task_end")
                
                submitted = st.form_submit_button("🔍 Filter")
            
            if submitted:
                filtered_df = df_all
                if user != "All":
                    filtered_df = filtered_df[filtered_df['Employee'] == user]
                filtered_df = filtered_df[(filtered_df['Date'] >= start.strftime('%Y-%m-%d')) & (filtered_df['Date'] <= end.strftime('%Y-%m-%d'))]
                st.dataframe(filtered_df.drop(columns=['TaskID', 'Attachment'], errors='ignore'), use_container_width=True)
                if not filtered_df.empty:
                    data, file_name = export_to_excel(filtered_df, "Filtered_Tasks", f"tasks_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.xlsx")
            
            if data and file_name:
                st.download_button(
                    label="⬇️ Download Filtered Tasks",
                    data=data,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"admin_task_download_{start.strftime('%Y%m%d')}"
                )
        
        # --- Edit Task ---
        if not df_all.empty and 'TaskID' in df_all.columns:
            st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
            st.markdown("<h3>✏️ Edit Task</h3>", unsafe_allow_html=True)
            task_dict = {f"{row['Description'][:20]}... ({row['Date']} | {row['Category']})": row["TaskID"] for _, row in df_all.iterrows()}
            selected_task = st.selectbox("Select Task", list(task_dict.keys()), key="admin_edit_task_select")
            task = df_all[df_all["TaskID"] == task_dict[selected_task]].iloc[0]
            
            if isinstance(task.get("Attachment"), dict):
                st.markdown(f"<p>File: {task['Attachment']['name']}</p>", unsafe_allow_html=True)
                if task['Attachment']['type'].startswith("image/"):
                    st.image(base64.b64decode(task['Attachment']['data']), width=150)
                st.download_button(
                    label="⬇️ Download Attachment",
                    data=base64.b64decode(task['Attachment']['data']),
                    file_name=task['Attachment']['name'],
                    mime=task['Attachment']['type'],
                    key=f"admin_attachment_{task['TaskID']}"
                )
            
            with st.form(key=f"admin_edit_task_form_{task['TaskID']}"):
                col1, col2 = st.columns(2)
                with col1:
                    shift = st.selectbox("Shift", SHIFTS, index=SHIFTS.index(task["Shift"]), key=f"admin_edit_shift_{task['TaskID']}")
                    date = st.date_input("Date", datetime.strptime(task["Date"], '%Y-%m-%d'), key=f"admin_edit_date_{task['TaskID']}")
                    dept = st.selectbox("Department", DEPARTMENTS, index=DEPARTMENTS.index(task["Department"]), key=f"admin_edit_dept_{task['TaskID']}")
                with col2:
                    category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(task["Category"]), key=f"admin_edit_category_{task['TaskID']}")
                    status = st.selectbox("Status", TASK_STATUSES, index=TASK_STATUSES.index(task["Status"]), key=f"admin_edit_status_{task['TaskID']}")
                    priority = st.selectbox("Priority", TASK_PRIORITIES, index=TASK_PRIORITIES.index(task["Priority"]), key=f"admin_edit_priority_{task['TaskID']}")
                desc = st.text_area("Description", task["Description"], height=100, key=f"admin_edit_desc_{task['TaskID']}")
                attachment = st.file_uploader("New Attachment", type=["png", "jpg", "jpeg", "pdf", "xlsx"], key=f"admin_edit_attachment_{task['TaskID']}")
                set_reminder = st.checkbox("Set Reminder", key=f"admin_edit_reminder_{task['TaskID']}") if status == "⏳ Not Started" else False
                reminder_date = st.date_input("Reminder Due Date", datetime.now(tz) + timedelta(days=1), key=f"admin_edit_reminder_date_{task['TaskID']}") if set_reminder else None
                
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
                    else:
                        st.error("⚠️ Description required!")
        
        # --- Delete All Data ---
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        with st.form(key="delete_all_data_form"):
            st.markdown("<h3>🗑 Delete All Data</h3>", unsafe_allow_html=True)
            st.warning("⚠️ This action is permanent and will delete all tasks, reminders, and login logs!")
            if st.form_submit_button("🗑 Delete All Data", type="primary"):
                st.session_state.timesheet = []
                st.session_state.reminders = []
                st.session_state.login_log = []
                save_data()
                st.warning("🗑 All data deleted!")
                st.rerun()
        
        # --- Delete Data for Specific Day ---
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        with st.form(key="delete_day_data_form"):
            st.markdown("<h3>🗑 Delete Data for Specific Day</h3>", unsafe_allow_html=True)
            tz = pytz.timezone("Asia/Riyadh")
            delete_date = st.date_input("Select Date to Delete", datetime.now(tz), key="delete_day_date")
            st.warning("⚠️ This action is permanent and will delete all tasks and reminders for the selected date!")
            if st.form_submit_button("🗑 Delete Day Data", type="primary"):
                delete_date_str = delete_date.strftime('%Y-%m-%d')
                st.session_state.timesheet = [t for t in st.session_state.timesheet if t["Date"] != delete_date_str]
                st.session_state.reminders = [r for r in st.session_state.reminders if r["date"] != delete_date_str]
                save_data()
                st.warning(f"🗑 Data for {delete_date_str} deleted!")
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

# --- Main App ---
if __name__ == "__main__":
    initialize_session()
    authenticate_user()
    
    st.sidebar.title("🔒 Session")
    if st.sidebar.button("Logout", key="logout_button"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_role_type = None
        st.session_state.reminders = []
        st.session_state.selected_tab = "Dashboard"
        save_data()
        st.rerun()
    
    if st.session_state.logged_in:
        st.markdown("<div class='main-container'>", unsafe_allow_html=True)
        df_all = pd.DataFrame(st.session_state.timesheet, columns=TASK_COLUMNS)
        df_user = df_all[df_all['Employee'] == st.session_state.user_role] if not df_all.empty else pd.DataFrame(columns=TASK_COLUMNS)
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
