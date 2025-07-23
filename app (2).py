import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
import uuid
import os
import base64
import io
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta, MO, SU
from PIL import Image
import time

# ===================== CONFIGURATION =====================
st.set_page_config(
    page_title="Task Management System",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== DATA MANAGEMENT =====================
def create_data_directories():
    """Create necessary directories if they don't exist."""
    directories = ["data", "weekly_exports"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def load_data():
    """Load data from the data.json file."""
    create_data_directories()
    data_file = "data/data.json"
    if not os.path.exists(data_file):
        default_data = {
            "tasks": [],
            "reminders": [],
            "login_logs": [],
            "user_profiles": {},
            "users": {
                "admin": {"password": "admin123", "role": "Admin", "name": "Administrator"}
            }
        }
        save_data(default_data)
        return default_data
    
    try:
        with open(data_file, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return {
            "tasks": [],
            "reminders": [],
            "login_logs": [],
            "user_profiles": {},
            "users": {
                "admin": {"password": "admin123", "role": "Admin", "name": "Administrator"}
            }
        }

def save_data(data):
    """Save data to the data.json file."""
    try:
        with open("data/data.json", "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving data: {e}")
# ===================== AUTHENTICATION =====================
def login_page():
    """Display the login page."""
    st.title("Task Management System")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if authenticate_user(username, password):
                return True
    
    return False

def authenticate_user(username, password):
    """Authenticate the user with given credentials."""
    data = load_data()
    
    if username in data["users"] and data["users"][username]["password"] == password:
        # Set user session data
        st.session_state.username = username
        st.session_state.role = data["users"][username]["role"]
        st.session_state.name = data["users"][username].get("name", username)
        st.session_state.logged_in = True
        
        # Log the login
        log_login(username)
        
        return True
    else:
        st.error("Invalid username or password")
        return False

def log_login(username):
    """Log user login."""
    data = load_data()
    data["login_logs"].append({
        "username": username,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_data(data)

def logout():
    """Log out the user."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()
# ===================== USER INTERFACE =====================
def display_sidebar():
    """Display the sidebar with navigation options."""
    with st.sidebar:
        st.title("Navigation")
        
        # User info
        st.subheader(f"Welcome, {st.session_state.name}")
        st.text(f"Role: {st.session_state.role}")
        
        # Navigation
        page = st.radio(
            "Go to",
            ["Dashboard", "Add Task", "Edit/Delete Task", "Employee Work", "Download Tasks", "Settings"],
            key="navigation"
        )
        
        # Admin Panel (Admin only)
        if st.session_state.role == "Admin":
            if st.button("Admin Panel"):
                st.session_state.page = "Admin Panel"
        
        # Logout button
        if st.button("Logout"):
            logout()
        
        # Display reminders
        display_reminders()
        
        return page

def display_reminders():
    """Display reminders in the sidebar."""
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    
    reminders = [r for r in data["reminders"] if r["due_date"] == today]
    
    if reminders:
        st.sidebar.subheader("Today's Reminders")
        for reminder in reminders:
            task = next((t for t in data["tasks"] if t["id"] == reminder["task_id"]), None)
            if task:
                st.sidebar.warning(
                    f"**Task Due Today!**\n\n"
                    f"- **Task**: {task['description'][:30]}...\n"
                    f"- **Department**: {task['department']}\n"
                    f"- **Priority**: {task['priority']}"
                )

# ===================== TASK MANAGEMENT =====================
def add_task_page():
    """Display the add task page."""
    st.header("Add New Task")
    
    data = load_data()
    
    with st.form("add_task_form"):
        # Task details
        employee = st.selectbox(
            "Assigned Employee", 
            [user for user, details in data["users"].items() if details["role"] == "Employee"]
        )
        date = st.date_input("Date", datetime.now())
        shift = st.selectbox("Shift", ["Morning", "Evening"])
        department = st.selectbox("Department", ["FLM", "CRM", "Job Orders", "Other"])
        category = st.text_input("Category")
        status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        description = st.text_area("Description")
        
        # File upload
        uploaded_file = st.file_uploader("Attach File (optional)", type=["jpg", "jpeg", "png", "pdf"])
        file_data = None
        file_type = None
        
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            file_data = base64.b64encode(file_bytes).decode()
            file_type = uploaded_file.type
        
        # Reminder (if status is "Not Started")
        set_reminder = False
        reminder_date = None
        
        if status == "Not Started":
            set_reminder = st.checkbox("Set Reminder")
            if set_reminder:
                reminder_date = st.date_input("Reminder Date", datetime.now() + timedelta(days=1))
        
        # Submit button
        submitted = st.form_submit_button("Add Task")
        
        if submitted:
            # Create task
            task_id = str(uuid.uuid4())
            new_task = {
                "id": task_id,
                "employee": employee,
                "date": date.strftime("%Y-%m-%d"),
                "shift": shift,
                "department": department,
                "category": category,
                "status": status,
                "priority": priority,
                "description": description,
                "file_data": file_data,
                "file_type": file_type,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add task to data
            data["tasks"].append(new_task)
            
            # Create reminder if needed
            if set_reminder and reminder_date:
                reminder = {
                    "task_id": task_id,
                    "due_date": reminder_date.strftime("%Y-%m-%d")
                }
                data["reminders"].append(reminder)
            
            # Save data
            save_data(data)
            
            st.success("Task added successfully!")
def edit_delete_task_page():
    """Display the edit/delete task page."""
    st.header("Edit or Delete Tasks")
    
    data = load_data()
    
    # Filter tasks based on user role
    filtered_tasks = []
    if st.session_state.role == "Admin":
        filtered_tasks = data["tasks"]
    elif st.session_state.role == "Supervisor":
        filtered_tasks = data["tasks"]  # Supervisors can see all tasks
    else:  # Employee
        filtered_tasks = [t for t in data["tasks"] if t["employee"] == st.session_state.username]
    
    # Display task table
    if filtered_tasks:
        task_df = pd.DataFrame(filtered_tasks)
        task_df = task_df[["id", "employee", "date", "department", "category", "status", "priority", "description"]]
        
        st.dataframe(task_df)
        
        # Select task to edit/delete
        task_ids = [t["id"] for t in filtered_tasks]
        selected_task_id = st.selectbox("Select Task to Edit/Delete", task_ids)
        
        # Find selected task
        selected_task = next((t for t in filtered_tasks if t["id"] == selected_task_id), None)
        
        if selected_task:
            # Display task details and edit form
            st.subheader("Edit Task")
            
            with st.form("edit_task_form"):
                # Task details
                employee = st.selectbox(
                    "Assigned Employee", 
                    [user for user, details in data["users"].items() if details["role"] == "Employee"],
                    index=[user for user, details in data["users"].items() if details["role"] == "Employee"].index(selected_task["employee"]) if selected_task["employee"] in [user for user, details in data["users"].items() if details["role"] == "Employee"] else 0
                )
                date = st.date_input("Date", datetime.strptime(selected_task["date"], "%Y-%m-%d"))
                shift = st.selectbox("Shift", ["Morning", "Evening"], index=0 if selected_task["shift"] == "Morning" else 1)
                department = st.selectbox("Department", ["FLM", "CRM", "Job Orders", "Other"], index=["FLM", "CRM", "Job Orders", "Other"].index(selected_task["department"]))
                category = st.text_input("Category", selected_task["category"])
                status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"], index=["Not Started", "In Progress", "Completed"].index(selected_task["status"]))
                priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(selected_task["priority"]))
                description = st.text_area("Description", selected_task["description"])
                
                # File handling
                if selected_task["file_data"]:
                    st.write("Current attachment: Available")
                    keep_file = st.checkbox("Keep current attachment", value=True)
                else:
                    keep_file = False
                
                uploaded_file = st.file_uploader("Upload New Attachment (optional)", type=["jpg", "jpeg", "png", "pdf"])
                
                # Process file data
                file_data = selected_task["file_data"] if keep_file else None
                file_type = selected_task["file_type"] if keep_file else None
                
                if uploaded_file is not None:
                    file_bytes = uploaded_file.read()
                    file_data = base64.b64encode(file_bytes).decode()
                    file_type = uploaded_file.type
                
                # Reminder handling
                reminder = next((r for r in data["reminders"] if r["task_id"] == selected_task_id), None)
                set_reminder = st.checkbox("Set Reminder", value=bool(reminder))
                reminder_date = None
                
                if set_reminder:
                    if reminder:
                        default_date = datetime.strptime(reminder["due_date"], "%Y-%m-%d")
                    else:
                        default_date = datetime.now() + timedelta(days=1)
                    
                    reminder_date = st.date_input("Reminder Date", default_date)
                
                # Submit button
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    update = st.form_submit_button("Update Task")
                
                with col3:
                    delete = st.form_submit_button("Delete Task")
                
                if update:
                    # Update task
                    updated_task = {
                        "id": selected_task_id,
                        "employee": employee,
                        "date": date.strftime("%Y-%m-%d"),
                        "shift": shift,
                        "department": department,
                        "category": category,
                        "status": status,
                        "priority": priority,
                        "description": description,
                        "file_data": file_data,
                        "file_type": file_type,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Find and replace task
                    task_index = next((i for i, t in enumerate(data["tasks"]) if t["id"] == selected_task_id), None)
                    if task_index is not None:
                        data["tasks"][task_index] = updated_task
                    
                    # Handle reminder
                    if reminder:
                        # Remove existing reminder
                        data["reminders"] = [r for r in data["reminders"] if r["task_id"] != selected_task_id]
                    
                    if set_reminder and reminder_date:
                        new_reminder = {
                            "task_id": selected_task_id,
                            "due_date": reminder_date.strftime("%Y-%m-%d")
                        }
                        data["reminders"].append(new_reminder)
                    
                    # Save data
                    save_data(data)
                    
                    st.success("Task updated successfully!")
                    time.sleep(1)
                    st.experimental_rerun()
                
                elif delete:
                    # Remove task
                    data["tasks"] = [t for t in data["tasks"] if t["id"] != selected_task_id]
                    
                    # Remove reminder if exists
                    data["reminders"] = [r for r in data["reminders"] if r["task_id"] != selected_task_id]
                    
                    # Save data
                    save_data(data)
                    
                    st.success("Task deleted successfully!")
                    time.sleep(1)
                    st.experimental_rerun()
    else:
        st.info("No tasks found.")
def employee_work_page():
    """Display the employee work page."""
    st.header("Employee Work")
    
    data = load_data()
    
    # Get all employees
    employees = [user for user, details in data["users"].items() if details["role"] == "Employee"]
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        selected_employee = st.selectbox(
            "Select Employee", 
            employees if st.session_state.role in ["Admin", "Supervisor"] else [st.session_state.username]
        )
    
    with col2:
        date_range = st.date_input(
            "Select Date Range",
            [datetime.now() - timedelta(days=7), datetime.now()],
            key="date_range"
        )
    
    # Filter tasks
    start_date, end_date = date_range
    filtered_tasks = [
        t for t in data["tasks"] 
        if t["employee"] == selected_employee and 
        start_date.strftime("%Y-%m-%d") <= t["date"] <= end_date.strftime("%Y-%m-%d")
    ]
    
    # Display tasks
    if filtered_tasks:
        st.subheader(f"Tasks for {selected_employee}")
        
        task_df = pd.DataFrame(filtered_tasks)
        task_df = task_df[["date", "department", "category", "status", "priority", "description"]]
        
        st.dataframe(task_df)
        
        # Task stats
        st.subheader("Task Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Tasks", len(filtered_tasks))
        
        with col2:
            completed_tasks = len([t for t in filtered_tasks if t["status"] == "Completed"])
            st.metric("Completed Tasks", completed_tasks)
        
        with col3:
            in_progress = len([t for t in filtered_tasks if t["status"] == "In Progress"])
            not_started = len([t for t in filtered_tasks if t["status"] == "Not Started"])
            st.metric("Pending Tasks", in_progress + not_started)
        
        # Charts
        st.subheader("Task Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution
            status_counts = pd.DataFrame(filtered_tasks).groupby("status").size().reset_index(name="count")
            fig1 = px.pie(status_counts, values="count", names="status", title="Task Status Distribution")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Department distribution
            dept_counts = pd.DataFrame(filtered_tasks).groupby("department").size().reset_index(name="count")
            fig2 = px.bar(dept_counts, x="department", y="count", title="Tasks by Department")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info(f"No tasks found for {selected_employee} in the selected date range.")
def download_tasks_page():
    """Display the download tasks page."""
    st.header("Download Tasks")
    
    data = load_data()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.role in ["Admin", "Supervisor"]:
            employees = ["All"] + [user for user, details in data["users"].items() if details["role"] == "Employee"]
            selected_employee = st.selectbox("Select Employee", employees)
        else:
            selected_employee = st.session_state.username
    
    with col2:
        date_range = st.date_input(
            "Select Date Range",
            [datetime.now() - timedelta(days=30), datetime.now()],
            key="download_date_range"
        )
    
    with col3:
        selected_status = st.selectbox("Task Status", ["All", "Not Started", "In Progress", "Completed"])
    
    # Filter tasks
    start_date, end_date = date_range
    filtered_tasks = data["tasks"]
    
    # Apply employee filter
    if selected_employee != "All":
        filtered_tasks = [t for t in filtered_tasks if t["employee"] == selected_employee]
    
    # Apply date filter
    filtered_tasks = [
        t for t in filtered_tasks 
        if start_date.strftime("%Y-%m-%d") <= t["date"] <= end_date.strftime("%Y-%m-%d")
    ]
    
    # Apply status filter
    if selected_status != "All":
        filtered_tasks = [t for t in filtered_tasks if t["status"] == selected_status]
    
    # Create DataFrame
    if filtered_tasks:
        # Create a DataFrame without file_data (to save space)
        download_df = pd.DataFrame([
            {k: v for k, v in task.items() if k != "file_data"} 
            for task in filtered_tasks
        ])
        
        # Generate Excel file
        excel_buffer = io.BytesIO()
        download_df.to_excel(excel_buffer, index=False, engine="openpyxl")
        excel_data = excel_buffer.getvalue()
        
        # Create download button
        st.download_button(
            label="Download as Excel",
            data=excel_data,
            file_name=f"tasks_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Preview data
        st.subheader("Task Data Preview")
        st.dataframe(download_df)
    else:
        st.info("No tasks match the selected filters.")
def settings_page():
    """Display the settings page."""
    st.header("Settings")
    
    data = load_data()
    user_data = data["users"].get(st.session_state.username, {})
    
    # User profile section
    st.subheader("User Profile")
    
    # User profile form
    with st.form("profile_form"):
        # User name
        name = st.text_input("Full Name", value=user_data.get("name", st.session_state.username))
        
        # Profile picture
        profile_picture = None
        
        if st.session_state.username in data["user_profiles"] and "profile_picture" in data["user_profiles"][st.session_state.username]:
            st.write("Current Profile Picture:")
            img_data = base64.b64decode(data["user_profiles"][st.session_state.username]["profile_picture"])
            st.image(img_data, width=100)
        
        uploaded_file = st.file_uploader("Upload Profile Picture (optional)", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            
            # Resize image to save space
            max_size = (200, 200)
            image.thumbnail(max_size)
            
            # Convert to bytes
            img_buffer = io.BytesIO()
            image.save(img_buffer, format="PNG")
            img_bytes = img_buffer.getvalue()
            
            # Convert to base64
            profile_picture = base64.b64encode(img_bytes).decode()
        
        # Password change
        st.subheader("Change Password")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        # Submit button
        submitted = st.form_submit_button("Save Changes")
        
        if submitted:
            updated = False
            
            # Update name
            if name != user_data.get("name", st.session_state.username):
                data["users"][st.session_state.username]["name"] = name
                st.session_state.name = name
                updated = True
            
            # Update profile picture
            if profile_picture:
                if st.session_state.username not in data["user_profiles"]:
                    data["user_profiles"][st.session_state.username] = {}
                
                data["user_profiles"][st.session_state.username]["profile_picture"] = profile_picture
                updated = True
            
            # Update password
            if current_password and new_password and confirm_password:
                if data["users"][st.session_state.username]["password"] == current_password:
                    if new_password == confirm_password:
                        data["users"][st.session_state.username]["password"] = new_password
                        updated = True
                        st.success("Password updated successfully!")
                    else:
                        st.error("New passwords do not match!")
                else:
                    st.error("Current password is incorrect!")
            
            # Save data if any changes were made
            if updated:
                save_data(data)
                st.success("Settings updated successfully!")
def admin_panel_page():
    """Display the admin panel page."""
    st.header("Admin Panel")
    
    if st.session_state.role != "Admin":
        st.error("Access denied. Only Admins can access this page.")
        return
    
    data = load_data()
    
    # User management section
    st.subheader("User Management")
    
    # Add new user form
    with st.expander("Add New User"):
        with st.form("add_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["Admin", "Supervisor", "Employee"])
            new_name = st.text_input("Full Name")
            
            submitted = st.form_submit_button("Add User")
            
            if submitted:
                if new_username and new_password and new_role and new_name:
                    if new_username not in data["users"]:
                        data["users"][new_username] = {
                            "password": new_password,
                            "role": new_role,
                            "name": new_name
                        }
                        save_data(data)
                        st.success(f"User '{new_username}' added successfully!")
                    else:
                        st.error(f"Username '{new_username}' already exists!")
                else:
                    st.error("All fields are required!")
    
    # Edit/Delete user
    st.subheader("Edit/Delete User")
    
    if data["users"]:
        user_list = list(data["users"].keys())
        selected_user = st.selectbox("Select User", user_list)
        
        with st.form("edit_user_form"):
            user_data = data["users"][selected_user]
            
            edit_role = st.selectbox("Role", ["Admin", "Supervisor", "Employee"], index=["Admin", "Supervisor", "Employee"].index(user_data["role"]))
            edit_name = st.text_input("Full Name", value=user_data.get("name", selected_user))
            reset_password = st.text_input("Reset Password (leave empty to keep current)", type="password")
            
            col1, col2 = st.columns(2)
            
            with col1:
                update = st.form_submit_button("Update User")
            
            with col2:
                delete = st.form_submit_button("Delete User")
            
            if update:
                user_data["role"] = edit_role
                user_data["name"] = edit_name
                
                if reset_password:
                    user_data["password"] = reset_password
                
                save_data(data)
                st.success(f"User '{selected_user}' updated successfully!")
            
            elif delete:
                if selected_user != st.session_state.username:
                    del data["users"][selected_user]
                    
                    # Also remove profile data if exists
                    if selected_user in data["user_profiles"]:
                        del data["user_profiles"][selected_user]
                    
                    save_data(data)
                    st.success(f"User '{selected_user}' deleted successfully!")
                else:
                    st.error("You cannot delete your own account!")
    
    # Data management section
    st.subheader("Data Management")
    
    with st.expander("Delete Data"):
        st.warning("Warning: This action cannot be undone!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Delete All Tasks", key="delete_all"):
                data["tasks"] = []
                data["reminders"] = []
                save_data(data)
                st.success("All tasks and reminders deleted successfully!")
        
        with col2:
            selected_date = st.date_input("Select Date", datetime.now())
            if st.button(f"Delete Tasks for {selected_date.strftime('%Y-%m-%d')}"):
                date_str = selected_date.strftime("%Y-%m-%d")
                
                # Get tasks for the selected date
                task_ids = [t["id"] for t in data["tasks"] if t["date"] == date_str]
                
                # Remove tasks
                data["tasks"] = [t for t in data["tasks"] if t["date"] != date_str]
                
                # Remove reminders for those tasks
                data["reminders"] = [r for r in data["reminders"] if r["task_id"] not in task_ids]
                
                save_data(data)
                st.success(f"Tasks for {date_str} deleted successfully!")

def dashboard_page():
    """Display the dashboard page."""
    st.header("Dashboard")
    
    data = load_data()
    
    # Date filter
    col1, col2 = st.columns(2)
    
    with col1:
        view_option = st.radio("View", ["Today", "Custom Date"])
    
    with col2:
        if view_option == "Today":
            selected_date = datetime.now().date()
        else:
            selected_date = st.date_input("Select Date", datetime.now().date())
    
    # Filter tasks by date
    date_str = selected_date.strftime("%Y-%m-%d")
    filtered_tasks = [t for t in data["tasks"] if t["date"] == date_str]
    
    # Show key metrics
    st.subheader("Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tasks", len(filtered_tasks))
    
    with col2:
        completed = len([t for t in filtered_tasks if t["status"] == "Completed"])
        completion_rate = f"{(completed / len(filtered_tasks) * 100):.1f}%" if filtered_tasks else "0%"
        st.metric("Completed", f"{completed} ({completion_rate})")
    
    with col3:
        in_progress = len([t for t in filtered_tasks if t["status"] == "In Progress"])
        st.metric("In Progress", in_progress)
    
    with col4:
        not_started = len([t for t in filtered_tasks if t["status"] == "Not Started"])
        st.metric("Not Started", not_started)
    
    # Display charts
    if filtered_tasks:
        st.subheader("Task Analysis")
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(filtered_tasks)
        
        # Create tabs for different charts
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Status", "Categories", "Priority", "Shift", "Department"])
        
        with tab1:
            # Status distribution chart
            status_counts = df["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            
            fig1 = px.pie(status_counts, values="Count", names="Status", title="Task Status Distribution")
            st.plotly_chart(fig1, use_container_width=True)
        
        with tab2:
            # Categories chart
            if "category" in df.columns and not df["category"].empty:
                category_counts = df["category"].value_counts().reset_index()
                category_counts.columns = ["Category", "Count"]
                
                fig2 = px.bar(category_counts, x="Category", y="Count", title="Tasks by Category")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No category data available")
        
        with tab3:
            # Priority chart
            priority_counts = df["priority"].value_counts().reset_index()
            priority_counts.columns = ["Priority", "Count"]
            
            fig3 = px.pie(priority_counts, values="Count", names="Priority", title="Tasks by Priority")
            st.plotly_chart(fig3, use_container_width=True)
        
        with tab4:
            # Shift chart
            shift_counts = df["shift"].value_counts().reset_index()
            shift_counts.columns = ["Shift", "Count"]
            
            fig4 = px.pie(shift_counts, values="Count", names="Shift", title="Tasks by Shift")
            st.plotly_chart(fig4, use_container_width=True)
        
        with tab5:
            # Department chart
            dept_counts = df["department"].value_counts().reset_index()
            dept_counts.columns = ["Department", "Count"]
            
            fig5 = px.bar(dept_counts, x="Department", y="Count", title="Tasks by Department")
            st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info(f"No tasks found for {date_str}")

# ===================== AUTO EXPORT FUNCTION =====================
def check_auto_export():
    """Check if it's Sunday and auto export weekly data if needed."""
    today = datetime.now()
    
    # If it's Sunday (weekday 6)
    if today.weekday() == 6:
        # Get last week's date range
        end_date = today.date() - timedelta(days=1)  # Saturday
        start_date = end_date - timedelta(days=6)    # Previous Sunday
        
        # File name for this week's export
        file_name = f"weekly_exports/tasks_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv"
        
        # Check if this week's export already exists
        if not os.path.exists(file_name):
            data = load_data()
            
            # Filter tasks for the last week
            weekly_tasks = [
                t for t in data["tasks"]
                if start_date.strftime("%Y-%m-%d") <= t["date"] <= end_date.strftime("%Y-%m-%d")
            ]
            
            # If there are tasks, export them
            if weekly_tasks:
                # Create a DataFrame without file_data (to save space)
                export_df = pd.DataFrame([
                    {k: v for k, v in task.items() if k != "file_data"} 
                    for task in weekly_tasks
                ])
                
                # Create the directory if it doesn't exist
                if not os.path.exists("weekly_exports"):
                    os.makedirs("weekly_exports")
                
                # Export to CSV
                export_df.to_csv(file_name, index=False)

# ===================== MAIN APP =====================
def main():
    """Main application entry point."""
    # Check for auto export
    check_auto_export()
    
    # Check if the user is already logged in
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        # Display login page
        if login_page():
            st.experimental_rerun()
    else:
        # Display the main app
        page = display_sidebar()
        
        # Handle page navigation from sidebar
        if "page" in st.session_state:
            page = st.session_state.page
            del st.session_state.page  # Clear the page state
        
        # Display the selected page
        if page == "Dashboard":
            dashboard_page()
        elif page == "Add Task":
            add_task_page()
        elif page == "Edit/Delete Task":
            edit_delete_task_page()
        elif page == "Employee Work":
            employee_work_page()
        elif page == "Download Tasks":
            download_tasks_page()
        elif page == "Settings":
            settings_page()
        elif page == "Admin Panel":
            admin_panel_page()

if __name__ == "__main__":
    main()
