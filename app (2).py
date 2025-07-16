import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import calendar
from io import BytesIO
import re


try:
    from streamlit_calendar import calendar
except ImportError:
    st.warning("⚠️ 'streamlit-calendar' not installed. Please install it via 'pip install streamlit-calendar'")

# --- Page Configuration ---
st.set_page_config(
    page_title="📋 FLM Task Tracker | INTERSOFT",
    layout="wide",
    page_icon="📋"
)

# --- Styling ---
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #0f172a;
        color: #e5e7eb;
    }
    .header, .card {
        background: #1e293b;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin: 1rem auto;
        max-width: 900px;
        animation: fadeIn 0.8s ease-in-out;
    }
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5, #6b21a8);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
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

st.markdown(f"<div class='header'><h2>👋 Welcome {st.session_state.user_role}</h2><p>📊 FLM Task Tracker Dashboard</p></div>", unsafe_allow_html=True)

if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

SHIFTS = ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"]
CATEGORIES = ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM", "📅 Meetings"]
PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]

# --- Sidebar Filters ---
with st.sidebar:
    st.header("🔍 Filters")
    start_date, end_date = st.date_input("📅 Date Range", [datetime.today(), datetime.today()])
    category = st.selectbox("📂 Category", ["All"] + CATEGORIES)
    status = st.selectbox("📌 Status", ["All"] + STATUSES)
    keyword = st.text_input("🔍 Search in Description")

# --- AI Classification ---
def classify_task(desc):
    desc = desc.lower()
    if any(word in desc for word in ["install", "setup", "assembly"]):
        return "🔧 Job Orders"
    elif "report" in desc:
        return "📄 Paper Work"
    elif "meeting" in desc:
        return "📅 Meetings"
    elif "support" in desc or "customer" in desc:
        return "🤝 CRM"
    return "🛠 Operations"

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["➕ Add Task", "📈 Analytics", "📅 Calendar View"])

with tab1:
    with st.form("task_form", clear_on_submit=True):
        st.subheader("📝 Add New Task")
        col1, col2 = st.columns(2)
        with col1:
            shift = st.selectbox("🕒 Shift", SHIFTS)
            date = st.date_input("📅 Date", value=datetime.today())
            department = st.selectbox("🏢 Department", ["FLM", "Tech Support", "CRM"])
        with col2:
            stat = st.selectbox("📌 Status", STATUSES)
            prio = st.selectbox("⚠️ Priority", PRIORITIES)
        desc = st.text_area("🗒 Task Description", height=100)
        cat = classify_task(desc)

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
        if keyword:
            df = df[df['Description'].str.contains(keyword, case=False, na=False)]
        df = df[(df['Date'] >= start_date.strftime('%Y-%m-%d')) & (df['Date'] <= end_date.strftime('%Y-%m-%d'))]

        # Alert
        today_str = datetime.today().strftime('%Y-%m-%d')
        overdue = df[(df['Status'] == "⏳ Not Started") & (df['Date'] < today_str)]
        if not overdue.empty:
            st.warning(f"🔔 {len(overdue)} overdue task(s) not started!")

        st.subheader("📊 Task Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("📌 Total", len(df))
        col2.metric("✅ Completed", df[df['Status'].str.contains("Completed")].shape[0])
        col3.metric("🔄 In Progress", df[df['Status'].str.contains("In Progress")].shape[0])

        st.subheader("📈 Tasks by Date")
        st.plotly_chart(px.histogram(df, x="Date", color="Status", barmode="group"), use_container_width=True)

        st.subheader("📉 Tasks by Category")
        st.plotly_chart(px.pie(df, names="Category", title="Task Distribution"), use_container_width=True)

        st.subheader("📊 Tasks by Priority")
        st.plotly_chart(px.bar(df, x="Priority", color="Priority"), use_container_width=True)

        st.subheader("📋 All Tasks")
        st.dataframe(df)

        st.subheader("📤 Export to Excel")
        if st.button("Download Excel 📥"):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Tasks')
                workbook = writer.book
                worksheet = writer.sheets['Tasks']
                header_format = workbook.add_format({
                    'bold': True, 'font_color': 'white', 'bg_color': '#4f81bd',
                    'font_size': 14, 'align': 'center', 'valign': 'vcenter'
                })
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    worksheet.set_column(col_num, col_num, 18)
            st.download_button("📥 Download Excel File", output.getvalue(), "FLM_Tasks.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("ℹ️ No tasks found.")

with tab3:
    st.subheader("🗓 Interactive Calendar")
    if "streamlit_calendar" in globals():
        if st.session_state.timesheet:
            df = pd.DataFrame(st.session_state.timesheet)
            events = [
                {"title": row['Category'], "start": row['Date'], "end": row['Date']} 
                for _, row in df.iterrows()
            ]
            calendar(events=events, options={"editable": False, "height": 600}, key="calendar_view")
        else:
            st.info("No tasks to display on calendar.")
    else:
        st.error("❌ Please install `streamlit-calendar` using `pip install streamlit-calendar`")

st.markdown(f"<center><small style='color:#888;'>📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</small></center>", unsafe_allow_html=True)
