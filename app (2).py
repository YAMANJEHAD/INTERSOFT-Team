import streamlit as st

# --- بيانات المستخدمين (ممكن توصلها بقاعدة لاحقًا) ---
USERS = {
    "admin": {"password": "admin123", "role": "Admin"},
    "yaman": {"password": "yaman1", "role": "Employee"},
    "hatem": {"password": "hatem1", "role": "Employee"},
    "qusai": {"password": "qusai1", "role": "Employee"},
}

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- تصميم تسجيل الدخول ---
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

# --- تسجيل الخروج ---
def logout_button():
    if st.sidebar.button("🚪 Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.experimental_rerun()

# --- واجهة الموظف (تدمجها مع كود الحضور) ---
def employee_interface():
    st.success(f"Welcome {st.session_state.username} 👷‍♂️ (Employee)")
    st.markdown("✅ Here comes the attendance system (Check In / Break / Out)...")
    # 👉 هنا أدمج كود الحضور اللي عملناه مسبقًا

# --- واجهة المدير (Dashboard) ---
def admin_interface():
    st.success("Welcome Admin 🧑‍💼")
    st.markdown("📊 This is the full manager dashboard with stats and controls.")
    # 👉 هون رح نكمل Dashboard المدير اللي فيه تحليلات ورسومات

# --- MAIN LOGIC ---
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
