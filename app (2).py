import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# Page Configuration
st.set_page_config(
    page_title="⏱ Time Sheet | INTERSOFT POS - FLM",
    layout="wide",
    page_icon="⏱️"
)

# Professional Dark Theme Styling
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        background-color: #0f1116;
        color: #f0f2f6;
    }
    .header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        color: white;
        padding: 2rem 1rem;
        border-radius: 0 0 12px 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        margin-bottom: 2.5rem;
        text-align: center;
    }
    .status-card {
        background: #1e1e2d;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.25);
        border-left: 4px solid #3949ab;
    }
    .stSelectbox, .stTextInput, .stTimeInput, .stTextArea, .stNumberInput {
        background-color: #252535 !important;
        border-radius: 6px !important;
        border: 1px solid #3d3d4d !important;
    }
    .stButton>button {
        background: linear-gradient(135deg, #3949ab 0%, #1a237e 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
    }
    .stDataFrame {
        border-radius: 10px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }
    .task-item {
        background-color: #252535;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 3px solid #3949ab;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header">
        <h1 style="margin:0;font-weight:600;">INTERSOFT POS</h1>
        <h3 style="margin:0;font-weight:400;">FLM Department - Professional Time Tracking System</h3>
    </div>
""", unsafe_allow_html=True)

# Session State Init
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Enhanced Shifts
SHIFTS = {
    "Morning Shift (8:30 AM - 5:30 PM)": {'start': time(8, 30), 'end': time(17, 30)},
    "Evening Shift (3:00 PM - 11:00 PM)": {'start': time(15, 0), 'end': time(23, 0)},
    "Night Shift (10:00 PM - 6:00 AM)": {'start': time(22, 0), 'end': time(6, 0)},
    "Custom Shift": {'start': time(8, 0), 'end': time(17, 0)}
}

# Enhanced Task Categories with Subcategories
TASK_CATEGORIES = {
    "TOMS": {
        "subcategories": ["Device Setup", "Maintenance", "Troubleshooting", "Software Update"],
        "requires_time": True,
        "icon": "💻"
    },
    "Paper Request": {
        "subcategories": ["Regular Paper", "Thermal Paper", "Special Paper"],
        "requires_time": False,
        "icon": "📄"
    },
    "J.O": {
        "subcategories": ["Installation", "Configuration", "Repair", "Inspection"],
        "requires_time": True,
        "icon": "🛠️"
    },
    "CRM": {
        "subcategories": ["Customer Support", "Issue Resolution", "Account Management", "Training"],
        "requires_time": True,
        "icon": "👥"
    },
    "Meeting": {
        "subcategories": ["Team Meeting", "Client Meeting", "Management Meeting"],
        "requires_time": True,
        "icon": "📅"
    },
    "Training": {
        "subcategories": ["New Employee", "Product Training", "Software Training"],
        "requires_time": True,
        "icon": "🎓"
    }
}

# Priority Levels
PRIORITY_LEVELS = {
    "Low": "🟢",
    "Medium": "🟡",
    "High": "🔴",
    "Critical": "⚠️"
}

# Status Options
STATUS_OPTIONS = ["Not Started", "In Progress", "Completed", "On Hold", "Cancelled"]

# Time Entry Form
with st.expander("➕ Add New Time Entry", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            employee = st.text_input("Employee Name *", placeholder="John Doe")
            shift_type = st.selectbox("Shift Type *", list(SHIFTS.keys()))
            
            if shift_type == "Custom Shift":
                custom_col1, custom_col2 = st.columns(2)
                with custom_col1:
                    start_time = st.time_input("Custom Start Time *", value=time(8, 0))
                with custom_col2:
                    end_time = st.time_input("Custom End Time *", value=time(17, 0))
            else:
                start_time = st.time_input("Start Time *", value=SHIFTS[shift_type]['start'])
                end_time = st.time_input("End Time *", value=SHIFTS[shift_type]['end'])
        
        with col2:
            date = st.date_input("Date *", value=datetime.today())
            task_category = st.selectbox("Task Category *", list(TASK_CATEGORIES.keys()), 
                                      format_func=lambda x: f"{TASK_CATEGORIES[x]['icon']} {x}")
            
            if TASK_CATEGORIES[task_category]['subcategories']:
                task_subcategory = st.selectbox("Subcategory", TASK_CATEGORIES[task_category]['subcategories'])
            else:
                task_subcategory = None
            
            priority = st.selectbox("Priority", list(PRIORITY_LEVELS.keys()), 
                                   format_func=lambda x: f"{PRIORITY_LEVELS[x]} {x}")
        
        # Task Details Section
        st.markdown("### Task Details")
        work_description = st.text_area("Work Description *", placeholder="Detailed description of the work performed...", height=120)
        
        # Multiple Tasks Section
        st.markdown("### Add Multiple Tasks")
        with st.container():
            task_col1, task_col2, task_col3 = st.columns([3, 2, 1])
            with task_col1:
                task_name = st.text_input("Task Name", placeholder="Specific task name")
            with task_col2:
                if TASK_CATEGORIES[task_category]['requires_time']:
                    task_duration = st.time_input("Task Duration", value=time(0, 30))
                else:
                    task_duration = None
            with task_col3:
                task_status = st.selectbox("Status", STATUS_OPTIONS)
            
            # Add Task button - now inside the form
            add_task = st.form_submit_button("Add Task to This Entry", use_container_width=True)
            
            if add_task and task_name:
                task_data = {
                    "name": task_name,
                    "duration": task_duration.strftime("%H:%M") if task_duration else "N/A",
                    "status": task_status
                }
                st.session_state.tasks.append(task_data)
                st.success(f"Task '{task_name}' added!")
                st.rerun()  # Refresh to show the new task
        
        # Display added tasks
        if st.session_state.tasks:
            st.markdown("#### Current Tasks for This Entry")
            for i, task in enumerate(st.session_state.tasks, 1):
                with st.container():
                    st.markdown(f"""
                        <div class="task-item">
                            <strong>Task {i}:</strong> {task['name']}<br>
                            <strong>Duration:</strong> {task['duration']} | 
                            <strong>Status:</strong> {task['status']}
                        </div>
                    """, unsafe_allow_html=True)
        
        # Main Submit Button
        submitted = st.form_submit_button("Submit Time Entry", use_container_width=True)
        
        if submitted:
            if not employee or not shift_type or not start_time or not end_time or not work_description:
                st.error("Please fill all required fields (*)")
            elif end_time <= start_time and shift_type != "Night Shift":
                st.error("End time must be after start time")
            else:
                duration = (datetime.combine(datetime.today(), end_time) - datetime.combine(datetime.today(), start_time)).total_seconds() / 3600
                if shift_type == "Night Shift" and end_time <= start_time:
                    duration = (24 - (start_time.hour + start_time.minute/60) + (end_time.hour + end_time.minute/60))
                
                entry = {
                    "Employee": employee,
                    "Date": date.strftime("%Y-%m-%d"),
                    "Shift": shift_type,
                    "Task Category": f"{TASK_CATEGORIES[task_category]['icon']} {task_category}",
                    "Subcategory": task_subcategory,
                    "Priority": f"{PRIORITY_LEVELS[priority]} {priority}",
                    "Start Time": start_time.strftime("%I:%M %p"),
                    "End Time": end_time.strftime("%I:%M %p"),
                    "Duration (hrs)": round(duration, 2),
                    "Work Description": work_description,
                    "Tasks": st.session_state.tasks.copy() if st.session_state.tasks else None
                }
                
                st.session_state.timesheet.append(entry)
                st.session_state.tasks = []  # Clear tasks for next entry
                st.success("✅ Time entry added successfully!")
                st.rerun()  # Refresh to show the new entry

# Timesheet Display
if st.session_state.timesheet:
    df = pd.DataFrame(st.session_state.timesheet)
    
    # Enhanced DataFrame display
    st.markdown("## 📋 Time Entries")
    display_df = df.drop(columns=['Tasks']).sort_values("Date", ascending=False)
    st.dataframe(
        display_df.style
        .applymap(lambda x: 'color: #4CAF50' if 'High' in str(x) else ('color: #FFC107' if 'Medium' in str(x) else 'color: #f0f2f6'), 
                 subset=["Priority"])
        .set_properties(**{'background-color': '#252535', 'color': '#f0f2f6', 'border': '1px solid #3d3d4d'}),
        use_container_width=True,
        height=600
    )
    
    # Enhanced Analytics Section
    st.markdown("## 📊 Advanced Analytics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        total_hours = df['Duration (hrs)'].sum()
        st.metric("Total Hours Tracked", f"{total_hours:.2f} hrs")
    with col2:
        avg_hours = df['Duration (hrs)'].mean()
        st.metric("Average Shift Duration", f"{avg_hours:.2f} hrs")
    with col3:
        unique_employees = df['Employee'].nunique()
        st.metric("Employees Tracked", unique_employees)
    
    # Interactive Charts
    tab1, tab2, tab3 = st.tabs(["Work Distribution", "Employee Analysis", "Priority Overview"])
    
    with tab1:
        fig1 = px.sunburst(
            df, 
            path=['Task Category', 'Subcategory'], 
            values='Duration (hrs)',
            title="Work Distribution by Category and Subcategory",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with tab2:
        fig2 = px.bar(
            df.groupby('Employee')['Duration (hrs)'].sum().reset_index(),
            x='Employee',
            y='Duration (hrs)',
            title="Total Hours by Employee",
            text='Duration (hrs)',
            color='Duration (hrs)',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        fig3 = px.pie(
            df, 
            names='Priority', 
            title="Task Priority Distribution",
            hole=0.4
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    # Enhanced Export Section
    st.markdown("## 📤 Professional Export Options")
    
    export_col1, export_col2 = st.columns(2)
    with export_col1:
        export_employee = st.selectbox("Filter by Employee", ["All Employees"] + sorted(df['Employee'].unique()))
        export_df = df if export_employee == "All Employees" else df[df['Employee'] == export_employee]
    
    with export_col2:
        date_range = st.date_input("Filter by Date Range", [])
        if len(date_range) == 2:
            export_df = export_df[(export_df['Date'] >= str(date_range[0])) & 
                                (export_df['Date'] <= str(date_range[1]))]
    
    # Excel Export with Multiple Sheets
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        # Main Data Sheet
        export_df.drop(columns=['Tasks']).to_excel(writer, index=False, sheet_name="Time Entries")
        
        # Summary Sheet
        summary_df = export_df.groupby(['Employee', 'Task Category']).agg({
            'Duration (hrs)': 'sum',
            'Priority': 'count'
        }).rename(columns={'Priority': 'Task Count'}).reset_index()
        summary_df.to_excel(writer, index=False, sheet_name="Summary")
        
        # Get the workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets["Time Entries"]
        
        # Add Excel formatting
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#1a237e',
            'font_color': 'white',
            'border': 1
        })
        
        for col_num, value in enumerate(export_df.drop(columns=['Tasks']).columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        worksheet.autofilter(0, 0, 0, len(export_df.columns)-1)
        worksheet.freeze_panes(1, 0)
    
    st.download_button(
        label="📊 Download Excel Report (Professional)",
        data=excel_buffer.getvalue(),
        file_name=f"timesheet_report_{datetime.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Includes formatted data sheet and summary analytics"
    )
    
    # Enhanced PDF Export
    def generate_pdf(data):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("INTERSOFT POS - FLM Professional Timesheet Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Summary
        summary_text = f"""
        <b>Report Summary:</b><br/>
        Period: {data['Date'].min()} to {data['Date'].max()}<br/>
        Total Hours: {data['Duration (hrs)'].sum():.2f}<br/>
        Employees: {data['Employee'].nunique()}<br/>
        Tasks Categories: {data['Task Category'].nunique()}
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 24))
        
        # Data
        story.append(Paragraph("<b>Time Entries:</b>", styles['Heading2']))
        for _, row in data.iterrows():
            entry_text = f"""
            <b>{row['Employee']}</b> | {row['Date']} | {row['Shift']}<br/>
            <font color="#1a237e">{row['Task Category']}</font> | {row['Subcategory']}<br/>
            {row['Start Time']} - {row['End Time']} ({row['Duration (hrs)']} hrs) | Priority: {row['Priority']}<br/>
            <i>{row['Work Description']}</i>
            """
            story.append(Paragraph(entry_text, styles['Normal']))
            story.append(Spacer(1, 12))
        
        doc.build(story)
        return buffer.getvalue()
    
    st.download_button(
        label="📄 Download PDF Report (Professional)",
        data=generate_pdf(export_df),
        file_name=f"timesheet_report_{datetime.today().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        help="Formatted PDF report with summary and all entries"
    )
    
    # Raw Data Export
    st.download_button(
        label="📝 Download Raw Data (CSV)",
        data=export_df.to_csv(index=False).encode('utf-8'),
        file_name="timesheet_raw_data.csv",
        mime="text/csv",
        help="Simple CSV export of all data"
    )
else:
    st.info("No time entries yet. Add your first record using the form above.")

# Footer
st.markdown("---")
st.markdown("""
    <center>
        <small>INTERSOFT POS - FLM Department • Professional Time Tracking System • v2.0<br/>
        Report Generated: {}</small>
    </center>
""".format(datetime.today().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)
