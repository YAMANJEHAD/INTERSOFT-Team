import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Page Configuration
st.set_page_config(
    page_title="⏱ Time Sheet InterSoft Pro", 
    layout="wide",
    page_icon="⏱️"
)

# Dark Theme CSS
st.markdown("""
    <style>
    :root {
        --primary: #6B73FF;
        --secondary: #000DFF;
        --dark-bg: #121212;
        --dark-card: #1E1E1E;
        --dark-text: #E0E0E0;
        --dark-border: #333333;
    }
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background-color: var(--dark-bg);
        color: var(--dark-text);
    }
    
    .header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        padding: 2rem;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin-bottom: 2rem;
    }
    
    .status-card {
        background: var(--dark-card);
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        border: 1px solid var(--dark-border);
    }
    </style>
""", unsafe_allow_html=True)

# Authentication System
def check_login(username, password):
    CREDENTIALS = {"admin": "admin123", "manager": "mgr123", "user": "user123"}
    return CREDENTIALS.get(username) == password

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.container():
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if check_login(username, password):
                st.session_state.logged_in = True
                st.session_state.user_role = username
                st.rerun()
            else:
                st.error("Invalid credentials")
    st.stop()

# Initialize session state
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []
if "notifications" not in st.session_state:
    st.session_state.notifications = []

# Shift configurations
SHIFTS = {
    "Morning Shift (8:30 AM - 5:30 PM)": {
        'start': time(8, 30),
        'end': time(17, 30),
        'break_duration': 60
    },
    "Evening Shift (3:00 PM - 11:00 PM)": {
        'start': time(15, 0),
        'end': time(23, 0),
        'break_duration': 30
    }
}

