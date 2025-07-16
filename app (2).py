import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar
from io import BytesIO
from streamlit_calendar import calendar

# --- Page Configuration ---
st.set_page_config(
    page_title="📋 INTERSOFT Task Tracker",
    layout="wide",
    page_icon="💼"
)

# --- Fix Selectbox Text Color ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0f172a;
        color: white;
    }

    .stSelectbox label, .stTextInput label, .stDateInput label, .stTextArea label {
        color: white !important;
    }

    .stSelectbox div div div {
        color: black !important;
    }

    .sidebar .sidebar-content {
        background-color: #1e293b;
    }

    .tab-header {
        background: linear-gradient(to right, #4f46e5, #9333ea);
        padding: 1rem;
        text-align: center;
        color: white;
        border-radius: 12px;
        margin-bottom: 1rem;
        font-size: 1.3rem;
        animation: fadeInSlide 1s ease-in-out;
    }

    @keyframes fadeInSlide {
        from { opacity: 0; transform: translateY(40px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
""", unsafe_allow_html=True)

# --- Authentication (Simple Version) ---
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
    st.markdown("<div class='tab-header'>🔐 INTERSOFT Login</div>", unsafe_allow_html=True)
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

# --- Pages Navigation ---
page = st.sidebar.radio("📁 Navigate", ["🏠 Dashboard", "🗓️ Calendar View"])

# --- Task Data Setup ---
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

SHIFTS = ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"]
CATEGORIES = ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM", "📅 Meetings", "💻TOMS"]
PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]

# --- Dashboard Page ---
if page == "🏠 Dashboard":
    st.markdown(f"<div class='tab-header'>👋 Welcome {st.session_state.user_role} | Task Dashboard</div>", unsafe_allow_html=True)

    # Filters
    start_date, end_date = st.date_input("📅 Select Date Range", [datetime.today(), datetime.today()])
    category = st.selectbox("📂 Category", ["All"] + CATEGORIES)
    status = st.selectbox("📌 Status", ["All"] + STATUSES)

    # Tabs
    tab1, tab2 = st.tabs(["➕ Add Task", "📊 Analytics"])

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

    with tab2:
        if st.session_state.timesheet:
            df = pd.DataFrame(st.session_state.timesheet)
            df = df[df['Employee'] == st.session_state.user_role]

            if category != "All":
                df = df[df['Category'] == category]
            if status != "All":
                df = df[df['Status'] == status]
            df = df[(df['Date'] >= start_date.strftime('%Y-%m-%d')) & (df['Date'] <= end_date.strftime('%Y-%m-%d'))]

            st.metric("📌 Total", len(df))
            st.metric("✅ Completed", df[df['Status'].str.contains("Completed")].shape[0])
            st.metric("🔄 In Progress", df[df['Status'].str.contains("In Progress")].shape[0])

            st.markdown("### 📈 Tasks by Date")
            fig1 = px.histogram(df, x="Date", color="Status", barmode="group")
            st.plotly_chart(fig1, use_container_width=True)

            st.markdown("### 📉 Task Distribution by Category")
            fig2 = px.pie(df, names="Category", title="Task Categories")
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown("### ⚠️ Tasks by Priority")
            fig3 = px.bar(df, x="Priority", color="Priority", title="Task Priorities")
            st.plotly_chart(fig3, use_container_width=True)

            st.dataframe(df)

            if st.button("📥 Download Excel"):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Tasks')
                st.download_button("📤 Download File", output.getvalue(), "FLM_Tasks.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("ℹ️ No tasks found.")

# --- Calendar View Page ---
elif page == "🗓️ Calendar View":
    st.markdown(f"<div class='tab-header'>📅 Task Calendar</div>", unsafe_allow_html=True)

    if st.session_state.timesheet:
        df = pd.DataFrame(st.session_state.timesheet)
        events = [
            {
                "title": f"{row['Category']} - {row['Status']}",
                "start": row["Date"],
                "end": row["Date"],
                "color": "#6366f1"
            }
            for _, row in df.iterrows()
        ]

        calendar_options = {
            "initialView": "dayGridMonth",
            "editable": False,
            "height": 650,
            "plugins": ["dayGrid", "interaction"],
        }

        calendar(events=events, options=calendar_options)
    else:
        st.info("ℹ️ No tasks to display in calendar.")

# --- Footer ---
st.markdown(f"<hr><center style='color:gray;'>INTERSOFT • {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</center>", unsafe_allow_html=True)
