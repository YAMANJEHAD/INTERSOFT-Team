# FLM Task Tracker – Enhanced, Cleaned, and Dynamic
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import calendar
from io import BytesIO

# --- Page Configuration ---
st.set_page_config(
    page_title="📋 FLM Task Tracker | INTERSOFT",
    layout="wide",
    page_icon="⏱"
)

# --- Enhanced Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(145deg, #0f172a, #1e293b);
        color: #f8fafc;
    }

    h2, h3, p { color: #f1f5f9; }

    .header {
        background: linear-gradient(to right, #3b82f6, #6366f1);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin: 2rem 0;
        text-align: center;
        animation: slideDown 0.6s ease;
    }

    @keyframes slideDown {
        from {opacity: 0; transform: translateY(-30px);}
        to {opacity: 1; transform: translateY(0);}
    }

    .stButton>button {
        background: linear-gradient(135deg, #6366f1, #7c3aed);
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.7rem 1.5rem;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        transform: scale(1.03);
    }

    .metric-box {
        background: #1e293b;
        padding: 1.2rem;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.4);
    }
    .metric-box span {
        display: block;
        font-size: 1.9rem;
        font-weight: bold;
        color: #facc15;
    }

    .task-card {
        background: rgba(255,255,255,0.05);
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 12px;
        transition: 0.3s;
    }
    .task-card:hover {
        background: rgba(255,255,255,0.1);
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
    st.markdown("<div class='header'><h2>🔐 INTERSOFT Task Tracker</h2><p>Please log in to continue</p></div>", unsafe_allow_html=True)
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

# --- Header After Login ---
st.markdown(f"<div class='header'><h2>👋 Welcome {st.session_state.user_role}</h2><p>Manage your tasks with confidence and clarity</p></div>", unsafe_allow_html=True)

# --- Constants ---
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

SHIFTS = ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"]
CATEGORIES = ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM", "📅 Meetings", "💻 TOMS"]
PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]

# --- Sidebar Filters ---
with st.sidebar:
    st.header("📋 Filters")
    start_date = st.date_input("📅 From", datetime.today() - timedelta(days=7))
    end_date = st.date_input("📅 To", datetime.today())
    category = st.selectbox("📂 Category", ["All"] + CATEGORIES)
    status = st.selectbox("📌 Status", ["All"] + STATUSES)

# --- Tabs ---
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
        submitted = st.form_submit_button("✅ Submit Task")
        if submitted:
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

# --- Analytics Tab ---
with tab2:
    if st.session_state.timesheet:
        df = pd.DataFrame(st.session_state.timesheet)
        df = df[df['Employee'] == st.session_state.user_role]
        df = df[(df['Date'] >= start_date.strftime('%Y-%m-%d')) & (df['Date'] <= end_date.strftime('%Y-%m-%d'))]
        if category != "All": df = df[df['Category'] == category]
        if status != "All": df = df[df['Status'] == status]

        st.subheader("📊 Task Overview")
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"<div class='metric-box'>Total<span>{len(df)}</span></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='metric-box'>Completed<span>{df[df['Status'] == '✅ Completed'].shape[0]}</span></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='metric-box'>In Progress<span>{df[df['Status'] == '🔄 In Progress'].shape[0]}</span></div>", unsafe_allow_html=True)

        st.markdown("### 📈 Tasks Over Time")
        st.plotly_chart(px.histogram(df, x="Date", color="Status", barmode="group"), use_container_width=True)

        st.markdown("### 🧠 Task Categories")
        st.plotly_chart(px.pie(df, names="Category", title="Category Breakdown"), use_container_width=True)

        st.markdown("### ⚠️ Priority Distribution")
        st.plotly_chart(px.bar(df, x="Priority", color="Priority", title="Tasks by Priority"), use_container_width=True)

        st.markdown("### 📋 Task Table")
        st.dataframe(df)

        st.markdown("### 📤 Export to Excel")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Tasks')
            workbook = writer.book
            worksheet = writer.sheets['Tasks']
            header_format = workbook.add_format({
                'bold': True, 'font_color': 'white', 'bg_color': '#4f81bd',
                'font_size': 12, 'align': 'center', 'valign': 'vcenter'
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
        st.info("ℹ️ No tasks found. Please add new ones to see analytics.")

# --- Footer ---
st.markdown(f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</footer>", unsafe_allow_html=True)
