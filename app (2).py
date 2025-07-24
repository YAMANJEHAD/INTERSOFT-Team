import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ========== Page Config ==========
st.set_page_config(page_title="Attendance Tracker", layout="centered")

# ========== Styling ==========
st.markdown("""
<style>
body, html {
    font-family: 'Segoe UI', sans-serif;
}
.stTextInput > div > div > input {
    font-size: 18px;
    padding: 10px;
}
.stButton button {
    background-color: #2563eb;
    color: white;
    font-size: 18px;
    padding: 0.5rem 1.5rem;
    border-radius: 8px;
    border: none;
}
.stButton button:hover {
    background-color: #1d4ed8;
}
h1, h2 {
    color: #1e3a8a;
    text-align: center;
}
.record {
    background-color: #f1f5f9;
    padding: 10px;
    border-radius: 10px;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ========== Page Title ==========
st.title("🕘 Work Attendance")
st.subheader("Enter your name to check in or out")

# ========== Input ==========
employee_name = st.text_input("👤 Employee Name", max_chars=50)

# ========== CSV File ==========
log_file = "attendance_log.csv"

# ========== Load or Create Log ==========
def load_log():
    if os.path.exists(log_file):
        return pd.read_csv(log_file)
    else:
        return pd.DataFrame(columns=["Name", "Action", "Date", "Time"])

def save_log(name, action):
    now = datetime.now()
    record = {
        "Name": name,
        "Action": action,
        "Date": now.strftime("%Y-%m-%d"),
        "Time": now.strftime("%H:%M:%S")
    }

    df = load_log()
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(log_file, index=False, encoding='utf-8-sig')

    st.success(f"{action} recorded at {record['Time']}")
    st.markdown(f"""<div class='record'>
    ✅ <strong>{action}</strong> for <strong>{name}</strong> on <strong>{record['Date']}</strong> at <strong>{record['Time']}</strong>
    </div>""", unsafe_allow_html=True)

# ========== Check if already checked in ==========
def already_checked_in(name):
    df = load_log()
    today = datetime.now().strftime("%Y-%m-%d")
    return (
        not df[
            (df["Name"].str.lower() == name.lower()) &
            (df["Date"] == today) &
            (df["Action"] == "Check In")
        ].empty
    )

# ========== Buttons ==========
col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Check In"):
        if employee_name.strip():
            if already_checked_in(employee_name.strip()):
                st.warning("⚠️ You already checked in today!")
            else:
                save_log(employee_name.strip(), "Check In")
        else:
            st.warning("Please enter your name.")

with col2:
    if st.button("📤 Check Out"):
        if employee_name.strip():
            save_log(employee_name.strip(), "Check Out")
        else:
            st.warning("Please enter your name.")

# ========== Show Last Records ==========
df = load_log()
if not df.empty:
    st.markdown("### 🗂️ Latest Records")
    st.dataframe(df.tail(10), use_container_width=True)
