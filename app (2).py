import streamlit as st
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import calendar
from io import BytesIO
import uuid
import os
import json
from PIL import Image
import pytz
import numpy as np

# --- Constants ---
USERS = {
    "yaman": {"pass": "YAMAN1", "role": "Admin"},
    "hatem": {"pass": "HATEM2", "role": "Supervisor"},
    "qusai": {"pass": "QUSAI4", "role": "Employee"},
}
USER_PROFILE = {
    "yaman": {"name": "Yaman", "email": "yaman@example.com", "picture": None},
    "hatem": {"name": "Hatem", "email": "hatem@example.com", "picture": None},
    "qusai": {"name": "Qusai", "email": "qusai@example.com", "picture": None},
}
EXPORT_FOLDER = "weekly_exports"
DATA_FILE = "data.json"
TASK_STATUSES = ["⏳ Not Started", "🔄 In Progress", "✅ Completed"]
TASK_PRIORITIES = ["🟢 Low", "🟡 Medium", "🔴 High"]
DEPARTMENTS = ["FLM", "Tech Support", "CRM"]
CATEGORIES = ["Job Orders", "CRM", "Meetings", "Paperwork"]
SHIFTS = ["Morning", "Evening"]
ROLES = ["Admin", "Supervisor", "Employee"]

# --- Page Config ---
st.set_page_config(
    page_title="⚡ INTERSOFT Dashboard | FLM",
    layout="wide",
    page_icon="🚀"
)

# --- Embed CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    scroll-behavior: smooth;
}

h1, h2, h3 {
    font-weight: 800;
    letter-spacing: 0.5px;
    margin-bottom: 1.5rem;
}

.top-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0 3rem; margin: 2rem 0;
    animation: fadeIn 1s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

.greeting {
    font-size: 1.2rem; font-weight: 600;
    text-align: right; line-height: 1.5;
}

.company {
    font-size: 1.6rem; font-weight: 800; letter-spacing: 0.8px;
}

.date-box {
    font-size: 1.2rem; font-weight: 600; text-align: center;
    padding: 1rem 2rem; border-radius: 24px;
    margin-bottom: 1.5rem; display: inline-block;
    animation: fadeIn 0.6s ease-in-out;
}

.nav-buttons {
    display: flex; flex-wrap: wrap; gap: 1.5rem; justify-content: center;
    margin: 2rem 0; padding: 1.5rem;
}

.stSelectbox {
    font-weight: 700; font-size: 1.2rem;
    border-radius: 26px; padding: 0.8rem; min-width: 220px;
}

.stButton>button {
    background: #FFD700; /* Vibrant yellow */
    color: #1E3A8A; /* Dark blue text */
    font-weight: 700; font-size: 1.2rem;
    border-radius: 26px; padding: 0.8rem; min-width: 220px; height: 52px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    border: 1px solid #1E3A8A; /* Dark blue border */
    cursor: pointer; text-align: center;
    display: flex; align-items: center; justify-content: center; gap: 12px;
    transition: background 0.3s ease, box-shadow 0.3s ease;
}

.stButton>button:hover {
    background: #FFC107; /* Slightly darker yellow on hover */
    box-shadow: 0 6px 16px rgba(0,0,0,0.3);
}

.stButton>button.delete-button {
    background: #FFB300; /* Darker yellow for delete button */
    color: #1E3A8A;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    border: 1px solid #1E3A8A;
}

.stButton>button.delete-button:hover {
    background: #FFA000; /* Even darker yellow on hover */
    box-shadow: 0 6px 16px rgba(0,0,0,0.3);
}

.overview-box {
    padding: 1.5rem; border-radius: 18px; text-align: center;
    margin: 1rem 0; transition: transform 0.3s ease;
    animation: zoomIn 0.6s ease-in-out;
}

.overview-box:hover {
    transform: translateY(-5px) scale(1.02);
}

