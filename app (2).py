import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os

# --- إعداد الصفحة ---
st.set_page_config(page_title="🕘 Attendance Tracker", layout="centered")

# --- التنسيق (CSS) مع تأثير البلالين ---
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
.balloons {
    animation: pop 1.2s ease-in-out forwards;
}
@keyframes pop {
    0% { transform: scale(0.2); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# --- الوقت المحلي ---
tz = pytz.timezone("Asia/Amman")  # عدّل حسب منطقتك
now = datetime.now(tz)
today_str = now.strftime("%Y-%m-%d")
current_time = now.strftime("%H:%M:%S")

# --- عنوان الصفحة ---
st.title("🕘 Daily Attendance Tracker")
st.subheader(f"📅 Today: {today_str} | ⏰ Time: {current_time}")

# --- إدخال الاسم ---
employee_name = st.text_input("👤 Employee Name", max_chars=50)

# --- اسم ملف السجل ---
LOG_FILE = "attendance_log.csv"

# --- تحميل السجل أو إنشاؤه ---
def load_log():
    if os.path.exists(LOG_FILE):
        return pd.read_csv(LOG_FILE)
    else:
        return pd.DataFrame(columns=["Name", "Action", "Date", "Time"])

# --- حفظ سجل جديد ---
def save_log(name, action):
    log = load_log()
    new_record = {
        "Name": name,
        "Action": action,
        "Date": today_str,
        "Time": current_time
    }
    log = pd.concat([log, pd.DataFrame([new_record])], ignore_index=True)
    log.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")

    st.success(f"{action} recorded at {current_time}")
    st.markdown(f"""<div class='record balloons'>
        ✅ <strong>{action}</strong> for <strong>{name}</strong> on <strong>{today_str}</strong> at <strong>{current_time}</strong>
    </div>""", unsafe_allow_html=True)

# --- تحقق من Check In مكرر ---
def already_checked_in(name):
    log = load_log()
    return not log[
        (log["Name"].str.lower() == name.lower()) &
        (log["Date"] == today_str) &
        (log["Action"] == "Check In")
    ].empty

# --- أزرار تسجيل ---
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Check In"):
        if employee_name.strip():
            if already_checked_in(employee_name.strip()):
                st.warning("⚠️ You already checked in today.")
            else:
                save_log(employee_name.strip(), "Check In")
        else:
            st.warning("Please enter your name.")

with col2:
    if st.button("☕ Break"):
        if employee_name.strip():
            save_log(employee_name.strip(), "Break")
        else:
            st.warning("Please enter your name.")

with col3:
    if st.button("📤 Check Out"):
        if employee_name.strip():
            save_log(employee_name.strip(), "Check Out")
        else:
            st.warning("Please enter your name.")

# --- تصدير إلى إكسل ---
st.markdown("### 📦 Export Attendance")
if os.path.exists(LOG_FILE):
    df = pd.read_csv(LOG_FILE)
    excel_file = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Download CSV",
        data=excel_file,
        file_name=f"attendance_{today_str}.csv",
        mime='text/csv'
    )

    # --- عرض السجلات الأخيرة ---
    st.markdown("### 🗂️ Recent Records")
    st.dataframe(df.tail(10), use_container_width=True)
