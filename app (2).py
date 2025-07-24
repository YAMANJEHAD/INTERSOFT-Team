import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import os

# --- Settings ---
st.set_page_config(page_title="Smart Attendance", layout="centered")
tz = pytz.timezone("Asia/Amman")
LOG_FILE = "attendance_log.csv"

# --- Styles ---
st.markdown("""
<style>
body {
    background-color: #f8fafc;
    font-family: 'Segoe UI', sans-serif;
}
h1, h2 {
    color: #1e3a8a;
    text-align: center;
}
input, .stButton>button {
    font-size: 16px !important;
}
.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    padding: 0.5rem 1.2rem;
}
.stButton>button:hover {
    background-color: #1d4ed8;
}
.live-clock {
    font-size: 22px;
    color: #16a34a;
    text-align: center;
    margin-top: -10px;
}
.success-msg {
    background-color: #e0f2fe;
    padding: 10px;
    border-radius: 10px;
    margin-top: 10px;
    color: #0c4a6e;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# --- Current Time ---
now = datetime.now(tz)
today_str = now.strftime("%Y-%m-%d")
current_time_str = now.strftime("%H:%M:%S")
st.title("🕘 Smart Attendance System")
st.markdown(f"<div class='live-clock'>📅 {today_str} | ⏰ {current_time_str}</div>", unsafe_allow_html=True)

# --- Input Name & Break Time ---
employee = st.text_input("👤 Enter your name")
break_time = st.time_input("☕ Choose break time", value=datetime.strptime("13:00", "%H:%M").time())

# --- Load & Save ---
def load_data():
    if os.path.exists(LOG_FILE):
        return pd.read_csv(LOG_FILE)
    return pd.DataFrame(columns=["Name", "Action", "Date", "Time"])

def save_action(name, action, custom_time=None):
    df = load_data()
    time_str = custom_time.strftime("%H:%M:%S") if custom_time else now.strftime("%H:%M:%S")
    new_row = pd.DataFrame([{
        "Name": name,
        "Action": action,
        "Date": today_str,
        "Time": time_str
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")
    st.markdown(f"<div class='success-msg'>✅ {action} saved at {time_str}</div>", unsafe_allow_html=True)

def already_done(name, action):
    df = load_data()
    return not df[(df["Name"].str.lower() == name.lower()) & (df["Date"] == today_str) & (df["Action"] == action)].empty

# --- Actions ---
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Check In"):
        if employee.strip() == "":
            st.warning("Please enter your name.")
        elif already_done(employee, "Check In"):
            st.warning("⚠️ Already checked in today.")
        else:
            save_action(employee, "Check In")

with col2:
    if st.button("☕ Take Break"):
        if employee.strip() == "":
            st.warning("Please enter your name.")
        elif already_done(employee, "Break"):
            st.warning("⚠️ Break already taken today.")
        else:
            save_action(employee, "Break", break_time)

with col3:
    if st.button("📤 Check Out"):
        if employee.strip() == "":
            st.warning("Please enter your name.")
        else:
            save_action(employee, "Check Out")

# --- Duration Calculation ---
def calculate_duration(name):
    df = load_data()
    records = df[(df["Name"].str.lower() == name.lower()) & (df["Date"] == today_str)]
    if "Check In" in records["Action"].values and "Check Out" in records["Action"].values:
        in_time = records[records["Action"] == "Check In"]["Time"].values[0]
        out_time = records[records["Action"] == "Check Out"]["Time"].values[0]
        fmt = "%H:%M:%S"
        duration = datetime.strptime(out_time, fmt) - datetime.strptime(in_time, fmt)
        return str(duration)
    return None

# --- Export + Show Data ---
if os.path.exists(LOG_FILE):
    st.markdown("### 📦 Export Attendance")
    df = pd.read_csv(LOG_FILE)
    st.download_button(
        label="📥 Download CSV",
        data=df.to_csv(index=False).encode('utf-8-sig'),
        file_name=f"attendance_{today_str}.csv",
        mime='text/csv'
    )

    st.markdown("### 📊 Last 10 Records")
    st.dataframe(df.tail(10), use_container_width=True)

    if employee.strip():
        duration = calculate_duration(employee)
        if duration:
            st.info(f"⏳ Total work duration today: **{duration}**")