# Header
st.markdown("""
    <div class="header">
        <h1 class="header-title">⏱ Advanced Time Tracking System</h1>
        <p class="header-subtitle">Professional Attendance Management Solution</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Filters
with st.sidebar:
    st.header("Filter Options")
    employee_list = list(set([r.get("Employee", "") for r in st.session_state.timesheet]))
    selected_employee = st.selectbox("Employee", ["All Employees"] + sorted(employee_list))
    
    selected_date = st.date_input("Date Filter", value=None)
    search_term = st.text_input("Search Records")
    
    # Quick Stats
    total_hours = sum(r.get("Duration (hrs)", 0) for r in st.session_state.timesheet)
    st.markdown(f"""
        <div class="status-card">
            <p>Total Hours: <strong>{total_hours:.1f}</strong></p>
            <p>Total Entries: <strong>{len(st.session_state.timesheet)}</strong></p>
        </div>
    """, unsafe_allow_html=True)

# Time Entry Form
with st.expander("➕ Add New Time Entry", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        cols = st.columns([1, 1, 1])
        
        with cols[0]:
            employee = st.text_input("Employee Name*", placeholder="John Doe")
            employee_id = st.text_input("Employee ID*", placeholder="EMP-1001")
            date = st.date_input("Date*", datetime.today())
            
        with cols[1]:
            shift_type = st.selectbox("Shift Type*", list(SHIFTS.keys()))
            actual_start = st.time_input("Actual Start Time*")
            project = st.text_input("Project*", placeholder="Project X")
            
        with cols[2]:
            actual_end = st.time_input("Actual End Time*")
            status = st.selectbox("Status", ["Present", "Half Day", "Leave", "Remote"])
            task_category = st.selectbox("Task Category", ["Development", "Meeting", "Testing", "Documentation"])
        
        task_description = st.text_area("Work Description", height=100)
        
        submitted = st.form_submit_button("Submit Entry")
        
        if submitted:
            if not all([employee, employee_id, actual_start, actual_end, project]):
                st.error("Please fill all required fields (*)")
            elif actual_end <= actual_start:
                st.error("End time must be after start time")
            else:
                shift = SHIFTS[shift_type]
                
                # Calculate time metrics
                start_dt = datetime.combine(datetime.today(), actual_start)
                end_dt = datetime.combine(datetime.today(), actual_end)
                duration = (end_dt - start_dt).total_seconds() / 3600
                
                scheduled_start = datetime.combine(datetime.today(), shift['start'])
                late_minutes = max(0, (start_dt - scheduled_start).total_seconds() / 60)
                
                scheduled_end = datetime.combine(datetime.today(), shift['end'])
                early_minutes = max(0, (scheduled_end - end_dt).total_seconds() / 60)
                
                # Calculate overtime
                standard_hours = 8.5 if "Evening" in shift_type else 8
                overtime = max(0, duration - standard_hours)
                
                # Add to timesheet
                entry = {
                    "Employee": employee,
                    "Employee ID": employee_id,
                    "Date": date,
                    "Shift": shift_type,
                    "Project": project,
                    "Task Category": task_category,
                    "Start Time": actual_start.strftime("%H:%M"),
                    "End Time": actual_end.strftime("%H:%M"),
                    "Duration (hrs)": round(duration, 2),
                    "Overtime (hrs)": round(overtime, 2),
                    "Late (min)": round(late_minutes),
                    "Early Departure (min)": round(early_minutes),
                    "Status": status,
                    "Description": task_description,
                    "Entry Timestamp": datetime.now()
                }
                
                st.session_state.timesheet.append(entry)
                
                # Add notification if late
                if late_minutes > 15:
                    st.session_state.notifications.append({
                        "type": "Late Arrival",
                        "employee": employee,
                        "minutes": late_minutes,
                        "date": date
                    })
                
                st.success("Time entry added successfully!")
                st.balloons()

# Main Dashboard
if st.session_state.timesheet:
    df = pd.DataFrame(st.session_state.timesheet)
    
    # Apply filters
    if selected_employee != "All Employees":
        df = df[df["Employee"] == selected_employee]
    if selected_date:
        df = df[df["Date"] == pd.to_datetime(selected_date)]
    if search_term:
        df = df[df.apply(lambda row: search_term.lower() in str(row.values).any(), axis=1)]
    
    if not df.empty:
        # Performance Metrics
        st.markdown("## 📊 Performance Dashboard")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Hours", f"{df['Duration (hrs)'].sum():.1f}")
        col2.metric("Overtime Hours", f"{df['Overtime (hrs)'].sum():.1f}")
        col3.metric("Avg. Late Arrival", f"{df['Late (min)'].mean():.1f} min")
        col4.metric("Productivity", f"{df['Duration (hrs)'].mean():.1f} hrs/day")
        
        # Data Display
        st.markdown("## 📝 Time Entries")
        st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True)
        
        # Analytics Section
        st.markdown("## 📈 Analytics")
        
        tab1, tab2, tab3 = st.tabs(["Shift Analysis", "Employee Performance", "Export Data"])
        
        with tab1:
            fig1 = px.pie(df, names="Shift", title="Time Distribution by Shift")
            st.plotly_chart(fig1, use_container_width=True)
            
            fig2 = px.bar(df.groupby("Task Category")["Duration (hrs)"].sum().reset_index(), 
                         x="Task Category", y="Duration (hrs)", title="Hours by Task Type")
            st.plotly_chart(fig2, use_container_width=True)
        
        with tab2:
            performance_df = df.groupby("Employee").agg({
                "Duration (hrs)": "sum",
                "Overtime (hrs)": "sum",
                "Late (min)": "mean"
            })
            
            fig3 = px.bar(performance_df, x=performance_df.index, y="Duration (hrs)", 
                         title="Total Hours by Employee")
            st.plotly_chart(fig3, use_container_width=True)
        
        with tab3:
            st.markdown("### Export Options")
            
            # Excel Export
            excel_data = BytesIO()
            with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button(
                label="📊 Export to Excel",
                data=excel_data.getvalue(),
                file_name="timesheet_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # PDF Export
            def generate_pdf(data):
                buffer = BytesIO()
                p = canvas.Canvas(buffer, pagesize=letter)
                p.drawString(100, 750, "Time Sheet Report")
                y = 700
                for _, row in data.iterrows():
                    p.drawString(100, y, f"{row['Employee']}: {row['Duration (hrs)']} hours")
                    y -= 20
                    if y < 50:
                        p.showPage()
                        y = 750
                p.save()
                return buffer.getvalue()
            
            st.download_button(
                label="📄 Export to PDF",
                data=generate_pdf(df.head(10)),
                file_name="timesheet_report.pdf",
                mime="application/pdf"
            )
        
        # Notifications
        if st.session_state.notifications:
            with st.expander("🔔 Notifications", expanded=True):
                for note in st.session_state.notifications:
                    st.warning(f"{note['employee']} was {note['minutes']} min late on {note['date']}")
    else:
        st.info("No records match your filters")
else:
    st.info("No time entries recorded yet. Add your first entry above.")

# Quick Actions
st.sidebar.markdown("### Quick Actions")
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()
if st.sidebar.button("🧹 Clear Filters"):
    selected_employee = "All Employees"
    selected_date = None

# Footer
st.markdown("---")
st.markdown("Time Sheet InterSoft Pro © 2023 | v3.0")
