
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
import streamlit.components.v1 as components

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
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: radial-gradient(circle at top left, #0f172a, #1e293b);
    color: #f8fafc;
    scroll-behavior: smooth;
}

.top-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0 2.5rem; margin: 1.5rem 0;
    animation: fadeIn 1s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}

.greeting {
    font-size: 1.1rem; font-weight: 600; color: #fcd34d;
    text-align: right; line-height: 1.4;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

.company {
    font-size: 1.4rem; font-weight: 700; color: #ffffff; letter-spacing: 0.5px;
}

.date-box {
    font-size: 1.1rem; font-weight: 600; color: #f8fafc; text-align: center;
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
    padding: 0.75rem 1.5rem; border-radius: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    margin-bottom: 1rem; display: inline-block;
    animation: fadeIn 0.6s ease-in-out;
}

.nav-buttons {
    display: flex; flex-wrap: wrap; gap: 1.3rem; justify-content: center;
    margin: 1.5rem 0; padding: 1rem;
}

.stButton>button {
    background: linear-gradient(135deg, #6d28d9, #e11d48);
    color: white; font-weight: 700; font-size: 1.2rem;
    border-radius: 26px; padding: 0.8rem; min-width: 220px; height: 52px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.4);
    transition: all 0.4s ease; border: 1px solid transparent;
    cursor: pointer; text-align: center;
    display: flex; align-items: center; justify-content: center; gap: 12px;
    animation: bounceIn 0.8s ease-in-out;
}

@keyframes bounceIn {
    0% { transform: scale(0.85); opacity: 0; }
    50% { transform: scale(1.2); opacity: 0.7; }
    100% { transform: scale(1); opacity: 1; }
}

.stButton>button:hover {
    transform: scale(1.15);
    background: linear-gradient(135deg, #8b5cf6, #f43f5e);
    box-shadow: 0 16px 36px rgba(139,92,246,0.5), 0 0 20px rgba(244,63,94,0.4);
    border: 1px solid #93c5fd;
}

.stButton>button:active {
    transform: scale(0.92);
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}

.stButton>button.selected {
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
    transform: scale(1.07);
    box-shadow: 0 14px 34px rgba(30,64,175,0.5);
    font-weight: 800;
    animation: pulseSelected 1.3s infinite;
}

@keyframes pulseSelected {
    0%, 100% { transform: scale(1.07); }
    50% { transform: scale(1.1); }
}

.stButton>button.delete-button {
    background: linear-gradient(135deg, #b91c1c, #ef4444);
}

.stButton>button.delete-button:hover {
    animation: shake 0.7s ease-in-out;
    background: linear-gradient(135deg, #991b1b, #dc2626);
    box-shadow: 0 16px 36px rgba(185,28,28,0.5);
    border: 1px solid #fca5a5;
}

@keyframes shake {
    0% { transform: translateX(0); }
    25% { transform: translateX(-8px); }
    50% { transform: translateX(8px); }
    75% { transform: translateX(-8px); }
    100% { transform: translateX(0); }
}

.overview-box {
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
    padding: 1rem; border-radius: 15px; text-align: center;
    margin: 0.5rem 0; transition: transform 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    animation: zoomIn 0.6s ease-in-out;
}

.overview-box:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 12px 30px rgba(0,0,0,0.4);
}

@keyframes zoomIn {
    from { transform: scale(0.95); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}

.overview-box span {
    font-size: 1.5rem; font-weight: 800; color: #fcd34d;
    display: block;
}

.overview-box small {
    font-size: 0.8rem; color: #e2e8f0;
}

.edit-section {
    background: #1e293b; padding: 2rem; border-radius: 16px; margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    animation: fadeIn 0.5s ease-in-out;
}

.alert-box {
    background: linear-gradient(135deg, #dc2626, #f87171);
    padding: 0.8rem; border-radius: 14px; color: white;
    font-size: 0.9rem; font-weight: 600; max-width: 380px;
    margin: 0.8rem 0; box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    opacity: 0.92; transition: opacity 0.5s ease-out, transform 0.5s ease-out;
    z-index: 1000; animation: slideInDown 0.5s ease-in-out;
}

.alert-box.reminder {
    background: linear-gradient(135deg, #eab308, #facc15);
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
    background: #1e293b; border-radius: 12px; overflow: hidden;
}

.stDataFrame th {
    background-color: #4f81bd; color: white; font-weight: 700;
    padding: 10px; font-size: 1.1rem;
}

.stDataFrame td {
    font-weight: 600; color: #f8fafc; padding: 10px;
    border-bottom: 1px solid #334155; font-size: 1rem;
}

footer {
    text-align: center; color: #94a3b8; padding: 2.5rem 0;
    font-size: 1rem; font-weight: 500;
    animation: fadeIn 1s ease-in-out;
}

.profile-picture {
    border-radius: 50%; width: 100px; height: 100px; object-fit: cover;
    border: 2px solid #60a5fa; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.task-attachment {
    max-width: 200px; border-radius: 12px; margin: 0.5rem;
    border: 2px solid #60a5fa; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.attachment-info {
    font-size: 0.9rem; color: #94a3b8; margin-top: 0.3rem;
}

.chart-container {
    background: #1e293b; padding: 1rem; border-radius: 16px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    margin-bottom: 1.5rem; transition: transform 0.3s ease;
    animation: slideInUp 0.6s ease-in-out;
}

.chart-container:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.5);
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
        st.session_state.user_role_type = None
        st.session_state.timesheet = []
        st.session_state.login_log = []
        st.session_state.reminders = []
        st.session_state.selected_tab = "Dashboard"
        st.session_state.login_error = ""
    if "reminders" not in st.session_state:
        st.session_state.reminders = []
    if "selected_tab" not in st.session_state:
        st.session_state.selected_tab = "Dashboard"
    load_data()

# --- Authentication ---
def authenticate_user():
    if not st.session_state.logged_in:
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;600&display=swap');

        .background {
            width: 430px;
            height: 520px;
            position: absolute;
            transform: translate(-50%,-50%);
            left: 50%;
            top: 50%;
        }

        .background .shape {
            height: 200px;
            width: 200px;
            position: absolute;
            border-radius: 50%;
        }

        .shape:first-child {
            background: linear-gradient(#1845ad, #23a2f6);
            left: -80px;
            top: -80px;
        }

        .shape:last-child {
            background: linear-gradient(to right, #ff512f, #f09819);
            right: -30px;
            bottom: -80px;
        }

        .glass-form {
            height: 520px;
            width: 400px;
            background-color: rgba(255,255,255,0.1);
            position: absolute;
            transform: translate(-50%,-50%);
            top: 50%;
            left: 50%;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255,255,255,0.1);
            box-shadow: 0 0 40px rgba(8,7,16,0.6);
            padding: 50px 35px;
            font-family: 'Poppins', sans-serif;
            color: white;
            z-index: 2;
        }

        .glass-form h3 {
            font-size: 32px;
            font-weight: 500;
            line-height: 42px;
            text-align: center;
            margin-bottom: 20px;
        }

        .glass-form label {
            display: block;
            margin-top: 20px;
            font-size: 16px;
            font-weight: 500;
        }

        .glass-form input {
            display: block;
            height: 50px;
            width: 100%;
            background-color: rgba(255,255,255,0.07);
            border-radius: 3px;
            padding: 0 10px;
            margin-top: 8px;
            font-size: 14px;
            font-weight: 300;
            color: white;
        }

        .glass-form ::placeholder {
            color: #e5e5e5;
        }

        .glass-form button {
            margin-top: 40px;
            width: 100%;
            background-color: #ffffff;
            color: #080710;
            padding: 15px 0;
            font-size: 18px;
            font-weight: 600;
            border-radius: 5px;
            cursor: pointer;
            border: none;
            transition: 0.3s ease;
        }

        .glass-form button:hover {
            background-color: #f0f0f0;
        }

        .error-msg {
            color: #f87171;
            font-weight: 600;
            margin-top: 1rem;
            font-size: 0.9rem;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="background">
            <div class="shape"></div>
            <div class="shape"></div>
        </div>
        <div class="glass-form">
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("<h3>Login Here</h3>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="Email or Phone")
            password = st.text_input("Password", placeholder="Password", type="password")
            submitted = st.form_submit_button("Log In")

            if submitted:
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
                    st.rerun()
                else:
                    st.session_state.login_error = "❌ Invalid username or password"

        if st.session_state.get("login_error"):
            st.markdown(f"<div class='error-msg'>{st.session_state.login_error}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()


        # Handle login data from JavaScript
        login_data = st.query_params.get("login_data", [""])[0]
        if login_data:
            try:
                print(f"Received login data: {login_data}")  # Server-side debug
                login_info = json.loads(login_data)
                print(f"Parsed login data: {login_info}")  # Server-side debug
                if isinstance(login_info, dict):
                    if login_info.get("action") == "close":
                        print("Login cancelled by user")  # Server-side debug
                        st.session_state.login_error = "Login cancelled."
                        st.query_params.clear()
                        st.rerun()
                    username = login_info.get("username")
                    password = login_info.get("password")
                    if username and password:
                        user = USERS.get(username.lower())
                        if user and user["pass"] == password:
                            print(f"Login successful for user: {username.lower()}")  # Server-side debug
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
                            st.session_state.login_error = ""
                            st.query_params.clear()
                            print("Login state updated, redirecting to Dashboard")  # Server-side debug
                            st.rerun()
                        else:
                            print(f"Invalid credentials for user: {username.lower()}")  # Server-side debug
                            st.session_state.login_error = "❌ Invalid username or password"
                            st.query_params.clear()
                            st.rerun()
                    else:
                        print("Missing username or password in login data")  # Server-side debug
                        st.session_state.login_error = "⚠️ Please enter both username and password"
                        st.query_params.clear()
                        st.rerun()
                else:
                    print("Invalid login data format")  # Server-side debug
                    st.session_state.login_error = "⚠️ Invalid login data"
                    st.query_params.clear()
                    st.rerun()
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")  # Server-side debug
                st.session_state.login_error = "⚠️ Error processing login data. Please try again."
                st.query_params.clear()
                st.rerun()
            except Exception as e:
                print(f"Unexpected error in authentication: {e}")  # Server-side debug
                st.session_state.login_error = f"⚠️ Authentication error: {e}"
                st.query_params.clear()
                st.rerun()

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
                'bold': True,
                'font_color': 'white',
                'bg_color': '#4f81bd',
                'font_size': 12,
                'align': 'center',
                'valign': 'vcenter'
            })
            cell_format = workbook.add_format({
                'font_color': '#000000',
                'align': 'left',
                'valign': 'vcenter'
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
def render_dashboard_stats(display_df):
    total_tasks = len(display_df)
    completed_tasks = display_df[display_df['Status'] == '✅ Completed'].shape[0] if not display_df.empty else 0
    in_progress_tasks = display_df[display_df['Status'] == '🔄 In Progress'].shape[0] if not display_df.empty else 0
    not_started_tasks = display_df[display_df['Status'] == '⏳ Not Started'].shape[0] if not display_df.empty else 0

    st.markdown("### 📊 Overall Task Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"<div class='overview-box'>Total Tasks<br><span>{total_tasks}</span></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='overview-box'>Completed<br><span>{completed_tasks}</span></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='overview-box'>In Progress<br><span>{in_progress_tasks}</span></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='overview-box'>Not Started<br><span>{not_started_tasks}</span></div>", unsafe_allow_html=True)

# --- Render Analytics in Dashboard ---
def render_analytics(display_df):
    if not display_df.empty:
        st.markdown("### 📈 Task Analytics")
        col1, col2 = st.columns(2)
        with col1:
            fig_hist = px.histogram(
                display_df,
                x="Date",
                color="Status",
                title="Tasks Over Time",
                color_discrete_sequence=px.colors.qualitative.Plotly,
                template="plotly_dark",
                height=400,
                animation_frame="Date" if len(display_df['Date'].unique()) > 1 else None
            )
            fig_hist.update_traces(
                hovertemplate="Date: %{x}<br>Tasks: %{y}<br>Status: %{customdata[0]}",
                customdata=display_df[["Status"]].values
            )
            fig_hist.update_layout(
                title_font_size=16,
                xaxis_title="Date",
                yaxis_title="Number of Tasks",
                showlegend=True,
                bargap=0.2
            )
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.plotly_chart(fig_hist, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            fig_pie = px.pie(
                display_df,
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

        fig_bar = px.bar(
            display_df,
            x="Priority",
            color="Priority",
            title="Priority Levels",
            color_discrete_sequence=px.colors.qualitative.Plotly,
            template="plotly_dark",
            height=400
        )
        fig_bar.update_traces(
            hovertemplate="Priority: %{x}<br>Tasks: %{y}"
        )
        fig_bar.update_layout(
            title_font_size=16,
            xaxis_title="Priority",
            yaxis_title="Number of Tasks",
            showlegend=False
        )
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### 📋 Task Table")
        st.dataframe(display_df.drop(columns=['TaskID', 'Attachment'], errors='ignore'))

        st.markdown("### 📥 Download Tasks")
        data, file_name = export_to_excel(display_df, "Tasks", "tasks_export.xlsx")
        if data:
            st.download_button("📥 Download Excel", data=data, file_name=file_name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.error("⚠️ Failed to generate Excel file.")

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
    current_user = st.session_state.user_role
    user_tasks = df_all[df_all['Employee'] == current_user] if not df_all.empty and 'Employee' in df_all.columns else pd.DataFrame()
    if not user_tasks.empty:
        data, file_name = export_to_excel(user_tasks, f"{current_user}_Tasks", f"{current_user}_tasks.xlsx")
        if data:
            st.download_button(
                label="⬇️ Download My Tasks",
                data=data,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("⚠️ Failed to generate Excel file.")
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
    current_time = "10:05 AM"  # Updated to match provided timestamp
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

    cols = st.columns(len(tabs))
    for idx, (tab_key, tab_label) in enumerate(tabs):
        with cols[idx]:
            button_class = "selected" if st.session_state.selected_tab == tab_key else ""
            if st.button(tab_label, key=f"nav_{tab_key.lower().replace(' ', '_')}", help=tab_label, use_container_width=True):
                st.session_state.selected_tab = tab_key
                st.rerun()
            st.markdown(f"""
                <script>
                    document.querySelectorAll('.stButton>button').forEach((btn, index) => {{
                        if (index === {idx} && "{st.session_state.selected_tab}" === "{tab_key}") {{
                            btn.classList.add('selected');
                        }} else {{
                            btn.classList.remove('selected');
                        }}
                    }});
                </script>
            """, unsafe_allow_html=True)
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
    
    if st.session_state.user_role_type == "Employee" and (df_user.empty or today_str not in df_user['Date'].values):
        st.sidebar.markdown(f"<div class='alert-box'>⚠️ You haven't submitted any tasks for today!</div>", unsafe_allow_html=True)
    
    if st.session_state.user_role_type in ["Admin", "Supervisor"]:
        users = list(set(df_all['Employee'].unique()) if not df_all.empty and 'Employee' in df_all.columns else [])
        for user in USERS.keys():
            if user.lower() not in users or not any(df_all[df_all['Employee'] == user.lower()]['Date'] == today_str):
                st.sidebar.markdown(f"<div class='alert-box'>🔔 Alert: <b>{user.capitalize()}</b> has not submitted a task today!</div>", unsafe_allow_html=True)

    try:
        reminders = st.session_state.reminders
    except AttributeError:
        st.session_state.reminders = []
        reminders = st.session_state.reminders
    for reminder in reminders:
        if reminder["user"] == st.session_state.user_role and reminder["date"] == today_str:
            st.sidebar.markdown(f"<div class='alert-box reminder'>🔔 Reminder: Task '{reminder['task_desc'][:30]}...' is still Not Started! Due: {reminder['due_date']}</div>", unsafe_allow_html=True)
    
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
                    if attachment.size > 5 * 1024 * 1024:
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
                                    "user": st.session_state.user_role,
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

        if st.session_state.user_role_type == "Admin":
            with st.form("delete_form"):
                st.warning("⚠️ This action cannot be undone!")
                delete_confirmed = st.checkbox("I confirm I want to delete this task", key="confirm_delete")
                submitted_delete = st.form_submit_button("🗑 Delete Task", type="primary", help="Delete selected task")
                if submitted_delete and delete_confirmed:
                    st.session_state.timesheet = [t for t in st.session_state.timesheet if t["TaskID"] != selected_id]
                    st.session_state.reminders = [r for r in st.session_state.reminders if r["task_id"] != selected_id]
                    save_data()
                    st.warning("🗑 Task deleted successfully!")
                    st.rerun()
        else:
            st.info("ℹ️ Task deletion is restricted to Admins only.")

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
        
        st.markdown("### 👤 Manage Users")
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

        if not df_all.empty and 'Employee' in df_all.columns:
            st.markdown("### 📅 View and Filter Tasks")
            col1, col2 = st.columns(2)
            with col1:
                users = df_all['Employee'].unique().tolist()
                selected_user = st.selectbox("Employee", options=["All"] + users, key="filter_employee")
            with col2:
                start = st.date_input("Start Date", value=datetime.now(tz) - timedelta(days=7), key="filter_start")
                end = st.date_input("End Date", value=datetime.now(tz), key="filter_end")
            filtered_df = df_all
            if selected_user != "All":
                filtered_df = filtered_df[filtered_df['Employee'] == selected_user]
            filtered_df = filtered_df[(filtered_df['Date'] >= start.strftime('%Y-%m-%d')) & (filtered_df['Date'] <= end.strftime('%Y-%m-%d'))]
            st.dataframe(filtered_df.drop(columns=['TaskID', 'Attachment'], errors='ignore'))

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
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("### 📜 Login Activity Log")
            st.dataframe(pd.DataFrame(st.session_state.login_log))

            st.markdown("### 📊 Employee Statistics")
            stats_df = df_all.groupby('Employee').agg({
                'TaskID': 'count',
                'Status': lambda x: (x == '✅ Completed').sum()
            }).rename(columns={'TaskID': 'Total Tasks', 'Status': 'Completed Tasks'})
            stats_df['Completion Rate'] = (stats_df['Completed Tasks'] / stats_df['Total Tasks'] * 100).round(2)
            st.dataframe(stats_df)

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
        else:
            st.info("ℹ️ No tasks recorded yet.")

# --- Main App Logic ---
if __name__ == "__main__":
    initialize_session()
    authenticate_user()

    # Sidebar
    st.sidebar.title("🔒 Session")
    if st.sidebar.button("Logout", key="logout_button"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_role_type = None
        st.session_state.reminders = []
        st.session_state.selected_tab = "Dashboard"
        save_data()
        st.rerun()

    # Render Alerts in Sidebar
    df_all = pd.DataFrame(st.session_state.timesheet)
    df_user = df_all[df_all['Employee'] == st.session_state.user_role] if not df_all.empty and 'Employee' in df_all.columns else pd.DataFrame()
    render_alerts(df_user, df_all)

    # Render Sidebar Stats
    render_sidebar_stats()

    # Data Setup
    display_df = df_user if st.session_state.user_role_type == "Employee" else df_all

    # Render Header with Navigation
    render_header()

    # Render Content Based on Selected Tab
    if st.session_state.selected_tab == "Dashboard":
        st.header("🏠 Dashboard")
        render_dashboard_stats(display_df)
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

    # Footer
    st.markdown(
        f"<footer>📅 INTERSOFT FLM Tracker • {datetime.now(pytz.timezone('Asia/Riyadh')).strftime('%A, %B %d, %Y')} - 10:05 AM (+03)</footer>",
        unsafe_allow_html=True
    )
