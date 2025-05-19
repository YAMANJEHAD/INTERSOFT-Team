import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# ملفات النظام
USER_FILE = "users.csv"
LOG_FILE = "activity_log.csv"
ATTEND_FILE = "attendance.csv"

# تحميل أو إنشاء الملفات
def load_or_create_csv(file_path, columns):
    if not os.path.exists(file_path):
        pd.DataFrame(columns=columns).to_csv(file_path, index=False)
    return pd.read_csv(file_path)

df_users = load_or_create_csv(USER_FILE, ["username", "password", "role"])
df_log = load_or_create_csv(LOG_FILE, ["username", "action", "timestamp"])
df_attend = load_or_create_csv(ATTEND_FILE, ["username", "start_time"])

# تسجيل نشاط
def log_action(user, action):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{user},{action},{timestamp}\n")

# واجهة تسجيل الدخول
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = df_users[(df_users["username"] == username) & (df_users["password"] == password)]
        if not user.empty:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user.iloc[0]["role"]
            log_action(username, "Login")
            st.rerun()
        else:
            st.error("❌ Invalid credentials.")
    st.stop()

# تسجيل خروج
with st.sidebar:
    st.markdown(f"*Logged in as: {st.session_state.username} ({st.session_state.role})*")
    if st.button("Logout"):
        log_action(st.session_state.username, "Logout")
        st.session_state.logged_in = False
        st.rerun()

    st.subheader("⚙️ Settings")
    if st.button("Start Work"):
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df_attend = pd.concat([df_attend, pd.DataFrame([[st.session_state.username, start_time]], columns=["username", "start_time"])], ignore_index=True)
        df_attend.to_csv(ATTEND_FILE, index=False)
        log_action(st.session_state.username, "Started work")

    with st.expander("🔑 Change Password"):
        old_pass = st.text_input("Old Password", type="password", key="old_pass")
        new_pass = st.text_input("New Password", type="password", key="new_pass")
        if st.button("Change Password", key="change_pass_btn"):
            idx = df_users[(df_users["username"] == st.session_state.username) & (df_users["password"] == old_pass)].index
            if not idx.empty:
                df_users.loc[idx[0], "password"] = new_pass
                df_users.to_csv(USER_FILE, index=False)
                st.success("✅ Password updated.")
                log_action(st.session_state.username, "Changed password")
            else:
                st.error("❌ Wrong old password.")

    if st.session_state.role == "manager":
        with st.expander("📜 Activity Log"):
            df_log = pd.read_csv(LOG_FILE)
            st.dataframe(df_log.sort_values("timestamp", ascending=False))

        with st.expander("🕒 Attendance Log"):
            df_attend = pd.read_csv(ATTEND_FILE)
            st.dataframe(df_attend.sort_values("start_time", ascending=False))

        with st.expander("👥 All Accounts"):
            st.dataframe(df_users)

# الصفحة الرئيسية
st.title("📊 INTERSOFT Dashboard")

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])
required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

def classify_note(note):
    note = str(note).strip().upper()
    if "TERMINAL ID" in note:
        return "TERMINAL ID"
    elif "WRONG DATE" in note:
        return "WRONG DATE"
    elif "DONE" in note:
        return "DONE"
    elif "NO SIGNATURE" in note:
        return "NO SIGNATURE"
    elif "NO J.O" in note:
        return "NO J.O"
    elif "NO BILL" in note:
        return "NO BILL"
    elif "MISSING" in note:
        return "MISSING INFO"
    else:
        return "OTHER"

if uploaded_file:
    log_action(st.session_state.username, "Uploaded Excel File")
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
    except:
        df = pd.read_excel(uploaded_file)

    if not all(col in df.columns for col in required_cols):
        st.error("❌ Missing columns in Excel file.")
    else:
        df["Note_Type"] = df["NOTE"].apply(classify_note)
        st.success("✅ File processed successfully.")

        if st.session_state.role == "employee":
            st.subheader("📄 Your Notes")
            filtered_df = df[df["Technician_Name"].str.lower() == st.session_state.username.lower()]
            st.dataframe(filtered_df)

        elif st.session_state.role == "manager":
            st.subheader("📊 Notes Summary")
            note_counts = df['Note_Type'].value_counts()
            st.bar_chart(note_counts)

            st.subheader("👨‍🔧 Notes by Technician")
            tech_counts = df.groupby("Technician_Name")["Note_Type"].count()
            st.bar_chart(tech_counts)

        # Export options
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Notes")
        st.download_button("📥 Download Processed Excel", buffer.getvalue(), "processed_notes.xlsx")
        log_action(st.session_state.username, "Downloaded processed Excel")

        # PDF
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 800, "Summary Report")
        c.setFont("Helvetica", 12)
        c.drawString(100, 780, f"Uploaded by: {st.session_state.username}")
        c.drawString(100, 760, f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(100, 740, f"Total Notes: {len(df)}")
        c.showPage()
        c.save()
        st.download_button("📥 Download PDF Report", pdf_buffer.getvalue(), "report.pdf")
        log_action(st.session_state.username, "Downloaded PDF Report")
