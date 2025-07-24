import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import pytz
import os

# --- User Data (can be connected to a database later) ---
USERS = {
    "admin": {"password": "admin123", "role": "Admin"},
    "yaman": {"password": "yaman1", "role": "Employee"},
    "hatem": {"password": "hatem1", "role": "Employee"},
    "qusai": {"password": "qusai1", "role": "Employee"},
}

# --- Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- Login Interface ---
def login_ui():
    st.title("🔐 Login to Attendance System")
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")

    if st.button("🚪 Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = USERS[username]["role"]
            st.success(f"✅ Logged in as {st.session_state.role}")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials. Try again.")

# --- Logout Button ---
def logout_button():
    if st.sidebar.button("🚪 Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.experimental_rerun()

# --- Employee Interface ---
def employee_interface():
    tz = pytz.timezone("Asia/Amman")
    now = datetime.now(tz)
    today_str = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    log_file = "attendance_log.csv"

    st.title("🕘 Employee Attendance Panel")
    st.markdown(f"<div class='live-clock'>📅 {today_str} | ⏰ {current_time}</div>", unsafe_allow_html=True)

    # Break time input
    break_time = st.time_input("☕ Choose your break time", value=datetime.strptime("13:00", "%H:%M").time())

    def load_log():
        if os.path.exists(log_file):
            return pd.read_csv(log_file)
        else:
            return pd.DataFrame(columns=["Name", "Action", "Date", "Time"])

    def save_log(action, custom_time=None):
        log = load_log()
        time_str = custom_time.strftime("%H:%M:%S") if custom_time else now.strftime("%H:%M:%S")
        record = {
            "Name": st.session_state.username,
            "Action": action,
            "Date": today_str,
            "Time": time_str
        }
        log = pd.concat([log, pd.DataFrame([record])], ignore_index=True)
        log.to_csv(log_file, index=False, encoding='utf-8-sig')
        st.success(f"✅ {action} recorded at {time_str}")
        st.markdown(f"<div class='success-msg'>✅ <strong>{action}</strong> for <strong>{st.session_state.username}</strong> at <strong>{time_str}</strong></div>", unsafe_allow_html=True)

    def already_logged(action):
        df = load_log()
        return not df[
            (df["Name"].str.lower() == st.session_state.username.lower()) &
            (df["Date"] == today_str) &
            (df["Action"] == action)
        ].empty

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📥 Check In"):
            if already_logged("Check In"):
                st.warning("⚠️ You already checked in today.")
            else:
                save_log("Check In")

    with col2:
        if st.button("☕ Break"):
            if already_logged("Break"):
                st.warning("⚠️ Break already taken today.")
            else:
                save_log("Break", break_time)

    with col3:
        if st.button("📤 Check Out"):
            save_log("Check Out")

    # Calculate Work Duration
    def calc_duration():
        df = load_log()
        user_df = df[(df["Name"].str.lower() == st.session_state.username.lower()) & (df["Date"] == today_str)]
        if "Check In" in user_df["Action"].values and "Check Out" in user_df["Action"].values:
            in_time = user_df[user_df["Action"] == "Check In"]["Time"].values[0]
            out_time = user_df[user_df["Action"] == "Check Out"]["Time"].values[0]
            fmt = "%H:%M:%S"
            duration = datetime.strptime(out_time, fmt) - datetime.strptime(in_time, fmt)
            return str(duration)
        return None

    df = load_log()
    st.markdown("### 🗂️ Last 10 Records")
    st.dataframe(df[df["Name"].str.lower() == st.session_state.username.lower()].tail(10), use_container_width=True)

    duration = calc_duration()
    if duration:
        st.info(f"⏳ Total Work Duration Today: **{duration}**")

    # Export User Records
    st.markdown("### 📤 Export My Records")
    user_df = df[df["Name"].str.lower() == st.session_state.username.lower()]
    st.download_button(
        label="📥 Download CSV",
        data=user_df.to_csv(index=False).encode('utf-8-sig'),
        file_name=f"{st.session_state.username}_attendance_{today_str}.csv",
        mime='text/csv'
    )

# --- Admin Interface ---
def admin_interface():
    st.title("📊 Admin Dashboard - Attendance Analytics")
    log_file = "attendance_log.csv"

    if not os.path.exists(log_file):
        st.warning("🚫 No attendance data found.")
        return

    df = pd.read_csv(log_file)

    # Filters
    with st.expander("🔍 Filter Options", expanded=True):
        col1, col2 = st.columns(2)
        employee_list = ["All"] + sorted(df["Name"].unique().tolist())
        selected_employee = col1.selectbox("👤 Select Employee", employee_list)
        selected_date = col2.date_input("📅 Select Date (optional)", value=None)

    # Apply filters
    filtered_df = df.copy()
    if selected_employee != "All":
        filtered_df = filtered_df[filtered_df["Name"] == selected_employee]
    if selected_date:
        filtered_df = filtered_df[filtered_df["Date"] == selected_date.strftime("%Y-%m-%d")]

    # Display Filtered Data
    st.markdown("### 🗂️ Filtered Attendance Records")
    st.dataframe(filtered_df, use_container_width=True)

    # Missing Check Out
    st.markdown("### 🕵️ Employees Missing Check Out")
    missing_checkout = []
    for name in df["Name"].unique():
        emp_df = df[(df["Name"] == name) & (df["Date"] == datetime.now().strftime("%Y-%m-%d"))]
        if "Check In" in emp_df["Action"].values and "Check Out" not in emp_df["Action"].values:
            missing_checkout.append(name)
    if missing_checkout:
        st.error("🚨 The following employees didn't Check Out today:")
        st.write(missing_checkout)
    else:
        st.success("✅ All employees checked out today.")

    # Attendance by Date Chart
    st.markdown("### 📈 Attendance Count by Date")
    attendance_count = df[df["Action"] == "Check In"].groupby("Date").count().reset_index()[["Date", "Action"]]
    attendance_count.columns = ["Date", "Check In Count"]
    fig = px.bar(attendance_count, x="Date", y="Check In Count", color="Check In Count", title="Daily Attendance")
    st.plotly_chart(fig, use_container_width=True)

    # Export Full Attendance
    st.markdown("### 📤 Export Full Attendance")
    st.download_button(
        label="📥 Download All Data (CSV)",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="full_attendance_log.csv",
        mime="text/csv"
    )

    # Quick Stats
    st.markdown("### 📊 Quick Stats")
    today = datetime.now().strftime("%Y-%m-%d")
    today_df = df[df["Date"] == today]
    employees_today = today_df["Name"].nunique()
    checkin_count = today_df[today_df["Action"] == "Check In"].shape[0]
    checkout_count = today_df[today_df["Action"] == "Check Out"].shape[0]
    st.info(f"""
    👥 Employees today: **{employees_today}**  
    ✅ Check Ins: **{checkin_count}**  
    📤 Check Outs: **{checkout_count}**
    """)

# --- Main Logic ---
if not st.session_state.logged_in:
    login_ui()
else:
    st.sidebar.markdown(f"👤 **User:** {st.session_state.username}")
    st.sidebar.markdown(f"🔐 **Role:** {st.session_state.role}")
    logout_button()

    if st.session_state.role == "Admin":
        admin_interface()
    else:
        employee_interface()
