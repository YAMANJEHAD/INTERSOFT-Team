import streamlit as st
import pandas as pd
import io
from datetime import datetime
import plotly.express as px
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

# الملفات المطلوبة
USER_FILE = "users.csv"
LOG_FILE = "activity_log.csv"

# تحميل المستخدمين
if not os.path.exists(USER_FILE):
    df_users = pd.DataFrame(columns=["username", "password", "role"])
    df_users.to_csv(USER_FILE, index=False)
else:
    df_users = pd.read_csv(USER_FILE)

# تحميل سجل النشاط
if not os.path.exists(LOG_FILE):
    df_log = pd.DataFrame(columns=["username", "action", "timestamp"])
    df_log.to_csv(LOG_FILE, index=False)
else:
    df_log = pd.read_csv(LOG_FILE)

# تسجيل النشاط
def log_action(username, action):
    new_log = pd.DataFrame([[username, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]], columns=["username", "action", "timestamp"])
    new_log.to_csv(LOG_FILE, mode='a', index=False, header=False)

# تسجيل الدخول
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        match = df_users[(df_users["username"] == username) & (df_users["password"] == password)]
        if not match.empty:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = match.iloc[0]["role"]
            log_action(username, "Login")
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Wrong credentials")
    st.stop()

# تسجيل الخروج
if st.button("Logout"):
    log_action(st.session_state.username, "Logout")
    st.session_state.logged_in = False
    st.rerun()

# الواجهة الرئيسية
st.markdown(f"<h1 style='text-align:center'>📊 INTERSOFT Analyzer ({st.session_state.role.upper()})</h1>", unsafe_allow_html=True)

# إدارة الحساب (للمدير)
if st.session_state.role == "manager":
    st.subheader("👥 User Management")
    with st.expander("➕ Add New User"):
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        new_role = st.selectbox("Role", ["employee", "manager"])
        if st.button("Create User"):
            if new_user in df_users["username"].values:
                st.warning("⚠️ Username already exists.")
            else:
                df_users.loc[len(df_users)] = [new_user, new_pass, new_role]
                df_users.to_csv(USER_FILE, index=False)
                st.success("✅ User created.")
                log_action(st.session_state.username, f"Created user: {new_user}")

# تغيير كلمة المرور
with st.expander("🔑 Change Password"):
    old_pass = st.text_input("Old Password", type="password")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Change Password"):
        idx = df_users[df_users["username"] == st.session_state.username].index
        if not idx.empty and df_users.loc[idx[0], "password"] == old_pass:
            df_users.loc[idx[0], "password"] = new_pass
            df_users.to_csv(USER_FILE, index=False)
            st.success("✅ Password changed.")
            log_action(st.session_state.username, "Changed password")
        else:
            st.error("❌ Wrong old password.")

# سجل النشاط (فقط للمدير)
if st.session_state.role == "manager":
    st.subheader("📜 Activity Log")
    log_df = pd.read_csv(LOG_FILE)
    st.dataframe(log_df.sort_values("timestamp", ascending=False), use_container_width=True)

# تحليل البيانات
uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])
required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

def classify_note(note):
    note = str(note).strip().upper()
    if "TERMINAL ID - WRONG DATE" in note:
        return "TERMINAL ID - WRONG DATE"
    elif "NO IMAGE FOR THE DEVICE" in note:
        return "NO IMAGE FOR THE DEVICE"
    elif "IMAGE FOR THE DEVICE ONLY" in note:
        return "IMAGE FOR THE DEVICE ONLY"
    elif "WRONG DATE" in note:
        return "WRONG DATE"
    elif "TERMINAL ID" in note:
        return "TERMINAL ID"
    elif "NO J.O" in note:
        return "NO J.O"
    elif "DONE" in note:
        return "DONE"
    elif "NO RETAILERS SIGNATURE" in note or ("RETAILER" in note and "SIGNATURE" in note):
        return "NO RETAILERS SIGNATURE"
    elif "UNCLEAR IMAGE" in note:
        return "UNCLEAR IMAGE"
    elif "NO ENGINEER SIGNATURE" in note:
        return "NO ENGINEER SIGNATURE"
    elif "NO SIGNATURE" in note:
        return "NO SIGNATURE"
    elif "PENDING" in note:
        return "PENDING"
    elif "NO INFORMATIONS" in note:
        return "NO INFORMATIONS"
    elif "MISSING INFORMATION" in note:
        return "MISSING INFORMATION"
    elif "NO BILL" in note:
        return "NO BILL"
    elif "NOT ACTIVE" in note:
        return "NOT ACTIVE"
    elif "NO RECEIPT" in note:
        return "NO RECEIPT"
    elif "ANOTHER TERMINAL RECEIPT" in note:
        return "ANOTHER TERMINAL RECEIPT"
    elif "UNCLEAR RECEIPT" in note:
        return "UNCLEAR RECEIPT"
    else:
        return "MISSING INFORMATION"

if uploaded_file:
    log_action(st.session_state.username, "Uploaded file")
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
    except:
        df = pd.read_excel(uploaded_file)

    if not all(col in df.columns for col in required_cols):
        st.error("❌ Missing columns.")
    else:
        df['Note_Type'] = df['NOTE'].apply(classify_note)
        st.success("✅ File processed.")

        st.subheader("📊 Notes by Type")
        note_counts = df['Note_Type'].value_counts()
        st.bar_chart(note_counts)

        st.subheader("👨‍🔧 Notes per Technician")
        tech_counts = df.groupby('Technician_Name')['Note_Type'].count()
        st.bar_chart(tech_counts)

        # تحميل Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="All Notes")
        st.download_button("📥 Download Excel", output.getvalue(), "summary.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        log_action(st.session_state.username, "Downloaded Excel")

        # تحميل PDF
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, height - 50, "Summary Report")
        c.setFont("Helvetica", 12)
        c.drawString(100, height - 100, f"Uploaded by: {st.session_state.username}")
        c.drawString(100, height - 130, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.showPage()
        c.save()
        st.download_button("📥 Download PDF", pdf_buffer.getvalue(), "summary_report.pdf", "application/pdf")
        log_action(st.session_state.username, "Downloaded PDF")
