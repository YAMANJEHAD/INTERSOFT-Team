import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO
import time


st.set_page_config(
    page_title="⏰ Time Sheet InterSoft",
    layout="wide",
    page_icon="⏱️",
    initial_sidebar_state="expanded"
)

# ---- Professional CSS Styling ----
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    .header {
        background: linear-gradient(135deg, #6B73FF 0%, #000DFF 100%);
        color: white;
        padding: 2rem;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
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
    
    .clock-container {
        background: #1E1E1E;
        color: #00FFAA;
        padding: 1rem;
        border-radius: 10px;
        font-family: 'Digital', monospace;
        font-size: 1.8rem;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stDataFrame {
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #6B73FF 0%, #000DFF 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(107, 115, 255, 0.3);
    }
    
    .sidebar .sidebar-content {
        background: #F9FAFF;
        border-right: 1px solid #E6E9F0;
    }
    
    .css-1aumxhk {
        background-color: #FFFFFF;
        border: 1px solid #E6E9F0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }
    
    .tab-content {
        padding: 1.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Real-Time Clock ----
def digital_clock():
    current_time = datetime.now().strftime("%H:%M:%S")
    clock_html = f"""
    <div class="clock-container">
        <div style="font-size:0.9rem; margin-bottom:0.5rem; color:#A0A0A0;">INTERSOFT LIVE</div>
        {current_time}
    </div>
    """
    return clock_html

# ---- System Constants ----
EMPLOYEES = ["Alex Johnson", "Sarah Williams", "Michael Brown", "Emily Davis", "David Lee"]
CATEGORIES = ["PAPER REQUEST", "TOMS", "CRM", "J.O", "Development", "Client Meeting", "Research", "Administrative", "Training", "Support"]
DEPARTMENTS = ["IT", "Finance", "Operations", "HR", "Marketing"]

# Initialize session state
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

# ---- Header Section ----
st.markdown(f"""
    <div class="header">
        <div class="header-title">⏰ Time Sheet InterSoft</div>
        <div class="header-subtitle">Professional Time Tracking System | Version 2.1</div>
    </div>
""", unsafe_allow_html=True)

# Display real-time clock
st.markdown(digital_clock(), unsafe_allow_html=True)

# ---- Sidebar Filters ----
with st.sidebar:
    st.markdown("""
        <div style="font-size:1.2rem; font-weight:600; margin-bottom:1rem; color:#4A4A4A;">
        🔍 Filter Dashboard
        </div>
    """, unsafe_allow_html=True)
    
    selected_employee = st.selectbox(
        "By Employee", 
        options=["All Employees"] + EMPLOYEES,
        index=0
    )
    
    selected_category = st.selectbox(
        "By Category", 
        options=["All Categories"] + CATEGORIES,
        index=0
    )
    
    selected_department = st.selectbox(
        "By Department", 
        options=["All Departments"] + DEPARTMENTS,
        index=0
    )
    
    selected_date = st.date_input(
        "By Date Range",
        value=None,
        help="Filter entries by specific date"
    )
    
    st.markdown("""
        <div style="margin-top:2rem; padding:1rem; background:#F3F5FF; border-radius:10px;">
        <h4 style="color:#4A4A4A;">System Analytics</h4>
        <p>📊 Total Entries: <strong>{}</strong></p>
        <p>⏱️ Total Hours: <strong>{:.1f}</strong></p>
        <p>👥 Active Employees: <strong>{}/5</strong></p>
        </div>
    """.format(
        len(st.session_state.timesheet),
        sum([row.get("Duration (hrs)", 0) for row in st.session_state.timesheet]),
        len(set([row.get("Employee", "") for row in st.session_state.timesheet]))
    ), unsafe_allow_html=True)

# ---- Time Entry Form ----
with st.expander("➕ ADD NEW TIME ENTRY", expanded=True):
    with st.form("time_entry_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            employee = st.selectbox("Employee*", EMPLOYEES)
            project = st.text_input("Project Name*", placeholder="Project Alpha")
            department = st.selectbox("Department*", DEPARTMENTS)
            
        with col2:
            date = st.date_input("Date*", datetime.today())
            start_time = st.time_input("Start Time*")
            end_time = st.time_input("End Time*")
            
        with col3:
            category = st.selectbox("Category*", CATEGORIES)
            priority = st.select_slider("Priority", ["Low", "Medium", "High"])
            attachments = st.file_uploader("Attachments", accept_multiple_files=True)
        
        task_description = st.text_area("Task Description*", 
                                      placeholder="Detailed description of work performed...",
                                      height=100)
        
        deliverables = st.text_area("Key Deliverables", 
                                 placeholder="Specific outcomes or achievements...",
                                 height=80)
        
        submitted = st.form_submit_button("🚀 Submit Time Entry")
        
        if submitted:
            if not all([employee, project, task_description]):
                st.error("Please complete all required fields (*)")
            elif end_time <= start_time:
                st.error("End time must be after start time")
            else:
                duration = (datetime.combine(datetime.today(), end_time) - 
                          datetime.combine(datetime.today(), start_time)).total_seconds() / 3600
                
                new_entry = {
                    "Timestamp": datetime.now(),
                    "Employee": employee,
                    "Department": department,
                    "Date": date,
                    "Start Time": start_time.strftime("%H:%M"),
                    "End Time": end_time.strftime("%H:%M"),
                    "Duration (hrs)": round(duration, 2),
                    "Project": project,
                    "Category": category,
                    "Priority": priority,
                    "Task Description": task_description,
                    "Deliverables": deliverables,
                    "Attachments": [file.name for file in attachments] if attachments else []
                }
                
                st.session_state.timesheet.append(new_entry)
                st.success("✅ Time entry successfully recorded!")
                st.balloons()

# ---- Time Sheet Display ----
st.markdown("""
    <div style="font-size:1.5rem; font-weight:600; margin:2rem 0 1rem 0; color:#4A4A4A;">
    📋 Time Entries Log
    </div>
""", unsafe_allow_html=True)

if st.session_state.timesheet:
    df = pd.DataFrame(st.session_state.timesheet)
    
    # Apply filters
    if selected_employee != "All Employees":
        df = df[df["Employee"] == selected_employee]
    if selected_category != "All Categories":
        df = df[df["Category"] == selected_category]
    if selected_department != "All Departments":
        df = df[df["Department"] == selected_department]
    if selected_date:
        df = df[df["Date"] == pd.to_datetime(selected_date)]
    
    # Display dataframe with custom columns
    display_cols = ["Employee", "Department", "Date", "Start Time", "End Time", 
                   "Duration (hrs)", "Project", "Category", "Priority"]
    
    st.dataframe(
        df[display_cols].sort_values("Date", ascending=False),
        column_config={
            "Duration (hrs)": st.column_config.NumberColumn(format="%.2f"),
            "Date": st.column_config.DateColumn(format="YYYY-MM-DD")
        },
        use_container_width=True,
        height=600
    )
    
    # ---- Analytics Dashboard ----
    st.markdown("""
        <div style="border-top:1px solid #E6E9F0; margin:2rem 0;"></div>
        <div style="font-size:1.5rem; font-weight:600; margin-bottom:1rem; color:#4A4A4A;">
        📊 Analytics Dashboard
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Time Distribution", "Productivity Metrics", "Data Export"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.pie(df, names="Category", values="Duration (hrs)",
                         title="Time Allocation by Category",
                         hole=0.3, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.bar(df.groupby("Employee")["Duration (hrs)"].sum().reset_index(),
                         x="Employee", y="Duration (hrs)",
                         title="Hours by Employee",
                         color="Employee")
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        fig3 = px.line(df.groupby("Date")["Duration (hrs)"].sum().reset_index(),
                      x="Date", y="Duration (hrs)",
                      title="Daily Productivity Trend",
                      markers=True, line_shape="spline")
        st.plotly_chart(fig3, use_container_width=True)
        
        fig4 = px.sunburst(df, path=["Department", "Employee", "Category"],
                          values="Duration (hrs)",
                          title="Departmental Time Distribution")
        st.plotly_chart(fig4, use_container_width=True)
    
    with tab3:
        st.markdown("""
            <div style="background:#F9FAFF; padding:1.5rem; border-radius:12px;">
            <h4 style="color:#4A4A4A;">Export Options</h4>
            <p style="color:#6C757D;">Generate reports for payroll, client billing, or performance analysis</p>
            </div>
        """, unsafe_allow_html=True)
        
        def generate_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='TimeEntries')
                workbook = writer.book
                worksheet = writer.sheets['TimeEntries']
                
                # Add formatting
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#6B73FF',
                    'font_color': 'white',
                    'border': 1
                })
                
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Auto-adjust columns
                worksheet.autofit()
                
                # Add InterSoft branding
                worksheet.header_footer = {
                    'first_header': '&C&"Poppins,Bold"&14Time Sheet InterSoft Report',
                    'first_footer': '&C&"Poppins"&12Generated on &D at &T'
                }
            
            return output.getvalue()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                label="💾 Excel Report",
                data=generate_excel(df),
                file_name=f"InterSoft_Time_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with col2:
            st.download_button(
                label="📄 CSV Export",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"Time_Data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        with col3:
            if st.button("🔄 Refresh Live View"):
                st.rerun()
else:
    st.info("""
        ℹ️ No time entries found. 
        Start by adding your first time entry using the form above.
    """)

# Auto-refresh the clock every second
st_autorefresh(interval=1000, limit=100, key="clock_refresh")
