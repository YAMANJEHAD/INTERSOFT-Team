import streamlit as st
import pandas as pd
import io
from datetime import datetime, date
import plotly.express as px
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

# إعداد الصفحة
st.set_page_config(page_title="INTERSOFT Analyzer PRO", layout="wide")

# تحميل أو إنشاء الملفات
def load_or_create_csv(path, columns):
    if not os.path.exists(path):
        pd.DataFrame(columns=columns).to_csv(path, index=False)
    return pd.read_csv(path)

USERS_FILE = "users.csv"
LOG_FILE = "activity_log.csv"
NOTES_FILE = "notes.csv"

df_users = load_or_create_csv(USERS_FILE, ["username", "password", "role"])
df_log = load_or_create_csv(LOG_FILE, ["username", "action", "timestamp"])
df_notes = load_or_create_csv(NOTES_FILE, ["from_user", "to_user", "note", "timestamp"])

def log_action(user, action):
    with open(LOG_FILE, "a") as f:
        f.write(f"{user},{action},{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# تسجيل الدخول
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
            st.error("Invalid credentials")
    st.stop()

# --- بعد الدخول ---
st.sidebar.title(f"👤 {st.session_state.username} ({st.session_state.role})")
nav = st.sidebar.radio("📁 Menu", ["Dashboard", "Upload & Analyze", "Notes", "Logout"])

if nav == "Logout":
    log_action(st.session_state.username, "Logout")
    st.session_state.logged_in = False
    st.rerun()
    
st.sidebar.markdown("### 📅 Select Date")
selected_date = st.sidebar.date_input("Filter Date (optional)", value=date.today())

# === تحليل الملفات ===
if nav == "Upload & Analyze":
    st.title("📊 Upload & Analyze Notes File")
    uploaded_file = st.file_uploader("📥 Upload Excel File", type=["xlsx"])

    required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

    def classify_note(note):
        note = str(note).upper().strip()
        known = {
            "WRONG DATE": "WRONG DATE", "DONE": "DONE", "NO SIGNATURE": "NO SIGNATURE",
            "TERMINAL ID": "TERMINAL ID", "NO J.O": "NO J.O", "UNCLEAR RECEIPT": "UNCLEAR RECEIPT"
        }
        for key in known:
            if key in note:
                return known[key]
        return "UNCLASSIFIED"

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
        except:
            df = pd.read_excel(uploaded_file)

        if not all(col in df.columns for col in required_cols):
            st.error("❌ Missing required columns.")
        else:
            df["Note_Type"] = df["NOTE"].apply(classify_note)
            st.success("✅ File processed successfully.")

            # فلترة فنية
            techs = df["Technician_Name"].unique().tolist()
            selected_tech = st.selectbox("🧑‍🔧 Filter by Technician", ["All"] + techs)
            if selected_tech != "All":
                df = df[df["Technician_Name"] == selected_tech]

            # ملخص النسب
            st.markdown("### 📈 Note Types (%)")
            type_percent = df["Note_Type"].value_counts(normalize=True) * 100
            st.dataframe(type_percent.round(2).reset_index().rename(columns={"index": "Note Type", "Note_Type": "Percentage"}))

            # رسم بياني تفاعلي
            fig = px.bar(df["Note_Type"].value_counts().reset_index(),
                         x="index", y="Note_Type", title="Note Type Count",
                         labels={"index": "Note Type", "Note_Type": "Count"})
            st.plotly_chart(fig)

            # عرض البيانات
            st.markdown("### 🧾 Full Data")
            st.dataframe(df)

            # حفظ Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name="Notes")
            st.download_button("📥 Download Excel", output.getvalue(), "processed_notes.xlsx")

            # PDF بسيط
            pdf_buffer = io.BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=A4)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(100, 800, "INTERSOFT Note Report")
            c.setFont("Helvetica", 12)
            c.drawString(100, 780, f"User: {st.session_state.username}")
            c.drawString(100, 760, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
            c.drawString(100, 740, f"Total Notes: {len(df)}")
            c.showPage()
            c.save()
            st.download_button("📄 Download PDF", pdf_buffer.getvalue(), "report.pdf")

if nav == "Notes":
    st.title("📝 Notes between Users")
    users = df_users[df_users.username != st.session_state.username]["username"].tolist()
    to_user = st.selectbox("Send to", users)
    note_text = st.text_area("Write your note here")

    if st.button("Send Note"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df_notes.loc[len(df_notes)] = [st.session_state.username, to_user, note_text, timestamp]
        df_notes.to_csv(NOTES_FILE, index=False)
        log_action(st.session_state.username, f"Sent note to {to_user}")
        st.success("✅ Note sent!")

    st.markdown("### 📬 Your Inbox")
    inbox = df_notes[df_notes["to_user"] == st.session_state.username].sort_values("timestamp", ascending=False)
    st.dataframe(inbox)

# === واجهة المدير ===
if nav == "Dashboard" and st.session_state.role == "manager":
    st.title("🧑‍💼 Admin Dashboard")
    
    # من أونلاين الآن
    latest_logs = df_log.groupby("username").tail(1).reset_index(drop=True)
    latest_logs["Online"] = latest_logs["action"] != "Logout"
    st.markdown("### 🟢 Online Users")
    st.dataframe(latest_logs[latest_logs["Online"] == True][["username", "action", "timestamp"]])

    # سجل الدخول والخروج
    st.markdown("### 📋 Activity Log")
    st.dataframe(df_log.sort_values("timestamp", ascending=False))

    # إدارة المستخدمين
    st.markdown("### 👥 User Management")
    st.dataframe(df_users)
    with st.expander("➕ Add New User"):
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password")
        new_role = st.selectbox("Role", ["employee", "manager"])
        if st.button("Create User"):
            if new_user in df_users["username"].values:
                st.warning("⚠️ User already exists.")
            else:
                df_users.loc[len(df_users)] = [new_user, new_pass, new_role]
                df_users.to_csv(USERS_FILE, index=False)
                st.success("✅ User created.")

# === إشعار ترحيبي عند الدخول ===
if "just_logged_in" not in st.session_state:
    st.session_state.just_logged_in = True
    st.toast(f"👋 Welcome, {st.session_state.username}!", icon="✅")
