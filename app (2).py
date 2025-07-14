import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time
from io import BytesIO

# Configure page settings
st.set_page_config(
    page_title="⏱ Time Sheet InterSoft", 
    layout="wide",
    page_icon="⏱️"
)

# Dark theme CSS styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
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
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    .status-card {
        background: var(--dark-card);
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        border: 1px solid var(--dark-border);
    }
    
    .status-value {
        font-size: 1.8rem;
        font-weight: 600;
        color: var(--primary);
    }
    
    .stDataFrame {
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        background-color: var(--dark-card) !important;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(107, 115, 255, 0.4);
    }
    
    /* Dark theme for sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--dark-card) !important;
        border-right: 1px solid var(--dark-border);
    }
    
    /* Dark theme for tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--dark-card) !important;
        border-bottom: 1px solid var(--dark-border);
    }
    
    /* Dark theme for select boxes */
    [data-baseweb="select"] {
        background-color: var(--dark-card) !important;
        color: var(--dark-text) !important;
    }
    
    /* Dark theme for date input */
    [data-baseweb="input"] {
        background-color: var(--dark-card) !important;
        color: var(--dark-text) !important;
    }
    
    /* Dark theme for text input */
    .stTextInput input {
        background-color: var(--dark-card) !important;
        color: var(--dark-text) !important;
    }
    
    /* Dark theme for text area */
    .stTextArea textarea {
        background-color: var(--dark-card) !important;
        color: var(--dark-text) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Shift configurations with additional details
MORNING_SHIFT = {
    'start': time(8, 30),
    'end': time(17, 30),
    'name': 'Morning Shift (8:30 AM - 5:30 PM)',
    'break_duration': 60,  # minutes
    'description': 'Standard office hours with 1-hour lunch break'
}

EVENING_SHIFT = {
    'start': time(15, 0),
    'end': time(23, 0),
    'name': 'Evening Shift (3:00 PM - 11:00 PM)',
    'break_duration': 30,  # minutes
    'description': 'Evening coverage shift with 30-minute dinner break'
}

# Initialize session state
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

# --- Header Section ---
st.markdown(f"""
    <div class="header">
        <div class="header-title">⏱ Time Sheet InterSoft</div>
        <div class="header-subtitle">Professional Attendance & Time Tracking System | v2.0</div>
    </div>
""", unsafe_allow_html=True)

# --- Sidebar Filters ---
with st.sidebar:
    st.header("🔍 Filter Options")
    selected_employee = st.selectbox(
        "Employee Filter", 
        options=["All Employees"] + sorted(list(set([row.get("Employee", "") for row in st.session_state.timesheet if "Employee" in row]))),
        index=0
    )
    selected_shift = st.selectbox(
        "Shift Filter",
        options=["All Shifts", MORNING_SHIFT['name'], EVENING_SHIFT['name']],
        index=0
    )
    selected_date = st.date_input(
        "Date Filter", 
        value=None,
        help="Filter entries by specific date"
    )
    
    # Additional filters
    show_late_only = st.checkbox("Show only late arrivals", False)
    show_early_only = st.checkbox("Show only early departures", False)
    
    # Shift information
    st.markdown("""
        <div style='margin-top: 2rem; background: var(--dark-card); padding:1.5rem; border-radius:10px; border: 1px solid var(--dark-border);'>
        <h4>Shift Information</h4>
        <p><strong>Morning Shift:</strong> {}</p>
        <p><em>{}</em></p>
        <p><strong>Evening Shift:</strong> {}</p>
        <em>{}</em>
        </div>
    """.format(
        MORNING_SHIFT['name'],
        MORNING_SHIFT['description'],
        EVENING_SHIFT['name'],
        EVENING_SHIFT['description']
    ), unsafe_allow_html=True)
    
    # Statistics
    total_hours = sum([row.get("Duration (hrs)", 0) for row in st.session_state.timesheet if "Duration (hrs)" in row])
    late_entries = sum([1 for row in st.session_state.timesheet if row.get("Late (min)", 0) > 0])
    overtime_hours = sum([max(0, row.get("Duration (hrs)", 0) - 8) for row in st.session_state.timesheet])
    
    st.markdown("""
        <div style='margin-top: 2rem; background: var(--dark-card); padding:1.5rem; border-radius:10px; border: 1px solid var(--dark-border);'>
        <h4>System Statistics</h4>
        <p>Total Entries: <strong>{}</strong></p>
        <p>Total Hours: <strong>{:.1f}</strong></p>
        <p>Overtime Hours: <strong>{:.1f}</strong></p>
        <p>Late Arrivals: <strong>{}</strong></p>
        </div>
    """.format(
        len(st.session_state.timesheet),
        total_hours,
        overtime_hours,
        late_entries
    ), unsafe_allow_html=True)

# --- Time Entry Form ---
with st.expander("➕ Add New Attendance Entry", expanded=True):
    with st.form("attendance_form", clear_on_submit=True):
        cols = st.columns([1, 1, 1])
        with cols[0]:
            employee = st.text_input("Employee Name*", placeholder="John Smith")
            date = st.date_input("Date*", datetime.today())
            shift_type = st.selectbox("Shift Type*", [MORNING_SHIFT['name'], EVENING_SHIFT['name']])
            
        with cols[1]:
            actual_start = st.time_input("Actual Start Time*")
            project = st.text_input("Project Name*", placeholder="Project Alpha")
            task_category = st.selectbox("Task Category", ["Development", "Testing", "Meeting", "Documentation", "Support"])
            
        with cols[2]:
            actual_end = st.time_input("Actual End Time*")
            status = st.selectbox("Status", ["Present", "Half Day", "Leave", "Sick Leave", "Remote Work"])
        
        task_description = st.text_area("Work Description", 
                                      placeholder="Describe work performed...",
                                      height=100)
        
        submitted = st.form_submit_button("Submit Attendance", 
                                        help="All fields marked with * are required")

        if submitted:
            if not all([employee, project, actual_start, actual_end]):
                st.error("Please complete all required fields (*)")
            elif actual_end <= actual_start:
                st.error("End time must be after start time")
            else:
                # Calculate shift details
                shift = MORNING_SHIFT if shift_type == MORNING_SHIFT['name'] else EVENING_SHIFT
                
                # Calculate duration
                start_datetime = datetime.combine(datetime.today(), actual_start)
                end_datetime = datetime.combine(datetime.today(), actual_end)
                duration = (end_datetime - start_datetime).total_seconds() / 3600
                
                # Calculate late arrival
                scheduled_start = datetime.combine(datetime.today(), shift['start'])
                late_minutes = max(0, (start_datetime - scheduled_start).total_seconds() / 60)
                
                # Calculate early departure
                scheduled_end = datetime.combine(datetime.today(), shift['end'])
                early_minutes = max(0, (scheduled_end - end_datetime).total_seconds() / 60)
                
                # Calculate overtime
                overtime = max(0, duration - (8 if shift_type == MORNING_SHIFT['name'] else 8.5))
                
                st.session_state.timesheet.append({
                    "Employee": employee,
                    "Date": date,
                    "Shift": shift_type,
                    "Scheduled Start": shift['start'].strftime("%H:%M"),
                    "Scheduled End": shift['end'].strftime("%H:%M"),
                    "Actual Start": actual_start.strftime("%H:%M"),
                    "Actual End": actual_end.strftime("%H:%M"),
                    "Duration (hrs)": round(duration, 2),
                    "Overtime (hrs)": round(overtime, 2),
                    "Late (min)": round(late_minutes, 0),
                    "Early Departure (min)": round(early_minutes, 0),
                    "Status": status,
                    "Project": project,
                    "Task Category": task_category,
                    "Work Description": task_description,
                    "Entry Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                st.success("Attendance record successfully added!")
                st.balloons()

# --- Dashboard ---
if st.session_state.timesheet:
    df = pd.DataFrame(st.session_state.timesheet)
    
    # Apply filters
    if selected_employee != "All Employees":
        df = df[df["Employee"] == selected_employee]
    if selected_shift != "All Shifts":
        df = df[df["Shift"] == selected_shift]
    if selected_date:
        df = df[df["Date"] == pd.to_datetime(selected_date)]
    if show_late_only:
        df = df[df["Late (min)"] > 0]
    if show_early_only:
        df = df[df["Early Departure (min)"] > 0]
    
    if not df.empty:
        # Summary cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class="status-card">
                    <div>Total Hours Worked</div>
                    <div class="status-value">{df["Duration (hrs)"].sum():.1f} hrs</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="status-card">
                    <div>Overtime Hours</div>
                    <div class="status-value">{df["Overtime (hrs)"].sum():.1f} hrs</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="status-card">
                    <div>Average Late Arrival</div>
                    <div class="status-value">{df["Late (min)"].mean():.1f} min</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
                <div class="status-card">
                    <div>Early Departures</div>
                    <div class="status-value">{len(df[df["Early Departure (min)"] > 0])}</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Main dataframe
        st.markdown("""
            <h2 style='margin-top: 2rem;'>Attendance Records</h2>
        """, unsafe_allow_html=True)
        
        display_cols = [
            "Employee", "Date", "Shift", 
            "Scheduled Start", "Scheduled End",
            "Actual Start", "Actual End",
            "Duration (hrs)", "Overtime (hrs)",
            "Late (min)", "Early Departure (min)", 
            "Status", "Project", "Task Category"
        ]
        
        st.dataframe(
            df[display_cols].sort_values("Date", ascending=False),
            column_config={
                "Duration (hrs)": st.column_config.NumberColumn(format="%.2f"),
                "Overtime (hrs)": st.column_config.NumberColumn(format="%.2f"),
                "Late (min)": st.column_config.NumberColumn(format="%.0f"),
                "Early Departure (min)": st.column_config.NumberColumn(format="%.0f"),
                "Date": st.column_config.DateColumn(format="YYYY-MM-DD")
            },
            use_container_width=True,
            height=600
        )
        
        # --- Analytics Section ---
        st.markdown("""
            <div style='border-top: 1px solid var(--dark-border); margin: 2rem 0;'></div>
            <h2>Attendance Analytics</h2>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["Shift Analysis", "Employee Performance", "Project Analysis", "Data Export"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                fig1 = px.pie(df, names="Shift", values="Duration (hrs)",
                             title="Hours by Shift Type",
                             hole=0.3,
                             color_discrete_sequence=px.colors.qualitative.Dark24)
                fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                                 paper_bgcolor='rgba(0,0,0,0)',
                                 font_color=st.get_option("theme.textColor"))
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = px.box(df, x="Shift", y="Late (min)",
                             title="Late Arrivals by Shift",
                             color="Shift",
                             color_discrete_sequence=px.colors.qualitative.Dark24)
                fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                                 paper_bgcolor='rgba(0,0,0,0)',
                                 font_color=st.get_option("theme.textColor")))
                st.plotly_chart(fig2, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                fig3 = px.bar(df.groupby("Employee")["Duration (hrs)"].sum().reset_index().sort_values("Duration (hrs)", ascending=False),
                             x="Employee", y="Duration (hrs)",
                             title="Total Hours by Employee",
                             color="Employee",
                             color_discrete_sequence=px.colors.qualitative.Dark24)
                fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                                 paper_bgcolor='rgba(0,0,0,0)',
                                 font_color=st.get_option("theme.textColor")))
                st.plotly_chart(fig3, use_container_width=True)
            
            with col2:
                fig4 = px.bar(df.groupby("Employee")["Late (min)"].mean().reset_index().sort_values("Late (min)", ascending=False),
                             x="Employee", y="Late (min)",
                             title="Average Late Arrival by Employee",
                             color="Employee",
                             color_discrete_sequence=px.colors.qualitative.Dark24)
                fig4.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                                 paper_bgcolor='rgba(0,0,0,0)',
                                 font_color=st.get_option("theme.textColor")))
                st.plotly_chart(fig4, use_container_width=True)
        
        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                fig5 = px.bar(df.groupby("Project")["Duration (hrs)"].sum().reset_index().sort_values("Duration (hrs)", ascending=False),
                             x="Project", y="Duration (hrs)",
                             title="Total Hours by Project",
                             color="Project",
                             color_discrete_sequence=px.colors.qualitative.Dark24)
                fig5.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                                 paper_bgcolor='rgba(0,0,0,0)',
                                 font_color=st.get_option("theme.textColor")))
                st.plotly_chart(fig5, use_container_width=True)
            
            with col2:
                fig6 = px.pie(df, names="Task Category", values="Duration (hrs)",
                             title="Time Distribution by Task Category",
                             hole=0.3,
                             color_discrete_sequence=px.colors.qualitative.Dark24)
                fig6.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                                 paper_bgcolor='rgba(0,0,0,0)',
                                 font_color=st.get_option("theme.textColor")))
                st.plotly_chart(fig6, use_container_width=True)
        
        with tab4:
            st.markdown("""
                <h4>Export Attendance Data</h4>
                <p>Download records for payroll processing or HR reporting.</p>
            """, unsafe_allow_html=True)
            
            def convert_to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Attendance')
                    workbook = writer.book
                    worksheet = writer.sheets['Attendance']
                    
                    # Format headers
                    header_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'valign': 'top',
                        'fg_color': '#4a6fa5',
                        'font_color': 'white',
                        'border': 1
                    })
                    
                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                    
                    # Auto-adjust columns
                    worksheet.autofit()
                    
                return output.getvalue()
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📊 Export to Excel",
                    data=convert_to_excel(df),
                    file_name=f"Attendance_Report_{datetime.today().strftime('%Y%m%d')}.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            with col2:
                st.download_button(
                    label="📄 Export to CSV",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name=f"Attendance_Data_{datetime.today().strftime('%Y%m%d')}.csv",
                    mime='text/csv'
                )
    else:
        st.info("No records match your current filters")
else:
    st.info("""
        ℹ️ No attendance records have been entered yet. 
        Use the form above to add your first record.
    """)

# Footer
st.markdown("""
    <div style='border-top: 1px solid var(--dark-border); margin-top: 2rem; padding-top: 1rem; color: var(--dark-text); opacity: 0.7;'>
    <p>Time Sheet InterSoft © 2023 | Version 2.1 | Professional Attendance Management System</p>
    </div>
""", unsafe_allow_html=True)
