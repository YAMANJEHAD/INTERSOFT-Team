import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="📅 Time Sheet Tracker", layout="wide")
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stDataFrame thead tr th {
        background-color: #f0f2f6;
        color: #333;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🕒 Professional Daily Time Sheet System")

# Initialize session state if not exists
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

# --- Filter Section ---
st.sidebar.header("🔍 Filter Entries")
selected_project = st.sidebar.selectbox("Filter by Project", options=["All"] + list(set([row["Project"] for row in st.session_state.timesheet])), index=0)
selected_date = st.sidebar.date_input("Filter by Date (optional)", value=None)

# --- Form to input daily tasks ---
st.markdown("""
### 📝 Log Work Entry
Use this form to record your work details, tasks, and accomplishments.
""")

with st.form("log_form"):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("📆 Date", datetime.today())
        start_time = st.time_input("🟢 Start Time")
        title = st.text_input("🏷️ Task Title")
        project = st.text_input("📁 Project Name", "General")
    with col2:
        end_time = st.time_input("🔴 End Time")
        notes = st.text_input("🗒️ Notes", "-")

    task = st.text_area("🛠️ Task Description", height=100)
    achievements = st.text_area("✅ What Was Achieved", height=100)
    uploaded_files = st.file_uploader("📎 Upload Files or Screenshots (Optional)", type=None, accept_multiple_files=True)
    submitted = st.form_submit_button("✅ Add to Log")

if submitted:
    duration = (datetime.combine(datetime.today(), end_time) - datetime.combine(datetime.today(), start_time)).total_seconds() / 3600
    file_names = [file.name for file in uploaded_files] if uploaded_files else []
    st.session_state.timesheet.append({
        "Date": date,
        "Start Time": start_time.strftime("%H:%M"),
        "End Time": end_time.strftime("%H:%M"),
        "Duration (hrs)": round(duration, 2),
        "Title": title,
        "Task": task,
        "Achievements": achievements,
        "Notes": notes,
        "Project": project,
        "Files": ", ".join(file_names)
    })
    st.success("✅ Entry added successfully!")

# --- Display Time Sheet Table ---
st.markdown("""
---
### 📋 Time Sheet Log
""")

df = pd.DataFrame(st.session_state.timesheet)

# Apply filters
if not df.empty:
    if selected_project != "All":
        df = df[df["Project"] == selected_project]
    if selected_date:
        df = df[df["Date"] == pd.to_datetime(selected_date)]

if not df.empty:
    st.dataframe(df, use_container_width=True, height=400)

    # --- Download as Excel ---
    def convert_df_to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='TimeSheet')
            writer.save()
        return output.getvalue()

    st.download_button(
        label="⬇️ Download Excel Report",
        data=convert_df_to_excel(df),
        file_name='Professional_Timesheet.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # --- Charts ---
    st.markdown("""
---
### 📊 Analytics Overview
""")

    daily_hours = df.groupby("Date")["Duration (hrs)"].sum().reset_index()
    fig1 = px.bar(daily_hours, x="Date", y="Duration (hrs)", title="🕓 Total Hours Logged per Day", text_auto=True)
    st.plotly_chart(fig1, use_container_width=True)

    project_hours = df.groupby("Project")["Duration (hrs)"].sum().reset_index()
    fig2 = px.pie(project_hours, names="Project", values="Duration (hrs)", title="📁 Time Distribution by Project")
    st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("ℹ️ No entries available with current filters. Try logging some work or removing filters.")
