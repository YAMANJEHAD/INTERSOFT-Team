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
    page_icon="⏱"
)

# --- Enhanced CSS Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0f172a;
        color: #f8fafc;
        scroll-behavior: smooth;
    }

    .header {
        background: linear-gradient(135deg, #4f46e5, #9333ea);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.5);
        margin: 2rem auto;
        max-width: 1000px;
        text-align: center;
        animation: fadeInSlide 1s ease-in-out;
    }

    h2 {
        font-size: 2.6rem;
        color: white;
        margin-bottom: 0.3rem;
    }

    p {
        color: #cbd5e1;
        font-size: 1.1rem;
    }

    @keyframes fadeInSlide {
        from { opacity: 0; transform: translateY(40px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .stButton>button {
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        color: white;
        border: none;
        padding: 0.8rem 1.6rem;
        border-radius: 10px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: all 0.3s ease-in-out;
    }

    .stButton>button:hover {
        transform: scale(1.06);
        background: linear-gradient(135deg, #8b5cf6, #6366f1);
    }

    .metric-box {
        background: radial-gradient(circle at top left, #4f46e5, #1e293b);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.5);
        color: white;
        text-align: center;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }

    .metric-box:hover {
        transform: translateY(-5px);
    }

    .metric-box::before {
        content: "";
        position: absolute;
        width: 120%;
        height: 120%;
        background: rgba(255,255,255,0.05);
        top: -10%;
        left: -10%;
        transform: rotate(45deg);
        animation: ripple 4s infinite linear;
    }

    @keyframes ripple {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .metric-box h3 {
        margin: 0;
        font-size: 1.4rem;
        color: #facc15;
        z-index: 1;
        position: relative;
    }

    .metric-box span {
        font-size: 2rem;
        font-weight: 800;
        color: white;
        z-index: 1;
        position: relative;
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 1.1rem;
        font-weight: 600;
        color: #f1f5f9;
    }

    .stTabs [aria-selected="true"] {
        background-color: #334155 !important;
        border-radius: 8px 8px 0 0 !important;
    }

    .stSelectbox>div>div>div {
        color: black !important;
    }

    footer {
        text-align: center;
        color: #94a3b8;
        padding-top: 1rem;
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
        st.markdown("<div class='header'><h2>🔐 INTERSOFT - Task Tracker</h2><p>Please log in to continue</p></div>", unsafe_allow_html=True)
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

# --- Header after login ---
st.markdown(f"<div class='header'><h2>👋 Welcome {st.session_state.user_role}</h2><p>Manage your daily operations with elegance and speed</p></div>", unsafe_allow_html=True)

if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

SHIFTS = ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"]
CATEGORIES = ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM", "📅 Meetings", "💻TOMS"]
PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]

# --- Sidebar Filters ---
with st.sidebar:
    st.markdown("## 🧠 INTERSOFT POS")
    st.markdown("### International Software Company")
    st.markdown("—" * 10)
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

        st.markdown("### 📊 Task Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='metric-box'><h3>Total</h3><span>{len(df)}</span></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-box'><h3>Completed</h3><span>{df[df['Status'].str.contains('Completed')].shape[0]}</span></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-box'><h3>In Progress</h3><span>{df[df['Status'].str.contains('In Progress')].shape[0]}</span></div>", unsafe_allow_html=True)

        st.markdown("### 📈 Tasks by Date")
        fig1 = px.histogram(df, x="Date", color="Status", barmode="group")
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("### 📉 Category Breakdown")
        fig2 = px.pie(df, names="Category", title="Task Categories")
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### ⚠️ Priority Overview")
        fig3 = px.bar(df, x="Priority", color="Priority", title="Tasks by Priority")
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("### 📋 All Tasks")
        st.dataframe(df)

        st.markdown("### 📤 Export to Excel")
        if st.button("📥 Download Excel File"):
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
st.markdown(f"""
<footer>
    📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
</footer>
""", unsafe_allow_html=True)
