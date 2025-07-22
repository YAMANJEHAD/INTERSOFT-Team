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

# --- Modern Dark Theme CSS ---
st.markdown("""
<style>
:root {
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --secondary: #10b981;
    --danger: #ef4444;
    --warning: #f59e0b;
    --info: #3b82f6;
    --dark: #0f172a;
    --darker: #020617;
    --light: #f8fafc;
    --lighter: #f1f5f9;
    --gray: #64748b;
    --gray-dark: #334155;
    --success: #10b981;
}

* {
    transition: all 0.2s ease;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--darker);
    color: var(--lighter);
    scroll-behavior: smooth;
}

h1, h2, h3, h4, h5, h6 {
    font-weight: 700;
    color: var(--light);
    margin-bottom: 0.75rem;
}

/* Main container styling */
.main-container {
    background-color: var(--dark);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    border: 1px solid var(--gray-dark);
}

/* Card styling */
.card {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    border: 1px solid var(--gray-dark);
}

.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 15px rgba(0,0,0,0.2);
}

/* Header styling */
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    margin-bottom: 2rem;
    border-bottom: 1px solid var(--gray-dark);
}

.company-name {
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--primary);
    letter-spacing: 0.5px;
}

.user-info {
    text-align: right;
}

.greeting {
    font-size: 1rem;
    color: var(--gray);
}

.current-time {
    font-size: 0.9rem;
    color: var(--secondary);
    font-weight: 600;
}

/* Navigation */
.nav-tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid var(--gray-dark);
    padding-bottom: 0.5rem;
}

.nav-tab {
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    background-color: var(--dark);
    color: var(--gray);
    font-weight: 600;
    cursor: pointer;
    border: 1px solid transparent;
}

.nav-tab:hover {
    background-color: var(--gray-dark);
    color: var(--light);
}

.nav-tab.active {
    background-color: var(--primary-dark);
    color: white;
    border-color: var(--primary);
}

/* Form elements */
.stTextInput>div>div>input, 
.stTextArea>div>textarea,
.stSelectbox>div>select,
.stDateInput>div>input,
.stFileUploader>div>section {
    background-color: var(--dark) !important;
    border: 1px solid var(--gray-dark) !important;
    color: var(--light) !important;
    border-radius: 8px !important;
}

.stButton>button {
    background-color: var(--primary) !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    border: none !important;
    font-weight: 600 !important;
}

.stButton>button:hover {
    background-color: var(--primary-dark) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(99, 102, 241, 0.3);
}

.stButton>button.delete-button {
    background-color: var(--danger) !important;
}

.stButton>button.delete-button:hover {
    background-color: #dc2626 !important;
}

/* Dataframe styling */
.stDataFrame {
    border-radius: 8px;
    overflow: hidden;
}

.stDataFrame th {
    background-color: var(--primary-dark) !important;
    color: white !important;
}

.stDataFrame tr:nth-child(even) {
    background-color: var(--dark) !important;
}

.stDataFrame tr:nth-child(odd) {
    background-color: var(--gray-dark) !important;
}

.stDataFrame tr:hover {
    background-color: #1e3a8a !important;
}

/* Alert boxes */
.alert {
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    font-weight: 600;
}

.alert-warning {
    background-color: rgba(234, 179, 8, 0.2);
    border-left: 4px solid var(--warning);
    color: var(--warning);
}

.alert-danger {
    background-color: rgba(239, 68, 68, 0.2);
    border-left: 4px solid var(--danger);
    color: var(--danger);
}

.alert-success {
    background-color: rgba(16, 185, 129, 0.2);
    border-left: 4px solid var(--success);
    color: var(--success);
}

/* Stats cards */
.stats-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border-radius: 10px;
    padding: 1.5rem;
    text-align: center;
    border-left: 4px solid var(--primary);
}

.stat-card .value {
    font-size: 2rem;
    font-weight: 800;
    color: var(--primary);
    margin-bottom: 0.5rem;
}

.stat-card .label {
    font-size: 0.9rem;
    color: var(--gray);
}

/* Sidebar */
.stSidebar {
    background-color: var(--dark) !important;
    border-right: 1px solid var(--gray-dark) !important;
}

/* Charts */
.plotly-chart {
    border-radius: 8px;
    overflow: hidden;
}

/* Utility classes */
.mb-3 { margin-bottom: 1rem !important; }
.mb-4 { margin-bottom: 1.5rem !important; }
.mt-3 { margin-top: 1rem !important; }
.text-muted { color: var(--gray) !important; }
.text-center { text-align: center !important; }

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-fade {
    animation: fadeIn 0.5s ease-out;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .stats-container {
        grid-template-columns: 1fr;
    }
    
    .header {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .user-info {
        text-align: left;
        margin-top: 1rem;
    }
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
        st.session_state.user_role_type = None
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
        with st.container():
            st.markdown("<div class='main-container animate-fade'>", unsafe_allow_html=True)
            st.markdown("<h1 class='text-center mb-4'>🔐 INTERSOFT Dashboard Login</h1>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                with st.form("login_form"):
                    username = st.text_input("Username", key="login_username")
                    password = st.text_input("Password", type="password", key="login_password")
                    
                    if st.form_submit_button("Login", use_container_width=True):
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
            st.markdown("</div>", unsafe_allow_html=True)
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
                'bold': True, 'font_color': 'white', 'bg_color': '#4f46e5',
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

    st.markdown(f"<h3 class='mb-3'>📊 Task Statistics for {date_str}</h3>", unsafe_allow_html=True)
    st.markdown("<div class='stats-container animate-fade'>", unsafe_allow_html=True)
    
    stats = [
        {"label": "Total Tasks", "value": total_tasks, "color": "var(--primary)"},
        {"label": "Completed", "value": completed_tasks, "color": "var(--success)"},
        {"label": "In Progress", "value": in_progress_tasks, "color": "var(--warning)"},
        {"label": "Not Started", "value": not_started_tasks, "color": "var(--danger)"}
    ]
    
    for stat in stats:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='value' style='color: {stat["color"]}'>{stat["value"]}</div>
            <div class='label'>{stat["label"]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- Render Analytics in Dashboard ---
def render_analytics(display_df):
    if not display_df.empty:
        st.markdown("<h3 class='mb-3'>📈 Task Analytics by Date</h3>", unsafe_allow_html=True)
        tz = pytz.timezone("Asia/Riyadh")
        today_str = datetime.now(tz).strftime('%Y-%m-%d')
        unique_dates = sorted(display_df['Date'].unique(), reverse=True)
        
        for date_str in unique_dates:
            date_df = display_df[display_df['Date'] == date_str]
            
            with st.expander(f"📅 {date_str} ({calendar.day_name[pd.to_datetime(date_str).weekday()]})", expanded=(date_str == today_str)):
                st.markdown("<div class='main-container animate-fade'>", unsafe_allow_html=True)
                render_dashboard_stats(date_df, date_str)
                
                col1, col2 = st.columns(2)
                with col1:
                    with st.container():
                        st.markdown("<div class='card'>", unsafe_allow_html=True)
                        fig_hist = px.histogram(
                            date_df,
                            x="Status",
                            title="Task Status Distribution",
                            color="Status",
                            color_discrete_sequence=['#ef4444', '#f59e0b', '#10b981'],
                            template="plotly_dark",
                            height=300
                        )
                        fig_hist.update_layout(
                            title_font_size=14,
                            xaxis_title=None,
                            yaxis_title="Number of Tasks",
                            showlegend=True,
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        st.plotly_chart(fig_hist, use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                with col2:
                    with st.container():
                        st.markdown("<div class='card'>", unsafe_allow_html=True)
                        fig_pie = px.pie(
                            date_df,
                            names="Category",
                            title="Category Distribution",
                            color_discrete_sequence=px.colors.sequential.Viridis,
                            template="plotly_dark",
                            height=300
                        )
                        fig_pie.update_traces(
                            hovertemplate="Category: %{label}<br>Tasks: %{value} (%{percent})",
                            textinfo="percent+label"
                        )
                        fig_pie.update_layout(
                            title_font_size=14,
                            showlegend=True,
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<h4 class='mb-3'>📋 Tasks List</h4>", unsafe_allow_html=True)
                st.dataframe(date_df.drop(columns=['TaskID', 'Attachment'], errors='ignore'))

                data, file_name = export_to_excel(date_df, f"Tasks_{date_str}", f"tasks_{date_str}.xlsx")
                if data:
                    st.download_button(
                        f"📥 Download Tasks for {date_str}",
                        data=data,
                        file_name=file_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown("<div class='alert alert-warning'>ℹ️ No tasks available for display.</div>", unsafe_allow_html=True)

# --- Render All Uploaded Files ---
def render_all_uploaded_files(df_all):
    st.markdown("<h3 class='mb-3'>📎 All Uploaded Files</h3>", unsafe_allow_html=True)
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
            with st.container():
                st.markdown("<div class='main-container animate-fade'>", unsafe_allow_html=True)
                for idx, row in attachments_df.iterrows():
                    with st.container():
                        st.markdown("<div class='card'>", unsafe_allow_html=True)
                        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                        col1.write(f"**{row['File Name']}**")
                        col2.write(f"`{row['File Type']}`")
                        col3.write(f"👤 {row['Employee']}")
                        col4.write(f"📅 {row['Task Date']}")
                        if row["Data"]:
                            col5.download_button(
                                label="📎 Download",
                                data=base64.b64decode(row["Data"]),
                                file_name=row["File Name"],
                                mime=row["File Type"],
                                key=f"download_all_attachment_{row['TaskID']}_{idx}",
                                use_container_width=True
                            )
                        st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='alert alert-warning'>ℹ️ No files uploaded yet.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='alert alert-warning'>ℹ️ No tasks with attachments found.</div>", unsafe_allow_html=True)

# --- Settings Popup ---
def render_settings():
    st.markdown("<h2 class='mb-4'>⚙️ User Settings</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='main-container animate-fade'>", unsafe_allow_html=True)
        user = st.session_state.user_role
        current_profile = USER_PROFILE.get(user, {"name": "", "email": "", "picture": None})
        
        tab1, tab2 = st.tabs(["👤 Profile", "🔑 Security"])
        
        with tab1:
            st.markdown("<h3 class='mb-3'>User Profile</h3>", unsafe_allow_html=True)
            with st.form("profile_form"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Name", value=current_profile["name"], key="profile_name")
                    email = st.text_input("Email", value=current_profile["email"], key="profile_email")
                with col2:
                    if current_profile["picture"]:
                        st.image(current_profile["picture"], width=100, caption="Profile Picture", output_format="PNG")
                    picture = st.file_uploader("Upload Profile Picture", type=["png", "jpg", "jpeg"], key="profile_picture")
                
                submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)
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

        with tab2:
            st.markdown("<h3 class='mb-3'>Change Password</h3>", unsafe_allow_html=True)
            with st.form("password_form"):
                current_password = st.text_input("Current Password", type="password", key="current_password")
                new_password = st.text_input("New Password", type="password", key="new_password")
                confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_password")
                
                submitted = st.form_submit_button("🔄 Change Password", use_container_width=True)
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
        
        st.markdown("</div>", unsafe_allow_html=True)

# --- Download Tasks ---
def render_download_tasks():
    st.markdown("<h2 class='mb-4'>⬇️ Download My Tasks</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='main-container animate-fade'>", unsafe_allow_html=True)
        tz = pytz.timezone("Asia/Riyadh")
        current_user = st.session_state.user_role
        user_tasks = df_all[df_all['Employee'] == current_user] if not df_all.empty and 'Employee' in df_all.columns else pd.DataFrame()
        
        if not user_tasks.empty:
            col1, col2 = st.columns(2)
            with col1:
                start = st.date_input("Start Date", value=datetime.now(tz) - timedelta(days=7), key="download_start")
            with col2:
                end = st.date_input("End Date", value=datetime.now(tz), key="download_end")
            
            col3, col4 = st.columns(2)
            with col3:
                category = st.selectbox("Category", options=["All"] + CATEGORIES, key="download_category")
            with col4:
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
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            else:
                st.error("⚠️ Failed to generate Excel file.")
        else:
            st.markdown("<div class='alert alert-warning'>ℹ️ No tasks available for your account.</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# --- Admin Download Other Users' Tasks ---
def render_admin_download_tasks():
    if st.session_state.user_role_type == "Admin":
        st.markdown("<h3 class='mb-3'>🛠 Admin Panel: Download Employee Tasks</h3>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div class='main-container animate-fade'>", unsafe_allow_html=True)
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
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                        else:
                            st.error("⚠️ Failed to generate Excel file.")
                    else:
                        st.markdown(f"<div class='alert alert-warning'>ℹ️ No tasks found for {selected_employee}.</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='alert alert-warning'>ℹ️ No employees with tasks found.</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='alert alert-warning'>ℹ️ No tasks recorded yet.</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

# --- Render Header ---
def render_header():
    tz = pytz.timezone("Asia/Riyadh")
    current_time = datetime.now(tz).strftime('%I:%M %p')
    current_date = datetime.now(tz).strftime('%A, %B %d, %Y')
    
    st.markdown("""
    <div class='header animate-fade'>
        <div class='company-name'>INTERSOFT FLM Dashboard</div>
        <div class='user-info'>
            <div class='greeting'>Welcome, <strong>{}</strong> ({})</div>
            <div class='current-time'>{} • {}</div>
        </div>
    </div>
    """.format(
        st.session_state.user_role.capitalize(),
        st.session_state.user_role_type,
        current_time,
        current_date
    ), unsafe_allow_html=True)

    # Navigation tabs
    tabs = [
        ("Dashboard", "🏠 Dashboard"),
        ("Add Task", "➕ Add Task"),
        ("Edit/Delete Task", "✏️ Edit/Delete Task"),
        ("Employee Work", "👥 Employee Work"),
        ("Download Tasks", "⬇️ Download My Tasks"),
        ("Settings", "⚙️ Settings")
    ]
    
    if st.session_state.user_role_type == "Admin":
        tabs.insert(4, ("Admin Panel", "🛠 Admin Panel"))

    st.markdown("<div class='nav-tabs animate-fade'>", unsafe_allow_html=True)
    for tab in tabs:
        if st.session_state.selected_tab == tab[0]:
            st.markdown(f"<div class='nav-tab active'>{tab[1]}</div>", unsafe_allow_html=True)
        else:
            if st.button(tab[1], key=f"nav_{tab[0]}"):
                st.session_state.selected_tab = tab[0]
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- Render Sidebar Stats ---
def render_sidebar_stats():
    tz = pytz.timezone("Asia/Riyadh")
    today_str = datetime.now(tz).strftime('%Y-%m-%d')
    
    st.sidebar.markdown(f"<h3 class='mb-3'>👤 Today's Stats ({today_str})</h3>", unsafe_allow_html=True)
    
    df_all = pd.DataFrame(st.session_state.timesheet)
    if not df_all.empty and 'Employee' in df_all.columns:
        today_df = df_all[df_all['Date'] == today_str]
        employees = sorted(today_df['Employee'].unique()) if not today_df.empty else []
        
        if employees:
            for employee in employees:
                emp_df = today_df[today_df['Employee'] == employee]
                emp_total = len(emp_df)
                emp_completed = emp_df[emp_df['Status'] == '✅ Completed'].shape[0]
                
                with st.sidebar.container():
                    st.markdown(f"""
                    <div class='card'>
                        <strong>{employee.capitalize()}</strong>
                        <div class='text-muted'>Total: {emp_total} • Completed: {emp_completed}</div>
                        <div class='mt-3' style='height: 6px; background: var(--gray-dark); border-radius: 3px;'>
                            <div style='width: {emp_completed/emp_total*100 if emp_total else 0}%; height: 100%; background: var(--success); border-radius: 3px;'></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.sidebar.markdown(f"<div class='alert alert-warning'>ℹ️ No tasks recorded for today.</div>", unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<div class='alert alert-warning'>ℹ️ No tasks recorded yet.</div>", unsafe_allow_html=True)

# --- Render Alerts in Sidebar ---
def render_alerts(df_user, df_all):
    tz = pytz.timezone("Asia/Riyadh")
    today_str = datetime.now(tz).strftime('%Y-%m-%d')
    
    alerts = []
    
    # Check for user's today tasks
    if hasattr(st.session_state, 'user_role_type') and st.session_state.user_role_type is not None:
        if st.session_state.user_role_type != "Admin":
            if df_user.empty or today_str not in df_user['Date'].values:
                alerts.append({
                    "type": "warning",
                    "message": "⚠️ You haven't submitted any tasks for today!"
                })
            
            # Supervisor alerts
            if st.session_state.user_role_type == "Supervisor":
                users = list(set(df_all['Employee'].unique()) if not df_all.empty and 'Employee' in df_all.columns else []
                for user in USERS.keys():
                    if user.lower() not in users or not any(df_all[df_all['Employee'] == user.lower()]['Date'] == today_str):
                        if USERS[user.lower()]["role"] != "Admin":
                            alerts.append({
                                "type": "danger",
                                "message": f"🔔 Alert: <b>{user.capitalize()}</b> has not submitted a task today!"
                            })

            # Reminders
            try:
                reminders = st.session_state.reminders
            except AttributeError:
                st.session_state.reminders = []
                reminders = st.session_state.reminders
            
            for reminder in reminders:
                if reminder["user"] == st.session_state.user_role and reminder["date"] == today_str:
                    alerts.append({
                        "type": "warning",
                        "message": f"🔔 Reminder: Task '{reminder['task_desc'][:30]}...' is still Not Started! Due: {reminder['due_date']}"
                    })
    
    # Display alerts
    if alerts:
        st.sidebar.markdown("<h3 class='mb-3'>🔔 Alerts</h3>", unsafe_allow_html=True)
        for alert in alerts:
            st.sidebar.markdown(f"""
            <div class='alert alert-{alert["type"]} animate-fade'>
                {alert["message"]}
            </div>
            """, unsafe_allow_html=True)

# --- Add Task ---
def render_add_task():
    st.markdown("<h2 class='mb-4'>➕ Add New Task</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='main-container animate-fade'>", unsafe_allow_html=True)
        tz = pytz.timezone("Asia/Riyadh")
        
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
            
            if status == "⏳ Not Started":
                set_reminder = st.checkbox("🔔 Set Reminder for Not Started Task", key="add_reminder")
                if set_reminder:
                    reminder_date = st.date_input("📅 Reminder Due Date", value=datetime.now(tz) + timedelta(days=1), key="add_reminder_date")
            
            submitted = st.form_submit_button("✅ Submit Task", use_container_width=True)
            
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
                    
                    if status == "⏳ Not Started" and set_reminder:
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
        
        st.markdown("</div>", unsafe_allow_html=True)

# --- Edit/Delete Task ---
def render_edit_delete_task(display_df):
    st.markdown("<h2 class='mb-4'>✏️ Edit/Delete Task</h2>", unsafe_allow_html=True)
    
    if not display_df.empty:
        with st.container():
            st.markdown("<div class='main-container animate-fade'>", unsafe_allow_html=True)
            
            task_dict = {f"{row['Description'][:30]}... ({row['Date']} | {row['Category']} | {row['Status']} | {row['Employee'].capitalize()})": row["TaskID"] for _, row in display_df.iterrows()}
            selected_label = st.selectbox("📋 Select Task", list(task_dict.keys()), key="select_task")
            selected_id = task_dict[selected_label]
            selected_task = display_df[display_df["TaskID"] == selected_id].iloc[0]
            
            # Display current attachment if exists
            if isinstance(selected_task.get("Attachment"), dict):
                st.markdown("<h4 class='mb-3'>📎 Current Attachment</h4>", unsafe_allow_html=True)
                attachment = selected_task["Attachment"]
                
                with st.container():
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    col1, col2 = st.columns([3, 1])
                    col1.markdown(f"""
                    <div>
                        <strong>{attachment.get('name', 'Unknown')}</strong>
                        <div class='text-muted'>{attachment.get('type', 'Unknown')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if attachment.get("data"):
                        col2.download_button(
                            label="📎 Download",
                            data=base64.b64decode(attachment["data"]),
                            file_name=attachment.get("name", "attachment"),
                            mime=attachment.get("type", "application/octet-stream"),
                            key=f"download_attachment_{selected_id}",
                            use_container_width=True
                        )
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Edit form
            with st.form("edit_form"):
                st.markdown("<h4 class='mb-3'>✏️ Edit Task</h4>", unsafe_allow_html=True)
                
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
                
                if stat == "⏳ Not Started":
                    set_reminder = st.checkbox("🔔 Set Reminder for Not Started Task", key="edit_reminder")
                    if set_reminder:
                        reminder_date = st.date_input("📅 Reminder Due Date", value=datetime.now(pytz.timezone("Asia/Riyadh")) + timedelta(days=1), key="edit_reminder_date")
                
                submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
                
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
                                    "Submitted": datetime.now(pytz.timezone("Asia/Riyadh")).strftime('%Y-%m-%d %H:%M:%S'),
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
                                
                                if stat == "⏳ Not Started" and set_reminder:
                                    st.session_state.reminders = [r for r in st.session_state.reminders if r["task_id"] != selected_id]
                                    st.session_state.reminders.append({
                                        "user": selected_task["Employee"],
                                        "task_id": selected_id,
                                        "task_desc": desc,
                                        "date": datetime.now(pytz.timezone("Asia/Riyadh")).strftime('%Y-%m-%d'),
                                        "due_date": reminder_date.strftime('%Y-%m-%d')
                                    })
                                
                                save_data()
                                st.success("✅ Task updated successfully!")
                                st.rerun()
                    else:
                        st.error("⚠️ Description cannot be empty!")
            
            # Delete form
            with st.form("delete_form"):
                st.markdown("<h4 class='mb-3'>🗑 Delete Task</h4>", unsafe_allow_html=True)
                st.markdown("<div class='alert alert-danger'>⚠️ This action cannot be undone!</div>", unsafe_allow_html=True)
                
                delete_confirmed = st.checkbox("I confirm I want to delete this task", key="confirm_delete")
                submitted_delete = st.form_submit_button("🗑 Delete Task", type="primary", use_container_width=True)
                
                if submitted_delete and delete_confirmed:
                    if selected_task["Employee"] == st.session_state.user_role or st.session_state.user_role_type == "Admin":
                        st.session_state.timesheet = [t for t in st.session_state.timesheet if t["TaskID"] != selected_id]
                        st.session_state.reminders = [r for r in st.session_state.reminders if r["task_id"] != selected_id]
                        save_data()
                        st.success("🗑 Task deleted successfully!")
                        st.rerun()
                    else:
                        st.error("⚠️ You can only delete your own tasks or tasks as an Admin.")
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='alert alert-warning'>ℹ️ No tasks available to edit.</div>", unsafe_allow_html=True)

# --- Employee Work Tab ---
def render_employee_work():
    st.markdown("<h2 class='mb-4'>👥 Employee Work</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='main-container animate-fade'>", unsafe_allow_html=True)
        tz = pytz.timezone("Asia/Riyadh")
        df_all = pd.DataFrame(st.session_state.timesheet)
        
        if not df_all.empty and 'Employee' in df_all.columns:
            st.markdown("<h3 class='mb-3'>📅 View Employee Tasks</h3>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                users = df_all['Employee'].unique().tolist()
                selected_user = st.selectbox("Employee", options=["All"] + users, key="employee_work_filter")
            with col2:
                col3, col4 = st.columns(2)
                with col3:
                    start = st.date_input("Start Date", value=datetime.now(tz) - timedelta(days=7), key="employee_work_start")
                with col4:
                    end = st.date_input("End Date", value=datetime.now(tz), key="employee_work_end")
            
            filtered_df = df_all
            if selected_user != "All":
                filtered_df = filtered_df[filtered_df['Employee'] == selected_user]
            filtered_df = filtered_df[(filtered_df['Date'] >= start.strftime('%Y-%m-%d')) & (filtered_df['Date'] <= end.strftime('%Y-%m-%d'))]
            
            st.dataframe(filtered_df.drop(columns=['TaskID', 'Attachment'], errors='ignore'))
            
            # Export button
            if not filtered_df.empty:
                file_name = f"employee_tasks_{selected_user}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.xlsx"
                data, file_name = export_to_excel(filtered_df, "Employee_Tasks", file_name)
                if data:
                    st.download_button(
                        label="📥 Download Tasks",
                        data=data,
                        file_name=file_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
        else:
            st.markdown("<div class='alert alert-warning'>ℹ️ No tasks recorded yet.</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# --- Admin Panel ---
def render_admin_panel():
    if st.session_state.user_role_type == "Admin":
        st.markdown("<h2 class='mb-4'>🛠 Admin Panel</h2>", unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["👤 User Management", "📊 Task Management", "📜 Activity Logs"])
        
        with tab1:
            with st.container():
                st.markdown("<div class='main-container animate-fade'>", unsafe_allow_html=True)
                st.markdown("<h3 class='mb-3'>👤 Manage Users</h3>", unsafe_allow_html=True)
                
                # Add new user
                with st.expander("➕ Add New User", expanded=True):
                    with st.form("add_user_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_username = st.text_input("Username", key="new_username")
                            new_password = st.text_input("Password", type="password", key="new_password")
                            new_role = st.selectbox("Role", ROLES, key="new_role")
                        with col2:
                            new_name = st.text_input("Name", key="new_name")
                            new_email = st.text_input("Email", key="new_email")
                        
                        submitted = st.form_submit_button("➕ Add User", use_container_width=True)
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
                
                # Change user role
                with st.expander("🔄 Change User Role", expanded=False):
                    with st.form("change_role_form"):
                        users = [u for u in USERS.keys() if u != st.session_state.user_role]
                        selected_user = st.selectbox("Select User", users, key="change_role_user")
                        new_role = st.selectbox("New Role", ROLES, key="change_role_select")
                        role_confirmed = st.checkbox("I confirm I want to change this user's role", key="confirm_role_change")
                        
                        submitted_role = st.form_submit_button("🔄 Change Role", use_container_width=True)
                        if submitted_role and role_confirmed:
                            if selected_user == st.session_state.user_role:
                                st.error("⚠️ Cannot change your own role!")
                            else:
                                USERS[selected_user]["role"] = new_role
                                save_data()
                                st.success(f"✅ Role for {selected_user} changed to {new_role}!")
                                st.rerun()
                
                # Delete user
                with st.expander("🗑 Delete User", expanded=False):
                    with st.form("delete_user_form"):
                        users = [u for u in USERS.keys() if u != st.session_state.user_role]
                        selected_user = st.selectbox("Select User to Delete", users, key="delete_user_select")
                        delete_confirmed = st.checkbox("I confirm I want to delete this user", key="confirm_user_delete")
                        
                        submitted_delete = st.form_submit_button("🗑 Delete User", type="primary", use_container_width=True)
                        if submitted_delete and delete_confirmed:
                            if selected_user == st.session_state.user_role:
                                st.error("⚠️ Cannot delete your own account!")
                            else:
                                del USERS[selected_user]
                                del USER_PROFILE[selected_user]
                                st.session_state.timesheet = [t for t in st.session_state.timesheet if t["Employee"] != selected_user]
                                st.session_state.reminders = [r for r in st.session_state.reminders if r["user"] != selected_user]
                                save_data()
                                st.success(f"🗑 User {selected_user} deleted successfully!")
                                st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        with tab2:
            with st.container():
                st.markdown("<div class='main-container animate-fade'>", unsafe_allow_html=True)
                st.markdown("<h3 class='mb-3'>📊 Task Management</h3>", unsafe_allow_html=True)
                
                df_all = pd.DataFrame(st.session_state.timesheet)
                if not df_all.empty and 'Employee' in df_all.columns:
                    # Task filtering
                    st.markdown("<h4 class='mb-3'>🔍 Filter Tasks</h4>", unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        users = df_all['Employee'].unique().tolist()
                        selected_user = st.selectbox("Employee", options=["All"] + users, key="filter_employee")
                    with col2:
                        start = st.date_input("Start Date", value=datetime.now(pytz.timezone("Asia/Riyadh")) - timedelta(days=7), key="filter_start")
                    with col3:
                        end = st.date_input("End Date", value=datetime.now(pytz.timezone("Asia/Riyadh")), key="filter_end")
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
                    
                    # Export filtered tasks
                    if not filtered_df.empty:
                        st.markdown("<h4 class='mb-3'>📥 Export Filtered Tasks</h4>", unsafe_allow_html=True)
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
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                        else:
                            st.error("⚠️ Failed to generate Excel file.")
                
                else:
                    st.markdown("<div class='alert alert-warning'>ℹ️ No tasks recorded yet.</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        with tab3:
            with st.container():
                st.markdown("<div class='main-container animate-fade'>", unsafe_allow_html=True)
                st.markdown("<h3 class='mb-3'>📜 Activity Logs</h3>", unsafe_allow_html=True)
                
                # Login logs
                st.markdown("<h4 class='mb-3'>🔐 Login Activity</h4>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(st.session_state.login_log))
                
                # Employee statistics
                st.markdown("<h4 class='mb-3'>📊 Employee Statistics</h4>", unsafe_allow_html=True)
                df_all = pd.DataFrame(st.session_state.timesheet)
                if not df_all.empty and 'Employee' in df_all.columns:
                    stats_df = df_all.groupby('Employee').agg({
                        'TaskID': 'count',
                        'Status': lambda x: (x == '✅ Completed').sum()
                    }).rename(columns={'TaskID': 'Total Tasks', 'Status': 'Completed Tasks'})
                    stats_df['Completion Rate'] = (stats_df['Completed Tasks'] / stats_df['Total Tasks'] * 100).round(2)
                    st.dataframe(stats_df)
                
                # Export all data
                st.markdown("<h4 class='mb-3'>📥 Export All Data</h4>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📥 Export All Tasks", use_container_width=True):
                        df_all = pd.DataFrame(st.session_state.timesheet)
                        if not df_all.empty:
                            data, file_name = export_to_excel(df_all, "All_Tasks", "all_tasks_export.xlsx")
                            if data:
                                st.download_button(
                                    label="📥 Download All Tasks",
                                    data=data,
                                    file_name=file_name,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                        else:
                            st.error("⚠️ No tasks to export")
                with col2:
                    if st.button("📥 Export Login Logs", use_container_width=True):
                        df_logs = pd.DataFrame(st.session_state.login_log)
                        if not df_logs.empty:
                            data, file_name = export_to_excel(df_logs, "Login_Logs", "login_logs_export.xlsx")
                            if data:
                                st.download_button(
                                    label="📥 Download Login Logs",
                                    data=data,
                                    file_name=file_name,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                        else:
                            st.error("⚠️ No login logs to export")
                
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("🚫 Access restricted to Admins only.")
        st.session_state.selected_tab = "Dashboard"
        st.rerun()

# --- Main App Logic ---
if __name__ == "__main__":
    initialize_session()
    authenticate_user()

    # Sidebar logout button
    with st.sidebar:
        if st.button("🚪 Logout", use_container_width=True):
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
        
        # Render sidebar components
        render_sidebar_stats()
        render_alerts(df_user, df_all)
        
        # Render main content
        render_header()
        
        if st.session_state.selected_tab == "Dashboard":
            render_analytics(df_user if st.session_state.user_role_type == "Employee" else df_all)
            render_all_uploaded_files(df_all)
            render_admin_download_tasks()
            auto_export_weekly()
        elif st.session_state.selected_tab == "Add Task":
            render_add_task()
        elif st.session_state.selected_tab == "Edit/Delete Task":
            render_edit_delete_task(df_user if st.session_state.user_role_type == "Employee" else df_all)
        elif st.session_state.selected_tab == "Employee Work":
            render_employee_work()
        elif st.session_state.selected_tab == "Admin Panel":
            render_admin_panel()
        elif st.session_state.selected_tab == "Settings":
            render_settings()
        elif st.session_state.selected_tab == "Download Tasks":
            render_download_tasks()

        # Footer
        st.markdown("""
        <div style='text-align: center; margin-top: 3rem; color: var(--gray); font-size: 0.9rem;'>
            INTERSOFT FLM Tracker • v1.0 • {}
        </div>
        """.format(datetime.now(pytz.timezone("Asia/Riyadh")).strftime('%Y-%m-%d %H:%M')), unsafe_allow_html=True)
