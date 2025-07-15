import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time, timedelta
from io import BytesIO
import calendar
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import numpy as np

# --- Page Configuration ---
st.set_page_config(
    page_title="⏱ Time Tracker | INTERSOFT POS - FLM",
    layout="wide",
    page_icon="⏱️"
)

# --- Simplified Dark Theme Styling ---
st.markdown("""
    <style>
    :root {
        --primary: #3949ab;
        --background: #121212;
        --surface: #1e1e1e;
        --text: #f5f5f5;
    }
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        background-color: var(--background);
        color: var(--text);
    }
    .header {
        background: var(--primary);
        color: white;
        padding: 2rem;
        border-radius: 8px;
        text-align: center;
    }
    .card {
        background: var(--surface);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .stSelectbox, .stTextInput, .stTimeInput, .stTextArea {
        background-color: #252535 !important;
        border-radius: 6px !important;
        border: 1px solid #3d3d4d !important;
    }
    .stButton>button {
        background: var(--primary) !important;
        color: white !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
    }
    .stDataFrame {
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
    <div class="header">
        <h2>INTERSOFT POS - FLM Time Tracker</h2>
    </div>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

# --- Simplified Shift Options ---
SHIFTS = {
    "Morning Shift": {'start': time(8, 30), 'end': time(17, 30), 'break_duration': timedelta(minutes=60)},
    "Evening Shift": {'start': time(15, 0), 'end': time(23, 0), 'break_duration': timedelta(minutes=45)},
    "Night Shift": {'start': time(22, 0), 'end': time(6, 0), 'break_duration': timedelta(minutes=60)},
    "Custom Shift": {'start': time(8, 0), 'end': time(17, 0), 'break_duration': timedelta(minutes=0)}
}

# --- Simplified Task Categories ---
TASK_CATEGORIES = {
    "TOMS Operations": {"icon": "💻", "requires_time": True, "billable": True},
    "Paper Management": {"icon": "📄", "requires_time": False, "billable": False},
    "Job Order Processing": {"icon": "🛠️", "requires_time": True, "billable": True},
    "CRM Activities": {"icon": "👥", "requires_time": True, "billable": True},
    "Meetings": {"icon": "📅", "requires_time": True, "billable": False}
}

# --- Priority Levels ---
PRIORITY_LEVELS = {
    "Low": {"emoji": "🟢"},
    "Medium": {"emoji": "🟡"},
    "High": {"emoji": "🔴"}
}

# --- Status Options ---
STATUS_OPTIONS = {
    "Not Started": {"color": "#9e9e9e", "icon": "⏸️"},
    "In Progress": {"color": "#2196f3", "icon": "🔄"},
    "Completed": {"color": "#4caf50", "icon": "✅"}
}

# --- Time Entry Form ---
with st.expander("⏱ Add Time Entry", expanded=True):
    with st.form("time_entry_form", clear_on_submit=True):
        st.markdown("### Employee")
        employee = st.text_input("Full Name *", placeholder="John Smith")
        department = st.selectbox("Department *", ["Field Operations", "Technical Support", "Customer Service"])

        st.markdown("### Shift")
        shift_type = st.selectbox("Shift Type *", list(SHIFTS.keys()))
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input("Start Time *", value=SHIFTS[shift_type]['start'])
        with col2:
            end_time = st.time_input("End Time *", value=SHIFTS[shift_type]['end'])
        break_duration = st.time_input("Break Duration", value=time(SHIFTS[shift_type]['break_duration'].seconds // 3600, (SHIFTS[shift_type]['break_duration'].seconds // 60) % 60))
        date = st.date_input("Date *", value=datetime.today())

        st.markdown("### Work")
        col1, col2 = st.columns(2)
        with col1:
            task_category = st.selectbox("Task Category *", list(TASK_CATEGORIES.keys()), 
                                       format_func=lambda x: f"{TASK_CATEGORIES[x]['icon']} {x}")
            priority = st.selectbox("Priority *", list(PRIORITY_LEVELS.keys()), 
                                   format_func=lambda x: f"{PRIORITY_LEVELS[x]['emoji']} {x}")
        with col2:
            status = st.selectbox("Status *", list(STATUS_OPTIONS.keys()), 
                                 format_func=lambda x: f"{STATUS_OPTIONS[x]['icon']} {x}")
            billable = st.checkbox("Billable", value=TASK_CATEGORIES[task_category]['billable'])

        work_description = st.text_area("Description *", placeholder="Describe the work performed", height=100)

        submitted = st.form_submit_button("Submit", use_container_width=True)

        if submitted:
            if not (employee and department and shift_type and start_time and end_time and work_description):
                st.error("Please fill all required fields (*)")
            elif end_time <= start_time and shift_type != "Night Shift":
                st.error("End time must be after start time")
            else:
                start_dt = datetime.combine(date, start_time)
                end_dt = datetime.combine(date, end_time)
                if shift_type == "Night Shift" and end_time <= start_time:
                    end_dt += timedelta(days=1)
                
                total_duration = (end_dt - start_dt).total_seconds() / 3600
                break_duration_hrs = (break_duration.hour + break_duration.minute/60)
                net_duration = total_duration - break_duration_hrs

                entry = {
                    "Employee": employee,
                    "Department": department,
                    "Date": date.strftime("%Y-%m-%d"),
                    "Shift Type": shift_type,
                    "Start Time": start_time.strftime("%I:%M %p"),
                    "End Time": end_time.strftime("%I:%M %p"),
                    "Total Duration (hrs)": round(total_duration, 2),
                    "Break Duration (hrs)": round(break_duration_hrs, 2),
                    "Net Duration (hrs)": round(net_duration, 2),
                    "Task Category": f"{TASK_CATEGORIES[task_category]['icon']} {task_category}",
                    "Priority": f"{PRIORITY_LEVELS[priority]['emoji']} {priority}",
                    "Status": f"{STATUS_OPTIONS[status]['icon']} {status}",
                    "Billable": billable,
                    "Work Description": work_description,
                    "Recorded At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                st.session_state.timesheet.append(entry)
                st.success("Time entry added!")
                st.balloons()

# --- Timesheet Display ---
if st.session_state.timesheet:
    df = pd.DataFrame(st.session_state.timesheet)

    st.markdown("## 📋 Time Entries")
    with st.expander("Filter"):
        col1, col2 = st.columns(2)
        with col1:
            filter_employee = st.multiselect("Employee", sorted(df['Employee'].unique()))
            filter_department = st.multiselect("Department", sorted(df['Department'].unique()))
        with col2:
            filter_category = st.multiselect("Task Category", sorted(df['Task Category'].unique()))
            filter_status = st.multiselect("Status", sorted(df['Status'].unique()))

    filtered_df = df.copy()
    if filter_employee:
        filtered_df = filtered_df[filtered_df['Employee'].isin(filter_employee)]
    if filter_department:
        filtered_df = filtered_df[filtered_df['Department'].isin(filter_department)]
    if filter_category:
        filtered_df = filtered_df[filtered_df['Task Category'].isin(filter_category)]
    if filter_status:
        filtered_df = filtered_df[filtered_df['Status'].isin(filter_status)]

    def get_priority_color(priority_str):
        try:
            priority_key = priority_str.split(' ')[-1]
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
        try:
            status_key = status_str.split(' ')[0]
            return STATUS_OPTIONS[status_key]['color']
        except:
            return '#f5f5f5'

    styled_df = filtered_df.sort_values("Date", ascending=False).style
    styled_df = styled_df.applymap(lambda x: f"color: {get_status_color(x)}", subset=["Status"])
    styled_df = styled_df.applymap(lambda x: f"color: {get_priority_color(x)}", subset=["Priority"])
    styled_df = styled_df.set_properties(**{'background-color': '#1e1e1e', 'color': '#f5f5f5', 'border': '1px solid #333'})
    st.dataframe(styled_df, use_container_width=True)

    # --- Simple Analytics ---
    st.markdown("## 📊 Analytics")
    col1, col2 = st.columns(2)
    with col1:
        total_hours = filtered_df['Net Duration (hrs)'].sum()
        st.metric("Total Hours", f"{total_hours:.1f} hrs")
    with col2:
        billable_hours = filtered_df[filtered_df['Billable']]['Net Duration (hrs)'].sum()
        st.metric("Billable Hours", f"{billable_hours:.1f} hrs", 
                 f"{billable_hours/total_hours*100:.1f}%" if total_hours > 0 else "N/A")

    fig = px.pie(
        filtered_df, 
        names="Task Category", 
        values="Net Duration (hrs)", 
        title="Time by Task Category",
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Simplified Report Generation ---
    st.markdown("## 📤 Generate Report")
    report_format = st.selectbox("Format", ["PDF", "Excel"])
    if st.button("Generate Report"):
        with st.spinner("Generating report..."):
            if report_format == "Excel":
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    filtered_df.to_excel(writer, index=False, sheet_name="Time Entries")
                st.download_button(
                    label="Download Excel",
                    data=excel_buffer.getvalue(),
                    file_name=f"Time_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                pdf_buffer = BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
                styles = getSampleStyleSheet()
                elements = []

                elements.append(Paragraph("<b>FLM Time Tracking Report</b>", styles['Title']))
                elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
                elements.append(Spacer(1, 12))

                summary_data = [
                    ["Metric", "Value"],
                    ["Total Hours", f"{total_hours:.1f} hrs"],
                    ["Billable Hours", f"{billable_hours:.1f} hrs"]
                ]
                summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), '#1a237e'),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(summary_table)
                elements.append(Spacer(1, 12))

                pdf_data = [list(filtered_df.columns)] + [list(row) for _, row in filtered_df.iterrows()]
                pdf_table = Table(pdf_data)
                pdf_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), '#1a237e'),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 0), (-1, -1), 8)
                ]))
                elements.append(pdf_table)

                doc.build(elements)
                st.download_button(
                    label="Download PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=f"Time_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )

else:
    st.markdown("""
        <div style="text-align:center; padding:3rem; border:2px dashed #444; border-radius:8px;">
            <h3>No entries yet</h3>
            <p>Add your first time entry above</p>
        </div>
    """, unsafe_allow_html=True)

# --- Footer ---
st.markdown(f"""
    <center>
        <small>INTERSOFT POS - FLM Time Tracker • {datetime.now().strftime('%Y-%m-%d')}</small>
    </center>
""", unsafe_allow_html=True)
