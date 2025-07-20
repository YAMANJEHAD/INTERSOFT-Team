import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import calendar
from io import BytesIO
import uuid

# --- Page Configuration ---
st.set_page_config(
    page_title="⚡ INTERSOFT Dashboard | FLM",
    layout="wide",
    page_icon="🚀"
)

# --- Beautiful Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background: radial-gradient(circle at top left, #0f172a, #1e293b);
        color: #f8fafc;
    }

    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 2rem;
        margin-top: 1rem;
    }

    .greeting {
        font-size: 1rem;
        font-weight: 500;
        color: #fcd34d;
        text-align: right;
    }

    .company {
        font-size: 1.2rem;
        font-weight: 600;
        color: #60a5fa;
    }

    .date-box {
        font-size: 1rem;
        font-weight: 500;
        color: #f8fafc;
        text-align: center;
        background: #1e293b;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        margin-bottom: 1.5rem;
        display: inline-block;
    }

    .overview-box {
        background: linear-gradient(to bottom right, #1e3a8a, #3b82f6);
        padding: 1.5rem;
        border-radius: 18px;
        text-align: center;
        margin: 1rem 0;
        transition: transform 0.4s ease;
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }

    .overview-box:hover {
        transform: translateY(-5px) scale(1.02);
    }
    .overview-box span {
        font-size: 2.2rem;
        font-weight: 800;
        color: #fcd34d;
    }

    .stButton>button {
        background: linear-gradient(135deg, #4f46e5, #9333ea);
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        box-shadow: 0 6px 25px rgba(0,0,0,0.3);
        transition: all 0.2s ease-in-out;
        border: none;
    }

    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 30px rgba(0,0,0,0.4);
    }

    .stButton>button:active {
        transform: scale(0.95);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    .edit-section {
        background: #1e293b;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }

    .alert-box {
        background: linear-gradient(135deg, #dc2626, #b91c1c);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
    }

    footer {
        text-align: center;
        color: #94a3b8;
        padding-top: 2rem;
    }
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
if "login_history" not in st.session_state:
    st.session_state.login_history = []
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

if not st.session_state.logged_in:
    st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>🔐 INTERSOFT Task Tracker</div></div>", unsafe_allow_html=True)
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    if st.button("Login 🚀"):
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

# --- Top Info Header ---
st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>👋 Welcome <b>{} ({})</b><br><small>Start tracking tasks, boost your day, and monitor progress like a pro!</small></div></div>".format(st.session_state.username.capitalize(), st.session_state.user_role), unsafe_allow_html=True)
st.markdown(f"<div class='date-box'>📅 {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}</div>", unsafe_allow_html=True)

# --- Logout Button ---
if st.button("🔓 Logout"):
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None
    st.rerun()

# --- Dashboard Overview ---
df = pd.DataFrame(st.session_state.timesheet)
df_user = df[df['Employee'] == st.session_state.username] if not df.empty else pd.DataFrame()
total_tasks = len(df_user) if st.session_state.user_role == "Employee" else len(df)
completed_tasks = df_user[df_user['Status'] == '✅ Completed'].shape[0] if not df_user.empty else 0 if st.session_state.user_role == "Employee" else df[df['Status'] == '✅ Completed'].shape[0] if not df.empty else 0
in_progress_tasks = df_user[df_user['Status'] == '🔄 In Progress'].shape[0] if not df_user.empty else 0 if st.session_state.user_role == "Employee" else df[df['Status'] == '🔄 In Progress'].shape[0] if not df.empty else 0
not_started_tasks = df_user[df_user['Status'] == '⏳ Not Started'].shape[0] if not df_user.empty else 0 if st.session_state.user_role == "Employee" else df[df['Status'] == '⏳ Not Started'].shape[0] if not df.empty else 0

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
    with st.form("task_form", clear_on_submit=True):
        st.subheader("📝 Add New Task")
        col1, col2 = st.columns(2)
        with col1:
            shift = st.selectbox("🕒 Shift", SHIFTS)
            date = st.date_input("📅 Date", value=datetime.today())
            department = st.selectbox("🏢 Department", ["FLM", "Tech Support", "CRM"])
        with col2:
            cat = st.selectbox("📂 Category", CATEGORIES)
            stat = st.selectbox("📌 Status", STATUSES)
            prio = st.selectbox("⚠️ Priority", PRIORITIES)
        desc = st.text_area("🗒 Task Description", height=100)
        btn1, btn2 = st.columns([1, 1])
        with btn1:
            submitted = st.form_submit_button("✅ Submit Task")
        with btn2:
            if st.session_state.user_role == "Admin":
                clear = st.form_submit_button("🧹 Clear All Tasks")
        if submitted:
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
                st.success("🎉 Task added successfully!")
                st.rerun()
            else:
                st.error("❌ Task description cannot be empty!")
        if st.session_state.user_role == "Admin" and clear:
            if st.checkbox("Confirm Clear All Tasks"):
                st.session_state.timesheet = []
                st.warning("🧹 All tasks cleared!")
                st.rerun()

# --- Edit/Delete Task ---
with tab2:
    st.subheader("✏️ Edit or Delete Existing Task")
    display_df = df_user if st.session_state.user_role == "Employee" else df
    if not display_df.empty:
        st.markdown("<div class='edit-section'>", unsafe_allow_html=True)
        task_options = {f"{row['Description'][:50]}... ({row['Date']} | {row['Category']} | {row['Status']} | {row['Employee'].capitalize()})": row['TaskID'] 
                       for _, row in display_df.iterrows()}
        selected_task_id = st.selectbox("📋 Select Task to Edit/Delete", 
                                      list(task_options.keys()), 
                                      help="Select a task to modify its details or delete it")
        selected_task_id = task_options.get(selected_task_id)
        
        selected_task = display_df[display_df['TaskID'] == selected_task_id].iloc[0] if selected_task_id else None
        
        with st.form("edit_task_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                shift = st.selectbox("🕒 Shift", SHIFTS, 
                                   index=SHIFTS.index(selected_task['Shift']) if selected_task is not None else 0)
                date = st.date_input("📅 Date", 
                                   value=datetime.strptime(selected_task['Date'], '%Y-%m-%d') if selected_task is not None else datetime.today())
                department = st.selectbox("🏢 Department", ["FLM", "Tech Support", "CRM"],
                                        index=["FLM", "Tech Support", "CRM"].index(selected_task['Department']) if selected_task is not None else 0)
            with col2:
                cat = st.selectbox("📂 Category", CATEGORIES,
                                 index=CATEGORIES.index(selected_task['Category']) if selected_task is not None else 0)
                stat = st.selectbox("📌 Status", STATUSES,
                                  index=STATUSES.index(selected_task['Status']) if selected_task is not None else 0)
                prio = st.selectbox("⚠️ Priority", PRIORITIES,
                                  index=PRIORITIES.index(selected_task['Priority']) if selected_task is not None else 0)
            desc = st.text_area("🗒 Task Description", 
                              value=selected_task['Description'] if selected_task is not None else "",
                              height=100)
            
            btn1, btn2 = st.columns([1, 1])
            with btn1:
                update_submitted = st.form_submit_button("✏️ Update Task")
            with btn2:
                delete_submitted = st.form_submit_button("🗑 Delete Task", key="delete_task_button")
            
            if update_submitted and selected_task_id:
                if desc.strip():
                    task_data = {
                        "TaskID": selected_task_id,
                        "Employee": selected_task['Employee'] if st.session_state.user_role == "Employee" else st.session_state.username,
                        "Date": date.strftime('%Y-%m-%d'),
                        "Day": calendar.day_name[date.weekday()],
                        "Shift": shift,
                        "Department": department,
                        "Category": cat,
                        "Status": stat,
                        "Priority": prio,
                        "Description": desc,
                        "Submitted": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    st.session_state.timesheet = [task if task['TaskID'] != selected_task_id else task_data 
                                               for task in st.session_state.timesheet]
                    st.success("🎉 Task updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Task description cannot be empty!")
            
            if delete_submitted and selected_task_id:
                if st.checkbox("Confirm Delete Task"):
                    st.session_state.timesheet = [task for task in st.session_state.timesheet 
                                               if task['TaskID'] != selected_task_id]
                    st.warning("🗑 Task deleted successfully!")
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("ℹ️ No tasks available to edit or delete. Add tasks in the 'Add Task' tab.")

# --- Analytics ---
with tab3:
    if not df_user.empty or (st.session_state.user_role in ["Admin", "Supervisor"] and not df.empty):
        st.subheader("📊 Task Analysis")
        display_df = df_user if st.session_state.user_role == "Employee" else df
        st.plotly_chart(px.histogram(display_df, x="Date", color="Status", barmode="group", title="Tasks Over Time"), use_container_width=True)
        st.plotly_chart(px.pie(display_df, names="Category", title="Category Breakdown"), use_container_width=True)
        st.plotly_chart(px.bar(display_df, x="Priority", color="Priority", title="Priority Distribution"), use_container_width=True)

        st.markdown("### 📋 Task Table")
        st.dataframe(display_df)

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
            for col_num, value in enumerate(display_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 18)
        st.download_button(
            label="📥 Download Excel File",
            data=output.getvalue(),
            file_name="FLM_Tasks.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # --- Calendar-Style Task Summary ---
        st.markdown("### 📅 Calendar-Style Task Summary")
        dates = pd.date_range(start=df['Date'].min(), end=df['Date'].max()) if not df.empty else pd.date_range(start=datetime.today(), end=datetime.today())
        calendar_data = []
        for d in dates:
            d_str = d.strftime('%Y-%m-%d')
            tasks_on_date = display_df[display_df['Date'] == d_str]
            task_count = len(tasks_on_date)
            calendar_data.append({"Date": d_str, "Task Count": task_count})
        calendar_df = pd.DataFrame(calendar_data)
        st.dataframe(calendar_df, use_container_width=True)
    else:
        st.info("ℹ️ No tasks found. Add some from the 'Add Task' tab.")

# --- Admin Panel ---
if st.session_state.user_role == "Admin" and admin_tab:
    with admin_tab[0]:
        st.subheader("🛠 Admin Panel")
        
        # --- Filter by Employee & Date ---
        st.markdown("### 🔍 Filter Tasks")
        col1, col2 = st.columns(2)
        with col1:
            filter_employee = st.selectbox("Select Employee", ["All"] + list(set(df['Employee'].unique()) if not df.empty else []))
        with col2:
            filter_date = st.date_input("Select Date Range", value=(datetime.today(), datetime.today()))
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
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 18)
        st.download_button(
            label="📥 Download All Tasks",
            data=output.getvalue(),
            file_name="All_FLM_Tasks.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# --- Footer ---
st.markdown(f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%Y-%m-%d %H:%M %p')}</footer>", unsafe_allow_html=True)
