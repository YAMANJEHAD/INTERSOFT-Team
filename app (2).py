# FLM Task Tracker with Enhanced UI/UX, Animations, and Smart Features
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

# --- Dynamic & Responsive Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(145deg, #0f172a, #1e293b);
        color: #f8fafc;
        scroll-behavior: smooth;
    }

    @media (max-width: 768px) {
        h2 { font-size: 1.5rem; }
        .metric-box span { font-size: 1.5rem; }
    }

    .header {
        background: linear-gradient(to right, #3b82f6, #6366f1);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        margin: 2rem auto;
        text-align: center;
        animation: fadeInSlide 0.8s ease-out;
    }

    @keyframes fadeInSlide {
        from { opacity: 0; transform: translateY(-40px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .stButton>button {
        background: linear-gradient(135deg, #6366f1, #7c3aed);
        color: white;
        font-weight: bold;
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: scale(1.05) rotate(-1deg);
        background: linear-gradient(135deg, #818cf8, #a78bfa);
    }

    .metric-box {
        background: linear-gradient(to bottom right, #1e3a8a, #3b82f6);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        font-size: 1.1rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.5);
        animation: fadeIn 1s ease;
    }
    .metric-box span { font-size: 2.2rem; font-weight: bold; }

    .task-card {
        background: #1e293b;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.2);
        transition: 0.3s ease;
    }
    .task-card:hover {
        transform: scale(1.01);
        background: #334155;
    }

    footer {
        text-align: center;
        margin-top: 2rem;
        color: #94a3b8;
    }
    </style>
""", unsafe_allow_html=True)

# --- User Image & Auth ---
USER_IMAGES = {
    "Yaman": "https://i.imgur.com/0XKznLy.png",
    "Hatem": "https://i.imgur.com/0XKznLy.png",
    "Mahmoud": "https://i.imgur.com/0XKznLy.png",
    "Qusai": "https://i.imgur.com/0XKznLy.png"
}

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
    st.image("https://i.imgur.com/0XKznLy.png", width=100)
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
col_a, col_b = st.columns([1, 5])
with col_a:
    st.image(USER_IMAGES.get(st.session_state.user_role, ""), width=80)
with col_b:
    st.markdown(f"<div class='header'><h2>👋 Welcome {st.session_state.user_role}</h2><p>Manage your tasks with elegance & power!</p></div>", unsafe_allow_html=True)

if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

SHIFTS = ["🌞 Morning (8:30 - 5:30)", "🌙 Evening (3:00 - 11:00)"]
CATEGORIES = ["🛠 Operations", "📄 Paper Work", "🔧 Job Orders", "🤝 CRM", "📅 Meetings", "💻 TOMS"]
PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]

# --- Sidebar ---
with st.sidebar:
    st.image("https://i.imgur.com/0XKznLy.png", width=100)
    st.markdown("## 📋 Filters")
    start_date = st.date_input("📅 From", datetime.today() - timedelta(days=7))
    end_date = st.date_input("📅 To", datetime.today())
    category = st.selectbox("📂 Category", ["All"] + CATEGORIES)
    status = st.selectbox("📌 Status", ["All"] + STATUSES)

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["➕ Add Task", "📈 Analytics", "👤 Profile"])

# --- Add Task Tab ---
with tab1:
    inner_tab1, inner_tab2 = st.tabs(["📄 Basic Info", "🧾 Description"])
    with st.form("task_form", clear_on_submit=True):
        with inner_tab1:
            col1, col2 = st.columns(2)
            with col1:
                shift = st.selectbox("🕒 Shift", SHIFTS)
                date = st.date_input("📅 Date", value=datetime.today())
                department = st.selectbox("🏢 Department", ["FLM", "Tech Support", "CRM"])
            with col2:
                cat = st.selectbox("📂 Category", CATEGORIES)
                stat = st.selectbox("📌 Status", STATUSES)
                prio = st.selectbox("⚠️ Priority", PRIORITIES)
        with inner_tab2:
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
            st.balloons()
            st.success("🎉 Task added successfully!")

# --- Analytics Tab ---
with tab2:
    if st.session_state.timesheet:
        df = pd.DataFrame(st.session_state.timesheet)
        df = df[df['Employee'] == st.session_state.user_role]
        df = df[(df['Date'] >= start_date.strftime('%Y-%m-%d')) & (df['Date'] <= end_date.strftime('%Y-%m-%d'))]
        if category != "All": df = df[df['Category'] == category]
        if status != "All": df = df[df['Status'] == status]

        st.subheader("📊 Task Summary")
        completed = df[df['Status'] == '✅ Completed'].shape[0]
        progress = int((completed / len(df)) * 100) if len(df) > 0 else 0
        st.progress(progress)

        st.plotly_chart(px.timeline(df, x_start='Date', x_end='Date', y='Category', color='Status', title="🕓 Task Timeline"), use_container_width=True)

        st.markdown("### 🗂 Task Cards")
        for _, row in df.iterrows():
            st.markdown(f"""
            <div class='task-card'>
            <b>{row['Date']} - {row['Category']}</b><br>
            {row['Description']}<br>
            <small>{row['Status']} | {row['Priority']}</small>
            </div>
            """, unsafe_allow_html=True)

# --- Profile Tab ---
with tab3:
    df = pd.DataFrame(st.session_state.timesheet)
    user_df = df[df['Employee'] == st.session_state.user_role]
    st.subheader("👤 User Summary")
    st.metric("Total Tasks", len(user_df))
    st.metric("Completed", user_df[user_df['Status'] == '✅ Completed'].shape[0])
    st.metric("Avg Daily", round(len(user_df) / max(1, (datetime.today() - pd.to_datetime(user_df['Date']).min()).days), 2) if not user_df.empty else 0)

# --- Smart Alerts ---
if st.session_state.timesheet:
    df = pd.DataFrame(st.session_state.timesheet)
    overdue = df[(df['Employee'] == st.session_state.user_role) &
                 (df['Status'] == '⏳ Not Started') &
                 (pd.to_datetime(df['Date']) < datetime.today() - timedelta(days=3))]
    high_priority = df[(df['Employee'] == st.session_state.user_role) &
                       (df['Priority'] == '🔴 High') &
                       (df['Status'] != '✅ Completed')]

    if not overdue.empty:
        st.warning(f"⚠️ You have {len(overdue)} task(s) overdue for more than 3 days!")
    if not high_priority.empty:
        st.error(f"🚨 You have {len(high_priority)} high priority task(s) not completed yet!")

# --- Footer ---
st.markdown(f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</footer>", unsafe_allow_html=True)
