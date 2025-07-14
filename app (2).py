import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time
from io import BytesIO

# Page Configuration
st.set_page_config(
    page_title="⏱ INTERSOFT POS FLM Time Tracker",
    layout="wide",
    page_icon="⏱️"
)

# Custom CSS for Professional Appearance
st.markdown("""
    <style>
    :root {
        --primary: #2563eb;
        --secondary: #1e40af;
        --dark-bg: #111827;
        --card-bg: #1f2937;
        --text-color: #f3f4f6;
        --border-color: #374151;
    }
    
    body, [class*="css"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: var(--dark-bg);
        color: var(--text-color);
    }
    
    .header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0 0 12px 12px;
        margin-bottom: 2rem;
    }
    
    .company-logo {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .dept-name {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    .status-card {
        background: var(--card-bg);
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border: 1px solid var(--border-color);
    }
    
    .required-field::after {
        content: " *";
        color: #ef4444;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

# Shift Configuration
SHIFTS = {
    "Morning Shift (8:30 AM - 5:30 PM)": {
        'start': time(8, 30),
        'end': time(17, 30)
    },
    "Evening Shift (3:00 PM - 11:00 PM)": {
        'start': time(15, 0),
        'end': time(23, 0)
    }
}

# Task Categories with TOMS devices option
TASK_CATEGORIES = {
    "TOMS": {
        "requires_device_count": True,
        "requires_task_time": True
    },
    "Paper Request": {
        "requires_device_count": False,
        "requires_task_time": False
    },
    "J.O": {
        "requires_device_count": False,
        "requires_task_time": True
    },
    "CRM": {
        "requires_device_count": False,
        "requires_task_time": True
    }
}

# Header with Company Info
st.markdown("""
    <div class="header">
        <div class="company-logo">INTERSOFT POS</div>
        <div class="dept-name">FLM Department - Time Tracking System</div>
    </div>
""", unsafe_allow_html=True)

# Sidebar Filters
with st.sidebar:
    st.header("Filter Options")
    employee_list = list(set([r.get("Employee", "") for r in st.session_state.timesheet]))
    selected_employee = st.selectbox("Employee", ["All Employees"] + sorted(employee_list))
    
    selected_date = st.date_input("Date Filter", value=None)
    selected_task = st.selectbox("Task Category", ["All Tasks"] + list(TASK_CATEGORIES.keys()))
    
    # Statistics
    total_hours = sum(r.get("Duration (hrs)", 0) for r in st.session_state.timesheet)
    st.markdown(f"""
        <div class="status-card">
            <p>Total Recorded Hours: <strong>{total_hours:.1f}</strong></p>
            <p>Total Entries: <strong>{len(st.session_state.timesheet)}</strong></p>
        </div>
    """, unsafe_allow_html=True)

# Time Entry Form
with st.expander("➕ Add New Time Entry", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        cols = st.columns([1, 1, 1])
        
        with cols[0]:
            st.markdown('<div class="required-field">Employee Name</div>', unsafe_allow_html=True)
            employee = st.text_input("Employee Name", label_visibility="collapsed", placeholder="e.g. Ahmed Mohamed")
            
            st.markdown('<div class="required-field">Shift Type</div>', unsafe_allow_html=True)
            shift_type = st.selectbox("Shift Type", list(SHIFTS.keys()), label_visibility="collapsed")
            
        with cols[1]:
            st.markdown('<div class="required-field">Start Time</div>', unsafe_allow_html=True)
            start_time = st.time_input("Start Time", label_visibility="collapsed", format="12h")
            
            st.markdown('<div class="required-field">End Time</div>', unsafe_allow_html=True)
            end_time = st.time_input("End Time", label_visibility="collapsed", format="12h")
            
        with cols[2]:
            st.markdown('<div class="required-field">Task Category</div>', unsafe_allow_html=True)
            task_category = st.selectbox("Task Category", list(TASK_CATEGORIES.keys()), label_visibility="collapsed")
            
            # Dynamic fields based on task category
            if TASK_CATEGORIES[task_category]["requires_device_count"]:
                device_count = st.number_input("Number of TOMS Devices Worked On", min_value=1, value=1)
            
            if TASK_CATEGORIES[task_category]["requires_task_time"]:
                task_time = st.time_input("Time Spent on Task", value=time(1, 0), format="12h")
        
        work_details = st.text_area("Work Details (Optional)", placeholder="Describe the work performed...")
        
        submitted = st.form_submit_button("Submit Time Entry")
        
        if submitted:
            if not all([employee, shift_type, start_time, end_time, task_category]):
                st.error("Please fill all required fields")
            elif end_time <= start_time:
                st.error("End time must be after start time")
            else:
                # Convert times to datetime for calculations
                start_dt = datetime.combine(datetime.today(), start_time)
                end_dt = datetime.combine(datetime.today(), end_time)
                
                # Calculate duration in hours
                duration = (end_dt - start_dt).total_seconds() / 3600
                
                # Prepare entry data
                entry = {
                    "Employee": employee,
                    "Date": datetime.today().date(),
                    "Shift": shift_type,
                    "Start Time": start_time.strftime("%I:%M %p"),
                    "End Time": end_time.strftime("%I:%M %p"),
                    "Duration (hrs)": round(duration, 2),
                    "Task Category": task_category,
                    "Work Details": work_details
                }
                
                # Add task-specific fields
                if TASK_CATEGORIES[task_category]["requires_device_count"]:
                    entry["TOMS Devices Count"] = device_count
                
                if TASK_CATEGORIES[task_category]["requires_task_time"]:
                    entry["Task Time"] = task_time.strftime("%I:%M %p")
                
                st.session_state.timesheet.append(entry)
                st.success("Time entry submitted successfully!")
                st.balloons()

# Main Dashboard
if st.session_state.timesheet:
    df = pd.DataFrame(st.session_state.timesheet)
    
    # Apply filters
    if selected_employee != "All Employees":
        df = df[df["Employee"] == selected_employee]
    if selected_date:
        df = df[df["Date"] == pd.to_datetime(selected_date)]
    if selected_task != "All Tasks":
        df = df[df["Task Category"] == selected_task]
    
    if not df.empty:
        # Display Time Entries
        st.markdown("## Time Entries")
        
        # Format columns for display
        display_cols = [
            "Employee", "Date", "Shift", 
            "Start Time", "End Time", 
            "Duration (hrs)", "Task Category"
        ]
        
        # Add conditional columns
        if "TOMS Devices Count" in df.columns:
            display_cols.append("TOMS Devices Count")
        if "Task Time" in df.columns:
            display_cols.append("Task Time")
        
        display_cols.append("Work Details")
        
        st.dataframe(
            df[display_cols].sort_values("Date", ascending=False),
            use_container_width=True,
            height=500
        )
        
        # Analytics Section
        st.markdown("## Analytics")
        
        tab1, tab2 = st.tabs(["Task Analysis", "Employee Productivity"])
        
        with tab1:
            fig1 = px.pie(df, names="Task Category", title="Time Distribution by Task Type")
            st.plotly_chart(fig1, use_container_width=True)
            
            if "TOMS" in df["Task Category"].values:
                toms_df = df[df["Task Category"] == "TOMS"]
                fig2 = px.bar(toms_df, x="Employee", y="TOMS Devices Count", 
                             title="TOMS Devices Serviced by Employee")
                st.plotly_chart(fig2, use_container_width=True)
        
        with tab2:
            fig3 = px.bar(df.groupby("Employee")["Duration (hrs)"].sum().reset_index(), 
                         x="Employee", y="Duration (hrs)", 
                         title="Total Hours Worked by Employee")
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No records match your filters")
else:
    st.info("No time entries recorded yet. Add your first entry above.")

# Footer
st.markdown("---")
st.markdown("INTERSOFT POS FLM Department • Professional Time Tracking System © 2023")
