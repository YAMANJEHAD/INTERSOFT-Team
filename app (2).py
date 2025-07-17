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

# --- Custom CSS Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0f172a;
        color: #f8fafc;
    }
    .header {
        background: linear-gradient(135deg, #4f46e5, #9333ea);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 0 25px rgba(0,0,0,0.3);
        margin-bottom: 2rem;
        text-align: center;
    }
    h2, h3, p {
        color: white;
    }
    .metric-box {
        background: rgba(255,255,255,0.05);
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: 0.3s;
    }
    .metric-box:hover {
        background-color: #1e293b;
    }
    .metric-box span {
        display: block;
        font-size: 1.8rem;
        font-weight: bold;
        color: #facc15;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: white;
        border-radius: 10px 10px 0 0;
    }
    .stSelectbox > div > div {
        background-color: white;
        color: black;
        border-radius: 8px;
    }
    .stTextInput > div > div > input, .stTextArea textarea {
        background-color: #f8fafc;
        color: black;
    }
    .form-section {
        background-color: #1e293b;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 0 30px rgba(0,0,0,0.4);
    }
    .stButton>button {
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        color: white;
        font-weight: bold;
        padding: 0.8rem 1.5rem;
        border-radius: 10px;
        border: none;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        background: linear-gradient(135deg, #8b5cf6, #6366f1);
    }
    footer {
        text-align: center;
        margin-top: 2rem;
        color: #94a3b8;
    }
    </style>
""", unsafe_allow_html=True)

# --- Login System ---
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

# --- Welcome Header ---
st.markdown(f"<div class='header'><h2>👋 Welcome {st.session_state.user_role}</h2><p>Start managing your daily activities with INTERSOFT</p></div>", unsafe_allow_html=True)

if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

SHIFTS = ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"]
CATEGORIES = ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM", "📅 Meetings", "💻 TOMS"]
PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]

# --- Sidebar Filters ---
with st.sidebar:
    st.header("📋 Filters")
    start_date = st.date_input("📅 Start Date", datetime.today())
    end_date = st.date_input("📅 End Date", datetime.today())
    category = st.selectbox("📂 Category", ["All"] + CATEGORIES)
    status = st.selectbox("📌 Status", ["All"] + STATUSES)

# --- Tabs ---
tab1, tab2 = st.tabs(["➕ Add Task", "📈 Analytics"])

with tab1:
    with st.form("task_form", clear_on_submit=True):
        st.markdown("<div class='form-section'>", unsafe_allow_html=True)
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

        submit = st.form_submit_button("✅ Submit Task")
        st.markdown("</div>", unsafe_allow_html=True)

        if submit:
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

        # Filter data
        df = df[(df['Date'] >= start_date.strftime('%Y-%m-%d')) & (df['Date'] <= end_date.strftime('%Y-%m-%d'))]
        if category != "All":
            df = df[df['Category'] == category]
        if status != "All":
            df = df[df['Status'] == status]

        st.subheader("📊 Task Summary")
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"<div class='metric-box'>Total<span>{len(df)}</span></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='metric-box'>Completed<span>{df[df['Status'] == '✅ Completed'].shape[0]}</span></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='metric-box'>In Progress<span>{df[df['Status'] == '🔄 In Progress'].shape[0]}</span></div>", unsafe_allow_html=True)

        st.subheader("📈 Timeline View")
        st.plotly_chart(px.histogram(df, x="Date", color="Status", barmode="group"), use_container_width=True)

        st.subheader("📂 Category Breakdown")
        st.plotly_chart(px.pie(df, names="Category", title="Task Categories"), use_container_width=True)

        st.subheader("⚠️ Priority Overview")
        st.plotly_chart(px.bar(df, x="Priority", color="Priority", title="Tasks by Priority"), use_container_width=True)

        st.subheader("📋 All Tasks")
        st.dataframe(df)

        st.subheader("📤 Export to Excel")
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
        st.info("ℹ️ No tasks found. Add some from the 'Add Task' tab.")

# --- Footer ---
st.markdown(f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</footer>", unsafe_allow_html=True)
