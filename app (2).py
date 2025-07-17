# FLM Task Tracker – Stunning Interactive Home Dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import calendar
from io import BytesIO

# --- Page Configuration ---
st.set_page_config(
    page_title="⚡ INTERSOFT Dashboard | FLM",
    layout="wide",
    page_icon="🚀"
)

# --- Gorgeous Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background: radial-gradient(circle at top left, #0f172a, #1e293b);
        color: #f8fafc;
        scroll-behavior: smooth;
    }
    h2, h3, p { color: #f1f5f9; }

    .header {
        background: linear-gradient(to right, #4f46e5, #7c3aed);
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0,0,0,0.6);
        margin-bottom: 2rem;
        animation: dropFade 0.8s ease-out;
    }
    @keyframes dropFade {
        0% { opacity: 0; transform: translateY(-60px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    .overview-box {
        background: linear-gradient(to bottom right, #1e3a8a, #3b82f6);
        padding: 1.5rem;
        border-radius: 18px;
        text-align: center;
        margin: 1rem 0;
        transition: 0.4s ease;
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
        animation: fadeScale 0.8s ease;
    }
    .overview-box:hover {
        transform: translateY(-5px) scale(1.02);
    }
    .overview-box span {
        font-size: 2.2rem;
        font-weight: 800;
        color: #fcd34d;
    }

    @keyframes fadeScale {
        from { opacity: 0; transform: scale(0.8); }
        to { opacity: 1; transform: scale(1); }
    }

    .stButton>button {
        background: linear-gradient(135deg, #4f46e5, #9333ea);
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.7rem 1.5rem;
        box-shadow: 0 6px 25px rgba(0,0,0,0.3);
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        transform: scale(1.05);
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
    st.markdown("<div class='header'><h2>🔐 INTERSOFT Task Tracker</h2><p>Please log in to access the dashboard</p></div>", unsafe_allow_html=True)
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

# --- State Init ---
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

SHIFTS = ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"]
CATEGORIES = ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM", "📅 Meetings", "💻 TOMS"]
PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]

# --- Header ---
st.markdown(f"""
    <div class='header'>
    <h2>👋 Welcome {st.session_state.user_role}</h2>
    <p>Start tracking tasks, boost your day, and monitor progress like a pro!</p>
    </div>
""", unsafe_allow_html=True)

# --- Home Overview ---
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

# --- Main Tabs ---
tab1, tab2 = st.tabs(["➕ Add Task", "📈 Analytics"])

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
        if st.form_submit_button("✅ Submit Task"):
            st.session_state.timesheet.append({
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

# --- Analytics ---
with tab2:
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
