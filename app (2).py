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
    page_title="⏱ FLM Time Tracker | INTERSOFT POS",
    layout="wide",
    page_icon="⏱"
)

# --- Professional Styling with Inter Font ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #3b82f6;
        --background: #0f172a;
        --surface: #1e293b;
        --text: #f1f5f9;
        --accent: #22d3ee;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: var(--background);
        color: var(--text);
    }
    
    .header {
        background: linear-gradient(135deg, var(--primary), #1e40af);
        color: var(--text);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        margin-bottom: 2rem;
    }
    
    .card {
        background: var(--surface);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        border-left: 4px solid var(--accent);
    }
    
    .stSelectbox, .stTextInput, .stTimeInput, .stTextArea {
        background-color: #2d3748 !important;
        border-radius: 8px !important;
        border: 1px solid #4b5563 !important;
        color: var(--text) !important;
    }
    
    .stButton>button {
        background: var(--primary) !important;
        color: var(--text) !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background: #1e40af !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    .stDataFrame {
        border-radius: 12px !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    
    .metric-card {
        background: var(--surface);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    h1, h2, h3 {
        font-weight: 600 !important;
        color: var(--text) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
    <div class="header">
        <h1>⏱ INTERSOFT POS</h1>
        <h3>FLM Time Tracker Dashboard 🚀</h3>
    </div>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

# --- Shift Options (12-hour format handled in form) ---
SHIFTS = {
    "Morning Shift": {'start': time(8, 30), 'end': time(17, 30), 'break_duration': timedelta(minutes=60)},
    "Evening Shift": {'start': time(15, 0), 'end': time(23, 0), 'break_duration': timedelta(minutes=45)},
    "Night Shift": {'start': time(22, 0), 'end': time(6, 0), 'break_duration': timedelta(minutes=60)},
    "Custom Shift": {'start': time(8, 0), 'end': time(17, 0), 'break_duration': timedelta(minutes=0)}
}

# --- Task Categories ---
TASK_CATEGORIES = {
    "TOMS Operations": {"icon": "💻", "billable": True},
    "Paper Management": {"icon": "📄", "billable": False},
    "Job Order Processing": {"icon": "🛠", "billable": True},
    "CRM Activities": {"icon": "👥", "billable": True},
    "Meetings": {"icon": "📅", "billable": False}
}

# --- Priority Levels ---
PRIORITY_LEVELS = {
    "Low": {"emoji": "🟢"},
    "Medium": {"emoji": "🟡"},
    "High": {"emoji": "🔴"}
}

# --- Status Options ---
STATUS_OPTIONS = {
    "Not Started": {"color": "#9e9e9e", "icon": "⏸"},
    "In Progress": {"color": "#3b82f6", "icon": "🔄"},
    "Completed": {"color": "#22c55e", "icon": "✅"}
}

# --- Dashboard Layout ---
st.markdown("## 📊 FLM Dashboard")
tab1, tab2 = st.tabs(["➕ Add Entry", "📈 Analytics"])

with tab1:
    with st.form("time_entry_form", clear_on_submit=True):
        st.markdown("### 👤 Employee")
        col1, col2 = st.columns(2)
        with col1:
            employee = st.text_input("Full Name *", placeholder="John Smith")
        with col2:
            department = st.selectbox("Department *", ["FLM Team", "Field Operations", "Technical Support", "Customer Service"])

        st.markdown("### ⏰ Shift")
        col1, col2, col3 = st.columns(3)
        with col1:
            shift_type = st.selectbox("Shift Type *", list(SHIFTS.keys()))
        with col2:
            start_time = st.time_input("Start Time *", value=SHIFTS[shift_type]['start'], format="hh:mm A")
        with col3:
            end_time = st.time_input("End Time *", value=SHIFTS[shift_type]['end'], format="hh:mm A")
        break_duration = st.time_input("Break Duration", value=time(SHIFTS[shift_type]['break_duration'].seconds // 3600, (SHIFTS[shift_type]['break_duration'].seconds // 60) % 60), format="hh:mm")
        date = st.date_input("Date *", value=datetime.today())

        st.markdown("### 📋 Work")
        col1, col2 = st.columns(2)
        with col1:
            task_category = st.selectbox("Task Category *", list(TASK_CATEGORIES.keys()), 
                                       format_func=lambda x: f"{TASK_CATEGORIES[x]['icon']} {x}")
        with col2:
            status = st.selectbox("Status *", list(STATUS_OPTIONS.keys()), 
                                 format_func=lambda x: f"{STATUS_OPTIONS[x]['icon']} {x}")
        priority = st.selectbox("Priority *", list(PRIORITY_LEVELS.keys()), 
                               format_func=lambda x: f"{PRIORITY_LEVELS[x]['emoji']} {x}")
        billable = st.checkbox("Billable 💰", value=TASK_CATEGORIES[task_category]['billable'])

        work_description = st.text_area("Description *", placeholder="Describe the work performed 📝", height=100)

        submitted = st.form_submit_button("✅ Submit Entry", use_container_width=True)

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
                    "Day": calendar.day_name[date.weekday()],
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
                st.success("🎉 Entry added successfully!")
                st.balloons()

with tab2:
    if st.session_state.timesheet:
        df = pd.DataFrame(st.session_state.timesheet)

        # --- Filters ---
        st.markdown("### 🔍 Filter Entries")
        col1, col2 = st.columns(2)
        with col1:
            filter_employee = st.multiselect("Employee 👤", sorted(df['Employee'].unique()))
            filter_department = st.multiselect("Department 🏢", sorted(df['Department'].unique()))
        with col2:
            filter_category = st.multiselect("Task Category 📋", sorted(df['Task Category'].unique()))
            filter_status = st.multiselect("Status 🔄", sorted(df['Status'].unique()))

        filtered_df = df.copy()
        if filter_employee:
            filtered_df = filtered_df[filtered_df['Employee'].isin(filter_employee)]
        if filter_department:
            filtered_df = filtered_df[filtered_df['Department'].isin(filter_department)]
        if filter_category:
            filtered_df = filtered_df[filtered_df['Task Category'].isin(filter_category)]
        if filter_status:
            filtered_df = filtered_df[filtered_df['Status'].isin(filter_status)]

        # --- Styling DataFrame ---
        def get_priority_color(priority_str):
            try:
                priority_key = priority_str.split(' ')[-1]
                for key in PRIORITY_LEVELS:
                    if priority_key in key:
                        emoji = PRIORITY_LEVELS[key]['emoji']
                        return '#ff5252' if emoji == '🔴' else '#ffd740' if emoji == '🟡' else '#22c55e'
                return '#22c55e'
            except:
                return '#22c55e'

        def get_status_color(status_str):
            try:
                status_key = status_str.split(' ')[0]
                return STATUS_OPTIONS[status_key]['color']
            except:
                return '#f1f5f9'

        styled_df = filtered_df.sort_values("Date", ascending=False).style
        styled_df = styled_df.applymap(lambda x: f"color: {get_status_color(x)}", subset=["Status"])
        styled_df = styled_df.applymap(lambda x: f"color: {get_priority_color(x)}", subset=["Priority"])
        styled_df = styled_df.set_properties(**{'background-color': '#1e293b', 'color': '#f1f5f9', 'border': '1px solid #4b5563', 'font-family': 'Inter'})

        # --- Dashboard Metrics ---
        st.markdown("### 📊 Key Metrics")
        col1, col2, col3 = st.columns(3)
        total_hours = filtered_df['Net Duration (hrs)'].sum()
        billable_hours = filtered_df[filtered_df['Billable']]['Net Duration (hrs)'].sum()
        completed_tasks = len(filtered_df[filtered_df['Status'].str.contains('Completed')])
        
        with col1:
            st.markdown('<div class="metric-card"><h4>🕒 Total Hours</h4></div>', unsafe_allow_html=True)
            st.metric("", f"{total_hours:.1f} hrs")
        with col2:
            st.markdown('<div class="metric-card"><h4>💰 Billable Hours</h4></div>', unsafe_allow_html=True)
            st.metric("", f"{billable_hours:.1f} hrs", f"{billable_hours/total_hours*100:.1f}%" if total_hours > 0 else "N/A")
        with col3:
            st.markdown('<div class="metric-card"><h4>✅ Completed Tasks</h4></div>', unsafe_allow_html=True)
            st.metric("", f"{completed_tasks}")

        # --- Visualizations ---
        st.markdown("### 📈 Work Distribution")
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.pie(
                filtered_df, 
                names="Task Category", 
                values="Net Duration (hrs)", 
                title="Time by Category 🎯",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig1.update_layout(paper_bgcolor="#1e293b", font_color="#f1f5f9")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.bar(
                filtered_df.groupby('Department')['Net Duration (hrs)'].sum().reset_index().sort_values('Net Duration (hrs)', ascending=False),
                x='Department',
                y='Net Duration (hrs)',
                title="Hours by Department 🏢",
                color='Department',
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig2.update_layout(paper_bgcolor="#1e293b", font_color="#f1f5f9")
            st.plotly_chart(fig2, use_container_width=True)

        # --- Data Table ---
        st.markdown("### 📋 All Entries")
        st.dataframe(styled_df, use_container_width=True)

        # --- Report Generation ---
        st.markdown("### 📤 Generate Report")
        report_format = st.selectbox("Format 📄", ["PDF", "Excel"])
        if st.button("🖨 Generate Report", use_container_width=True):
            with st.spinner("Generating report..."):
                if report_format == "Excel":
                    excel_buffer = BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                        filtered_df.to_excel(writer, index=False, sheet_name="Time Entries")
                        workbook = writer.book
                        worksheet = writer.sheets["Time Entries"]
                        header_format = workbook.add_format({
                            'bold': True,
                            'fg_color': '#3b82f6',
                            'font_color': '#f1f5f9',
                            'border': 1
                        })
                        for col_num, value in enumerate(filtered_df.columns.values):
                            worksheet.write(0, col_num, value, header_format)
                    st.download_button(
                        label="📥 Download Excel",
                        data=excel_buffer.getvalue(),
                        file_name=f"FLM_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    pdf_buffer = BytesIO()
                    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
                    styles = getSampleStyleSheet()
                    styles['Title'].fontName = 'Helvetica-Bold'
                    styles['Normal'].fontName = 'Helvetica'
                    elements = []

                    elements.append(Paragraph("FLM Time Tracking Report 📊", styles['Title']))
                    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d')} 🕒", styles['Normal']))
                    elements.append(Spacer(1, 12))

                    summary_data = [
                        ["Metric", "Value"],
                        ["Total Hours 🕒", f"{total_hours:.1f} hrs"],
                        ["Billable Hours 💰", f"{billable_hours:.1f} hrs"],
                        ["Completed Tasks ✅", f"{completed_tasks}"]
                    ]
                    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
                    summary_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), '#3b82f6'),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica')
                    ]))
                    elements.append(summary_table)
                    elements.append(Spacer(1, 12))

                    pdf_data = [list(filtered_df.columns)] + [list(row) for _, row in filtered_df.iterrows()]
                    pdf_table = Table(pdf_data)
                    pdf_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), '#3b82f6'),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica')
                    ]))
                    elements.append(pdf_table)

                    doc.build(elements)
                    st.download_button(
                        label="📄 Download PDF",
                        data=pdf_buffer.getvalue(),
                        file_name=f"FLM_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )

    else:
        st.markdown("""
            <div style="text-align:center; padding:3rem; border:2px dashed #4b5563; border-radius:12px;">
                <h3>📭 No Entries Yet</h3>
                <p>Add your first time entry in the 'Add Entry' tab ➕</p>
            </div>
        """, unsafe_allow_html=True)

# --- Footer ---
st.markdown(f"""
    <center>
        <small>INTERSOFT POS - FLM Time Tracker • {datetime.now().strftime('%Y-%m-%d')} 🌟</small>
    </center>
""", unsafe_allow_html=True)
