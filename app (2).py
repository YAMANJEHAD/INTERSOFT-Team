import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time

# Page Configuration
st.set_page_config(
    page_title="⏱ INTERSOFT POS FLM Time Tracker",
    layout="wide",
    page_icon="⏱️"
)

# Custom CSS
st.markdown("""
    <style>
    body {
        background-color: #111827;
        color: #f3f4f6;
    }
    .header {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0 0 12px 12px;
        margin-bottom: 2rem;
    }
    .company-logo {
        font-size: 1.8rem;
        font-weight: bold;
    }
    .dept-name {
        font-size: 1.1rem;
        opacity: 0.85;
    }
    </style>
""", unsafe_allow_html=True)

# Session init
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

# Constants
SHIFTS = {
    "Morning (8:30-5:30)": {"start": time(8, 30), "end": time(17, 30)},
    "Evening (3:00-11:00)": {"start": time(15, 0), "end": time(23, 0)},
}

TASK_CATEGORIES = {
    "TOMS": {"requires_device_count": True, "requires_task_time": True, "description": "TOMS System Maintenance"},
    "Paper Request": {"requires_device_count": False, "requires_task_time": False, "description": "Paper Request Handling"},
    "J.O": {"requires_device_count": False, "requires_task_time": True, "description": "Job Order Processing"},
    "CRM": {"requires_device_count": False, "requires_task_time": True, "description": "CRM System Tasks"},
}

# Header
st.markdown("""
    <div class="header">
        <div class="company-logo">INTERSOFT POS</div>
        <div class="dept-name">FLM Department - Time Tracking System</div>
    </div>
""", unsafe_allow_html=True)

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    all_employees = list({e["Employee"] for e in st.session_state.timesheet})
    selected_emp = st.selectbox("Employee", ["All"] + sorted(all_employees))
    selected_task = st.selectbox("Task", ["All"] + list(TASK_CATEGORIES.keys()))
    selected_date = st.date_input("Date", value=None)

    total_hours = sum(r.get("Duration (hrs)", 0) for r in st.session_state.timesheet)
    st.metric("Total Hours", f"{total_hours:.2f}")
    st.metric("Entries", len(st.session_state.timesheet))

# Time Entry Form
with st.expander("➕ Add Time Entry", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            employee = st.text_input("Employee Name")
            shift = st.selectbox("Shift", list(SHIFTS.keys()))
        with col2:
            start_time = st.time_input("Start Time", value=time(8, 30))
            end_time = st.time_input("End Time", value=time(17, 30))
        with col3:
            task = st.selectbox("Task Category", list(TASK_CATEGORIES.keys()))

        device_count = None
        task_time = None

        if TASK_CATEGORIES[task]["requires_device_count"]:
            device_count = st.number_input("TOMS Devices", min_value=1, value=1)

        if TASK_CATEGORIES[task]["requires_task_time"]:
            task_time = st.time_input("Task Time", value=time(0, 30))

        details = st.text_area("Work Details (optional)")

        submitted = st.form_submit_button("Submit Entry")

        if submitted:
            if not employee or end_time <= start_time:
                st.error("Please fill all fields correctly.")
            else:
                duration = (datetime.combine(datetime.today(), end_time) -
                            datetime.combine(datetime.today(), start_time)).total_seconds() / 3600
                entry = {
                    "Employee": employee,
                    "Date": datetime.today().date(),
                    "Shift": shift,
                    "Start Time": start_time.strftime("%H:%M"),
                    "End Time": end_time.strftime("%H:%M"),
                    "Duration (hrs)": round(duration, 2),
                    "Task Category": task,
                    "Task Description": TASK_CATEGORIES[task]["description"],
                    "Work Details": details,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                if device_count is not None:
                    entry["TOMS Devices Count"] = device_count
                if task_time is not None:
                    entry["Task Time"] = task_time.strftime("%H:%M")

                st.session_state.timesheet.append(entry)
                st.success("✅ Entry added!")
                st.balloons()

# Data Display
if st.session_state.timesheet:
    df = pd.DataFrame(st.session_state.timesheet)

    # Filters
    if selected_emp != "All":
        df = df[df["Employee"] == selected_emp]
    if selected_task != "All":
        df = df[df["Task Category"] == selected_task]
    if selected_date:
        df = df[df["Date"] == pd.to_datetime(selected_date)]

    if not df.empty:
        st.subheader("📋 Time Entries")
        st.dataframe(df, use_container_width=True)

        st.subheader("📊 Analytics")
        tab1, tab2 = st.tabs(["Task Summary", "Employee Summary"])

        with tab1:
            fig = px.pie(df, names="Task Category", title="Task Distribution")
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            agg = df.groupby("Employee")["Duration (hrs)"].sum().reset_index()
            fig2 = px.bar(agg, x="Employee", y="Duration (hrs)", title="Total Hours by Employee")
            st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("No entries match your filters.")
else:
    st.info("No data yet. Start by adding entries.")

# Footer
st.markdown("---")
st.markdown("<center>© 2025 INTERSOFT POS FLM Tracker</center>", unsafe_allow_html=True)
