import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO

# Configure page settings
st.set_page_config(
    page_title="⏱ Time Tracking Dashboard", 
    layout="wide",
    page_icon="⏱"
)

# Professional CSS styling
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stDataFrame {
        border: 1px solid #e1e4e8;
        border-radius: 8px;
    }
    .stDataFrame thead tr th {
        background-color: #f8f9fa;
        color: #212529;
        font-weight: 600;
    }
    .stButton>button {
        background-color: #4a6fa5;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #3a5a80;
        color: white;
    }
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea,
    .stDateInput>div>div>input,
    .stTimeInput>div>div>input {
        border: 1px solid #ced4da;
        border-radius: 4px;
    }
    .css-1aumxhk {
        background-color: #f8f9fa;
        border: 1px solid #e1e4e8;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

# --- Header Section ---
st.title("⏱ Professional Time Tracking System")
st.markdown("""
    <div style='border-bottom: 1px solid #e1e4e8; margin-bottom: 2rem;'></div>
""", unsafe_allow_html=True)

# --- Sidebar Filters ---
with st.sidebar:
    st.header("🔍 Filter Options")
    selected_project = st.selectbox(
        "Project Filter", 
        options=["All Projects"] + sorted(list(set([row["Project"] for row in st.session_state.timesheet]))),
        index=0
    )
    selected_date = st.date_input(
        "Date Filter", 
        value=None,
        help="Filter entries by specific date"
    )
    
    st.markdown("""
        <div style='margin-top: 2rem;'>
        <h4>System Summary</h4>
        <p>Total Entries: <strong>{}</strong></p>
        <p>Total Hours: <strong>{:.1f}</strong></p>
        </div>
    """.format(
        len(st.session_state.timesheet),
        sum([row["Duration (hrs)"] for row in st.session_state.timesheet])
    ), unsafe_allow_html=True)

# --- Time Entry Form ---
with st.expander("➕ Add New Time Entry", expanded=True):
    with st.form("time_entry_form"):
        cols = st.columns([1, 1, 1])
        with cols[0]:
            date = st.date_input("Date", datetime.today())
            project = st.text_input("Project Name*", placeholder="Project Alpha")
        with cols[1]:
            start_time = st.time_input("Start Time*")
            title = st.text_input("Task Title*", placeholder="Task description")
        with cols[2]:
            end_time = st.time_input("End Time*")
            category = st.selectbox("Category", ["Development", "Meeting", "Research", "Administrative", "Other"])
        
        task_details = st.text_area("Detailed Description*", 
                                  placeholder="Describe the work performed in detail...",
                                  height=120)
        deliverables = st.text_area("Key Deliverables/Outcomes", 
                                   placeholder="List specific achievements or outputs...",
                                   height=100)
        uploaded_files = st.file_uploader("Supporting Documents (Optional)", 
                                        type=["pdf", "docx", "xlsx", "png", "jpg"],
                                        accept_multiple_files=True)
        
        submitted = st.form_submit_button("Submit Time Entry", 
                                        help="All fields marked with * are required")

if submitted:
    if not all([project, title, task_details]):
        st.error("Please complete all required fields (marked with *)")
    elif end_time <= start_time:
        st.error("End time must be after start time")
    else:
        duration = (datetime.combine(datetime.today(), end_time) - 
                  datetime.combine(datetime.today(), start_time)).total_seconds() / 3600
        file_names = [file.name for file in uploaded_files] if uploaded_files else []
        
        st.session_state.timesheet.append({
            "Date": date,
            "Project": project,
            "Category": category,
            "Title": title,
            "Start Time": start_time.strftime("%H:%M"),
            "End Time": end_time.strftime("%H:%M"),
            "Duration (hrs)": round(duration, 2),
            "Description": task_details,
            "Deliverables": deliverables,
            "Attachments": ", ".join(file_names)
        })
        
        st.success("Time entry successfully recorded")
        st.balloons()

# --- Time Sheet Display ---
st.markdown("""
    <h2 style='margin-top: 2rem;'>Time Entries Log</h2>
    <p style='color: #6c757d;'>Review and analyze your recorded time entries</p>
""", unsafe_allow_html=True)

if st.session_state.timesheet:
    df = pd.DataFrame(st.session_state.timesheet)
    
    # Apply filters
    if selected_project != "All Projects":
        df = df[df["Project"] == selected_project]
    if selected_date:
        df = df[df["Date"] == pd.to_datetime(selected_date)]
    
    # Display dataframe with custom formatting
    st.dataframe(
        df.sort_values("Date", ascending=False),
        column_config={
            "Duration (hrs)": st.column_config.NumberColumn(format="%.2f"),
            "Date": st.column_config.DateColumn(format="YYYY-MM-DD")
        },
        use_container_width=True,
        height=600
    )
    
    # --- Analytics Section ---
    st.markdown("""
        <div style='border-top: 1px solid #e1e4e8; margin: 2rem 0;'></div>
        <h2>Performance Analytics</h2>
    """, unsafe_allow_html=True)
    
    if len(df) > 0:
        tab1, tab2, tab3 = st.tabs(["Time Distribution", "Productivity Trends", "Data Export"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                project_hours = df.groupby("Project")["Duration (hrs)"].sum().reset_index()
                fig1 = px.pie(project_hours, 
                             names="Project", 
                             values="Duration (hrs)",
                             title="Time Allocation by Project",
                             hole=0.3)
                st.plotly_chart(fig1, use_container_width=True)
            with col2:
                category_hours = df.groupby("Category")["Duration (hrs)"].sum().reset_index()
                fig2 = px.bar(category_hours, 
                              x="Category", 
                              y="Duration (hrs)",
                              title="Time Distribution by Category",
                              color="Category")
                st.plotly_chart(fig2, use_container_width=True)
        
        with tab2:
            daily_hours = df.groupby("Date")["Duration (hrs)"].sum().reset_index()
            fig3 = px.line(daily_hours, 
                          x="Date", 
                          y="Duration (hrs)",
                          title="Daily Productivity Trend",
                          markers=True)
            fig3.update_traces(line_color='#4a6fa5', line_width=2.5)
            st.plotly_chart(fig3, use_container_width=True)
        
        with tab3:
            st.markdown("""
                <h4>Export Time Tracking Data</h4>
                <p>Download your time entries for reporting or analysis purposes.</p>
            """, unsafe_allow_html=True)
            
            def convert_to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='TimeEntries')
                    # Add some Excel formatting
                    workbook = writer.book
                    worksheet = writer.sheets['TimeEntries']
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
                    worksheet.autofit()
                return output.getvalue()
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📊 Export to Excel",
                    data=convert_to_excel(df),
                    file_name=f"Time_Tracking_Report_{datetime.today().strftime('%Y%m%d')}.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    help="Download all filtered entries in Excel format"
                )
            with col2:
                st.download_button(
                    label="📄 Export to CSV",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name=f"Time_Tracking_Data_{datetime.today().strftime('%Y%m%d')}.csv",
                    mime='text/csv',
                    help="Download all filtered entries in CSV format"
                )
else:
    st.info("""
        ℹ️ No time entries have been recorded yet. 
        Use the form above to add your first time entry.
    """)

# Footer
st.markdown("""
    <div style='border-top: 1px solid #e1e4e8; margin-top: 2rem; padding-top: 1rem; color: #6c757d;'>
    <p>Professional Time Tracking System v1.0</p>
    </div>
""", unsafe_allow_html=True)
