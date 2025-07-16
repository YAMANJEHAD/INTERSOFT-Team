import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar
import re
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# --- Page Configuration ---
st.set_page_config(
    page_title="📋 FLM Task Tracker | INTERSOFT",
    layout="wide",
    page_icon="📋"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #0f172a;
        color: #e5e7eb;
        scroll-behavior: smooth;
    }

    .header, .card, .login-container {
        background: #1e293b;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin: 1rem auto;
        max-width: 900px;
        animation: fadeIn 0.8s ease-in-out;
    }

    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    .stButton>button {
        background: linear-gradient(135deg, #4f46e5, #6b21a8);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        transition: transform 0.3s ease;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #3730a3, #7e22ce);
        transform: scale(1.03);
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
        st.markdown("""
            <div class="header">
                <h2>🔐 INTERSOFT - Task Tracker</h2>
                <p>Please log in to continue</p>
            </div>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            username = st.text_input("👤 Username")
            password = st.text_input("🔑 Password", type="password")
            if st.button("Login 🚀"):
                if check_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.user_role = username
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
            st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- Header ---
st.markdown(f"""
    <div class="header">
        <h2>👋 Welcome {st.session_state.user_role}</h2>
        <p>📊 FLM Task Tracker Dashboard</p>
    </div>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

SHIFTS = ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"]
CATEGORIES = ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM", "📅 Meetings"]
PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]

# --- Sidebar Filters ---
with st.sidebar:
    st.header("🔍 Filters")
    start_date, end_date = st.date_input("📅 Select Date Range", [datetime.today(), datetime.today()])
    category = st.selectbox("📂 Category", ["All"] + CATEGORIES)
    status = st.selectbox("📌 Status", ["All"] + STATUSES)

# --- Tabs ---
tab1, tab2 = st.tabs(["➕ Add Task", "📈 Analytics"])

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

        st.subheader("📊 Task Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("📌 Total", len(df))
        col2.metric("✅ Completed", df[df['Status'].str.contains("Completed")].shape[0])
        col3.metric("🔄 In Progress", df[df['Status'].str.contains("In Progress")].shape[0])

        st.subheader("📈 Tasks Over Time")
        fig = px.histogram(df, x="Date", color="Status", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 All Tasks")
        st.dataframe(df)
    else:
        st.info("ℹ️ No tasks found.")

# --- Footer ---
st.markdown(f"""
    <center>
        <small style="color:#888;">📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</small>
    </center>
""", unsafe_allow_html=True)
