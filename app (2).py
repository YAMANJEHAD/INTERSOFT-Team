import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar
from io import BytesIO

# --- Page Configuration ---
st.set_page_config(
    page_title="📋 FLM Task Tracker | INTERSOFT",
    layout="wide",
    page_icon=""
)

# --- Custom Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #0f172a;
        color: #e5e7eb;
    }
    .header, .card {
        background: #1e293b;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4);
        margin: 1.5rem auto;
        max-width: 1000px;
        animation: fadeIn 0.8s ease-in-out;
    }
    h2 {
        font-size: 2rem;
        color: #facc15;
        margin-bottom: 0.5rem;
    }
    p {
        color: #94a3b8;
        font-size: 1rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.03);
    }
    .stSelectbox>div>div>div {
        color: black !important;
    }
    .sidebar .sidebar-content {
        background-color: #1e293b;
    }
    .metric-label {
        color: #cbd5e1 !important;
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
    with st.container():
        st.markdown("<div class='header'><h2>🔐 INTERSOFT - Task Tracker</h2><p>Login to continue</p></div>", unsafe_allow_html=True)
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

# --- Header ---
st.markdown(f"<div class='header'><h2>👋 Welcome Back {st.session_state.user_role}</h2><p>📊 FLM Task Tracker Dashboard</p></div>", unsafe_allow_html=True)

if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

SHIFTS = ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"]
CATEGORIES = ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM", "📅 Meetings", "💻TOMS"]
PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]

# --- Sidebar Filters ---
with st.sidebar:
    st.markdown("## INTERSOFT POS")
    st.markdown("### International Software Company")
    st.markdown("---")
    st.markdown("🔍 **Filters**")
    start_date, end_date = st.date_input("📅 Select Date Range", [datetime.today(), datetime.today()])
    category = st.selectbox("📂 Category", ["All"] + CATEGORIES)
    status = st.selectbox("📌 Status", ["All"] + STATUSES)

# --- Tabs ---
tab1, tab2 = st.tabs(["➕ Add Task", "📈 Analytics"])

with tab1:
    with st.form("task_form", clear_on_submit=True):
        st.markdown("### 📝 Add New Task")
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

        if st.form_submit_button("Submit Task ✅"):
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
            st.success("✅ Task added successfully!")

with tab2:
    if st.session_state.timesheet:
        df = pd.DataFrame(st.session_state.timesheet)
        df = df[df['Employee'] == st.session_state.user_role]

        if category != "All":
            df = df[df['Category'] == category]
        if status != "All":
            df = df[df['Status'] == status]
        df = df[(df['Date'] >= start_date.strftime('%Y-%m-%d')) & (df['Date'] <= end_date.strftime('%Y-%m-%d'))]

        st.markdown("### 📊 Task Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("📌 Total", len(df))
        col2.metric("✅ Completed", df[df['Status'].str.contains("Completed")].shape[0])
        col3.metric("🔄 In Progress", df[df['Status'].str.contains("In Progress")].shape[0])

        st.markdown("### 📈 Tasks by Date")
        fig1 = px.histogram(df, x="Date", color="Status", barmode="group")
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("### 📉 Tasks by Category")
        fig2 = px.pie(df, names="Category", title="Task Distribution by Category")
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### 📊 Tasks by Priority")
        fig3 = px.bar(df, x="Priority", color="Priority", title="Tasks by Priority")
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("### 📋 All Tasks")
        st.dataframe(df)

        st.markdown("### 📤 Export to Excel")
        if st.button("Download Excel 📥"):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Tasks')
                workbook = writer.book
                worksheet = writer.sheets['Tasks']
                header_format = workbook.add_format({
                    'bold': True,
                    'font_color': 'white',
                    'bg_color': '#4f81bd',
                    'font_size': 14,
                    'align': 'center',
                    'valign': 'vcenter'
                })
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    worksheet.set_column(col_num, col_num, 18)
            st.download_button(
                label="📥 Download Excel File",
                data=output.getvalue(),
                file_name="FLM_Tasks.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("ℹ️ No tasks found.")

# --- Footer ---
st.markdown(f"<center><small style='color:#888;'>📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</small></center>", unsafe_allow_html=True)
