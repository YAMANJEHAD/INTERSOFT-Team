import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import calendar
from io import BytesIO
import uuid
import os
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
    padding: 0 2.5rem; margin: 1.5rem 0;
}
.greeting { font-size: 1.1rem; font-weight: 600; color: #fcd34d; text-align: right; line-height: 1.4; }
.company { font-size: 1.4rem; font-weight: 700; color: #60a5fa; letter-spacing: 0.5px; }
.date-box {
    font-size: 1.1rem; font-weight: 600; color: #f8fafc; text-align: center;
    background: #1e293b; padding: 0.75rem 1.5rem; border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3); margin-bottom: 2rem; display: inline-block;
}
.overview-box {
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
    padding: 2rem; border-radius: 20px; text-align: center;
    margin: 1.2rem 0; transition: transform 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
}
.overview-box:hover {
    transform: translateY(-8px) scale(1.03);
    box-shadow: 0 16px 48px rgba(0,0,0,0.5);
}
.overview-box span {
    font-size: 2.5rem; font-weight: 800; color: #fcd34d;
}
.stButton>button {
    background: linear-gradient(135deg, #4f46e5, #9333ea);
    color: white; font-weight: 600; font-size: 1rem;
    border-radius: 12px; padding: 0.7rem 1.5rem;
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    transition: all 0.2s ease-in-out; border: none;
}
.stButton>button:hover {
    transform: scale(1.06); box-shadow: 0 8px 25px rgba(0,0,0,0.4);
}
.stButton>button:active {
    transform: scale(0.94); box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.stButton>button.delete-button {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
}
.edit-section {
    background: #1e293b; padding: 2rem; border-radius: 16px; margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.alert-box {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    padding: 1.2rem; border-radius: 14px; color: white;
    margin-bottom: 1.5rem; font-weight: 600;
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
.stTabs [role="tab"] {
    font-size: 1.1rem; font-weight: 600; color: #f8fafc;
    background: #1e293b; border-radius: 10px; padding: 0.8rem 1.5rem;
    transition: background 0.3s ease;
}
.stTabs [role="tab"]:hover {
    background: #334155;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4f46e5, #9333ea);
    color: white;
}
footer {
    text-align: center; color: #94a3b8; padding: 2.5rem 0;
    font-size: 1rem; font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# --- Users & Roles ---
USERS = {
    "yaman": {"pass": "YAMAN1", "role": "Admin"},
    "hatem": {"pass": "HATEM2", "role": "Supervisor"},
    "qusai": {"pass": "QUSAI4", "role": "Employee"},
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
    username = st.text_input("👤 Username", key="login_username")
    password = st.text_input("🔑 Password", type="password", key="login_password")
    if st.button("Login 🚀", key="login_button"):
        user = USERS.get(username.lower())
        if user and user["pass"] == password:
            st.session_state.logged_in = True
            st.session_state.user_role = username.lower()
            st.session_state.user_role_type = user["role"]
            st.session_state.login_log.append({
                "user": username.lower(),
                "time": datetime.now().strftime("%Y-%m-%d %I:%M %p")
            })
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
                st.info(f"✅ Auto-exported weekly tasks to {filename}")

# Call auto export
auto_export_weekly()

# --- Logout Button ---
st.sidebar.title("🔒 Session")
if st.sidebar.button("Logout", key="logout_button"):
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_role_type = None
    st.rerun()

# --- Header & Date ---
st.markdown(f"<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>👋 Welcome <b>{st.session_state.user_role.capitalize()} ({st.session_state.user_role_type})</b><br><small>Today is {datetime.now().strftime('%A, %B %d, %Y')}</small></div></div>", unsafe_allow_html=True)
st.markdown(f"<div class='date-box'>🕒 {datetime.now().strftime('%I:%M %p')}</div>", unsafe_allow_html=True)

# --- DataFrame Setup ---
df = pd.DataFrame(st.session_state.timesheet)
df_user = df[df['Employee'] == st.session_state.user_role] if not df.empty else pd.DataFrame()

# --- Dashboard Stats ---
display_df = df_user if st.session_state.user_role_type == "Employee" else df
total_tasks = len(display_df)
completed_tasks = display_df[display_df['Status'] == '✅ Completed'].shape[0] if not display_df.empty else 0
in_progress_tasks = display_df[display_df['Status'] == '🔄 In Progress'].shape[0] if not display_df.empty else 0
not_started_tasks = display_df[display_df['Status'] == '⏳ Not Started'].shape[0] if not display_df.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div class='overview-box'>Total Tasks<br><span>{total_tasks}</span></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='overview-box'>Completed<br><span>{completed_tasks}</span></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='overview-box'>In Progress<br><span>{in_progress_tasks}</span></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='overview-box'>Not Started<br><span>{not_started_tasks}</span></div>", unsafe_allow_html=True)

# --- Alert: No task added today (All Roles) ---
today_str = datetime.now().strftime('%Y-%m-%d')
if st.session_state.user_role_type == "Employee" and (df_user.empty or today_str not in df_user['Date'].values):
    st.markdown(f"<div class='alert-box'>⚠️ You haven't submitted any tasks for today!</div>", unsafe_allow_html=True)

# --- Alert for No Tasks Today (Admin/Supervisor) ---
if st.session_state.user_role_type in ["Admin", "Supervisor"]:
    users = list(set(df['Employee'].unique()) if not df.empty else [])
    for user in USERS.keys():
        if user.lower() not in users or not any(df[df['Employee'] == user.lower()]['Date'] == today_str):
            st.markdown(f"<div class='alert-box'>🔔 Alert: <b>{user.capitalize()}</b> has not submitted a task today!</div>", unsafe_allow_html=True)

# --- Tabs ---
tabs = ["➕ Add Task", "✏️ Edit/Delete Task", "📈 Analytics"]
if st.session_state.user_role_type == "Admin":
    tabs.append("🛠 Admin Panel")
tab1, tab2, tab3, *admin_tab = st.tabs(tabs)

# --- Add Task ---
with tab1:
    st.header("➕ Add New Task")
    with st.form("task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            shift = st.selectbox("🕒 Shift", ["Morning", "Evening"], key="add_shift")
            date_selected = st.date_input("📅 Date", value=datetime.today(), key="add_date")
            department = st.selectbox("🏢 Department", ["FLM", "Tech Support", "CRM"], key="add_dept")
        with col2:
            category = st.selectbox("📂 Category", ["Job Orders", "CRM", "Meetings", "Paperwork"], key="add_cat")
            status = st.selectbox("📌 Status", ["⏳ Not Started", "🔄 In Progress", "✅ Completed"], key="add_stat")
            priority = st.selectbox("⚠️ Priority", ["🟢 Low", "🟡 Medium", "🔴 High"], key="add_prio")
        description = st.text_area("🗒 Description", height=120, key="add_desc")
        if st.form_submit_button("✅ Submit Task", key="submit_task_button"):
            if description.strip():
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
            else:
                st.error("⚠️ Description cannot be empty!")

# --- Edit/Delete Task ---
with tab2:
    st.header("✏️ Edit/Delete Task")
    display_df = df_user if st.session_state.user_role_type == "Employee" else df
    if not display_df.empty:
        st.markdown("<div class='edit-section'>", unsafe_allow_html=True)
        task_dict = {f"{row['Description'][:30]}... ({row['Date']} | {row['Category']} | {row['Status']} | {row['Employee'].capitalize()})": row["TaskID"] for _, row in display_df.iterrows()}
        selected_label = st.selectbox("📋 Select Task", list(task_dict.keys()), key="select_task")
        selected_id = task_dict[selected_label]
        selected_task = display_df[display_df["TaskID"] == selected_id].iloc[0]

        with st.form("edit_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                shift = st.selectbox("🕒 Shift", ["Morning", "Evening"], index=["Morning", "Evening"].index(selected_task["Shift"]), key="edit_shift")
                date = st.date_input("📅 Date", datetime.strptime(selected_task["Date"], '%Y-%m-%d'), key="edit_date")
                dept = st.selectbox("🏢 Department", ["FLM", "Tech Support", "CRM"], index=["FLM", "Tech Support", "CRM"].index(selected_task["Department"]), key="edit_dept")
            with col2:
                cat = st.selectbox("📂 Category", ["Job Orders", "CRM", "Meetings", "Paperwork"], index=["Job Orders", "CRM", "Meetings", "Paperwork"].index(selected_task["Category"]), key="edit_cat")
                stat = st.selectbox("📌 Status", ["⏳ Not Started", "🔄 In Progress", "✅ Completed"], index=["⏳ Not Started", "🔄 In Progress", "✅ Completed"].index(selected_task["Status"]), key="edit_stat")
                prio = st.selectbox("⚠️ Priority", ["🟢 Low", "🟡 Medium", "🔴 High"], index=["🟢 Low", "🟡 Medium", "🔴 High"].index(selected_task["Priority"]), key="edit_prio")
            desc = st.text_area("🗒 Description", selected_task["Description"], height=120, key="edit_desc")

            save, delete = st.columns(2)
            if save.form_submit_button("💾 Update Task", key="update_task_button"):
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
                            st.success("✅ Task updated successfully!")
                            st.rerun()
                else:
                    st.error("⚠️ Description cannot be empty!")
            if delete.form_submit_button("🗑 Delete Task", key="delete_task_button", html_class="delete-button"):
                if st.checkbox("Confirm Delete Task", key="confirm_delete"):
                    st.session_state.timesheet = [t for t in st.session_state.timesheet if t["TaskID"] != selected_id]
                    st.warning("🗑 Task deleted successfully!")
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("ℹ️ No tasks available to edit/delete.")

# --- Analytics ---
with tab3:
    st.header("📈 Analytics")
    if display_df.empty:
        st.info("ℹ️ No tasks yet.")
    else:
        st.plotly_chart(px.histogram(display_df, x="Date", color="Status", title="Tasks Over Time", color_discrete_sequence=px.colors.qualitative.Plotly), use_container_width=True)
        st.plotly_chart(px.pie(display_df, names="Category", title="Category Distribution", color_discrete_sequence=px.colors.qualitative.Plotly), use_container_width=True)
        st.plotly_chart(px.bar(display_df, x="Priority", color="Priority", title="Priority Levels", color_discrete_sequence=px.colors.qualitative.Plotly), use_container_width=True)
        
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

        st.markdown("### 📥 Download Tasks")
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
        st.download_button("📥 Download Excel", data=output.getvalue(), file_name="tasks_export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- Admin Panel ---
if st.session_state.user_role_type == "Admin" and admin_tab:
    with admin_tab[0]:
        st.header("🛠 Admin Panel")
        df_all = pd.DataFrame(st.session_state.timesheet)
        if not df_all.empty:
            st.markdown("### 📅 Filter by Date and Employee")
            col1, col2 = st.columns(2)
            with col1:
                users = df_all['Employee'].unique().tolist()
                selected_user = st.selectbox("Employee", options=["All"] + users, key="filter_employee")
            with col2:
                start = st.date_input("Start Date", value=datetime.now() - timedelta(days=7), key="filter_start")
                end = st.date_input("End Date", value=datetime.now(), key="filter_end")
            filtered_df = df_all
            if selected_user != "All":
                filtered_df = filtered_df[filtered_df['Employee'] == selected_user]
            filtered_df = filtered_df[(filtered_df['Date'] >= start.strftime('%Y-%m-%d')) & (filtered_df['Date'] <= end.strftime('%Y-%m-%d'))]
            st.dataframe(filtered_df)

            st.markdown("### 🧠 Login Activity Log")
            st.dataframe(pd.DataFrame(st.session_state.login_log))

            st.markdown("### 📊 Employee Statistics")
            stats_df = df_all.groupby('Employee').agg({
                'TaskID': 'count',
                'Status': lambda x: (x == '✅ Completed').sum()
            }).rename(columns={'TaskID': 'Total Tasks', 'Status': 'Completed Tasks'})
            stats_df['Completion Rate'] = (stats_df['Completed Tasks'] / stats_df['Total Tasks'] * 100).round(2)
            st.dataframe(stats_df)

            st.markdown("### 📥 Export All Tasks")
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_all.to_excel(writer, index=False, sheet_name='All_Tasks')
                workbook = writer.book
                worksheet = writer.sheets['All_Tasks']
                header_format = workbook.add_format({
                    'bold': True, 'font_color': 'white', 'bg_color': '#4f81bd',
                    'font_size': 12, 'align': 'center', 'valign': 'vcenter'
                })
                cell_format = workbook.add_format({
                    'bold': True, 'font_color': '#f8fafc'
                })
                for i, col in enumerate(df_all.columns):
                    worksheet.write(0, i, col, header_format)
                    worksheet.set_column(i, i, 18)
                for row_num in range(1, len(df_all) + 1):
                    for col_num in range(len(df_all.columns)):
                        worksheet.write(row_num, col_num, df_all.iloc[row_num-1, col_num], cell_format)
            st.download_button("📥 Download All Tasks", data=output.getvalue(), file_name="all_tasks_export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("ℹ️ No tasks recorded yet.")

# --- Footer ---
st.markdown(f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}</footer>", unsafe_allow_html=True)
