# FLM Task Tracker – Full Code with SQLite Integration (Old UI Style Restored)
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import calendar
import uuid
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from io import BytesIO

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

Base.metadata.create_all(bind=engine)

# --- Page Configuration ---
st.set_page_config(page_title="📋 FLM Task Tracker | INTERSOFT", layout="wide", page_icon="⏱")

# --- Enhanced Styling ---
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
</style>
""", unsafe_allow_html=True)

# --- Authentication ---
def check_login(username, password):
    return {"Yaman": "YAMAN1", "Hatem": "HATEM2", "Mahmoud": "MAHMOUD3", "Qusai": "QUSAI4"}.get(username) == password

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

if not st.session_state.logged_in:
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

# --- Load tasks from DB ---
session = SessionLocal()
tasks = session.query(Task).filter(Task.employee == st.session_state.user_role).all()
df = pd.DataFrame([t.__dict__ for t in tasks]).drop(columns=['_sa_instance_state', 'id']) if tasks else pd.DataFrame()

# --- Header after login ---
st.markdown(f"<div class='header'><h2>👋 Welcome {st.session_state.user_role}</h2><p>Manage your daily operations with elegance and speed</p></div>", unsafe_allow_html=True)

# --- Overview ---
total_tasks = len(df)
completed_tasks = df[df['status'] == '✅ Completed'].shape[0] if not df.empty else 0
in_progress_tasks = df[df['status'] == '🔄 In Progress'].shape[0] if not df.empty else 0
not_started_tasks = df[df['status'] == '⏳ Not Started'].shape[0] if not df.empty else 0
col1, col2, col3, col4 = st.columns(4)
col1.metric("📋 Total Tasks", total_tasks)
col2.metric("✅ Completed", completed_tasks)
col3.metric("🔄 In Progress", in_progress_tasks)
col4.metric("⏳ Not Started", not_started_tasks)

# --- Constants ---
SHIFTS = ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"]
CATEGORIES = ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM", "📅 Meetings", "💻 TOMS"]
PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]

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
            task = Task(
                id=str(uuid.uuid4()),
                employee=st.session_state.user_role,
                date=date.strftime('%Y-%m-%d'),
                day=calendar.day_name[date.weekday()],
                shift=shift,
                department=department,
                category=cat,
                status=stat,
                priority=prio,
                description=desc
            )
            session.add(task)
            session.commit()
            st.success("🎉 Task added and saved to the database!")
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

# --- Footer ---
st.markdown(f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</footer>", unsafe_allow_html=True)
