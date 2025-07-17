# FLM Task Tracker – Enhanced UX + Header Layout + SQLite + Admin Panel
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import calendar
from io import BytesIO
import uuid
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- Database Setup ---
engine = create_engine('sqlite:///tasks.db')
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(String, primary_key=True)
    employee = Column(String)
    date = Column(String)
    day = Column(String)
    shift = Column(String)
    department = Column(String)
    category = Column(String)
    status = Column(String)
    priority = Column(String)
    description = Column(String)
    submitted = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = 'users'
    username = Column(String, primary_key=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)

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

    footer {
        text-align: center;
        color: #94a3b8;
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Authentication ---
def check_login(username, password):
    session = SessionLocal()
    user = session.query(User).filter(User.username == username, User.password == password).first()
    return user is not None

def register_user(username, password):
    session = SessionLocal()
    if session.query(User).filter_by(username=username).first():
        return False
    user = User(username=username, password=password)
    session.add(user)
    session.commit()
    return True

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

if not st.session_state.logged_in:
    st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>🔐 INTERSOFT Task Tracker</div></div>", unsafe_allow_html=True)
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    col_login, col_register = st.columns(2)
    if col_login.button("Login 🚀"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.session_state.user_role = username
            st.rerun()
        else:
            st.error("❌ Invalid credentials")
    if col_register.button("➕ Register New User"):
        if register_user(username, password):
            st.success("✅ User registered. You can now log in.")
        else:
            st.warning("⚠️ Username already exists.")
    st.stop()

# --- Role-Based Tabs ---
if st.session_state.user_role == "admin":
    st.header("🔐 Admin Panel")
    st.subheader("👥 Manage Users")
    st.info("(Feature coming soon: modify user passwords and roles)")
    session = SessionLocal()
    users = session.query(User).all()
    st.write(pd.DataFrame([u.__dict__ for u in users]).drop(columns=['_sa_instance_state']))
    st.stop()

# --- Regular User Dashboard ---
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

SHIFTS = ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"]
CATEGORIES = ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM", "📅 Meetings", "💻 TOMS"]
PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]

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
        btn1, btn2 = st.columns([1, 1])
        with btn1:
            submitted = st.form_submit_button("✅ Submit Task")
        with btn2:
            clear = st.form_submit_button("🧹 Clear All Tasks")
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
        if clear:
            st.session_state.timesheet = []
            st.warning("🧹 All tasks cleared!")

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
