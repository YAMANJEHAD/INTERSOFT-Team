import streamlit as st
import pandas as pd
import json
from datetime import datetime
import pytz
import os

# --- Constants ---
USERS = {
    "yaman": {"pass": "YAMAN1", "role": "Employee"},
    "hatem": {"pass": "HATEM2", "role": "Employee"},
    "qusai": {"pass": "QUSAI4", "role": "Employee"},
    "mahmoud": {"pass": "mahmoud4", "role": "Employee"},
    "mohammad aleem": {"pass": "moh00", "role": "Admin"},
}
DATA_FILE = "shift_data.json"
SHIFT_COLUMNS = ["Employee", "Date", "Start Time", "End Time", "Submitted"]

# --- Page Config ---
st.set_page_config(
    page_title="⚡ INTERSOFT Shift Tracker",
    layout="wide",
    page_icon="⏰"
)

# --- Basic CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
* { font-family: 'Inter', sans-serif; }
body { background: #0a1122; color: #e2e8f0; }
.main-container { max-width: 800px; margin: 0 auto; padding: 2rem; }
.card { background: #1c2526; padding: 2rem; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
.card-title { font-size: 1.5rem; font-weight: 600; color: #4ade80; margin-bottom: 1.5rem; }
.stButton>button { 
    background: #2d3748; 
    color: #e2e8f0; 
    border-radius: 10px; 
    padding: 0.8rem 1.5rem; 
    border: none; 
}
.stButton>button:hover { background: #4ade80; color: #1c2526; }
.stSelectbox, .stDateInput, .stTimeInput { 
    background: #2d3748; 
    color: #e2e8f0; 
    border-radius: 10px; 
    padding: 0.6rem; 
    border: 1px solid #4b5563; 
}
</style>
""", unsafe_allow_html=True)

# --- Persistent Storage ---
def save_data():
    try:
        data = {"shifts": st.session_state.shifts}
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"⚠️ Failed to save data: {e}")

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                st.session_state.shifts = data.get("shifts", [])
        else:
            st.session_state.shifts = []
    except json.JSONDecodeError:
        st.error("⚠️ Corrupted data file. Starting fresh.")
        st.session_state.shifts = []

# --- Session Initialization ---
def initialize_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.shifts = []

# --- Authentication ---
def authenticate_user():
    if not st.session_state.logged_in:
        st.markdown("<div class='card'><h2 class='card-title'>🔐 Login</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])
        with col1:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Login", use_container_width=True):
                user = USERS.get(username.lower())
                if user and user["pass"] == password:
                    st.session_state.logged_in = True
                    st.session_state.user_role = username.lower()
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

# --- Record Shift ---
def record_shift():
    st.markdown("<div class='card'><h2 class='card-title'>⏰ Record Shift</h2>", unsafe_allow_html=True)
    tz = pytz.timezone("Asia/Riyadh")
    today = datetime.now(tz).date()
    
    with st.form("shift_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", today, min_value=today, max_value=today)
            start_time = st.time_input("Start Time", datetime.now(tz).time())
        with col2:
            employee = st.selectbox("Employee", [u.capitalize() for u in USERS.keys()])
            end_time = st.time_input("End Time", datetime.now(tz).time())
        
        if st.form_submit_button("✅ Submit"):
            shift = {
                "Employee": employee.lower(),
                "Date": date.strftime('%Y-%m-%d'),
                "Start Time": start_time.strftime('%H:%M:%S'),
                "End Time": end_time.strftime('%H:%M:%S'),
                "Submitted": datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
            }
            st.session_state.shifts.append(shift)
            save_data()
            st.success("🎉 Shift recorded!")
            st.rerun()
    
    # Display shifts
    df_shifts = pd.DataFrame(st.session_state.shifts, columns=SHIFT_COLUMNS)
    if not df_shifts.empty:
        st.markdown("<h3>📋 Today's Shifts</h3>", unsafe_allow_html=True)
        today_shifts = df_shifts[df_shifts['Date'] == today.strftime('%Y-%m-%d')]
        if not today_shifts.empty:
            st.dataframe(today_shifts.drop(columns=['Submitted'], errors='ignore'), use_container_width=True)
        else:
            st.info("ℹ️ No shifts recorded for today.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Main App ---
if __name__ == "__main__":
    initialize_session()
    load_data()
    authenticate_user()
    
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.sidebar.title("🔒 Session")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        save_data()
        st.rerun()
    
    record_shift()
    st.markdown(f"<footer>© INTERSOFT {datetime.now(pytz.timezone('Asia/Riyadh')).strftime('%Y')}</footer>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
