import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Page Configuration
st.set_page_config(
    page_title="⏱ Time Sheet | INTERSOFT POS - FLM",
    layout="wide",
    page_icon="⏱️"
)

# Dark Theme Styling
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background-color: #121212;
        color: #E0E0E0;
    }
    .header {
        background: linear-gradient(135deg, #6B73FF 0%, #000DFF 100%);
        color: white;
        padding: 2rem;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin-bottom: 2rem;
        text-align: center;
    }
    .status-card {
        background: #1E1E1E;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        border: 1px solid #333;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header">
        <h1>INTERSOFT POS</h1>
        <h3>FLM Department - Time Tracking System</h3>
    </div>
""", unsafe_allow_html=True)

# Session State Init
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

# Shifts
SHIFTS = {
    "Morning Shift (8:30 AM - 5:30 PM)": {'start': time(8, 30), 'end': time(17, 30)},
    "Evening Shift (3:00 PM - 11:00 PM)": {'start': time(15, 0), 'end': time(23, 0)}
}

# Tasks
TASK_CATEGORIES = {
    "TOMS": {"requires_devices": True, "requires_task_time": True},
    "Paper Request": {"requires_devices": False, "requires_task_time": False},
    "J.O": {"requires_devices": False, "requires_task_time": True},
    "CRM": {"requires_devices": False, "requires_task_time": True}
}

# Time Entry Form
with st.expander("➕ Add New Time Entry", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            employee = st.text_input("Employee Name *")
            shift_type = st.selectbox("Shift Type *", list(SHIFTS.keys()))

        with col2:
            start_time = st.time_input("Start Time *", value=time(8, 30), format="%I:%M %p")
            end_time = st.time_input("End Time *", value=time(17, 30), format="%I:%M %p")

        with col3:
            task_category = st.selectbox("Task Category", list(TASK_CATEGORIES.keys()))

        device_count = None
        task_duration = None
        if TASK_CATEGORIES[task_category].get("requires_devices"):
            device_count = st.number_input("Number of Devices (TOMS)", min_value=1, step=1)
        if TASK_CATEGORIES[task_category].get("requires_task_time"):
            task_duration = st.time_input("Task Duration (optional)", value=time(0, 30), format="%I:%M %p")

        work_description = st.text_area("Work Description (optional)", height=100)
        submitted = st.form_submit_button("Submit Entry")

        if submitted:
            if not employee or not shift_type or not start_time or not end_time:
                st.error("Please fill all required fields (*)")
            elif end_time <= start_time:
                st.error("End time must be after start time")
            else:
                duration = (datetime.combine(datetime.today(), end_time) - datetime.combine(datetime.today(), start_time)).total_seconds() / 3600
                entry = {
                    "Employee": employee,
                    "Date": datetime.today().date(),
                    "Shift": shift_type,
                    "Task Category": task_category,
                    "Start Time": start_time.strftime("%I:%M %p"),
                    "End Time": end_time.strftime("%I:%M %p"),
                    "Duration (hrs)": round(duration, 2),
                    "Work Description": work_description,
                }
                if device_count:
                    entry["TOMS Devices"] = device_count
                if task_duration:
                    entry["Task Duration"] = task_duration.strftime("%I:%M %p")

                st.session_state.timesheet.append(entry)
                st.success("✅ Time entry added successfully!")

# Timesheet Display
if st.session_state.timesheet:
    df = pd.DataFrame(st.session_state.timesheet)
    st.markdown("## 📋 Time Entries")
    st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True)

    st.markdown("## 📊 Summary")
    st.metric("Total Hours", f"{df['Duration (hrs)'].sum():.2f}")
    fig = px.bar(df, x="Employee", y="Duration (hrs)", color="Task Category", title="Work Distribution")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("## 📤 Export Options")
    export_employee = st.selectbox("Filter by Employee for Export", ["All"] + sorted(df["Employee"].unique()))
    export_df = df if export_employee == "All" else df[df["Employee"] == export_employee]

    # Export to Excel
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        export_df.to_excel(writer, index=False, sheet_name="Timesheet")
    st.download_button(
        label="📥 Download Excel",
        data=excel_buffer.getvalue(),
        file_name="timesheet_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Export to PDF
    def generate_pdf(data):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica", 12)
        y = 750
        c.drawString(220, 780, "INTERSOFT POS - FLM Timesheet Report")
        for _, row in data.iterrows():
            text = f"{row['Date']} | {row['Employee']} | {row['Task Category']} | {row['Duration (hrs)']} hrs"
            c.drawString(50, y, text)
            y -= 20
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = 750
        c.save()
        return buffer.getvalue()

    st.download_button(
        label="📄 Download PDF",
        data=generate_pdf(export_df),
        file_name="timesheet_report.pdf",
        mime="application/pdf"
    )
else:
    st.info("No time entries yet. Please add your first record.")

# Footer
st.markdown("---")
st.markdown("<center>INTERSOFT POS - FLM Department • v1.0</center>", unsafe_allow_html=True)
