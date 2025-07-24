import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import os
import time

# ========== CONFIG ==========
st.set_page_config(page_title="Smart Attendance", layout="centered")
tz = pytz.timezone("Asia/Amman")
LOG_FILE = "attendance_log.csv"

# ========== STYLING ==========
st.markdown("""
<style>
html, body {
    font-family: 'Segoe UI', sans-serif;
    background-color: #f8fafc;
}
h1, h2 {
    color: #1e40af;
    text-align: center;
}
.stTextInput > div > div > input {
    font-size: 18px;
    padding: 10px;
}
.stButton > button {
    background-color: #3b82f6;
    color: white;
    font-size: 16px;
    padding: 0.6rem 1.2rem;
    border: none;
    border-radius: 8px;
}
.stButton > button:hover {
    background-color: #2563eb;
}
.record {
    background-color: #eff6ff;
    padding: 12px;
    border-radius: 10px;
    margin-top: 1rem;
}
.live-time {
    font-size: 20px;
    font-weight: bold;
    color: #16a34a;
    text-align: center;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ========== TIME DISPLAY ==========
def get_live_time():
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), now

today_str, current_time_str, now = get_live_time()
st.markdown(f"<div class='live-time'>📅 {today_str} | ⏰ {current_time_str}</div>", unsafe_allow_html=True)

# ========== INPUT ==========
employee_name = st.text_input("👤 Employee Name", max_chars=50)
break_time = st.time_input("☕ Set Break Time (Optional)")

# ========== LOAD DATA ==========
def load_log():
    if os.path.exists(LOG_FILE):
        return pd.read_csv(LOG_FILE)
    else:
        return pd.DataFrame(columns=["Name", "Action", "Date", "Time"])

# ========== SAVE LOG ==========
def save_log(name, action, time_override=None):
    log = load_log()
    record_time = time_override if time_override else now.strftime("%H:%M:%S")
    record = {
        "Name": name,
        "Action": action,
        "Date": today_str,
        "Time": record_time
    }
    log = pd.concat([log, pd.DataFrame([record])], ignore_index=True)
    log.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")
    st.success(f"✅ {action} recorded at {record_time}")
    st.markdown(f"<div class='record'>✅ <strong>{action}</strong> for <strong>{name}</strong> at <strong>{record_time}</strong></div>", unsafe_allow_html=True)

# ========== VALIDATION ==========
def already_logged(name, action):
    df = load_log()
    return not df[
        (df["Name"].str.lower() == name.lower()) &
        (df["Date"] == today_str) &
        (df["Action"] == action)
    ].empty

# ========== BUTTONS ==========
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Check In"):
        if employee_name.strip():
            if already_logged(employee_name.strip(), "Check In"):
                st.warning("⚠️ Already checked in today.")
            else:
                save_log(employee_name.strip(), "Check In")
        else:
            st.warning("Please enter your name.")

with col2:
    if st.button("☕ Break"):
        if employee_name.strip():
            if already_logged(employee_name.strip(), "Break"):
                st.warning("⚠️ Break already recorded today.")
            else:
                save_log(employee_name.strip(), "Break", break_time.strftime("%H:%M:%S"))
        else:
            st.warning("Please enter your name.")

with col3:
    if st.button("📤 Check Out"):
        if employee_name.strip():
            save_log(employee_name.strip(), "Check Out")
        else:
            st.warning("Please enter your name.")

# ========== CALCULATE DURATION ==========
def calculate_duration(name):
    df = load_log()
    records = df[(df["Name"].str.lower() == name.lower()) & (df["Date"] == today_str)]
    if "Check In" in records["Action"].values and "Check Out" in records["Action"].values:
        in_time = records[records["Action"] == "Check In"]["Time"].values[0]
        out_time = records[records["Action"] == "Check Out"]["Time"].values[0]
        fmt = "%H:%M:%S"
        duration = datetime.strptime(out_time, fmt) - datetime.strptime(in_time, fmt)
        return str(duration)
    return None

# ========== EXPORT ==========
st.markdown("### 📦 Export Records")
if os.path.exists(LOG_FILE):
    df = load_log()
    st.download_button(
        label="📥 Download CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"attendance_{today_str}.csv",
        mime="text/csv"
    )

    st.markdown("### 🗂️ Last 10 Records")
    st.dataframe(df.tail(10), use_container_width=True)

    if employee_name.strip():
        work_duration = calculate_duration(employee_name.strip())
        if work_duration:
            st.info(f"⏳ Total Work Duration Today: **{work_duration}**")

