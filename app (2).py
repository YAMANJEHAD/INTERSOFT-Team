# FLM Task Tracker – Full Version with Admin Panel, Roles, Alerts, Calendar

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import calendar
from io import BytesIO
import uuid

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

# --- Logout Button ---
st.sidebar.title(f"Welcome, {st.session_state.user_role} 👋")
if st.sidebar.button("Logout 🔓"):
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_role_type = None
    st.rerun()

# --- Constants ---
SHIFTS = ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"]
CATEGORIES = ["💪 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM", "🗕 Meetings", "💻 TOMS"]
PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]

# --- Top Info ---
st.markdown(f"<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>👋 Welcome <b>{st.session_state.user_role}</b><br><small>Role: {st.session_state.user_role_type}</small></div></div>", unsafe_allow_html=True)
st.markdown(f"<div class='date-box'>🗓 {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}</div>", unsafe_allow_html=True)

# --- Data ---
df = pd.DataFrame(st.session_state.timesheet)
df_user = df[df["Employee"] == st.session_state.user_role] if not df.empty else pd.DataFrame()

# --- Late Task Alert ---
today_str = datetime.today().strftime('%Y-%m-%d')
if df_user.empty or today_str not in df_user["Date"].values:
    st.error("⚠️ You haven't submitted any tasks today!")

# --- Overview ---
total = len(df_user)
completed = df_user[df_user["Status"] == "✅ Completed"].shape[0] if not df_user.empty else 0
progress = df_user[df_user["Status"] == "🔄 In Progress"].shape[0] if not df_user.empty else 0
not_started = df_user[df_user["Status"] == "⏳ Not Started"].shape[0] if not df_user.empty else 0
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div class='overview-box'>Total Tasks<br><span>{total}</span></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='overview-box'>Completed<br><span>{completed}</span></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='overview-box'>In Progress<br><span>{progress}</span></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='overview-box'>Not Started<br><span>{not_started}</span></div>", unsafe_allow_html=True)

# --- Tabs ---
tabs = ["➕ Add Task", "📊 Analytics"]
if st.session_state.user_role_type == "Admin":
    tabs.append("🧭 Admin Panel")
page = st.tabs(tabs)

# === TAB 1: Add Task ===
with page[0]:
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            shift = st.selectbox("🕒 Shift", SHIFTS)
            date_val = st.date_input("📅 Date", value=date.today())
            dept = st.selectbox("🏢 Department", ["FLM", "Tech Support", "CRM"])
        with c2:
            cat = st.selectbox("📂 Category", CATEGORIES)
            status = st.selectbox("📌 Status", STATUSES)
            prio = st.selectbox("⚠️ Priority", PRIORITIES)
        desc = st.text_area("📝 Task Description", height=100)
        if st.form_submit_button("✅ Submit Task"):
            if desc.strip():
                st.session_state.timesheet.append({
                    "TaskID": str(uuid.uuid4()),
                    "Employee": st.session_state.user_role,
                    "Date": date_val.strftime('%Y-%m-%d'),
                    "Day": calendar.day_name[date_val.weekday()],
                    "Shift": shift,
                    "Department": dept,
                    "Category": cat,
                    "Status": status,
                    "Priority": prio,
                    "Description": desc,
                    "Submitted": datetime.now().strftime('%Y-%m-%d %I:%M:%S')
                })
                st.success("✅ Task added.")
                st.rerun()

# === TAB 2: Analytics ===
with page[1]:
    st.subheader("📊 Task Analytics")
    if not df_user.empty:
        st.plotly_chart(px.histogram(df_user, x="Date", color="Status", title="Tasks Over Time"), use_container_width=True)
        st.plotly_chart(px.pie(df_user, names="Category", title="Category Breakdown"), use_container_width=True)
        st.bar_chart(df_user["Priority"].value_counts())

        df_user["Date"] = pd.to_datetime(df_user["Date"])
        st.markdown("### 📆 Task Calendar View")
        cal = df_user.groupby("Date")["TaskID"].count().reset_index()
        cal.columns = ["Date", "Tasks"]
        st.bar_chart(cal.set_index("Date"))
    else:
        st.info("No tasks to display.")

