import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar
from io import BytesIO
import uuid

# --- Page Config ---
st.set_page_config("INTERSOFT Dashboard | FLM", layout="wide", page_icon="🚀")

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

# --- Authentication ---
def check_login(username, password):
    return {
        "Yaman": "YAMAN1",
        "Hatem": "HATEM2",
        "Mahmoud": "MAHMOUD3",
        "Qusai": "QUSAI4"
    }.get(username) == password

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

if not st.session_state.logged_in:
    st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>🔐 INTERSOFT Task Tracker</div></div>", unsafe_allow_html=True)
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    if st.button("Login 🚀"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.session_state.user_role = username
            st.rerun()
        else:
            st.error("❌ Invalid credentials")
    st.stop()

# --- Initialize Session ---
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

SHIFTS = ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"]
CATEGORIES = ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM", "📅 Meetings", "💻 TOMS"]
PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]

# --- Header ---
st.markdown(f"<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>👋 Welcome <b>{st.session_state.user_role}</b><br><small>Start tracking tasks, boost your day, and monitor progress like a pro!</small></div></div>", unsafe_allow_html=True)
st.markdown(f"<div class='date-box'>📅 {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}</div>", unsafe_allow_html=True)

# --- Data ---
df = pd.DataFrame(st.session_state.timesheet)
df_user = df[df["Employee"] == st.session_state.user_role] if not df.empty else pd.DataFrame()

# --- Dashboard Stats ---
if not df_user.empty and "Status" in df_user.columns:
    total_tasks = len(df_user)
    completed_tasks = df_user[df_user["Status"] == "✅ Completed"].shape[0]
    in_progress_tasks = df_user[df_user["Status"] == "🔄 In Progress"].shape[0]
    not_started_tasks = df_user[df_user["Status"] == "⏳ Not Started"].shape[0]
else:
    total_tasks = completed_tasks = in_progress_tasks = not_started_tasks = 0

col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div class='overview-box'>Total Tasks<br><span>{total_tasks}</span></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='overview-box'>Completed<br><span>{completed_tasks}</span></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='overview-box'>In Progress<br><span>{in_progress_tasks}</span></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='overview-box'>Not Started<br><span>{not_started_tasks}</span></div>", unsafe_allow_html=True)

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["➕ Add Task", "✏️ Edit/Delete Task", "📊 Analytics"])

# --- Add Task ---
with tab1:
    with st.form("add_task_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            shift = st.selectbox("🕒 Shift", SHIFTS)
            date = st.date_input("📅 Date", value=datetime.today())
            department = st.selectbox("🏢 Department", ["FLM", "Tech Support", "CRM"])
        with c2:
            cat = st.selectbox("📂 Category", CATEGORIES)
            stat = st.selectbox("📌 Status", STATUSES)
            prio = st.selectbox("⚠️ Priority", PRIORITIES)
        desc = st.text_area("🗒 Task Description", height=100)
        submit = st.form_submit_button("✅ Submit Task")
        if submit:
            if desc.strip():
                st.session_state.timesheet.append({
                    "TaskID": str(uuid.uuid4()),
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
                st.success("✅ Task added successfully.")
                st.rerun()
            else:
                st.error("⚠️ Task description cannot be empty!")

# --- Edit/Delete Task ---
with tab2:
    if not df_user.empty:
        task_dict = {f"{row['Description'][:30]}... ({row['Date']})": row["TaskID"] for _, row in df_user.iterrows()}
        selected_label = st.selectbox("📋 Select Task", list(task_dict.keys()))
        selected_id = task_dict[selected_label]
        selected_task = df_user[df_user["TaskID"] == selected_id].iloc[0]

        with st.form("edit_form"):
            c1, c2 = st.columns(2)
            with c1:
                shift = st.selectbox("🕒 Shift", SHIFTS, index=SHIFTS.index(selected_task["Shift"]))
                date = st.date_input("📅 Date", datetime.strptime(selected_task["Date"], '%Y-%m-%d'))
                dept = st.selectbox("🏢 Department", ["FLM", "Tech Support", "CRM"], index=["FLM", "Tech Support", "CRM"].index(selected_task["Department"]))
            with c2:
                cat = st.selectbox("📂 Category", CATEGORIES, index=CATEGORIES.index(selected_task["Category"]))
                stat = st.selectbox("📌 Status", STATUSES, index=STATUSES.index(selected_task["Status"]))
                prio = st.selectbox("⚠️ Priority", PRIORITIES, index=PRIORITIES.index(selected_task["Priority"]))
            desc = st.text_area("🗒 Task Description", selected_task["Description"])

            save, delete = st.columns(2)
            update = save.form_submit_button("💾 Update Task")
            remove = delete.form_submit_button("🗑 Delete Task")

            if update:
                for i, t in enumerate(st.session_state.timesheet):
                    if t["TaskID"] == selected_id:
                        st.session_state.timesheet[i] = {
                            "TaskID": selected_id,
                            "Employee": st.session_state.user_role,
                            "Date": date.strftime('%Y-%m-%d'),
                            "Day": calendar.day_name[date.weekday()],
                            "Shift": shift,
                            "Department": dept,
                            "Category": cat,
                            "Status": stat,
                            "Priority": prio,
                            "Description": desc,
                            "Submitted": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        st.success("✅ Task updated.")
                        st.rerun()

            if remove:
                st.session_state.timesheet = [t for t in st.session_state.timesheet if t["TaskID"] != selected_id]
                st.warning("🗑 Task deleted.")
                st.rerun()
    else:
        st.info("ℹ️ No tasks available to edit/delete.")

# --- Analytics ---
with tab3:
    if not df_user.empty:
        st.subheader("📊 Task Analysis")
        st.plotly_chart(px.histogram(df_user, x="Date", color="Status", title="Tasks Over Time"), use_container_width=True)
        st.plotly_chart(px.pie(df_user, names="Category", title="Category Breakdown"), use_container_width=True)
        st.plotly_chart(px.bar(df_user, x="Priority", color="Priority", title="Priority Distribution"), use_container_width=True)

        st.markdown("### 📋 Task Table")
        st.dataframe(df_user)

        st.markdown("### 📥 Export to Excel")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_user.to_excel(writer, index=False, sheet_name='Tasks')
            for i, col in enumerate(df_user.columns): writer.sheets['Tasks'].set_column(i, i, 18)
        st.download_button("⬇️ Download Excel", data=output.getvalue(), file_name="FLM_Tasks.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("ℹ️ No tasks to show. Add some tasks first.")

# --- Footer ---
st.markdown(f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</footer>", unsafe_allow_html=True)
