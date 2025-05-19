import streamlit as st
import pandas as pd
import os, io
from datetime import datetime
import plotly.express as px
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# ملفات البيانات
USERS_FILE = "users.csv"
ATTEND_FILE = "attendance.csv"
LOG_FILE = "activity_log.csv"
NOTES_FILE = "notes.csv"

# تحميل أو إنشاء ملفات
def load_csv(path, cols):
    if not os.path.exists(path):
        pd.DataFrame(columns=cols).to_csv(path, index=False)
    return pd.read_csv(path)

df_users = load_csv(USERS_FILE, ["username", "password", "role", "full_name", "email"])
df_attend = load_csv(ATTEND_FILE, ["username", "action", "timestamp"])
df_log = load_csv(LOG_FILE, ["username", "action", "timestamp"])
df_notes = load_csv(NOTES_FILE, ["from_user", "to_user", "note", "timestamp"])

def log_action(user, action):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{user},{action},{timestamp}\n")

def record_attendance(user, action_type):
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ATTEND_FILE, "a") as f:
        f.write(f"{user},{action_type},{time}\n")
    log_action(user, action_type)

# تسجيل دخول
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 INTERSOFT Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        user = df_users[(df_users.username == u) & (df_users.password == p)]
        if not user.empty:
            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.role = user.iloc[0]["role"]
            st.session_state.full_name = user.iloc[0]["full_name"]
            st.session_state.email = user.iloc[0]["email"]
            log_action(u, "Login")
            st.rerun()
        else:
            st.error("❌ Invalid credentials")
    st.stop()

# واجهة المستخدم
username = st.session_state.username
role = st.session_state.role
full_name = st.session_state.full_name

st.set_page_config(layout="wide")
with st.sidebar:
    st.image(f"https://i.pravatar.cc/150?u={username}", width=100)
    st.markdown(f"*{full_name}*\n\n`{username}` • {role}")
    st.markdown("---")

    if st.button("Start Work"): record_attendance(username, "Start Work")
    if st.button("Take Break"): record_attendance(username, "Break")
    if st.button("End Work"): record_attendance(username, "End Work")

    nav = st.radio("Navigate", ["Dashboard", "Profile", "Team", "Notes", "Upload & Analyze"])

    if st.button("Logout"):
        log_action(username, "Logout")
        st.session_state.logged_in = False
        st.rerun()

st.title(f"📌 {nav}")

# --- Dashboard ---
if nav == "Dashboard":
    st.subheader("System Overview")
    if role == "manager":
        st.markdown("### 👥 Attendance Records")
        st.dataframe(df_attend.sort_values("timestamp", ascending=False), use_container_width=True)

        online_users = df_log.groupby("username").tail(1)
        online_status = online_users[online_users["action"] != "Logout"]
        st.markdown("### 🟢 Currently Online")
        st.dataframe(online_status[["username", "action", "timestamp"]])

        fig = px.histogram(df_attend, x="action", color="username", title="Attendance Activity")
        st.plotly_chart(fig)

    else:
        personal_logs = df_log[df_log["username"] == username].sort_values("timestamp", ascending=False)
        st.markdown("### 🕒 Your Recent Activity")
        st.dataframe(personal_logs)

# --- Profile ---
elif nav == "Profile":
    user_info = df_users[df_users.username == username].iloc[0]
    st.markdown(f"*Full Name:* {user_info.full_name}")
    st.markdown(f"*Email:* {user_info.email}")
    st.markdown(f"*Role:* {user_info.role}")

    with st.expander("✏️ Edit Profile"):
        new_name = st.text_input("Full Name", value=user_info.full_name)
        new_email = st.text_input("Email", value=user_info.email)
        if st.button("Update Info"):
            df_users.loc[df_users.username == username, ["full_name", "email"]] = [new_name, new_email]
            df_users.to_csv(USERS_FILE, index=False)
            st.success("✅ Updated")

    with st.expander("🔐 Change Password"):
        old = st.text_input("Old Password", type="password")
        new = st.text_input("New Password", type="password")
        if st.button("Change Password"):
            if df_users[df_users.username == username].iloc[0].password == old:
                df_users.loc[df_users.username == username, "password"] = new
                df_users.to_csv(USERS_FILE, index=False)
                st.success("✅ Password changed")

# --- Team ---
elif nav == "Team":
    st.subheader("Team Status")
    for _, row in df_users.iterrows():
        name = row["full_name"]
        u = row["username"]
        last_action = df_log[df_log["username"] == u].tail(1)
        status = "🟢 Online" if not last_action.empty and last_action.iloc[0]["action"] != "Logout" else "⚪ Offline"
        st.markdown(f"- *{name}* ({row['role']}) — {status}")

# --- Notes ---
elif nav == "Notes":
    st.subheader("📝 Send Note")
    users = df_users[df_users.username != username]["username"].tolist()
    to = st.selectbox("To", users)
    txt = st.text_area("Note")
    if st.button("Send Note"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df_notes.loc[len(df_notes)] = [username, to, txt, now]
        df_notes.to_csv(NOTES_FILE, index=False)
        log_action(username, f"Note to {to}")
        st.success("✅ Sent!")

    st.markdown("### 📨 Notes You Received")
    inbox = df_notes[df_notes.to_user == username].sort_values("timestamp", ascending=False)
    st.dataframe(inbox)

# --- Upload & Analyze ---
elif nav == "Upload & Analyze":
    file = st.file_uploader("Upload Excel", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        if "NOTE" in df.columns:
            def classify(note):
                note = str(note).upper()
                if "TERMINAL" in note: return "TERMINAL ID"
                if "DONE" in note: return "DONE"
                if "WRONG" in note: return "WRONG DATE"
                return "OTHER"

            df["Note_Type"] = df["NOTE"].apply(classify)
            st.success("✅ File processed.")

            fig = px.pie(df["Note_Type"].value_counts().reset_index(),
                         names="index", values="Note_Type", title="Note Types")
            st.plotly_chart(fig)
            st.dataframe(df)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Download", output.getvalue(), "processed_notes.xlsx")

            pdf = io.BytesIO()
            c = canvas.Canvas(pdf, pagesize=A4)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 800, "INTERSOFT Report")
            c.setFont("Helvetica", 12)
            c.drawString(100, 780, f"User: {username} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(100, 760, f"Total Notes: {len(df)}")
            c.showPage()
            c.save()
            st.download_button("Download PDF", pdf.getvalue(), "report.pdf")
        else:
            st.error("❌ Missing 'NOTE' column in file.")
