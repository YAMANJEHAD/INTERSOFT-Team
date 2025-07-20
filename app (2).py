# FLM Task Tracker – Full Version with Admin Panel, Roles, Alerts, Calendar + Auto Export Weekly + Persistent Storage + Main Interface

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import calendar
from io import BytesIO
import uuid
import os
import calplot
import matplotlib.pyplot as plt

# --- Page Config ---
st.set_page_config("⚡ INTERSOFT Dashboard | FLM", layout="wide", page_icon="🚀")

# --- Styling ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: radial-gradient(circle at top left, #0f172a, #1e293b);
    color: #f8fafc;
}
.top-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0 2rem; margin-top: 1rem;
}
.greeting { font-size: 1rem; font-weight: 500; color: #fcd34d; text-align: right; }
.company { font-size: 1.2rem; font-weight: 600; color: #60a5fa; }
.date-box {
    font-size: 1rem; font-weight: 500; color: #f8fafc; text-align: center;
    background: #1e293b; padding: 0.5rem 1rem; border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3); margin-bottom: 1.5rem; display: inline-block;
}
.overview-box {
    background: linear-gradient(to bottom right, #1e3a8a, #3b82f6);
    padding: 1.5rem; border-radius: 18px; text-align: center;
    margin: 1rem 0; transition: transform 0.4s ease;
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
}
.overview-box:hover { transform: translateY(-5px) scale(1.02); }
.overview-box span { font-size: 2.2rem; font-weight: 800; color: #fcd34d; }
footer { text-align: center; color: #94a3b8; padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- Users & Roles ---
USERS = {
    "Yaman": {"pass": "YAMAN1", "role": "Admin"},
    "Hatem": {"pass": "HATEM2", "role": "Supervisor"},
    "Qusai": {"pass": "QUSAI4", "role": "Employee"},
}

# --- Paths ---
DATA_FILE = "data/tasks.csv"
EXPORT_FOLDER = "weekly_exports"
os.makedirs("data", exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)

REQUIRED_COLUMNS = ["TaskID", "Employee", "Date", "Day", "Shift", "Department", "Category", "Status", "Priority", "Description", "Submitted"]

# --- Session Init ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_role_type = None
    st.session_state.login_log = []

# --- Load Persistent Data ---
if "timesheet" not in st.session_state:
    if os.path.exists(DATA_FILE):
        df_temp = pd.read_csv(DATA_FILE)
        for col in REQUIRED_COLUMNS:
            if col not in df_temp.columns:
                df_temp[col] = ""
        st.session_state.timesheet = df_temp[REQUIRED_COLUMNS].to_dict("records")
    else:
        st.session_state.timesheet = []

if "login_log" not in st.session_state:
    st.session_state.login_log = []

# --- Save Persistent Data Function ---
def save_data():
    pd.DataFrame(st.session_state.timesheet).to_csv(DATA_FILE, index=False)

# --- Authentication ---
if not st.session_state.logged_in:
    st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>🔐 INTERSOFT Task Tracker</div></div>", unsafe_allow_html=True)
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    if st.button("Login 🚀"):
        user = USERS.get(username)
        if user and user["pass"] == password:
            st.session_state.logged_in = True
            st.session_state.user_role = username
            st.session_state.user_role_type = user["role"]
            st.session_state.login_log.append({"user": username, "time": datetime.now().strftime("%Y-%m-%d %I:%M %p")})
            st.rerun()
        else:
            st.error("❌ Invalid credentials")
    st.stop()

# --- Auto Weekly Export ---
def auto_export_weekly():
    now = datetime.now()
    if now.weekday() == 6:
        filename = os.path.join(EXPORT_FOLDER, f"flm_tasks_week_{now.strftime('%Y_%U')}.csv")
        if not os.path.exists(filename):
            df_export = pd.DataFrame(st.session_state.timesheet)
            if not df_export.empty:
                df_export.to_csv(filename, index=False)
                print(f"✅ Auto-exported weekly tasks to {filename}")

# --- Alert for Delayed Tasks ---
def show_late_task_alert():
    df = pd.DataFrame(st.session_state.timesheet)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        late_tasks = df[(df["Status"] == "⏳ Not Started") & (df["Date"] < datetime.today())]
        if not late_tasks.empty:
            st.warning(f"🔔 {len(late_tasks)} task(s) are overdue! Please review them.")

# --- Calendar View ---
def show_task_calendar():
    df = pd.DataFrame(st.session_state.timesheet)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df_count = df.groupby("Date").size()
        fig, ax = calplot.calplot(df_count)
        st.pyplot(fig)

# --- Export Button ---
def export_excel_button():
    df = pd.DataFrame(st.session_state.timesheet)
    if df.empty:
        st.info("ℹ️ No tasks to export.")
        return
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Tasks')
        writer.save()
    st.download_button(
        label="📥 Download Tasks Excel",
        data=output.getvalue(),
        file_name="FLM_Tasks_Export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- Admin View: Login History ---
def admin_login_log():
    if st.session_state.user_role_type == "Admin":
        log_df = pd.DataFrame(st.session_state.login_log)
        if not log_df.empty:
            st.markdown("### 🧾 Login Activity")
            st.dataframe(log_df)

# Call auto export & alerts
auto_export_weekly()
show_late_task_alert()

# Optional UI
st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>📊 Dashboard for <b>{}</b> ({})</div></div>".format(st.session_state.user_role, st.session_state.user_role_type), unsafe_allow_html=True)

st.markdown(f"<div class='date-box'>📅 {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}</div>", unsafe_allow_html=True)

# Calendar & Export
with st.expander("📆 Task Calendar"):
    show_task_calendar()

with st.expander("📤 Export Excel"):
    export_excel_button()

admin_login_log()

# --- Main Dashboard: Task Interface ---
st.markdown("### ✅ Add or Manage Tasks")

with st.form("add_task_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        shift = st.selectbox("🕒 Shift", ["Morning", "Evening"])
        task_date = st.date_input("📅 Date", value=date.today())
        department = st.selectbox("🏢 Department", ["FLM", "Tech Support", "CRM"])
    with col2:
        category = st.selectbox("📂 Category", ["Operations", "Paper Work", "Job Orders", "CRM", "Meetings", "TOMS"])
        status = st.selectbox("📌 Status", ["⏳ Not Started", "🔄 In Progress", "✅ Completed"])
        priority = st.selectbox("⚠️ Priority", ["🟢 Low", "🟡 Medium", "🔴 High"])
    description = st.text_area("📝 Task Description")
    submitted = st.form_submit_button("✅ Add Task")

    if submitted and description.strip():
        task = {
            "TaskID": str(uuid.uuid4()),
            "Employee": st.session_state.user_role,
            "Date": task_date.strftime("%Y-%m-%d"),
            "Day": calendar.day_name[task_date.weekday()],
            "Shift": shift,
            "Department": department,
            "Category": category,
            "Status": status,
            "Priority": priority,
            "Description": description,
            "Submitted": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.timesheet.append(task)
        save_data()
        st.success("🎉 Task added successfully!")
        st.experimental_rerun()

# View & Edit Tasks
st.markdown("### 📋 Your Tasks")
df_tasks = pd.DataFrame(st.session_state.timesheet)
if st.session_state.user_role_type != "Admin":
    df_tasks = df_tasks[df_tasks["Employee"] == st.session_state.user_role]
if not df_tasks.empty:
    st.dataframe(df_tasks.sort_values("Date", ascending=False), use_container_width=True)
else:
    st.info("🚫 No tasks available.")

# Footer
st.markdown("<footer>📅 INTERSOFT FLM Tracker • {} </footer>".format(datetime.now().strftime("%A, %B %d, %Y - %I:%M %p")), unsafe_allow_html=True)
