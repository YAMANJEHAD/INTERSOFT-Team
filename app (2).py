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

# --- Constants ---
USERS = {
    "yaman": {"pass": "YAMAN1", "role": "Admin"},
    "hatem": {"pass": "HATEM2", "role": "Supervisor"},
    "qusai": {"pass": "QUSAI4", "role": "Employee"},
}
EXPORT_FOLDER = "weekly_exports"
TASK_STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]
TASK_PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
DEPARTMENTS = ["FLM", "Tech Support", "CRM"]
CATEGORIES = ["Job Orders", "CRM", "Meetings", "Paperwork"]
SHIFTS = ["Morning", "Evening"]

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
    font-size: 1.4rem; font-weight: 700; color: #60a5fa; letter-spacing: 0.5px;
}

.date-box {
    font-size: 1.1rem; font-weight: 600; color: #f8fafc; text-align: center;
    background: linear-gradient(135deg, #1e293b, #334155);
    padding: 0.75rem 1.5rem; border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    margin-bottom: 2rem; display: inline-block;
    animation: fadeIn 0.6s ease-in-out;
}

.overview-box {
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
    padding: 2rem; border-radius: 20px; text-align: center;
    margin: 1.2rem 0; transition: transform 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    animation: zoomIn 0.6s ease-in-out;
}

.overview-box:hover {
    transform: translateY(-8px) scale(1.03);
    box-shadow: 0 16px 48px rgba(0,0,0,0.5);
}

@keyframes zoomIn {
    from { transform: scale(0.95); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}

.overview-box span {
    font-size: 2.5rem; font-weight: 800; color: #fcd34d;
    display: block;
}

.stButton>button {
    background: linear-gradient(135deg, #4f46e5, #9333ea);
    color: white; font-weight: 600; font-size: 1rem;
    border-radius: 12px; padding: 0.7rem 1.5rem;
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    transition: all 0.2s ease-in-out; border: none;
    cursor: pointer;
    animation: slideIn 0.4s ease-in-out;
}

@keyframes slideIn {
    from { transform: translateY(10px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
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
    animation: fadeIn 1s ease-in-out;
}
</style>
""", unsafe_allow_html=True)

# --- Session Initialization ---
def initialize_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_role_type = None
        st.session_state.timesheet = []
        st.session_state.login_log = []

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
                    "Login Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "Role": user["role"]
                })
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
        st.stop()

# --- Excel Export Function ---
def export_to_excel(df, sheet_name, file_name):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
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
    return output.getvalue(), file_name

# --- Auto Weekly Export ---
def auto_export_weekly():
    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    now = datetime.now()
    if now.weekday() == 6:  # Sunday
        filename = os.path.join(EXPORT_FOLDER, f"flm_tasks_week_{now.strftime('%Y_%U')}.csv")
        if not os.path.exists(filename):
            df_export = pd.DataFrame(st.session_state.timesheet)
            if not df_export.empty:
                df_export.to_csv(filename, index=False)
                st.info(f"✅ Auto-exported weekly tasks to {filename}")

# --- Download Tasks ---
def render_download_tasks():
    st.markdown("### 📥 Download Your Tasks")
    current_user = st.session_state.user_role
    user_tasks = df_all[df_all['Employee'] == current_user] if not df_all.empty else pd.DataFrame()
    if not user_tasks.empty:
        data, file_name = export_to_excel(user_tasks, f"{current_user}_Tasks", f"{current_user}_tasks.xlsx")
        st.download_button(
            label="⬇️ Download My Tasks",
            data=data,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("ℹ️ No tasks available for your account.")

# --- Admin Download Other Users' Tasks ---
def render_admin_download_tasks():
    if st.session_state.user_role_type == "Admin":
        st.markdown("### 🛠 Admin Panel: Download Employee Tasks")
        employees = df_all['Employee'].unique().tolist()
        if employees:
            selected_employee = st.selectbox("Select Employee", employees, key="admin_download_employee")
            emp_tasks = df_all[df_all['Employee'] == selected_employee]
            if not emp_tasks.empty:
                data, file_name = export_to_excel(emp_tasks, f"{selected_employee}_Tasks", f"{selected_employee}_tasks.xlsx")
                st.download_button(
                    label=f"⬇️ Download {selected_employee.capitalize()} Tasks",
                    data=data,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info(f"ℹ️ No tasks found for {selected_employee}.")

# --- Render Header ---
def render_header():
    st.markdown(
        f"""
        <div class='top-header'>
            <div class='company'>INTERSOFT<br>International Software Company</div>
            <div class='greeting'>👋 Welcome <b>{st.session_state.user_role.capitalize()} ({st.session_state.user_role_type})</b><br>
            <small>Today is {datetime.now().strftime('%A, %B %d, %Y')}</small></div>
        </div>
        <div class='date-box'>🕒 {datetime.now().strftime('%I:%M %p')}</div>
        """,
        unsafe_allow_html=True
    )

# --- Render Dashboard Stats ---
def render_dashboard_stats(display_df):
    total_tasks = len(display_df)
    completed_tasks = display_df[display_df['Status'] == '✅ Completed'].shape[0] if not display_df.empty else 0
    in_progress_tasks = display_df[display_df['Status'] == '🔄 In Progress'].shape[0] if not display_df.empty else 0
    not_started_tasks = display_df[display_df['Status'] == '⏳ Not Started'].shape[0] if not display_df.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"<div class='overview-box'>Total Tasks<br><span>{total_tasks}</span></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='overview-box'>Completed<br><span>{completed_tasks}</span></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='overview-box'>In Progress<br><span>{in_progress_tasks}</span></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='overview-box'>Not Started<br><span>{not_started_tasks}</span></div>", unsafe_allow_html=True)

# --- Render Alerts ---
def render_alerts(df_user, df_all):
    today_str = datetime.now().strftime('%Y-%m-%d')
    if st.session_state.user_role_type == "Employee" and (df_user.empty or today_str not in df_user['Date'].values):
        st.markdown(f"<div class='alert-box'>⚠️ You haven't submitted any tasks for today!</div>", unsafe_allow_html=True)
    
    if st.session_state.user_role_type in ["Admin", "Supervisor"]:
        users = list(set(df_all['Employee'].unique()) if not df_all.empty else [])
        for user in USERS.keys():
            if user.lower() not in users or not any(df_all[df_all['Employee'] == user.lower()]['Date'] == today_str):
                st.markdown(f"<div class='alert-box'>🔔 Alert: <b>{user.capitalize()}</b> has not submitted a task today!</div>", unsafe_allow_html=True)

# --- Add Task ---
def render_add_task():
    with tab1:
        st.header("➕ Add New Task")
        with st.form("task_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                shift = st.selectbox("🕒 Shift", SHIFTS, key="add_shift")
                date_selected = st.date_input("📅 Date", value=datetime.today(), key="add_date")
                department = st.selectbox("🏢 Department", DEPARTMENTS, key="add_dept")
            with col2:
                category = st.selectbox("📂 Category", CATEGORIES, key="add_cat")
                status = st.selectbox("📌 Status", TASK_STATUSES, key="add_stat")
                priority = st.selectbox("⚠️ Priority", TASK_PRIORITIES, key="add_prio")
            description = st.text_area("🗒 Description", height=120, key="add_desc")
            
            submitted = st.form_submit_button("✅ Submit Task")
            
            if submitted:
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
def render_edit_delete_task(display_df):
    with tab2:
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
                                    "Submitted": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                }
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
                        st.warning("🗑 Task deleted successfully!")
                        st.rerun()
            else:
                st.info("ℹ️ Task deletion is restricted to Admins only.")

            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("ℹ️ No tasks available to edit.")

# --- Analytics ---
def render_analytics(display_df):
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
                try:
                    cal_df = display_df.groupby('Date').size().reset_index(name='Task Count')
                    cal_df['Date'] = pd.to_datetime(cal_df['Date'])
                    cal_df = cal_df.set_index('Date')
                    fig, ax = calplot.calplot(
                        data=cal_df['Task Count'],
                        how='sum',
                        cmap='Blues',
                        fillcolor='lightgrey',
                        linewidth=2,
                        dropzero=True
                    )
                    st.pyplot(fig)
                except Exception as e:
                    st.error(f"⚠️ Error in Calplot: {e}")
            else:
                dates = pd.date_range(start=display_df['Date'].min(), end=display_df['Date'].max()) if not display_df.empty else pd.date_range(start=datetime.today(), end=datetime.today())
                calendar_data = [{"Date": d.strftime('%Y-%m-%d'), "Task Count": len(display_df[display_df['Date'] == d.strftime('%Y-%m-%d')])} for d in dates]
                calendar_df = pd.DataFrame(calendar_data)
                st.dataframe(calendar_df, use_container_width=True)
                st.warning("⚠️ Install 'calplot' for a visual calendar (pip install calplot).")

            st.markdown("### 📥 Download Tasks")
            data, file_name = export_to_excel(display_df, "Tasks", "tasks_export.xlsx")
            st.download_button("📥 Download Excel", data=data, file_name=file_name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- Admin Panel ---
def render_admin_panel():
    if st.session_state.user_role_type == "Admin" and admin_tab:
        with admin_tab[0]:
            st.header("🛠 Admin Panel")
            df_all = pd.DataFrame(st.session_state.timesheet)
            if not df_all.empty:
                # Filter Tasks
                st.markdown("### 📅 View and Filter Tasks")
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
                                        "Submitted": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    }
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
                st.download_button("📥 Download All Tasks", data=data, file_name=file_name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.info("ℹ️ No tasks recorded yet.")

# --- Main App Logic ---
if __name__ == "__main__":
    initialize_session()
    authenticate_user()

    # Sidebar Logout
    st.sidebar.title("🔒 Session")
    if st.sidebar.button("Logout", key="logout_button"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_role_type = None
        st.rerun()

    # Data Setup
    df_all = pd.DataFrame(st.session_state.timesheet)
    df_user = df_all[df_all['Employee'] == st.session_state.user_role] if not df_all.empty else pd.DataFrame()
    display_df = df_user if st.session_state.user_role_type == "Employee" else df_all

    # Render UI Components
    render_header()
    render_download_tasks()
    render_admin_download_tasks()
    auto_export_weekly()
    render_dashboard_stats(display_df)
    render_alerts(df_user, df_all)

    # Tabs
    tabs = ["➕ Add Task", "✏️ Edit/Delete Task", "📈 Analytics"]
    if st.session_state.user_role_type == "Admin":
        tabs.append("🛠 Admin Panel")
    tab1, tab2, tab3, *admin_tab = st.tabs(tabs)

    # Render Tab Content
    render_add_task()
    render_edit_delete_task(display_df)
    render_analytics(display_df)
    render_admin_panel()

    # Footer
    st.markdown(
        f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}</footer>",
        unsafe_allow_html=True
    )
