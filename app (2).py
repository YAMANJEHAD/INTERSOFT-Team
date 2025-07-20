import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import calendar
from io import BytesIO
import uuid
try:
    import calplot
    CALPLOT_AVAILABLE = True
except ImportError:
    CALPLOT_AVAILABLE = False

# --- Page Config ---
st.set_page_config(
    page_title="⚡ INTERSOFT Dashboard | FLM",
    layout="wide",
    page_icon="🚀"
)

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
.stButton>button {
    background: linear-gradient(135deg, #4f46e5, #9333ea);
    color: white; font-weight: 600; border-radius: 10px;
    padding: 0.6rem 1.4rem; box-shadow: 0 6px 25px rgba(0,0,0,0.3);
    transition: all 0.2s ease-in-out; border: none;
}
.stButton>button:hover {
    transform: scale(1.05); box-shadow: 0 8px 30px rgba(0,0,0,0.4);
}
.stButton>button:active {
    transform: scale(0.95); box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.edit-section {
    background: #1e293b; padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;
}
.alert-box {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    padding: 1rem; border-radius: 12px; color: white; margin-bottom: 1rem;
}
.stDataFrame table {
    width: 100%; border-collapse: collapse;
}
.stDataFrame th {
    background-color: #4f81bd; color: white; font-weight: bold; padding: 8px;
}
.stDataFrame td {
    font-weight: 600; color: #f8fafc; padding: 8px; border-bottom: 1px solid #334155;
}
footer { text-align: center; color: #94a3b8; padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- Authentication ---
def check_login(username, password):
    users = {
        "admin": {"password": "ADMIN1", "role": "Admin"},
        "supervisor": {"password": "SUPERVISOR2", "role": "Supervisor"},
        "yaman": {"password": "YAMAN1", "role": "Employee"},
        "hatem": {"password": "HATEM2", "role": "Employee"},
        "mahmoud": {"password": "MAHMOUD3", "role": "Employee"},
        "qusai": {"password": "QUSAI4", "role": "Employee"}
    }
    user = users.get(username.lower())
    if user and user["password"] == password:
        return user["role"]
    return None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []
if "login_history" not in st.session_state:
    st.session_state.login_history = []

if not st.session_state.logged_in:
    st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>🔐 INTERSOFT Task Tracker</div></div>", unsafe_allow_html=True)
    username = st.text_input("👤 Username", key="login_username")
    password = st.text_input("🔑 Password", type="password", key="login_password")
    if st.button("Login 🚀", key="login_button"):
        role = check_login(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.user_role = role
            st.session_state.username = username.lower()
            st.session_state.login_history.append({
                "username": username.lower(),
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "role": role
            })
            st.rerun()
        else:
            st.error("❌ Invalid credentials")
    st.stop()

# --- Initialize Constants ---
SHIFTS = ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"]
CATEGORIES = ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM", "📅 Meetings", "💻 TOMS"]
PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]

# --- Header ---
st.markdown(f"<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>👋 Welcome <b>{st.session_state.username.capitalize()} ({st.session_state.user_role})</b><br><small>Start tracking tasks, boost your day, and monitor progress like a pro!</small></div></div>", unsafe_allow_html=True)
st.markdown(f"<div class='date-box'>📅 {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}</div>", unsafe_allow_html=True)

# --- Logout Button ---
if st.button("🔓 Logout", key="logout_button"):
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None
    st.rerun()

# --- Data ---
df = pd.DataFrame(st.session_state.timesheet)
df_user = df[df["Employee"] == st.session_state.username] if not df.empty else pd.DataFrame()

# --- Dashboard Stats ---
display_df = df_user if st.session_state.user_role == "Employee" else df
if not display_df.empty and "Status" in display_df.columns:
    total_tasks = len(display_df)
    completed_tasks = display_df[display_df["Status"] == "✅ Completed"].shape[0]
    in_progress_tasks = display_df[display_df["Status"] == "🔄 In Progress"].shape[0]
    not_started_tasks = display_df[display_df["Status"] == "⏳ Not Started"].shape[0]
else:
    total_tasks = completed_tasks = in_progress_tasks = not_started_tasks = 0

col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div class='overview-box'>Total Tasks<br><span>{total_tasks}</span></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='overview-box'>Completed<br><span>{completed_tasks}</span></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='overview-box'>In Progress<br><span>{in_progress_tasks}</span></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='overview-box'>Not Started<br><span>{not_started_tasks}</span></div>", unsafe_allow_html=True)

# --- Alert for No Tasks Today (Admin/Supervisor) ---
if st.session_state.user_role in ["Admin", "Supervisor"]:
    today = datetime.now().strftime('%Y-%m-%d')
    users = list(set(df['Employee'].unique()) if not df.empty else [])
    for user in ["yaman", "hatem", "mahmoud", "qusai"]:
        if user not in users or not any(df[df['Employee'] == user]['Date'] == today):
            st.markdown(f"<div class='alert-box'>🔔 Alert: <b>{user.capitalize()}</b> has not submitted a task today!</div>", unsafe_allow_html=True)

# --- Tabs ---
tabs = ["➕ Add Task", "✏️ Edit/Delete Task", "📈 Analytics"]
if st.session_state.user_role == "Admin":
    tabs.append("🛠 Admin Panel")
tab1, tab2, tab3, *admin_tab = st.tabs(tabs)

# --- Add Task ---
with tab1:
    with st.form("add_task_form", clear_on_submit=True):
        st.subheader("📝 Add New Task")
        c1, c2 = st.columns(2)
        with c1:
            shift = st.selectbox("🕒 Shift", SHIFTS, key="add_shift")
            date = st.date_input("📅 Date", value=datetime.today(), key="add_date")
            department = st.selectbox("🏢 Department", ["FLM", "Tech Support", "CRM"], key="add_dept")
        with c2:
            cat = st.selectbox("📂 Category", CATEGORIES, key="add_cat")
            stat = st.selectbox("📌 Status", STATUSES, key="add_stat")
            prio = st.selectbox("⚠️ Priority", PRIORITIES, key="add_prio")
        desc = st.text_area("🗒 Task Description", height=100, key="add_desc")
        submit = st.form_submit_button("✅ Submit Task", key="submit_task_button")
        if submit:
            if desc.strip():
                st.session_state.timesheet.append({
                    "TaskID": str(uuid.uuid4()),
                    "Employee": st.session_state.username,
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
    st.subheader("✏️ Edit or Delete Existing Task")
    display_df = df_user if st.session_state.user_role == "Employee" else df
    if not display_df.empty:
        st.markdown("<div class='edit-section'>", unsafe_allow_html=True)
        task_dict = {f"{row['Description'][:30]}... ({row['Date']} | {row['Category']} | {row['Status']} | {row['Employee'].capitalize()})": row["TaskID"] for _, row in display_df.iterrows()}
        selected_label = st.selectbox("📋 Select Task", list(task_dict.keys()), key="select_task")
        selected_id = task_dict[selected_label]
        selected_task = display_df[display_df["TaskID"] == selected_id].iloc[0]

        with st.form("edit_form", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                shift = st.selectbox("🕒 Shift", SHIFTS, index=SHIFTS.index(selected_task["Shift"]), key="edit_shift")
                date = st.date_input("📅 Date", datetime.strptime(selected_task["Date"], '%Y-%m-%d'), key="edit_date")
                dept = st.selectbox("🏢 Department", ["FLM", "Tech Support", "CRM"], index=["FLM", "Tech Support", "CRM"].index(selected_task["Department"]), key="edit_dept")
            with c2:
                cat = st.selectbox("📂 Category", CATEGORIES, index=CATEGORIES.index(selected_task["Category"]), key="edit_cat")
                stat = st.selectbox("📌 Status", STATUSES, index=STATUSES.index(selected_task["Status"]), key="edit_stat")
                prio = st.selectbox("⚠️ Priority", PRIORITIES, index=PRIORITIES.index(selected_task["Priority"]), key="edit_prio")
            desc = st.text_area("🗒 Task Description", selected_task["Description"], key="edit_desc")

            save, delete = st.columns(2)
            update = save.form_submit_button("💾 Update Task", key="update_task_button")
            remove = delete.form_submit_button("🗑 Delete Task", key="delete_task_button")

            if update:
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
                                "Submitted": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            st.success("✅ Task updated.")
                            st.rerun()
                else:
                    st.error("⚠️ Task description cannot be empty!")

            if remove:
                if st.checkbox("Confirm Delete Task", key="confirm_delete"):
                    st.session_state.timesheet = [t for t in st.session_state.timesheet if t["TaskID"] != selected_id]
                    st.warning("🗑 Task deleted.")
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("ℹ️ No tasks available to edit/delete.")

# --- Analytics ---
with tab3:
    if not display_df.empty:
        st.subheader("📊 Task Analysis")
        st.plotly_chart(px.histogram(display_df, x="Date", color="Status", title="Tasks Over Time"), use_container_width=True)
        st.plotly_chart(px.pie(display_df, names="Category", title="Category Breakdown"), use_container_width=True)
        st.plotly_chart(px.bar(display_df, x="Priority", color="Priority", title="Priority Distribution"), use_container_width=True)

        st.markdown("### 📋 Task Table")
        st.dataframe(display_df)

        st.markdown("### 📅 Calendar-Style Task Summary")
        if CALPLOT_AVAILABLE:
            cal_df = display_df.groupby('Date').size().reset_index(name='Task Count')
            cal_df['Date'] = pd.to_datetime(cal_df['Date'])
            cal_df = cal_df.set_index('Date')
            calplot.calplot(
                data=cal_df['Task Count'],
                how='sum',
                cmap='Blues',
                fillcolor='lightgrey',
                linewidth=2,
                dropzero=True,
                textformat='{:.0f}',
                textcolor='black',
                textfillcolor='white'
            )
            st.pyplot()
        else:
            dates = pd.date_range(start=display_df['Date'].min(), end=display_df['Date'].max()) if not display_df.empty else pd.date_range(start=datetime.today(), end=datetime.today())
            calendar_data = []
            for d in dates:
                d_str = d.strftime('%Y-%m-%d')
                tasks_on_date = display_df[display_df['Date'] == d_str]
                task_count = len(tasks_on_date)
                calendar_data.append({"Date": d_str, "Task Count": task_count})
            calendar_df = pd.DataFrame(calendar_data)
            st.dataframe(calendar_df, use_container_width=True)
            st.warning("⚠️ Install 'calplot' for a visual calendar (pip install calplot).")

        st.markdown("### 📥 Export to Excel")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            display_df.to_excel(writer, index=False, sheet_name='Tasks')
            workbook = writer.book
            worksheet = writer.sheets['Tasks']
            header_format = workbook.add_format({
                'bold': True, 'font_color': 'white', 'bg_color': '#4f81bd',
                'font_size': 12, 'align': 'center', 'valign': 'vcenter'
            })
            cell_format = workbook.add_format({
                'bold': True, 'font_color': '#f8fafc'
            })
            for i, col in enumerate(display_df.columns):
                worksheet.write(0, i, col, header_format)
                worksheet.set_column(i, i, 18)
            for row_num in range(1, len(display_df) + 1):
                for col_num in range(len(display_df.columns)):
                    worksheet.write(row_num, col_num, display_df.iloc[row_num-1, col_num], cell_format)
        st.download_button("⬇️ Download Excel", data=output.getvalue(), file_name="FLM_Tasks.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("ℹ️ No tasks to show. Add some tasks first.")

# --- Admin Panel ---
if st.session_state.user_role == "Admin" and admin_tab:
    with admin_tab[0]:
        st.subheader("🛠 Admin Panel")

        # --- Filter by Employee & Date ---
        st.markdown("### 🔍 Filter Tasks")
        col1, col2 = st.columns(2)
        with col1:
            filter_employee = st.selectbox("Select Employee", ["All"] + list(set(df['Employee'].unique()) if not df.empty else []), key="filter_employee")
        with col2:
            filter_date = st.date_input("Select Date Range", value=(datetime.today(), datetime.today()), key="filter_date")
        filtered_df = df
        if filter_employee != "All":
            filtered_df = filtered_df[filtered_df['Employee'] == filter_employee]
        if filter_date:
            start_date, end_date = filter_date if isinstance(filter_date, tuple) else (filter_date, filter_date)
            filtered_df = filtered_df[(filtered_df['Date'] >= start_date.strftime('%Y-%m-%d')) & (filtered_df['Date'] <= end_date.strftime('%Y-%m-%d'))]
        st.dataframe(filtered_df)

        # --- Employee Stats ---
        st.markdown("### 📊 Employee Statistics")
        if not df.empty:
            stats_df = df.groupby('Employee').agg({
                'TaskID': 'count',
                'Status': lambda x: (x == '✅ Completed').sum()
            }).rename(columns={'TaskID': 'Total Tasks', 'Status': 'Completed Tasks'})
            stats_df['Completion Rate'] = (stats_df['Completed Tasks'] / stats_df['Total Tasks'] * 100).round(2)
            st.dataframe(stats_df)
        else:
            st.info("ℹ️ No employee stats available.")

        # --- Login History Viewer ---
        st.markdown("### ⏱ Login History")
        login_df = pd.DataFrame(st.session_state.login_history)
        if not login_df.empty:
            st.dataframe(login_df.sort_values(by="timestamp", ascending=False))
        else:
            st.info("ℹ️ No login history available.")

        # --- Export All Tasks ---
        st.markdown("### 📥 Export All Tasks")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='All_Tasks')
            workbook = writer.book
            worksheet = writer.sheets['All_Tasks']
            header_format = workbook.add_format({
                'bold': True, 'font_color': 'white', 'bg_color': '#4f81bd',
                'font_size': 12, 'align': 'center', 'valign': 'vcenter'
            })
            cell_format = workbook.add_format({
                'bold': True, 'font_color': '#f8fafc'
            })
            for i, col in enumerate(df.columns):
                worksheet.write(0, i, col, header_format)
                worksheet.set_column(i, i, 18)
            for row_num in range(1, len(df) + 1):
                for col_num in range(len(df.columns)):
                    worksheet.write(row_num, col_num, df.iloc[row_num-1, col_num], cell_format)
        st.download_button("⬇️ Download All Tasks", data=output.getvalue(), file_name="All_FLM_Tasks.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- Footer ---
st.markdown(f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</footer>", unsafe_allow_html=True)
