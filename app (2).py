# FLM Task Tracker – Full Version with Admin Panel, Roles, Alerts, Calendar + Auto Export Weekly

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import calendar
from io import BytesIO
import uuid
import os

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

# --- Session Init ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_role_type = None
    st.session_state.timesheet = []
    st.session_state.login_log = []

if "login_log" not in st.session_state:
    st.session_state.login_log = []

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
EXPORT_FOLDER = "weekly_exports"
os.makedirs(EXPORT_FOLDER, exist_ok=True)

def auto_export_weekly():
    now = datetime.now()
    if now.weekday() == 6:  # Sunday
        filename = os.path.join(EXPORT_FOLDER, f"flm_tasks_week_{now.strftime('%Y_%U')}.csv")
        if not os.path.exists(filename):
            df_export = pd.DataFrame(st.session_state.timesheet)
            if not df_export.empty:
                df_export.to_csv(filename, index=False)
                print(f"✅ Auto-exported weekly tasks to {filename}")

# Call auto export
auto_export_weekly()

# --- Logout Button ---
st.sidebar.title("🔒 Session")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_role_type = None
    st.rerun()

# --- Header & Date ---
st.markdown(f"<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>👋 Welcome <b>{st.session_state.user_role}</b><br><small>Today is {datetime.now().strftime('%A, %B %d, %Y')}</small></div></div>", unsafe_allow_html=True)
st.markdown(f"<div class='date-box'>🕒 {datetime.now().strftime('%I:%M %p')}</div>", unsafe_allow_html=True)

# --- DataFrame Setup ---
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

# --- Alert: No task added today ---
today_str = datetime.now().strftime('%Y-%m-%d')
if df_user.empty or today_str not in df_user['Date'].values:
    st.warning("⚠️ You haven't submitted any task for today!")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["➕ Add Task", "📈 Analytics", "🛠 Admin Panel"])

with tab1:
    st.header("➕ Add New Task")
    with st.form("task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            shift = st.selectbox("🕒 Shift", ["Morning", "Evening"])
            date_selected = st.date_input("📅 Date", value=datetime.today())
            department = st.selectbox("🏢 Department", ["FLM", "Tech Support", "CRM"])
        with col2:
            category = st.selectbox("📂 Category", ["Job Orders", "CRM", "Meetings", "Paperwork"])
            status = st.selectbox("📌 Status", ["⏳ Not Started", "🔄 In Progress", "✅ Completed"])
            priority = st.selectbox("⚠️ Priority", ["🟢 Low", "🟡 Medium", "🔴 High"])
        description = st.text_area("🗒 Description")
        submitted = st.form_submit_button("Submit")

        if submitted and description.strip():
            st.session_state.timesheet.append({
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
                "Submitted": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            st.success("🎉 Task added successfully!")
            st.rerun()

with tab2:
    st.header("📊 Analytics")
    if df_user.empty:
        st.info("No tasks yet.")
    else:
        st.plotly_chart(px.histogram(df_user, x="Date", color="Status", title="Tasks Over Time"))
        st.plotly_chart(px.pie(df_user, names="Category", title="Category Distribution"))
        st.plotly_chart(px.bar(df_user, x="Priority", color="Priority", title="Priority Levels"))
        st.dataframe(df_user)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_user.to_excel(writer, index=False, sheet_name='Tasks')
        st.download_button("📥 Download Excel", data=output.getvalue(), file_name="tasks_export.xlsx")

with tab3:
    st.header("🛠 Admin Panel")
    if st.session_state.user_role_type != "Admin":
        st.error("Access restricted to Admins only.")
    else:
        df_all = pd.DataFrame(st.session_state.timesheet)
        if not df_all.empty:
            st.subheader("📅 Filter by Date and Employee")
            users = df_all['Employee'].unique().tolist()
            selected_user = st.selectbox("Employee", options=["All"] + users)
            start = st.date_input("Start Date", value=datetime.now() - timedelta(days=7))
            end = st.date_input("End Date", value=datetime.now())

            if selected_user != "All":
                df_all = df_all[df_all['Employee'] == selected_user]
            df_all = df_all[(df_all['Date'] >= start.strftime('%Y-%m-%d')) & (df_all['Date'] <= end.strftime('%Y-%m-%d'))]

            st.dataframe(df_all)
            st.subheader("🧠 Login Activity Log")
            st.dataframe(pd.DataFrame(st.session_state.login_log))
        else:
            st.info("No tasks recorded yet.")

# --- Footer ---
st.markdown(f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}</footer>", unsafe_allow_html=True)
