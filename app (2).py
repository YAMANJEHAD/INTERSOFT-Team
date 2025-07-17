# FLM Task Tracker – Enhanced UX + Database + Admin Panel
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
    role = Column(String)  # 'admin' or 'user'

Base.metadata.create_all(bind=engine)

# --- Page Configuration ---
st.set_page_config(
    page_title="⚡ INTERSOFT Dashboard | FLM",
    layout="wide",
    page_icon="🚀"
)

# --- Styling (unchanged) ---
st.markdown("""<style>...</style>""", unsafe_allow_html=True)

# --- Session Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = ""

# --- Authentication ---
def login_user(username, password):
    db = SessionLocal()
    user = db.query(User).filter_by(username=username, password=password).first()
    return user

def register_user(username, password, role):
    db = SessionLocal()
    if db.query(User).filter_by(username=username).first():
        return False
    new_user = User(username=username, password=password, role=role)
    db.add(new_user)
    db.commit()
    return True

if not st.session_state.logged_in:
    auth_tab, reg_tab = st.tabs(["🔐 Login", "📝 Register"])
    with auth_tab:
        username = st.text_input("👤 Username")
        password = st.text_input("🔑 Password", type="password")
        if st.button("Login 🚀"):
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user.username
                st.session_state.user_role = user.role
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

    with reg_tab:
        new_username = st.text_input("👤 New Username")
        new_password = st.text_input("🔑 New Password", type="password")
        new_role = st.selectbox("🧑‍💼 Role", ["user", "admin"])
        if st.button("Register ✅"):
            if register_user(new_username, new_password, new_role):
                st.success("✅ User registered. You can now login.")
            else:
                st.error("⚠️ Username already exists.")

    st.stop()

# --- Top Header ---
st.markdown(f"<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>👋 Welcome <b>{st.session_state.username}</b><br><small>Start tracking tasks, boost your day, and monitor progress like a pro!</small></div></div>", unsafe_allow_html=True)
st.markdown(f"<div class='date-box'>📅 {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}</div>", unsafe_allow_html=True)

# --- Task Management ---
db = SessionLocal()
tasks = db.query(Task).filter_by(employee=st.session_state.username).all() if st.session_state.user_role != "admin" else db.query(Task).all()
df = pd.DataFrame([t.__dict__ for t in tasks]).drop(columns=['_sa_instance_state', 'id']) if tasks else pd.DataFrame()

total_tasks = len(df)
completed_tasks = df[df['status'] == '✅ Completed'].shape[0] if not df.empty else 0
in_progress_tasks = df[df['status'] == '🔄 In Progress'].shape[0] if not df.empty else 0
not_started_tasks = df[df['status'] == '⏳ Not Started'].shape[0] if not df.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div class='overview-box'>Total Tasks<br><span>{total_tasks}</span></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='overview-box'>Completed<br><span>{completed_tasks}</span></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='overview-box'>In Progress<br><span>{in_progress_tasks}</span></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='overview-box'>Not Started<br><span>{not_started_tasks}</span></div>", unsafe_allow_html=True)

# --- Tabs ---
tabs = ["➕ Add Task", "📈 Analytics"]
if st.session_state.user_role == "admin":
    tabs.append("👥 Manage Users")
tab1, tab2, *extra_tabs = st.tabs(tabs)

# --- Add Task ---
with tab1:
    with st.form("task_form", clear_on_submit=True):
        st.subheader("📝 Add New Task")
        col1, col2 = st.columns(2)
        with col1:
            shift = st.selectbox("🕒 Shift", ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"])
            date = st.date_input("📅 Date", value=datetime.today())
            department = st.selectbox("🏢 Department", ["FLM", "Tech Support", "CRM"])
        with col2:
            cat = st.selectbox("📂 Category", ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM", "📅 Meetings", "💻 TOMS"])
            stat = st.selectbox("📌 Status", ["⏳ Not Started", "🔄 In Progress", "✅ Completed"])
            prio = st.selectbox("⚠️ Priority", ["🟢 Low", "🟡 Medium", "🔴 High"])
        desc = st.text_area("🗒 Task Description", height=100)
        if st.form_submit_button("✅ Submit Task"):
            new_task = Task(
                id=str(uuid.uuid4()),
                employee=st.session_state.username,
                date=date.strftime('%Y-%m-%d'),
                day=calendar.day_name[date.weekday()],
                shift=shift,
                department=department,
                category=cat,
                status=stat,
                priority=prio,
                description=desc
            )
            db.add(new_task)
            db.commit()
            st.success("🎉 Task added successfully!")
            st.rerun()

# --- Analytics ---
with tab2:
    if not df.empty:
        st.subheader("📊 Task Analysis")
        st.plotly_chart(px.histogram(df, x="date", color="status", barmode="group", title="Tasks Over Time"), use_container_width=True)
        st.plotly_chart(px.pie(df, names="category", title="Category Breakdown"), use_container_width=True)
        st.plotly_chart(px.bar(df, x="priority", color="priority", title="Priority Distribution"), use_container_width=True)

        st.markdown("### 📋 Task Table")
        st.dataframe(df)

        st.markdown("### 📥 Export to Excel")
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

# --- Admin Tab ---
if st.session_state.user_role == "admin" and extra_tabs:
    with extra_tabs[0]:
        st.subheader("👥 Manage Users")
        users = db.query(User).all()
        df_users = pd.DataFrame([u.__dict__ for u in users]).drop(columns=['_sa_instance_state'])
        st.dataframe(df_users)

# --- Footer ---
st.markdown(f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</footer>", unsafe_allow_html=True)
