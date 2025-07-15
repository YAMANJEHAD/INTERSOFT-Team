import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time, timedelta
from io import BytesIO
import calendar
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import numpy as np

# --- Page Configuration ---
st.set_page_config(
    page_title="⏱ Professional Time Tracker | INTERSOFT POS - FLM",
    layout="wide",
    page_icon="⏱️"
)

# --- Professional Dark Theme Styling ---
st.markdown("""
    <style>
    :root {
        --primary: #3949ab;
        --primary-dark: #1a237e;
        --secondary: #ff5722;
        --text: #f5f5f5;
        --background: #121212;
        --surface: #1e1e1e;
        --error: #cf6679;
    }
    
    html, body, [class*="css"] {
        font-family: 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        background-color: var(--background);
        color: var(--text);
    }
    
    .header {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%);
        color: white;
        padding: 2.5rem 1rem;
        border-radius: 0 0 16px 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        margin-bottom: 3rem;
        text-align: center;
    }
    
    .card {
        background: var(--surface);
        border-radius: 12px;
        padding: 1.75rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        border-left: 5px solid var(--primary);
    }
    
    .stSelectbox, .stTextInput, .stTimeInput, .stTextArea, .stNumberInput, .stDateInput {
        background-color: #252535 !important;
        border-radius: 8px !important;
        border: 1px solid #3d3d4d !important;
        padding: 0.5rem !important;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    }
    
    .stDataFrame {
        border-radius: 12px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2) !important;
    }
    
    .task-item {
        background-color: #252535;
        padding: 1.25rem;
        border-radius: 10px;
        margin-bottom: 1.25rem;
        border-left: 4px solid var(--primary);
        transition: all 0.3s ease;
    }
    
    .task-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }
    
    .metric-card {
        background: var(--surface);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    
    .tab-content {
        padding: 1.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
    <div class="header">
        <h1 style="margin:0;font-weight:600;letter-spacing:0.5px;">INTERSOFT POS</h1>
        <h3 style="margin:0;font-weight:400;opacity:0.9;">FLM Department - Professional Time & Work Management System</h3>
    </div>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "work_breakdown" not in st.session_state:
    st.session_state.work_breakdown = []

# --- Enhanced Shift Options ---
SHIFTS = {
    "Morning Shift (8:30 AM - 5:30 PM)": {'start': time(8, 30), 'end': time(17, 30), 'break_duration': timedelta(minutes=60)},
    "Evening Shift (3:00 PM - 11:00 PM)": {'start': time(15, 0), 'end': time(23, 0), 'break_duration': timedelta(minutes=45)},
    "Night Shift (10:00 PM - 6:00 AM)": {'start': time(22, 0), 'end': time(6, 0), 'break_duration': timedelta(minutes=60)},
    "Flexible Shift": {'start': time(9, 0), 'end': time(17, 0), 'break_duration': timedelta(minutes=30)},
    "Custom Shift": {'start': time(8, 0), 'end': time(17, 0), 'break_duration': timedelta(minutes=0)}
}

# --- Comprehensive Task Categories with Metadata ---
TASK_CATEGORIES = {
    "TOMS Operations": {
        "subcategories": ["Device Setup", "System Maintenance", "Troubleshooting", "Software Update", "Configuration"],
        "requires_time": True,
        "icon": "💻",
        "department": "IT",
        "billable": True
    },
    "Paper Management": {
        "subcategories": ["Regular Paper Order", "Thermal Paper Request", "Special Paper Handling", "Inventory Check"],
        "requires_time": False,
        "icon": "📄",
        "department": "Operations",
        "billable": False
    },
    "Job Order Processing": {
        "subcategories": ["Installation", "Configuration", "Repair", "Inspection", "Preventive Maintenance"],
        "requires_time": True,
        "icon": "🛠️",
        "department": "Field Service",
        "billable": True
    },
    "CRM Activities": {
        "subcategories": ["Customer Support", "Issue Resolution", "Account Management", "Client Training", "Feedback Collection"],
        "requires_time": True,
        "icon": "👥",
        "department": "Customer Service",
        "billable": True
    },
    "Meetings": {
        "subcategories": ["Team Sync", "Client Meeting", "Management Review", "Project Planning", "Retrospective"],
        "requires_time": True,
        "icon": "📅",
        "department": "All",
        "billable": False
    },
    "Training & Development": {
        "subcategories": ["New Employee Onboarding", "Product Training", "Software Training", "Safety Training", "Skill Development"],
        "requires_time": True,
        "icon": "🎓",
        "department": "HR",
        "billable": False
    },
    "Administrative Work": {
        "subcategories": ["Documentation", "Reporting", "Email Correspondence", "Data Entry", "Scheduling"],
        "requires_time": True,
        "icon": "📋",
        "department": "Administration",
        "billable": False
    }
}

# --- Detailed Priority Levels ---
PRIORITY_LEVELS = {
    "Low (P4)": {"emoji": "🟢", "severity": 1, "response_time": "Within 5 days"},
    "Medium (P3)": {"emoji": "🟡", "severity": 2, "response_time": "Within 3 days"},
    "High (P2)": {"emoji": "🔴", "severity": 3, "response_time": "Within 24 hours"},
    "Critical (P1)": {"emoji": "⚠️", "severity": 4, "response_time": "Immediate"},
    "Emergency (P0)": {"emoji": "🚨", "severity": 5, "response_time": "Drop everything"}
}

# --- Comprehensive Status Options ---
STATUS_OPTIONS = {
    "Not Started": {"color": "#9e9e9e", "icon": "⏸️"},
    "In Progress": {"color": "#2196f3", "icon": "🔄"},
    "On Hold": {"color": "#ff9800", "icon": "⏸️"},
    "Completed": {"color": "#4caf50", "icon": "✅"},
    "Cancelled": {"color": "#f44336", "icon": "❌"},
    "Pending Review": {"color": "#ffc107", "icon": "🔍"},
    "Blocked": {"color": "#9c27b0", "icon": "🚧"}
}

# --- Work Types ---
WORK_TYPES = {
    "Project Work": "📂",
    "Routine Maintenance": "⚙️",
    "Emergency Fix": "🚨",
    "Customer Request": "👥",
    "Internal Improvement": "🏗️",
    "Documentation": "📝",
    "Research": "🔍"
}

# --- Time Entry Form ---
with st.expander("⏱️ Add New Time Entry", expanded=True):
    with st.form("time_entry_form", clear_on_submit=True):
        st.markdown("### 🧑‍💼 Employee Information")
        emp_col1, emp_col2 = st.columns(2)
        with emp_col1:
            employee = st.text_input("Full Name *", placeholder="John D. Smith")
            employee_id = st.text_input("Employee ID", placeholder="FLM-1234")
        with emp_col2:
            department = st.selectbox("Department *", ["Field Operations", "Technical Support", "Customer Service", "Management", "Administration"])
            position = st.text_input("Position", placeholder="Field Technician")
        
        st.markdown("### 🕒 Shift Details")
        shift_col1, shift_col2 = st.columns(2)
        with shift_col1:
            shift_type = st.selectbox("Shift Type *", list(SHIFTS.keys()))
            
            if shift_type == "Custom Shift":
                custom_col1, custom_col2 = st.columns(2)
                with custom_col1:
                    start_time = st.time_input("Start Time *", value=time(8, 0))
                with custom_col2:
                    end_time = st.time_input("End Time *", value=time(17, 0))
                break_duration = st.time_input("Break Duration", value=time(0, 30))
            else:
                start_time = st.time_input("Start Time *", value=SHIFTS[shift_type]['start'])
                end_time = st.time_input("End Time *", value=SHIFTS[shift_type]['end'])
                # Convert timedelta to time for the default value
                break_delta = SHIFTS[shift_type]['break_duration']
                break_time = time(break_delta.seconds // 3600, (break_delta.seconds // 60) % 60)
                break_duration = st.time_input("Break Duration", value=break_time)
        
        with shift_col2:
            date = st.date_input("Date *", value=datetime.today())
            timezone = st.selectbox("Timezone", ["GMT+3 (Egypt)", "GMT+4 (UAE)", "GMT+5 (Pakistan)", "GMT+0 (UK)"])
            overtime = st.checkbox("Overtime Work")
            if overtime:
                overtime_hours = st.number_input("Overtime Hours", min_value=0.5, max_value=12.0, step=0.5, value=1.0)
        
        st.markdown("### 📋 Work Details")
        work_col1, work_col2 = st.columns(2)
        with work_col1:
            task_category = st.selectbox("Task Category *", list(TASK_CATEGORIES.keys()), 
                                      format_func=lambda x: f"{TASK_CATEGORIES[x]['icon']} {x}")
            
            if TASK_CATEGORIES[task_category]['subcategories']:
                task_subcategory = st.selectbox("Subcategory *", TASK_CATEGORIES[task_category]['subcategories'])
            else:
                task_subcategory = "General"
            
            work_type = st.selectbox("Work Type", list(WORK_TYPES.keys()), 
                                   format_func=lambda x: f"{WORK_TYPES[x]} {x}")
            
        with work_col2:
            priority = st.selectbox("Priority *", list(PRIORITY_LEVELS.keys()), 
                                   format_func=lambda x: f"{PRIORITY_LEVELS[x]['emoji']} {x}")
            
            status = st.selectbox("Status", list(STATUS_OPTIONS.keys()), 
                                 format_func=lambda x: f"{STATUS_OPTIONS[x]['icon']} {x}")
            
            billable = st.checkbox("Billable Work", value=TASK_CATEGORIES[task_category]['billable'])
        
        st.markdown("### 📝 Task Description")
        work_description = st.text_area("Detailed Description *", 
                                      placeholder="Provide comprehensive details about the work performed, including:\n- Specific actions taken\n- Tools/equipment used\n- Challenges encountered\n- Solutions implemented\n- Outcomes achieved", 
                                      height=150)
        
        st.markdown("### ⏳ Time Breakdown")
        time_col1, time_col2, time_col3 = st.columns(3)
        with time_col1:
            planning_time = st.time_input("Planning Time", value=time(0, 15))
        with time_col2:
            execution_time = st.time_input("Execution Time", value=time(1, 0))
        with time_col3:
            review_time = st.time_input("Review/Testing Time", value=time(0, 15))
        
        st.markdown("### 📊 Additional Details")
        additional_col1, additional_col2 = st.columns(2)
        with additional_col1:
            client_name = st.text_input("Client/Project Name", placeholder="Client XYZ / Project ABC")
            reference_number = st.text_input("Reference/Ticket Number", placeholder="TKT-12345")
        with additional_col2:
            location = st.text_input("Location", placeholder="Head Office / Field Site")
            equipment_used = st.text_input("Equipment Used", placeholder="Laptop, Multimeter, etc.")
        
        # Submit Button - Fixed position at the end of the form
        submitted = st.form_submit_button("📌 Submit Time Entry", use_container_width=True)
        
        if submitted:
            if not employee or not department or not shift_type or not start_time or not end_time or not work_description:
                st.error("Please fill all required fields (*)")
            elif end_time <= start_time and shift_type != "Night Shift":
                st.error("End time must be after start time")
            else:
                # Calculate total duration
                start_dt = datetime.combine(date, start_time)
                end_dt = datetime.combine(date, end_time)
                if shift_type == "Night Shift" and end_time <= start_time:
                    end_dt += timedelta(days=1)
                
                total_duration = (end_dt - start_dt).total_seconds() / 3600
                break_duration_hrs = (break_duration.hour + break_duration.minute/60)
                net_duration = total_duration - break_duration_hrs
                
                # Time breakdown calculations
                planning_hrs = (planning_time.hour + planning_time.minute/60)
                execution_hrs = (execution_time.hour + execution_time.minute/60)
                review_hrs = (review_time.hour + review_time.minute/60)
                
                # Create comprehensive entry
                entry = {
                    # Employee Info
                    "Employee": employee,
                    "Employee ID": employee_id,
                    "Department": department,
                    "Position": position,
                    
                    # Time Info
                    "Date": date.strftime("%Y-%m-%d"),
                    "Day": calendar.day_name[date.weekday()],
                    "Shift Type": shift_type,
                    "Start Time": start_time.strftime("%I:%M %p"),
                    "End Time": end_time.strftime("%I:%M %p"),
                    "Timezone": timezone,
                    "Total Duration (hrs)": round(total_duration, 2),
                    "Break Duration (hrs)": round(break_duration_hrs, 2),
                    "Net Duration (hrs)": round(net_duration, 2),
                    "Overtime": overtime,
                    "Overtime Hours": overtime_hours if overtime else 0,
                    
                    # Work Details
                    "Task Category": f"{TASK_CATEGORIES[task_category]['icon']} {task_category}",
                    "Subcategory": task_subcategory,
                    "Work Type": f"{WORK_TYPES[work_type]} {work_type}",
                    "Priority": f"{PRIORITY_LEVELS[priority]['emoji']} {priority}",
                    "Status": f"{STATUS_OPTIONS[status]['icon']} {status}",
                    "Billable": billable,
                    
                    # Time Breakdown
                    "Planning Time (hrs)": round(planning_hrs, 2),
                    "Execution Time (hrs)": round(execution_hrs, 2),
                    "Review Time (hrs)": round(review_hrs, 2),
                    "Efficiency Ratio": round(execution_hrs / (planning_hrs + execution_hrs + review_hrs) * 100, 1) if (planning_hrs + execution_hrs + review_hrs) > 0 else 0,
                    
                    # Additional Info
                    "Client/Project": client_name,
                    "Reference/Ticket": reference_number,
                    "Location": location,
                    "Equipment Used": equipment_used,
                    "Work Description": work_description,
                    
                    # Metadata
                    "Recorded At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Recorded By": "System User"  # Could be replaced with actual user
                }
                
                st.session_state.timesheet.append(entry)
                st.success("✅ Time entry added successfully!")
                st.balloons()

# --- Timesheet Display & Analysis ---
if st.session_state.timesheet:
    df = pd.DataFrame(st.session_state.timesheet)
    
    # --- Enhanced Data Display ---
    st.markdown("## 📋 Comprehensive Time Entries")
    
    # Filtering Options
    with st.expander("🔍 Filter Options"):
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        with filter_col1:
            filter_employee = st.multiselect("Filter by Employee", options=sorted(df['Employee'].unique()))
            filter_department = st.multiselect("Filter by Department", options=sorted(df['Department'].unique()))
        with filter_col2:
            filter_category = st.multiselect("Filter by Task Category", options=sorted(df['Task Category'].unique()))
            filter_status = st.multiselect("Filter by Status", options=sorted(df['Status'].unique()))
        with filter_col3:
            date_range = st.date_input("Filter by Date Range", [])
            filter_billable = st.selectbox("Billable Status", ["All", "Billable Only", "Non-Billable"])
    
    # Apply filters
    filtered_df = df.copy()
    if filter_employee:
        filtered_df = filtered_df[filtered_df['Employee'].isin(filter_employee)]
    if filter_department:
        filtered_df = filtered_df[filtered_df['Department'].isin(filter_department)]
    if filter_category:
        filtered_df = filtered_df[filtered_df['Task Category'].isin(filter_category)]
    if filter_status:
        filtered_df = filtered_df[filtered_df['Status'].isin(filter_status)]
    if len(date_range) == 2:
        filtered_df = filtered_df[(filtered_df['Date'] >= str(date_range[0])) & 
                                (filtered_df['Date'] <= str(date_range[1]))]
    if filter_billable == "Billable Only":
        filtered_df = filtered_df[filtered_df['Billable'] == True]
    elif filter_billable == "Non-Billable":
        filtered_df = filtered_df[filtered_df['Billable'] == False]
    
    # Display filtered data with robust styling
    def get_priority_color(priority_str):
        """Safely get color based on priority string"""
        try:
            # Handle cases where the string might be formatted differently
            if '(' in priority_str and ')' in priority_str:
                priority_key = priority_str.split('(')[1].split(')')[0].strip()
            else:
                priority_key = priority_str.split()[-1]  # Get last word as fallback
                
            # Match with our PRIORITY_LEVELS keys
            for key in PRIORITY_LEVELS:
                if priority_key in key:
                    emoji = PRIORITY_LEVELS[key]['emoji']
                    if emoji == '🔴':
                        return '#ff5252'
                    elif emoji == '🟡':
                        return '#ffd740'
                    else:
                        return '#69f0ae'
            return '#69f0ae'
        except:
            return '#69f0ae'
    
    def get_status_color(status_str):
        """Safely get color based on status string"""
        try:
            status_key = status_str.split(' ')[0]  # Get first word
            return STATUS_OPTIONS[status_key]['color']
        except:
            return '#f5f5f5'
    
    styled_df = filtered_df.sort_values("Date", ascending=False).style
    styled_df = styled_df.background_gradient(subset=["Efficiency Ratio"], cmap="RdYlGn")
    styled_df = styled_df.applymap(lambda x: f"color: {get_status_color(x)}", subset=["Status"])
    styled_df = styled_df.applymap(lambda x: f"color: {get_priority_color(x)}", subset=["Priority"])
    styled_df = styled_df.set_properties(**{'background-color': '#1e1e1e', 'color': '#f5f5f5', 'border': '1px solid #333'})
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=600
    )
    
    # --- Advanced Analytics Dashboard ---
    st.markdown("## 📊 Professional Analytics Dashboard")
    
    # Summary Metrics
    st.markdown("### 📈 Key Performance Indicators")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        total_hours = filtered_df['Net Duration (hrs)'].sum()
        st.metric("Total Productive Hours", f"{total_hours:.1f} hrs", 
                 help="Sum of all net working hours excluding breaks")
    with kpi2:
        avg_efficiency = filtered_df['Efficiency Ratio'].mean()
        st.metric("Average Efficiency", f"{avg_efficiency:.1f}%", 
                 help="Execution time as percentage of total task time")
    with kpi3:
        billable_hours = filtered_df[filtered_df['Billable']]['Net Duration (hrs)'].sum()
        st.metric("Billable Hours", f"{billable_hours:.1f} hrs", 
                 f"{billable_hours/total_hours*100:.1f}% of total" if total_hours > 0 else "N/A")
    with kpi4:
        overtime_hours = filtered_df['Overtime Hours'].sum()
        st.metric("Overtime Hours", f"{overtime_hours:.1f} hrs", 
                 f"{overtime_hours/total_hours*100:.1f}% of total" if total_hours > 0 else "N/A")
    
    # Detailed Analytics Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Work Distribution", "Employee Productivity", "Time Analysis", "Advanced Metrics"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### By Category")
            fig1 = px.pie(
                filtered_df, 
                names="Task Category", 
                values="Net Duration (hrs)", 
                title="Time Distribution by Task Category",
                hole=0.4
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.markdown("#### By Department")
            fig2 = px.bar(
                filtered_df.groupby('Department')['Net Duration (hrs)'].sum().reset_index().sort_values('Net Duration (hrs)', ascending=False),
                x='Department',
                y='Net Duration (hrs)',
                title="Total Hours by Department",
                color='Department'
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        st.markdown("#### Employee Productivity Analysis")
        emp_prod_df = filtered_df.groupby('Employee').agg({
            'Net Duration (hrs)': 'sum',
            'Efficiency Ratio': 'mean',
            'Billable': lambda x: sum(x)/len(x)*100
        }).reset_index()
        
        fig3 = px.scatter(
            emp_prod_df,
            x="Net Duration (hrs)",
            y="Efficiency Ratio",
            size="Billable",
            color="Employee",
            hover_name="Employee",
            title="Efficiency vs. Hours Worked",
            labels={
                "Net Duration (hrs)": "Total Hours Worked",
                "Efficiency Ratio": "Average Efficiency (%)",
                "Billable": "Billable Work %"
            }
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with tab3:
        st.markdown("#### Time Utilization Analysis")
        
        time_col1, time_col2 = st.columns(2)
        with time_col1:
            fig4 = px.box(
                filtered_df,
                x="Task Category",
                y="Net Duration (hrs)",
                title="Task Duration Distribution",
                color="Task Category"
            )
            st.plotly_chart(fig4, use_container_width=True)
        
        with time_col2:
            fig5 = px.histogram(
                filtered_df,
                x="Net Duration (hrs)",
                nbins=20,
                title="Time Allocation Distribution",
                marginal="box"
            )
            st.plotly_chart(fig5, use_container_width=True)
    
    with tab4:
        st.markdown("#### Advanced Work Metrics")
        
        # Create a correlation matrix
        numeric_df = filtered_df.select_dtypes(include=[np.number])
        if not numeric_df.empty:
            corr_matrix = numeric_df.corr()
            
            fig6 = px.imshow(
                corr_matrix,
                text_auto=True,
                title="Metrics Correlation Matrix",
                color_continuous_scale='RdBu',
                zmin=-1,
                zmax=1
            )
            st.plotly_chart(fig6, use_container_width=True)
        else:
            st.info("No numeric data available for correlation analysis")
    
    # --- Professional Reporting ---
    st.markdown("## 📤 Professional Report Generation")
    
    report_col1, report_col2 = st.columns(2)
    with report_col1:
        report_scope = st.selectbox("Report Scope", ["Current View", "All Data", "Date Range"])
        report_format = st.selectbox("Report Format", ["PDF (Detailed)", "Excel (Data)", "HTML (Interactive)"])
    with report_col2:
        report_title = st.text_input("Report Title", "FLM Time Tracking Report")
        report_notes = st.text_area("Report Notes", "Key observations and analysis...")
    
    if st.button("🖨️ Generate Comprehensive Report", use_container_width=True):
        with st.spinner("Generating professional report..."):
            # Excel Report
            if report_format == "Excel (Data)":
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    # Main Data Sheet
                    filtered_df.to_excel(writer, index=False, sheet_name="Time Entries")
                    
                    # Summary Sheets
                    summary_df = filtered_df.groupby(['Employee', 'Task Category']).agg({
                        'Net Duration (hrs)': 'sum',
                        'Billable': 'sum'
                    }).reset_index()
                    summary_df.to_excel(writer, index=False, sheet_name="Summary")
                    
                    # Efficiency Analysis
                    efficiency_df = filtered_df.groupby('Employee').agg({
                        'Net Duration (hrs)': 'sum',
                        'Efficiency Ratio': 'mean'
                    }).reset_index()
                    efficiency_df.to_excel(writer, index=False, sheet_name="Efficiency")
                    
                    # Get workbook and add formatting
                    workbook = writer.book
                    worksheet = writer.sheets["Time Entries"]
                    
                    header_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'valign': 'top',
                        'fg_color': '#1a237e',
                        'font_color': 'white',
                        'border': 1
                    })
                    
                    for col_num, value in enumerate(filtered_df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                    
                    worksheet.autofilter(0, 0, 0, len(filtered_df.columns)-1)
                    worksheet.freeze_panes(1, 0)
                
                st.download_button(
                    label="📥 Download Excel Report",
                    data=excel_buffer.getvalue(),
                    file_name=f"FLM_Time_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            # PDF Report
            elif report_format == "PDF (Detailed)":
                pdf_buffer = BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
                
                styles = getSampleStyleSheet()
                elements = []
                
                # Title
                title = Paragraph(f"<b>{report_title}</b>", styles['Title'])
                elements.append(title)
                
                # Report Details
                details_text = f"""
                <b>Report Scope:</b> {report_scope}<br/>
                <b>Date Range:</b> {filtered_df['Date'].min()} to {filtered_df['Date'].max()}<br/>
                <b>Generated On:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}<br/>
                <b>Total Entries:</b> {len(filtered_df)}<br/>
                <b>Total Hours:</b> {total_hours:.1f}
                """
                elements.append(Paragraph(details_text, styles['Normal']))
                elements.append(Spacer(1, 24))
                
                # Summary Table
                summary_data = [
                    ["Metric", "Value"],
                    ["Total Employees", filtered_df['Employee'].nunique()],
                    ["Total Departments", filtered_df['Department'].nunique()],
                    ["Average Efficiency", f"{avg_efficiency:.1f}%"],
                    ["Billable Hours", f"{billable_hours:.1f} hrs"],
                    ["Overtime Hours", f"{overtime_hours:.1f} hrs"]
                ]
                
                summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), '#1a237e'),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), '#f5f5f5'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(summary_table)
                elements.append(Spacer(1, 24))
                
                # Time Entries
                elements.append(Paragraph("<b>Detailed Time Entries</b>", styles['Heading2']))
                
                # Prepare data for PDF table
                pdf_data = [list(filtered_df.columns)]
                for _, row in filtered_df.iterrows():
                    pdf_data.append(list(row))
                
                pdf_table = Table(pdf_data)
                pdf_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), '#1a237e'),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), '#f5f5f5'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 6)
                ]))
                elements.append(pdf_table)
                
                # Notes
                if report_notes:
                    elements.append(Spacer(1, 24))
                    elements.append(Paragraph("<b>Analyst Notes</b>", styles['Heading2']))
                    elements.append(Paragraph(report_notes, styles['Normal']))
                
                doc.build(elements)
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_buffer.getvalue(),
                    file_name=f"FLM_Time_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf"
                )
            
            # HTML Report
            else:
                html = filtered_df.to_html(index=False)
                st.download_button(
                    label="🌐 Download HTML Report",
                    data=html,
                    file_name=f"FLM_Time_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                    mime="text/html"
                )

# --- Empty State ---
else:
    st.markdown("""
        <div style="text-align:center; padding:5rem; border:2px dashed #444; border-radius:12px;">
            <h3>No time entries recorded yet</h3>
            <p>Start by adding your first time entry using the form above</p>
        </div>
    """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown("""
    <center>
        <small>INTERSOFT POS - FLM Department • Professional Time & Work Management System • v3.0<br/>
        Report Generated: {}</small>
    </center>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)