# === TAB 3: Admin Panel ===
if st.session_state.user_role_type == "Admin":
    with page[2]:
        st.subheader("🧭 Admin Panel")
        all_df = pd.DataFrame(st.session_state.timesheet)
        if not all_df.empty:
            employees = sorted(all_df["Employee"].unique())
            filter_emp = st.selectbox("👤 Filter by Employee", ["All"] + employees)
            filter_date = st.date_input("📅 Filter by Date (Optional)", value=None)
            filtered = all_df.copy()
            if filter_emp != "All":
                filtered = filtered[filtered["Employee"] == filter_emp]
            if filter_date:
                filtered = filtered[pd.to_datetime(filtered["Date"]).dt.date == filter_date]
            st.dataframe(filtered)

            # Task selection
            task_map = {f"{row['Employee']} | {row['Description'][:30]} ({row['Date']})": row["TaskID"] for _, row in filtered.iterrows()}
            task_label = st.selectbox("✏️ Choose Task to Edit/Delete", list(task_map.keys()))
            task_id = task_map[task_label]
            target = all_df[all_df["TaskID"] == task_id].iloc[0]

            with st.form("admin_edit_form"):
                c1, c2 = st.columns(2)
                with c1:
                    shift = st.selectbox("🕒 Shift", SHIFTS, index=SHIFTS.index(target["Shift"]))
                    date_val = st.date_input("📅 Date", datetime.strptime(target["Date"], "%Y-%m-%d"))
                    dept = st.selectbox("🏢 Department", ["FLM", "Tech Support", "CRM"], index=["FLM", "Tech Support", "CRM"].index(target["Department"]))
                    emp = st.selectbox("👤 Employee", employees, index=employees.index(target["Employee"]))
                with c2:
                    cat = st.selectbox("📂 Category", CATEGORIES, index=CATEGORIES.index(target["Category"]))
                    status = st.selectbox("📌 Status", STATUSES, index=STATUSES.index(target["Status"]))
                    prio = st.selectbox("⚠️ Priority", PRIORITIES, index=PRIORITIES.index(target["Priority"]))
                desc = st.text_area("📝 Task Description", target["Description"])

                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Update Task"):
                    for i, task in enumerate(st.session_state.timesheet):
                        if task["TaskID"] == task_id:
                            st.session_state.timesheet[i] = {
                                "TaskID": task_id,
                                "Employee": emp,
                                "Date": date_val.strftime('%Y-%m-%d'),
                                "Day": calendar.day_name[date_val.weekday()],
                                "Shift": shift,
                                "Department": dept,
                                "Category": cat,
                                "Status": status,
                                "Priority": prio,
                                "Description": desc,
                                "Submitted": datetime.now().strftime('%Y-%m-%d %I:%M:%S')
                            }
                            st.success("✅ Task updated!")
                            st.rerun()
                if b2.form_submit_button("🗑 Delete Task"):
                    st.session_state.timesheet = [t for t in st.session_state.timesheet if t["TaskID"] != task_id]
                    st.warning("🗑 Task deleted.")
                    st.rerun()

            # Login Log
            st.markdown("### 🕒 Login History")
            log_df = pd.DataFrame(st.session_state.login_log)
            st.dataframe(log_df)

            # Stats
            st.markdown("### 📊 Employee Stats")
            sum_df = all_df.groupby("Employee")["TaskID"].count().reset_index().rename(columns={"TaskID": "Total"})
            comp = all_df[all_df["Status"] == "✅ Completed"].groupby("Employee")["Status"].count().reset_index().rename(columns={"Status": "Completed"})
            sum_df = sum_df.merge(comp, on="Employee", how="left").fillna(0)
            sum_df["Completed"] = sum_df["Completed"].astype(int)
            sum_df["Completion Rate"] = ((sum_df["Completed"] / sum_df["Total"]) * 100).round(0).astype(int).astype(str) + "%"
            st.dataframe(sum_df)
            st.bar_chart(sum_df.set_index("Employee")["Total"])
        else:
            st.info("🚫 No tasks available.")

# --- Footer ---
st.markdown(f"<footer>🗓 INTERSOFT FLM Tracker • {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</footer>", unsafe_allow_html=True)
