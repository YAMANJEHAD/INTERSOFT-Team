import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
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
        transition: 0.4s ease;
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
        transition: all 0.3s ease-in-out;
    }

    .stButton>button:hover {
        transform: scale(1.05);
    }

    .delete-button {
        background: linear-gradient(135deg, #dc2626, #b91c1c);
    }

    .edit-section {
        background: #1e293b;
        padding: 1.5rem;
        border-radius: 12px;
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

# --- Top Info Header ---
st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>👋 Welcome <b>{}</b><br><small>Start tracking tasks, boost your day, and monitor progress like a pro!</small></div></div>".format(st.session_state.user_role), unsafe_allow_html=True)
st.markdown(f"<div class='date-box'>📅 {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}</div>", unsafe_allow_html=True)

# --- Dashboard Overview ---
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

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["➕ Add Task", "✏️ Edit/Delete Task", "📈 Analytics"])

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
            clear = st.form_submit_button("🧹 Clear All Tasks")
        if submitted:
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
            st.success("🎉 Task added successfully!")
            st.rerun()
        if clear:
            if st.checkbox("Confirm Clear All Tasks"):
                st.session_state.timesheet = []
                st.warning("🧹 All tasks cleared!")
                st.rerun()

# --- Edit/Delete Task ---
with tab2:
    st.subheader("✏️ Edit or Delete Existing Task")
    if not df_user.empty:
        st.markdown("<div class='edit-section'>", unsafe_allow_html=True)
        task_options = {f"{row['Description'][:50]}... ({row['Date']} | {row['Category']} | {row['Status']})": row['TaskID'] 
                       for _, row in df_user.iterrows()}
        selected_task_id = st.selectbox("📋 Select Task to Edit/Delete", 
                                      list(task_options.keys()), 
                                      help="Select a task to modify its details or delete it")
        selected_task_id = task_options.get(selected_task_id)
        
        selected_task = df_user[df_user['TaskID'] == selected_task_id].iloc[0] if selected_task_id else None
        
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
                delete_submitted = st.form_submit_button("🗑 Delete Task", 
                                                      html_class="delete-button")
            
            if update_submitted and selected_task_id:
                task_data = {
                    "TaskID": selected_task_id,
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
                }
                st.session_state.timesheet = [task if task['TaskID'] != selected_task_id else task_data 
                                           for task in st.session_state.timesheet]
                st.success("🎉 Task updated successfully!")
                st.rerun()
            
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
    if not df_user.empty:
        st.subheader("📊 Task Analysis")
        st.plotly_chart(px.histogram(df_user, x="Date", color="Status", barmode="group", title="Tasks Over Time"), use_container_width=True)
        st.plotly_chart(px.pie(df_user, names="Category", title="Category Breakdown"), use_container_width=True)
        st.plotly_chart(px.bar(df_user, x="Priority", color="Priority", title="Priority Distribution"), use_container_width=True)

        st.markdown("### 📋 Task Table")
        st.dataframe(df_user)

        st.markdown("### 📥 Export to Excel")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_user.to_excel(writer, index=False, sheet_name='Tasks')
            workbook = writer.book
            worksheet = writer.sheets['Tasks']
            header_format = workbook.add_format({
                'bold': True, 'font_color': 'white', 'bg_color': '#4f81bd',
                'font_size': 12, 'align': 'center', 'valign': 'vcenter'
            })
            for col_num, value in enumerate(df_user.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 18)
        st.download_button(
            label="📥 Download Excel File",
            data=output.getvalue(),
            file_name="FLM_Tasks.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("ℹ️ No tasks found. Add some from the 'Add Task' tab.")

# --- Footer ---
st.markdown(f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</footer>", unsafe_allow_html=True)