@keyframes zoomIn {
    from { transform: scale(0.95); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}

.overview-box span {
    font-size: 1.8rem; font-weight: 800;
    display: block;
}

.overview-box small {
    font-size: 0.9rem;
}

.edit-section {
    padding: 2.5rem; border-radius: 18px; margin-bottom: 2rem;
    animation: fadeIn 0.5s ease-in-out;
}

.alert-box {
    padding: 1rem; border-radius: 16px;
    font-size: 1rem; font-weight: 600; max-width: 400px;
    margin: 1rem 0;
    opacity: 0.92; transition: opacity 0.3s ease-out, transform 0.3s ease-out;
    z-index: 1000; animation: slideInDown 0.5s ease-in-out;
}

@keyframes slideInDown {
    from { transform: translateY(-20px); opacity: 0; }
    to { transform: translateY(0); opacity: 0.92; }
}

@keyframes fadeOut {
    from { opacity: 0.92; transform: translateY(0); }
    to { opacity: 0; transform: translateY(-20px); }
}

.alert-box.hide {
    animation: fadeOut 0.5s ease-out forwards;
}

.stDataFrame table {
    width: 100%; border-collapse: collapse;
    border-radius: 12px; overflow: hidden;
}

.stDataFrame tr:hover {
    transition: background-color 0.3s ease;
}

.stDataFrame th {
    font-weight: 700;
    padding: 12px; font-size: 1.2rem;
}

.stDataFrame td {
    font-weight: 600; padding: 12px;
    border-bottom: 1px solid transparent; font-size: 1.1rem;
}

footer {
    text-align: center; padding: 3rem 0;
    font-size: 1.1rem; font-weight: 500;
    animation: fadeIn 1s ease-in-out;
}

.profile-picture {
    border-radius: 50%; width: 100px; height: 100px; object-fit: cover;
}

.task-attachment {
    max-width: 200px; border-radius: 12px; margin-top: 0.5rem;
}

.attachment-info {
    font-size: 0.9rem; margin-top: 0.3rem;
}

.chart-container {
    padding: 1.5rem; border-radius: 18px;
    margin-bottom: 2rem; transition: transform 0.3s ease;
    animation: slideInUp 0.6s ease-in-out;
}

.chart-container:hover {
    transform: translateY(-5px);
}

@keyframes slideInUp {
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# --- Persistent Storage ---
def save_data():
    try:
        data = {
            "timesheet": st.session_state.timesheet,
            "reminders": st.session_state.reminders,
            "user_profile": {
                k: {"name": v["name"], "email": v["email"], "picture": None}
                for k, v in USER_PROFILE.items()
            },
            "users": USERS,
            "login_log": st.session_state.login_log
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"⚠️ Failed to save data: {e}")

def load_data():
    global USERS, USER_PROFILE
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                timesheet = data.get("timesheet", [])
                valid_timesheet = []
                for task in timesheet:
                    try:
                        pd.to_datetime(task["Submitted"], format='%Y-%m-%d %H:%M:%S')
                        valid_timesheet.append(task)
                    except (ValueError, TypeError):
                        st.warning(f"Invalid timestamp in task {task.get('TaskID', 'Unknown')}: {task.get('Submitted', 'N/A')}")
                st.session_state.timesheet = valid_timesheet
                st.session_state.reminders = data.get("reminders", [])
                st.session_state.login_log = data.get("login_log", [])
                USERS.update(data.get("users", {}))
                for user, profile in data.get("user_profile", {}).items():
                    if user in USER_PROFILE:
                        USER_PROFILE[user]["name"] = profile.get("name", USER_PROFILE[user]["name"])
                        USER_PROFILE[user]["email"] = profile.get("email", USER_PROFILE[user]["email"])
                    else:
                        USER_PROFILE[user] = {"name": profile.get("name", ""), "email": profile.get("email", ""), "picture": None}
    except Exception as e:
        st.error(f"⚠️ Failed to load data: {e}")

# --- Session Initialization ---
def initialize_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_role_type = None  # Initialize user_role_type
        st.session_state.timesheet = []
        st.session_state.login_log = []
        st.session_state.reminders = []
        st.session_state.selected_tab = "Dashboard"
    if "reminders" not in st.session_state:
        st.session_state.reminders = []
    if "selected_tab" not in st.session_state:
        st.session_state.selected_tab = "Dashboard"
    load_data()

# --- Authentication ---
def authenticate_user():
    if not st.session_state.logged_in:
        st.title("🔐 Login to INTERSOFT Dashboard")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", key="login_button"):
            user = USERS.get(username.lower())
            if user and user["pass"] == password:
                st.session_state.logged_in = True
                st.session_state.user_role = username.lower()
                st.session_state.user_role_type = user["role"]
                st.session_state.login_log.append({
                    "Username": username.lower(),
                    "Login Time": datetime.now(pytz.timezone("Asia/Riyadh")).strftime('%Y-%m-%d %H:%M:%S'),
                    "Role": user["role"]
                })
                save_data()
                st.session_state.selected_tab = "Dashboard"
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
        st.stop()

# --- Excel Export Function ---
def export_to_excel(df, sheet_name, file_name):
    output = BytesIO()
    try:
        df_clean = df.drop(columns=['TaskID', 'Attachment'], errors='ignore')
        df_clean = df_clean.replace([np.nan, np.inf, -np.inf], '')
        with pd.ExcelWriter(output, engine="xlsxwriter", engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
            df_clean.to_excel(writer, index=False, sheet_name=sheet_name)
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            header_format = workbook.add_format({
                'bold': True, 'font_color': 'white', 'bg_color': '#4f81bd',
                'font_size': 12, 'align': 'center', 'valign': 'vcenter'
            })
            cell_format = workbook.add_format({
                'font_color': '#000000', 'align': 'left', 'valign': 'vcenter'
            })
            for col_num, col in enumerate(df_clean.columns):
                worksheet.write(0, col_num, col, header_format)
                max_len = max(
                    df_clean[col].astype(str).map(len).max() if not df_clean[col].empty else 10,
                    len(col)
                )
                worksheet.set_column(col_num, col_num, max_len + 2)
            for row_num in range(1, len(df_clean) + 1):
                for col_num in range(len(df_clean.columns)):
                    worksheet.write(row_num, col_num, df_clean.iloc[row_num-1, col_num], cell_format)
        return output.getvalue(), file_name
    except Exception as e:
        st.error(f"⚠️ Failed to export to Excel: {e}")
        return None, file_name

# --- Auto Weekly Export ---
def auto_export_weekly():
    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    now = datetime.now(pytz.timezone("Asia/Riyadh"))
    if now.weekday() == 6:  # Sunday
        filename = os.path.join(EXPORT_FOLDER, f"flm_tasks_week_{now.strftime('%Y_%U')}.csv")
        if not os.path.exists(filename):
            df_export = pd.DataFrame(st.session_state.timesheet)
            if not df_export.empty:
                try:
                    df_export = df_export.drop(columns=['TaskID', 'Attachment'], errors='ignore')
                    df_export = df_export.replace([np.nan, np.inf, -np.inf], '')
                    df_export.to_csv(filename, index=False)
                    st.info(f"✅ Auto-exported weekly tasks to {filename}")
                except Exception as e:
                    st.error(f"⚠️ Failed to export tasks: {e}")

# --- Dashboard Stats ---
def render_dashboard_stats(display_df, date_str):
    total_tasks = len(display_df)
    completed_tasks = display_df[display_df['Status'] == '✅ Completed'].shape[0] if not display_df.empty else 0
    in_progress_tasks = display_df[display_df['Status'] == '🔄 In Progress'].shape[0] if not display_df.empty else 0
    not_started_tasks = display_df[display_df['Status'] == '⏳ Not Started'].shape[0] if not display_df.empty else 0

    st.markdown(f"### 📊 Task Statistics for {date_str}")
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"<div class='overview-box'>Total Tasks<br><span>{total_tasks}</span></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='overview-box'>Completed<br><span>{completed_tasks}</span></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='overview-box'>In Progress<br><span>{in_progress_tasks}</span></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='overview-box'>Not Started<br><span>{not_started_tasks}</span></div>", unsafe_allow_html=True)

# --- Render Analytics in Dashboard ---
def render_analytics(display_df):
    if not display_df.empty:
        st.markdown("### 📈 Task Analytics by Date")
        tz = pytz.timezone("Asia/Riyadh")
        today_str = datetime.now(tz).strftime('%Y-%m-%d')
        unique_dates = sorted(display_df['Date'].unique(), reverse=True)  # Sort dates descending
        for date_str in unique_dates:
            date_df = display_df[display_df['Date'] == date_str]
            st.markdown(f"<div class='edit-section'>", unsafe_allow_html=True)
            st.markdown(f"#### 📅 {date_str} ({calendar.day_name[pd.to_datetime(date_str).weekday()]})")
            render_dashboard_stats(date_df, date_str)
            
            col1, col2 = st.columns(2)
            with col1:
                fig_hist = px.histogram(
                    date_df,
                    x="Status",
                    title="Task Status Distribution",
                    color="Status",
                    color_discrete_sequence=px.colors.qualitative.Plotly,
                    template="plotly_dark",
                    height=400
                )
                fig_hist.update_traces(
                    hovertemplate="Status: %{x}<br>Tasks: %{y}"
                )
                fig_hist.update_layout(
                    title_font_size=16,
                    xaxis_title="Status",
                    yaxis_title="Number of Tasks",
                    showlegend=True
                )
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.plotly_chart(fig_hist, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                fig_pie = px.pie(
                    date_df,
                    names="Category",
                    title="Category Distribution",
                    color_discrete_sequence=px.colors.qualitative.Plotly,
                    template="plotly_dark",
                    height=400
                )
                fig_pie.update_traces(
                    hovertemplate="Category: %{label}<br>Tasks: %{value} (%{percent})",
                    textinfo="percent+label"
                )
                fig_pie.update_layout(
                    title_font_size=16,
                    showlegend=True
                )
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.plotly_chart(fig_pie, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(f"### 📋 Tasks for {date_str}")
            st.dataframe(date_df.drop(columns=['TaskID', 'Attachment'], errors='ignore'))

            data, file_name = export_to_excel(date_df, f"Tasks_{date_str}", f"tasks_{date_str}.xlsx")
            if data:
                st.download_button(
                    f"📥 Download Tasks for {date_str}",
                    data=data,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.info("ℹ️ No tasks available for display.")

# --- Render All Uploaded Files ---
def render_all_uploaded_files(df_all):
    st.markdown("### 📎 All Uploaded Files")
    if not df_all.empty and 'Attachment' in df_all.columns:
        attachments = []
        for _, row in df_all.iterrows():
            if isinstance(row.get("Attachment"), dict):
                attachments.append({
                    "File Name": row["Attachment"].get("name", "Unknown"),
                    "File Type": row["Attachment"].get("type", "Unknown"),
                    "Employee": row["Employee"].capitalize(),
                    "Task Date": row["Date"],
                    "Data": row["Attachment"].get("data"),
                    "TaskID": row["TaskID"]
                })
        if attachments:
            attachments_df = pd.DataFrame(attachments)
            st.markdown("<div class='edit-section'>", unsafe_allow_html=True)
            for idx, row in attachments_df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                col1.write(row["File Name"])
                col2.write(row["File Type"])
                col3.write(row["Employee"])
                col4.write(row["Task Date"])
                if row["Data"]:
                    col5.download_button(
                        label="📎 Download",
                        data=base64.b64decode(row["Data"]),
                        file_name=row["File Name"],
                        mime=row["File Type"],
                        key=f"download_all_attachment_{row['TaskID']}_{idx}"
                    )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("ℹ️ No files uploaded yet.")
    else:
        st.info("ℹ️ No tasks with attachments found.")

# --- Settings Popup ---
def render_settings():
    with st.expander("⚙️ User Settings", expanded=False):
        st.subheader("User Profile")
        user = st.session_state.user_role
        current_profile = USER_PROFILE.get(user, {"name": "", "email": "", "picture": None})
        
        if current_profile["picture"]:
            st.image(current_profile["picture"], width=100, caption="Profile Picture", output_format="PNG")
        
        with st.form("profile_form"):
            name = st.text_input("Name", value=current_profile["name"], key="profile_name")
            email = st.text_input("Email", value=current_profile["email"], key="profile_email")
            picture = st.file_uploader("Upload Profile Picture", type=["png", "jpg", "jpeg"], key="profile_picture")
            submitted = st.form_submit_button("💾 Save Profile")
            if submitted:
                USER_PROFILE[user]["name"] = name
                USER_PROFILE[user]["email"] = email
                if picture:
                    img = Image.open(picture)
                    img = img.resize((100, 100))
                    USER_PROFILE[user]["picture"] = img
                save_data()
                st.success("✅ Profile updated successfully!")
                st.rerun()

        st.subheader("🔑 Change Password")
        with st.form("password_form"):
            current_password = st.text_input("Current Password", type="password", key="current_password")
            new_password = st.text_input("New Password", type="password", key="new_password")
            confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_password")
            submitted = st.form_submit_button("🔄 Change Password")
            if submitted:
                if current_password == USERS[user]["pass"]:
                    if new_password == confirm_password and new_password:
                        USERS[user]["pass"] = new_password
                        save_data()
                        st.success("✅ Password changed successfully!")
                        st.rerun()
                    else:
                        st.error("⚠️ New password and confirmation do not match or are empty!")
                else:
                    st.error("⚠️ Current password is incorrect!")

# --- Download Tasks ---
def render_download_tasks():
    tz = pytz.timezone("Asia/Riyadh")
    st.header("⬇️ Download My Tasks")
    current_user = st.session_state.user_role
    user_tasks = df_all[df_all['Employee'] == current_user] if not df_all.empty and 'Employee' in df_all.columns else pd.DataFrame()
    if not user_tasks.empty:
        st.markdown("<div class='edit-section'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            start = st.date_input("Start Date", value=datetime.now(tz) - timedelta(days=7), key="download_start")
        with col2:
            end = st.date_input("End Date", value=datetime.now(tz), key="download_end")
        with col3:
            category = st.selectbox("Category", options=["All"] + CATEGORIES, key="download_category")
        priority = st.selectbox("Priority", options=["All"] + TASK_PRIORITIES, key="download_priority")
        
        filtered_tasks = user_tasks
        if category != "All":
            filtered_tasks = filtered_tasks[filtered_tasks['Category'] == category]
        if priority != "All":
            filtered_tasks = filtered_tasks[filtered_tasks['Priority'] == priority]
        filtered_tasks = filtered_tasks[(filtered_tasks['Date'] >= start.strftime('%Y-%m-%d')) & (filtered_tasks['Date'] <= end.strftime('%Y-%m-%d'))]
        
        st.dataframe(filtered_tasks.drop(columns=['TaskID', 'Attachment'], errors='ignore'))
        
        file_name = f"{current_user}_tasks_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.xlsx"
        if category != "All":
            file_name = f"{current_user}_tasks_{category}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.xlsx"
        if priority != "All":
            file_name = f"{current_user}_tasks_{category}_{priority}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.xlsx"
        
        data, file_name = export_to_excel(filtered_tasks, f"{current_user}_Tasks", file_name)
        if data:
            st.download_button(
                label="⬇️ Download Filtered Tasks",
                data=data,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("⚠️ Failed to generate Excel file.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("ℹ️ No tasks available for your account.")

# --- Admin Download Other Users' Tasks ---
def render_admin_download_tasks():
    if st.session_state.user_role_type == "Admin":
        st.markdown("### 🛠 Admin Panel: Download Employee Tasks")
        df_all = pd.DataFrame(st.session_state.timesheet)
        if not df_all.empty and 'Employee' in df_all.columns:
            employees = df_all['Employee'].unique().tolist()
            if employees:
                selected_employee = st.selectbox("Select Employee", employees, key="admin_download_employee")
                emp_tasks = df_all[df_all['Employee'] == selected_employee]
                if not emp_tasks.empty:
                    data, file_name = export_to_excel(emp_tasks, f"{selected_employee}_Tasks", f"{selected_employee}_tasks.xlsx")
                    if data:
                        st.download_button(
                            label=f"⬇️ Download {selected_employee.capitalize()} Tasks",
                            data=data,
                            file_name=file_name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.error("⚠️ Failed to generate Excel file.")
                else:
                    st.info(f"ℹ️ No tasks found for {selected_employee}.")
            else:
                st.info("ℹ️ No employees with tasks found.")
        else:
            st.info("ℹ️ No tasks recorded yet.")

# --- Render Header ---
def render_header():
    tz = pytz.timezone("Asia/Riyadh")
    current_time = datetime.now(tz).strftime('%I:%M %p')
    st.markdown(
        f"""
        <div class='top-header'>
            <div class='company'>INTERSOFT<br>International Software Company</div>
            <div class='greeting'>👋 Welcome <b>{st.session_state.user_role.capitalize()} ({st.session_state.user_role_type})</b><br>
            <small>Today is {datetime.now(tz).strftime('%A, %B %d, %Y')}</small></div>
        </div>
        <div class='date-box'>🕒 {current_time} (+03)</div>
        """,
        unsafe_allow_html=True
    )

    # Dropdown Menu for Navigation
    st.markdown("<div class='nav-buttons'>", unsafe_allow_html=True)
    tabs = [
        ("Dashboard", "🏠 Dashboard"),
        ("Add Task", "➕ Add Task"),
        ("Edit/Delete Task", "✏️ Edit/Delete Task"),
        ("Employee Work", "👥 Employee Work"),
        ("Settings", "⚙️ Settings"),
        ("Download Tasks", "⬇️ Download My Tasks")
    ]
    if st.session_state.user_role_type == "Admin":
        tabs.insert(-2, ("Admin Panel", "🛠 Admin Panel"))

    selected_tab = st.selectbox(
        "Navigate to",
        options=[tab[0] for tab in tabs],
        format_func=lambda x: next(tab[1] for tab in tabs if tab[0] == x),
        key="nav_dropdown"
    )
    if selected_tab != st.session_state.selected_tab:
        st.session_state.selected_tab = selected_tab
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- Render Sidebar Stats ---
def render_sidebar_stats():
    tz = pytz.timezone("Asia/Riyadh")
    today_str = datetime.now(tz).strftime('%Y-%m-%d')
    st.sidebar.markdown(f"### 👥 Today's Employee Statistics ({today_str})")
    df_all = pd.DataFrame(st.session_state.timesheet)
    if not df_all.empty and 'Employee' in df_all.columns:
        today_df = df_all[df_all['Date'] == today_str]
        employees = sorted(today_df['Employee'].unique()) if not today_df.empty else []
        if employees:
            for employee in employees:
                emp_df = today_df[today_df['Employee'] == employee]
                emp_total = len(emp_df)
                emp_completed = emp_df[emp_df['Status'] == '✅ Completed'].shape[0]
                emp_in_progress = emp_df[emp_df['Status'] == '🔄 In Progress'].shape[0]
                emp_not_started = emp_df[emp_df['Status'] == '⏳ Not Started'].shape[0]
                st.sidebar.markdown(
                    f"""
                    <div class='overview-box'>
                        <div>{employee.capitalize()}</div>
                        <span>{emp_total}</span>
                        <small>Completed: {emp_completed} | In Progress: {emp_in_progress} | Not Started: {emp_not_started}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.sidebar.info(f"ℹ️ No tasks recorded for today ({today_str}).")
    else:
        st.sidebar.info("ℹ️ No tasks recorded yet.")

# --- Render Alerts in Sidebar ---
def render_alerts(df_user, df_all):
    tz = pytz.timezone("Asia/Riyadh")
    today_str = datetime.now(tz).strftime('%Y-%m-%d')
    st.sidebar.markdown("<div id='alert-container'>", unsafe_allow_html=True)
    
    # Check if user_role_type exists and is not None
    if hasattr(st.session_state, 'user_role_type') and st.session_state.user_role_type is not None:
        if st.session_state.user_role_type != "Admin":
            if df_user.empty or today_str not in df_user['Date'].values:
                st.sidebar.markdown(f"<div class='alert-box'>⚠️ You haven't submitted any tasks for today!</div>", unsafe_allow_html=True)
            
            if st.session_state.user_role_type == "Supervisor":
                users = list(set(df_all['Employee'].unique()) if not df_all.empty and 'Employee' in df_all.columns else [])
                for user in USERS.keys():
                    if user.lower() not in users or not any(df_all[df_all['Employee'] == user.lower()]['Date'] == today_str):
                        if USERS[user.lower()]["role"] != "Admin":
                            st.sidebar.markdown(f"<div class='alert-box'>🔔 Alert: <b>{user.capitalize()}</b> has not submitted a task today!</div>", unsafe_allow_html=True)

            try:
                reminders = st.session_state.reminders
            except AttributeError:
                st.session_state.reminders = []
                reminders = st.session_state.reminders
            for reminder in reminders:
                if reminder["user"] == st.session_state.user_role and reminder["date"] == today_str:
                    st.sidebar.markdown(f"<div class='alert-box reminder'>🔔 Reminder: Task '{reminder['task_desc'][:30]}...' is still Not Started! Due: {reminder['due_date']}</div>", unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<div class='alert-box'>⚠️ Please log in to view alerts.</div>", unsafe_allow_html=True)
    
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    st.sidebar.markdown("""
        <script>
            setTimeout(() => {
                const alerts = document.querySelectorAll('.alert-box');
                alerts.forEach((alert) => {
                    alert.classList.add('hide');
                });
                setTimeout(() => {
                    const alertContainer = document.getElementById('alert-container');
                    if (alertContainer) {
                        alertContainer.style.display = 'none';
                    }
                }, 500);
            }, 5000);
        </script>
    """, unsafe_allow_html=True)

# --- Add Task ---
def render_add_task():
    tz = pytz.timezone("Asia/Riyadh")
    st.header("➕ Add New Task")
    with st.form("task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            shift = st.selectbox("🕒 Shift", SHIFTS, key="add_shift")
            date_selected = st.date_input("📅 Date", value=datetime.now(tz), key="add_date")
            department = st.selectbox("🏢 Department", DEPARTMENTS, key="add_dept")
        with col2:
            category = st.selectbox("📂 Category", CATEGORIES, key="add_cat")
            status = st.selectbox("📌 Status", TASK_STATUSES, key="add_stat")
            priority = st.selectbox("⚠️ Priority", TASK_PRIORITIES, key="add_prio")
        description = st.text_area("🗒 Description", height=120, key="add_desc")
        attachment = st.file_uploader("📎 Upload File (Optional)", type=["png", "jpg", "jpeg", "pdf", "xlsx", "xls"], key="add_attachment")
        set_reminder = st.checkbox("🔔 Set Reminder for Not Started Task", key="add_reminder") if status == "⏳ Not Started" else False
        reminder_date = st.date_input("📅 Reminder Due Date", value=datetime.now(tz) + timedelta(days=1), key="add_reminder_date") if set_reminder else None
        
        submitted = st.form_submit_button("✅ Submit Task")
        
        if submitted:
            if description.strip():
                task = {
                    "TaskID": str(uuid.uuid4()),
                    "Employee": st.session_state.user_role,
                    "Date": date_selected.strftime('%Y-%m-%d'),
                    "Day": calendar.day_name[date_selected.weekday()],
                    "Shift": shift,
                    "Department": department,
                    "Category": category,
                    "Status": status,
                    "Priority": priority,
                    "Description": description,
                    "Submitted": datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'),
                    "Attachment": None
                }
                if attachment:
                    if attachment.size > 5 * 1024 * 1024:  # Limit to 5MB
                        st.error("⚠️ File size exceeds 5MB limit!")
                    else:
                        task["Attachment"] = {
                            "name": attachment.name,
                            "data": base64.b64encode(attachment.read()).decode('utf-8'),
                            "type": attachment.type
                        }
                st.session_state.timesheet.append(task)
                if set_reminder and status == "⏳ Not Started":
                    st.session_state.reminders.append({
                        "user": st.session_state.user_role,
                        "task_id": task["TaskID"],
                        "task_desc": task["Description"],
                        "date": datetime.now(tz).strftime('%Y-%m-%d'),
                        "due_date": reminder_date.strftime('%Y-%m-%d')
                    })
                save_data()
                st.success("🎉 Task added successfully!")
                st.rerun()
            else:
                st.error("⚠️ Description cannot be empty!")

# --- Edit/Delete Task ---
def render_edit_delete_task(display_df):
    tz = pytz.timezone("Asia/Riyadh")
    st.header("✏️ Edit/Delete Task")
    if not display_df.empty:
        st.markdown("<div class='edit-section'>", unsafe_allow_html=True)
        task_dict = {f"{row['Description'][:30]}... ({row['Date']} | {row['Category']} | {row['Status']} | {row['Employee'].capitalize()})": row["TaskID"] for _, row in display_df.iterrows()}
        selected_label = st.selectbox("📋 Select Task", list(task_dict.keys()), key="select_task")
        selected_id = task_dict[selected_label]
        selected_task = display_df[display_df["TaskID"] == selected_id].iloc[0]

        if isinstance(selected_task.get("Attachment"), dict):
            st.markdown("### 📎 Current Attachment")
            attachment = selected_task["Attachment"]
            st.markdown(f"<div class='attachment-info'>File: {attachment.get('name', 'Unknown')} ({attachment.get('type', 'Unknown')})</div>", unsafe_allow_html=True)
            if attachment.get("type", "").startswith("image/"):
                st.image(base64.b64decode(attachment["data"]), caption=attachment.get("name", "Image"), width=200, use_column_width=False)
            st.download_button(
                label=f"📎 Download {attachment.get('name', 'File')}",
                data=base64.b64decode(attachment["data"]),
                file_name=attachment.get("name", "attachment"),
                mime=attachment.get("type", "application/octet-stream"),
                key=f"download_attachment_{selected_id}"
            )

        with st.form("edit_form"):
            col1, col2 = st.columns(2)
            with col1:
                shift = st.selectbox("🕒 Shift", SHIFTS, index=SHIFTS.index(selected_task["Shift"]), key="edit_shift")
                date = st.date_input("📅 Date", datetime.strptime(selected_task["Date"], '%Y-%m-%d'), key="edit_date")
                dept = st.selectbox("🏢 Department", DEPARTMENTS, index=DEPARTMENTS.index(selected_task["Department"]), key="edit_dept")
            with col2:
                cat = st.selectbox("📂 Category", CATEGORIES, index=CATEGORIES.index(selected_task["Category"]), key="edit_cat")
                stat = st.selectbox("📌 Status", TASK_STATUSES, index=TASK_STATUSES.index(selected_task["Status"]), key="edit_stat")
                prio = st.selectbox("⚠️ Priority", TASK_PRIORITIES, index=TASK_PRIORITIES.index(selected_task["Priority"]), key="edit_prio")
            desc = st.text_area("🗒 Description", selected_task["Description"], height=120, key="edit_desc")
            attachment = st.file_uploader("📎 Upload New File (Optional)", type=["png", "jpg", "jpeg", "pdf", "xlsx", "xls"], key="edit_attachment")
            set_reminder = st.checkbox("🔔 Set Reminder for Not Started Task", key="edit_reminder") if stat == "⏳ Not Started" else False
            reminder_date = st.date_input("📅 Reminder Due Date", value=datetime.now(tz) + timedelta(days=1), key="edit_reminder_date") if set_reminder else None

            submitted = st.form_submit_button("💾 Save Changes")
            if submitted:
                if desc.strip():
                    for i, t in enumerate(st.session_state.timesheet):
                        if t["TaskID"] == selected_id:
                            st.session_state.timesheet[i] = {
                                "TaskID": selected_id,
                                "Employee": selected_task["Employee"],
                                "Date": date.strftime('%Y-%m-%d'),
                                "Day": calendar.day_name[date.weekday()],
                                "Shift": shift,
                                "Department": dept,
                                "Category": cat,
                                "Status": stat,
                                "Priority": prio,
                                "Description": desc,
                                "Submitted": datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'),
                                "Attachment": t.get("Attachment")
                            }
                            if attachment:
                                if attachment.size > 5 * 1024 * 1024:
                                    st.error("⚠️ File size exceeds 5MB limit!")
                                    st.stop()
                                else:
                                    st.session_state.timesheet[i]["Attachment"] = {
                                        "name": attachment.name,
                                        "data": base64.b64encode(attachment.read()).decode('utf-8'),
                                        "type": attachment.type
                                    }
                            if set_reminder and stat == "⏳ Not Started":
                                st.session_state.reminders = [r for r in st.session_state.reminders if r["task_id"] != selected_id]
                                st.session_state.reminders.append({
                                    "user": selected_task["Employee"],
                                    "task_id": selected_id,
                                    "task_desc": desc,
                                    "date": datetime.now(tz).strftime('%Y-%m-%d'),
                                    "due_date": reminder_date.strftime('%Y-%m-%d')
                                })
                            save_data()
                            st.success("✅ Task updated successfully!")
                            st.rerun()
                else:
                    st.error("⚠️ Description cannot be empty!")

        with st.form("delete_form"):
            st.warning("⚠️ This action cannot be undone!")
            delete_confirmed = st.checkbox("I confirm I want to delete this task", key="confirm_delete")
            submitted_delete = st.form_submit_button("🗑 Delete Task", type="primary", help="Delete selected task")
            if submitted_delete and delete_confirmed:
                if selected_task["Employee"] == st.session_state.user_role or st.session_state.user_role_type == "Admin":
                    st.session_state.timesheet = [t for t in st.session_state.timesheet if t["TaskID"] != selected_id]
                    st.session_state.reminders = [r for r in st.session_state.reminders if r["task_id"] != selected_id]
                    save_data()
                    st.warning("🗑 Task deleted successfully!")
                    st.rerun()
                else:
                    st.error("⚠️ You can only delete your own tasks or tasks as an Admin.")

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("ℹ️ No tasks available to edit.")

# --- Employee Work Tab ---
def render_employee_work():
    tz = pytz.timezone("Asia/Riyadh")
    st.header("👥 Employee Work")
    df_all = pd.DataFrame(st.session_state.timesheet)
    if not df_all.empty and 'Employee' in df_all.columns:
        st.markdown("### 📅 View Employee Tasks")
        col1, col2 = st.columns(2)
        with col1:
            users = df_all['Employee'].unique().tolist()
            selected_user = st.selectbox("Employee", options=["All"] + users, key="employee_work_filter")
        with col2:
            start = st.date_input("Start Date", value=datetime.now(tz) - timedelta(days=7), key="employee_work_start")
            end = st.date_input("End Date", value=datetime.now(tz), key="employee_work_end")
        filtered_df = df_all
        if selected_user != "All":
            filtered_df = filtered_df[filtered_df['Employee'] == selected_user]
        filtered_df = filtered_df[(filtered_df['Date'] >= start.strftime('%Y-%m-%d')) & (filtered_df['Date'] <= end.strftime('%Y-%m-%d'))]
        st.dataframe(filtered_df.drop(columns=['TaskID', 'Attachment'], errors='ignore'))
    else:
        st.info("ℹ️ No tasks recorded yet.")

# --- Admin Panel ---
def render_admin_panel():
    tz = pytz.timezone("Asia/Riyadh")
    if st.session_state.user_role_type == "Admin":
        st.header("🛠 Admin Panel")
        df_all = pd.DataFrame(st.session_state.timesheet)
        
        with st.expander("👤 Manage Users", expanded=False):
            st.markdown("<div class='edit-section'>", unsafe_allow_html=True)
            st.subheader("Add New User")
            with st.form("add_user_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_username = st.text_input("Username", key="new_username")
                    new_password = st.text_input("Password", type="password", key="new_password")
                    new_role = st.selectbox("Role", ROLES, key="new_role")
                with col2:
                    new_name = st.text_input("Name", key="new_name")
                    new_email = st.text_input("Email", key="new_email")
                submitted = st.form_submit_button("➕ Add User")
                if submitted:
                    if new_username.lower() in USERS:
                        st.error("⚠️ Username already exists!")
                    elif not all([new_username, new_password, new_name, new_email]):
                        st.error("⚠️ All fields are required!")
                    else:
                        USERS[new_username.lower()] = {"pass": new_password, "role": new_role}
                        USER_PROFILE[new_username.lower()] = {"name": new_name, "email": new_email, "picture": None}
                        save_data()
                        st.success(f"✅ User {new_username} added successfully!")
                        st.rerun()

            st.markdown("<hr>", unsafe_allow_html=True)
            st.subheader("Change User Role")
            with st.form("change_role_form"):
                users = [u for u in USERS.keys() if u != st.session_state.user_role]
                selected_user = st.selectbox("Select User", users, key="change_role_user")
                new_role = st.selectbox("New Role", ROLES, key="change_role_select")
                role_confirmed = st.checkbox("I confirm I want to change this user's role", key="confirm_role_change")
                submitted_role = st.form_submit_button("🔄 Change Role")
                if submitted_role and role_confirmed:
                    if selected_user == st.session_state.user_role:
                        st.error("⚠️ Cannot change your own role!")
                    else:
                        USERS[selected_user]["role"] = new_role
                        save_data()
                        st.success(f"✅ Role for {selected_user} changed to {new_role}!")
                        st.rerun()

            st.markdown("<hr>", unsafe_allow_html=True)
            st.subheader("Delete User")
            with st.form("delete_user_form"):
                users = [u for u in USERS.keys() if u != st.session_state.user_role]
                selected_user = st.selectbox("Select User to Delete", users, key="delete_user_select")
                delete_confirmed = st.checkbox("I confirm I want to delete this user", key="confirm_user_delete")
                submitted_delete = st.form_submit_button("🗑 Delete User", type="primary", help="Delete selected user")
                if submitted_delete and delete_confirmed:
                    if selected_user == st.session_state.user_role:
                        st.error("⚠️ Cannot delete your own account!")
                    else:
                        del USERS[selected_user]
                        del USER_PROFILE[selected_user]
                        st.session_state.timesheet = [t for t in st.session_state.timesheet if t["Employee"] != selected_user]
                        st.session_state.reminders = [r for r in st.session_state.reminders if r["user"] != selected_user]
                        save_data()
                        st.warning(f"🗑 User {selected_user} deleted successfully!")
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("📅 Task Management", expanded=False):
            if not df_all.empty and 'Employee' in df_all.columns:
                st.markdown("### 📅 View and Filter Tasks")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    users = df_all['Employee'].unique().tolist()
                    selected_user = st.selectbox("Employee", options=["All"] + users, key="filter_employee")
                with col2:
                    start = st.date_input("Start Date", value=datetime.now(tz) - timedelta(days=7), key="filter_start")
                with col3:
                    end = st.date_input("End Date", value=datetime.now(tz), key="filter_end")
                with col4:
                    category = st.selectbox("Category", options=["All"] + CATEGORIES, key="filter_category")
                priority = st.selectbox("Priority", options=["All"] + TASK_PRIORITIES, key="filter_priority")
                
                filtered_df = df_all
                if selected_user != "All":
                    filtered_df = filtered_df[filtered_df['Employee'] == selected_user]
                if category != "All":
                    filtered_df = filtered_df[filtered_df['Category'] == category]
                if priority != "All":
                    filtered_df = filtered_df[filtered_df['Priority'] == priority]
                filtered_df = filtered_df[(filtered_df['Date'] >= start.strftime('%Y-%m-%d')) & (filtered_df['Date'] <= end.strftime('%Y-%m-%d'))]
                st.dataframe(filtered_df.drop(columns=['TaskID', 'Attachment'], errors='ignore'))

                st.markdown("### 📥 Export Filtered Tasks")
                file_name = f"tasks_{selected_user}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.xlsx"
                if category != "All":
                    file_name = f"tasks_{selected_user}_{category}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.xlsx"
                if priority != "All":
                    file_name = f"tasks_{selected_user}_{category}_{priority}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.xlsx"
                data, file_name = export_to_excel(filtered_df, "Filtered_Tasks", file_name)
                if data:
                    st.download_button(
                        label="📥 Download Filtered Tasks",
                        data=data,
                        file_name=file_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error("⚠️ Failed to generate Excel file.")

                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown("### ✏️ Edit Any Task")
                st.markdown("<div class='edit-section'>", unsafe_allow_html=True)
                task_dict = {f"{row['Description'][:30]}... ({row['Date']} | {row['Category']} | {row['Status']} | {row['Employee'].capitalize()})": row["TaskID"] for _, row in df_all.iterrows()}
                selected_label = st.selectbox("📋 Select Task to Edit", list(task_dict.keys()), key="admin_select_task")
                selected_id = task_dict[selected_label]
                selected_task = df_all[df_all["TaskID"] == selected_id].iloc[0]

                if isinstance(selected_task.get("Attachment"), dict):
                    st.markdown("### 📎 Current Attachment")
                    attachment = selected_task["Attachment"]
                    st.markdown(f"<div class='attachment-info'>File: {attachment.get('name', 'Unknown')} ({attachment.get('type', 'Unknown')})</div>", unsafe_allow_html=True)
                    if attachment.get("type", "").startswith("image/"):
                        st.image(base64.b64decode(attachment["data"]), caption=attachment.get("name", "Image"), width=200, use_column_width=False)
                    st.download_button(
                        label=f"📎 Download {attachment.get('name', 'File')}",
                        data=base64.b64decode(attachment["data"]),
                        file_name=attachment.get("name", "attachment"),
                        mime=attachment.get("type", "application/octet-stream"),
                        key=f"admin_download_attachment_{selected_id}"
                    )

                with st.form("admin_edit_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        shift = st.selectbox("🕒 Shift", SHIFTS, index=SHIFTS.index(selected_task["Shift"]), key="admin_edit_shift")
                        date = st.date_input("📅 Date", datetime.strptime(selected_task["Date"], '%Y-%m-%d'), key="admin_edit_date")
                        dept = st.selectbox("🏢 Department", DEPARTMENTS, index=DEPARTMENTS.index(selected_task["Department"]), key="admin_edit_dept")
                    with col2:
                        cat = st.selectbox("📂 Category", CATEGORIES, index=CATEGORIES.index(selected_task["Category"]), key="admin_edit_cat")
                        stat = st.selectbox("📌 Status", TASK_STATUSES, index=TASK_STATUSES.index(selected_task["Status"]), key="admin_edit_stat")
                        prio = st.selectbox("⚠️ Priority", TASK_PRIORITIES, index=TASK_PRIORITIES.index(selected_task["Priority"]), key="admin_edit_prio")
                    desc = st.text_area("🗒 Description", selected_task["Description"], height=120, key="admin_edit_desc")
                    attachment = st.file_uploader("📎 Upload New File (Optional)", type=["png", "jpg", "jpeg", "pdf", "xlsx", "xls"], key="admin_edit_attachment")
                    set_reminder = st.checkbox("🔔 Set Reminder for Not Started Task", key="admin_edit_reminder") if stat == "⏳ Not Started" else False
                    reminder_date = st.date_input("📅 Reminder Due Date", value=datetime.now(tz) + timedelta(days=1), key="admin_edit_reminder_date") if set_reminder else None

                    submitted = st.form_submit_button("💾 Save Changes")
                    if submitted:
                        if desc.strip():
                            for i, t in enumerate(st.session_state.timesheet):
                                if t["TaskID"] == selected_id:
                                    st.session_state.timesheet[i] = {
                                        "TaskID": selected_id,
                                        "Employee": selected_task["Employee"],
                                        "Date": date.strftime('%Y-%m-%d'),
                                        "Day": calendar.day_name[date.weekday()],
                                        "Shift": shift,
                                        "Department": dept,
                                        "Category": cat,
                                        "Status": stat,
                                        "Priority": prio,
                                        "Description": desc,
                                        "Submitted": datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'),
                                        "Attachment": t.get("Attachment")
                                    }
                                    if attachment:
                                        if attachment.size > 5 * 1024 * 1024:
                                            st.error("⚠️ File size exceeds 5MB limit!")
                                            st.stop()
                                        else:
                                            st.session_state.timesheet[i]["Attachment"] = {
                                                "name": attachment.name,
                                                "data": base64.b64encode(attachment.read()).decode('utf-8'),
                                                "type": attachment.type
                                            }
                                    if set_reminder and stat == "⏳ Not Started":
                                        st.session_state.reminders = [r for r in st.session_state.reminders if r["task_id"] != selected_id]
                                        st.session_state.reminders.append({
                                            "user": selected_task["Employee"],
                                            "task_id": selected_id,
                                            "task_desc": desc,
                                            "date": datetime.now(tz).strftime('%Y-%m-%d'),
                                            "due_date": reminder_date.strftime('%Y-%m-%d')
                                        })
                                    save_data()
                                    st.success("✅ Task updated successfully!")
                                    st.rerun()
                        else:
                            st.error("⚠️ Description cannot be empty!")

                with st.form("admin_delete_form"):
                    st.warning("⚠️ This action cannot be undone!")
                    delete_confirmed = st.checkbox("I confirm I want to delete this task", key="admin_confirm_delete")
                    submitted_delete = st.form_submit_button("🗑 Delete Task", type="primary", help="Delete selected task")
                    if submitted_delete and delete_confirmed:
                        st.session_state.timesheet = [t for t in st.session_state.timesheet if t["TaskID"] != selected_id]
                        st.session_state.reminders = [r for r in st.session_state.reminders if r["task_id"] != selected_id]
                        save_data()
                        st.warning("🗑 Task deleted successfully!")
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("ℹ️ No tasks recorded yet.")

        with st.expander("📊 Statistics & Logs", expanded=False):
            st.markdown("### 📜 Login Activity Log")
            st.dataframe(pd.DataFrame(st.session_state.login_log))

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("### 📊 Employee Statistics")
            stats_df = df_all.groupby('Employee').agg({
                'TaskID': 'count',
                'Status': lambda x: (x == '✅ Completed').sum()
            }).rename(columns={'TaskID': 'Total Tasks', 'Status': 'Completed Tasks'})
            stats_df['Completion Rate'] = (stats_df['Completed Tasks'] / stats_df['Total Tasks'] * 100).round(2)
            st.dataframe(stats_df)

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("### 📥 Export All Tasks")
            data, file_name = export_to_excel(df_all, "All_Tasks", "all_tasks_export.xlsx")
            if data:
                st.download_button(
                    label="📥 Download All Tasks",
                    data=data,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("⚠️ Failed to generate Excel file.")

# --- Main App Logic ---
if __name__ == "__main__":
    initialize_session()
    authenticate_user()

    st.sidebar.title("🔒 Session")
    if st.sidebar.button("Logout", key="logout_button"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_role_type = None
        st.session_state.reminders = []
        st.session_state.selected_tab = "Dashboard"
        save_data()
        st.rerun()

    # Only proceed if logged in
    if st.session_state.logged_in:
        df_all = pd.DataFrame(st.session_state.timesheet)
        df_user = df_all[df_all['Employee'] == st.session_state.user_role] if not df_all.empty and 'Employee' in df_all.columns else pd.DataFrame()
        render_alerts(df_user, df_all)
        render_sidebar_stats()
        display_df = df_user if st.session_state.user_role_type == "Employee" else df_all
        render_header()

        if st.session_state.selected_tab == "Dashboard":
            st.header("🏠 Dashboard")
            render_analytics(display_df)
            render_all_uploaded_files(df_all)
            render_admin_download_tasks()
            auto_export_weekly()
        elif st.session_state.selected_tab == "Add Task":
            render_add_task()
        elif st.session_state.selected_tab == "Edit/Delete Task":
            render_edit_delete_task(display_df)
        elif st.session_state.selected_tab == "Employee Work":
            render_employee_work()
        elif st.session_state.selected_tab == "Admin Panel":
            if st.session_state.user_role_type == "Admin":
                render_admin_panel()
            else:
                st.error("🚫 Access restricted to Admins only.")
                st.session_state.selected_tab = "Dashboard"
                st.rerun()
        elif st.session_state.selected_tab == "Settings":
            render_settings()
        elif st.session_state.selected_tab == "Download Tasks":
            render_download_tasks()

        st.markdown(
            f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now(pytz.timezone('Asia/Riyadh')).strftime('%A, %B %d, %Y - %I:%M %p')}</footer>",
            unsafe_allow_html=True
        )
