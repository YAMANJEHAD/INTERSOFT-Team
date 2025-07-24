from datetime import datetime
import pandas as pd
import pytz
import os

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

    # حساب مدة الدوام
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

    # Export
    st.markdown("### 📤 Export My Records")
    user_df = df[df["Name"].str.lower() == st.session_state.username.lower()]
    st.download_button(
        label="📥 Download CSV",
        data=user_df.to_csv(index=False).encode('utf-8-sig'),
        file_name=f"{st.session_state.username}_attendance_{today_str}.csv",
        mime='text/csv'
    )
