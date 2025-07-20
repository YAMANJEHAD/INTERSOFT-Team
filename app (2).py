# FLM Task Tracker – Full Version with Admin Panel, Roles, Alerts, Calendar + Auto Export Weekly + Persistent Storage

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

# --- Paths ---
DATA_FILE = "data/tasks.csv"
EXPORT_FOLDER = "weekly_exports"
os.makedirs("data", exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)

# --- Session Init ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_role_type = None
    st.session_state.login_log = []

# --- Load Persistent Data ---
if "timesheet" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.timesheet = pd.read_csv(DATA_FILE).to_dict("records")
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
    if now.weekday() == 6:  # Sunday
        filename = os.path.join(EXPORT_FOLDER, f"flm_tasks_week_{now.strftime('%Y_%U')}.csv")
        if not os.path.exists(filename):
            df_export = pd.DataFrame(st.session_state.timesheet)
            if not df_export.empty:
                df_export.to_csv(filename, index=False)
                print(f"✅ Auto-exported weekly tasks to {filename}")

# Call auto export
auto_export_weekly()

# --- Dashboard ---
st.markdown(f"<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>👋 Welcome <b>{st.session_state.user_role}</b><br><small>Role: {st.session_state.user_role_type}</small></div></div>", unsafe_allow_html=True)
st.markdown(f"<div class='date-box'>📅 {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}</div>", unsafe_allow_html=True)

# --- Overview Boxes ---
df = pd.DataFrame(st.session_state.timesheet)
df_user = df[df['Employee'] == st.session_state.user_role] if st.session_state.user_role_type == 'Employee' else df
total_tasks = len(df_user)
completed_tasks = df_user[df_user['Status'] == '✅ Completed'].shape[0]
in_progress_tasks = df_user[df_user['Status'] == '🔄 In Progress'].shape[0]
not_started_tasks = df_user[df_user['Status'] == '⏳ Not Started'].shape[0]

col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div class='overview-box'>Total Tasks<br><span>{total_tasks}</span></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='overview-box'>Completed<br><span>{completed_tasks}</span></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='overview-box'>In Progress<br><span>{in_progress_tasks}</span></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='overview-box'>Not Started<br><span>{not_started_tasks}</span></div>", unsafe_allow_html=True)

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["➕ Add Task", "✏️ Edit/Delete Task", "📈 Analytics"])

# --- Add Task ---
with tab1:
    with st.form("add_task", clear_on_submit=True):
        st.subheader("📝 Add New Task")
        col1, col2 = st.columns(2)
        with col1:
            shift = st.selectbox("🕒 Shift", ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"])
            task_date = st.date_input("📅 Date", value=date.today())
            dept = st.selectbox("🏢 Department", ["FLM", "Support", "CRM"])
        with col2:
            category = st.selectbox("📂 Category", ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM"])
            status = st.selectbox("📌 Status", ["⏳ Not Started", "🔄 In Progress", "✅ Completed"])
            priority = st.selectbox("⚠️ Priority", ["🟢 Low", "🟡 Medium", "🔴 High"])
        desc = st.text_area("🗒 Task Description")
        submitted = st.form_submit_button("✅ Submit Task")
        if submitted and desc.strip():
            new_task = {
                "TaskID": str(uuid.uuid4()),
                "Employee": st.session_state.user_role,
                "Date": task_date.strftime('%Y-%m-%d'),
                "Day": calendar.day_name[task_date.weekday()],
                "Shift": shift,
                "Department": dept,
                "Category": category,
                "Status": status,
                "Priority": priority,
                "Description": desc,
                "Submitted": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            st.session_state.timesheet.append(new_task)
            save_data()
            st.success("🎉 Task added successfully!")
            st.rerun()

# --- Edit/Delete Task ---
with tab2:
    st.subheader("✏️ Edit or Delete Existing Task")
    if not df_user.empty:
        options = {f"{row['Description'][:50]} | {row['Date']}": row['TaskID'] for _, row in df_user.iterrows()}
        selected = st.selectbox("📋 Choose Task", list(options.keys()))
        task_id = options[selected]
        selected_task = df_user[df_user['TaskID'] == task_id].iloc[0]
        with st.form("edit_form"):
            col1, col2 = st.columns(2)
            with col1:
                shift = st.selectbox("🕒 Shift", ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"], index=["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"].index(selected_task['Shift']))
                task_date = st.date_input("📅 Date", value=datetime.strptime(selected_task['Date'], '%Y-%m-%d'))
                dept = st.selectbox("🏢 Department", ["FLM", "Support", "CRM"], index=["FLM", "Support", "CRM"].index(selected_task['Department']))
            with col2:
                category = st.selectbox("📂 Category", ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM"], index=["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM"].index(selected_task['Category']))
                status = st.selectbox("📌 Status", ["⏳ Not Started", "🔄 In Progress", "✅ Completed"], index=["⏳ Not Started", "🔄 In Progress", "✅ Completed"].index(selected_task['Status']))
                priority = st.selectbox("⚠️ Priority", ["🟢 Low", "🟡 Medium", "🔴 High"], index=["🟢 Low", "🟡 Medium", "🔴 High"].index(selected_task['Priority']))
            desc = st.text_area("🗒 Task Description", value=selected_task['Description'])
            update = st.form_submit_button("✏️ Update Task")
            delete = st.form_submit_button("🗑 Delete Task")
            if update:
                st.session_state.timesheet = [task if task['TaskID'] != task_id else {
                    **task, "Shift": shift, "Date": task_date.strftime('%Y-%m-%d'),
                    "Day": calendar.day_name[task_date.weekday()], "Department": dept,
                    "Category": category, "Status": status, "Priority": priority, "Description": desc
                } for task in st.session_state.timesheet]
                save_data()
                st.success("✅ Task updated successfully!")
                st.rerun()
            if delete:
                st.session_state.timesheet = [task for task in st.session_state.timesheet if task['TaskID'] != task_id]
                save_data()
                st.warning("🗑 Task deleted successfully!")
                st.rerun()

# --- Analytics ---
with tab3:
    st.subheader("📊 Task Analytics")
    if df_user.empty:
        st.info("ℹ️ No tasks to show.")
    else:
        st.plotly_chart(px.histogram(df_user, x="Date", color="Status", barmode="group", title="Tasks Over Time"), use_container_width=True)
        st.plotly_chart(px.pie(df_user, names="Category", title="Category Breakdown"), use_container_width=True)
        st.plotly_chart(px.bar(df_user, x="Priority", color="Priority", title="Priority Distribution"), use_container_width=True)
        st.markdown("### 📋 Task Table")
        st.dataframe(df_user)
        st.markdown("### 📥 Export to Excel")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_user.to_excel(writer, index=False, sheet_name='Tasks')
        st.download_button("📥 Download Excel File", data=output.getvalue(), file_name="FLM_Tasks.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- Logout ---
st.sidebar.markdown("---")
if st.sidebar.button("🔓 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- Footer ---
st.markdown(f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}</footer>", unsafe_allow_html=True)
