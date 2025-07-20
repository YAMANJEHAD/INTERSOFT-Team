# FLM Task Tracker – Full Version with Admin Panel, Roles, Alerts, Calendar + Auto Export Weekly + Persistent Storage + Main Interface + Logout + Enhanced UI + Analytics + Interactive Enhancements

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import calendar
from io import BytesIO
import uuid
import os
import calplot
import matplotlib.pyplot as plt

# --- Page Config ---
st.set_page_config("⚡ INTERSOFT Dashboard | FLM", layout="wide", page_icon="🚀")

# --- Ensure session keys exist ---
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []
if "user_role" not in st.session_state:
    st.session_state.user_role = "Unknown"
if "user_role_type" not in st.session_state:
    st.session_state.user_role_type = "Employee"

# --- Styling ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(120deg, #1f2937, #0f172a);
    color: #e2e8f0;
}
.top-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0 2rem; margin-top: 1rem;
    animation: fadeInDown 1s ease-out;
}
.greeting { font-size: 1rem; font-weight: 500; color: #facc15; text-align: right; }
.company { font-size: 1.2rem; font-weight: 600; color: #60a5fa; }
.date-box {
    font-size: 1rem; font-weight: 500; color: #f8fafc; text-align: center;
    background: #1e3a8a; padding: 0.5rem 1rem; border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3); margin-bottom: 1.5rem; display: inline-block;
    animation: fadeIn 1s ease-out;
}
.overview-box {
    background: linear-gradient(to right, #2563eb, #3b82f6);
    padding: 1.5rem; border-radius: 18px; text-align: center;
    margin: 1rem 0; transition: transform 0.4s ease;
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    animation: bounceIn 0.8s;
}
.overview-box:hover { transform: translateY(-5px) scale(1.03); }
.overview-box span { font-size: 2.4rem; font-weight: 800; color: #fcd34d; }
footer { text-align: center; color: #94a3b8; padding-top: 2rem; }
.logout-btn { text-align: right; margin-top: -20px; margin-bottom: 20px; }
/* Table Styling */
thead tr th { background-color: #60a5fa !important; font-weight: bold; color: white !important; }
tbody tr td { font-weight: 600; color: #cbd5e1; }
@keyframes fadeInDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes bounceIn { 0% { transform: scale(0.9); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# --- Count Boxes ---
df_count = pd.DataFrame(st.session_state.timesheet)
df_filtered = df_count if st.session_state.user_role_type == "Admin" else df_count[df_count['Employee'] == st.session_state.user_role]
total_tasks = len(df_filtered)
completed_tasks = df_filtered[df_filtered['Status'] == '✅ Completed'].shape[0]
in_progress_tasks = df_filtered[df_filtered['Status'] == '🔄 In Progress'].shape[0]

col1, col2, col3 = st.columns(3)
col1.markdown(f"<div class='overview-box'>Total Tasks<br><span>{total_tasks}</span></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='overview-box'>Completed<br><span>{completed_tasks}</span></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='overview-box'>In Progress<br><span>{in_progress_tasks}</span></div>", unsafe_allow_html=True)

# --- Analytics ---
if not df_filtered.empty:
    st.markdown("### 📊 Task Analytics")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.histogram(df_filtered, x="Date", color="Status", barmode="group", title="Tasks Over Time"), use_container_width=True)
    with col2:
        st.plotly_chart(px.pie(df_filtered, names="Category", title="Category Breakdown"), use_container_width=True)
    st.plotly_chart(px.bar(df_filtered, x="Priority", color="Priority", title="Priority Distribution"), use_container_width=True)

    # --- Calendar Plot ---
    df_cal = df_filtered.copy()
    df_cal['Date'] = pd.to_datetime(df_cal['Date'])
    task_counts = df_cal.groupby('Date').size()
    fig, ax = calplot.calplot(task_counts, cmap='Blues', figsize=(16, 3))
    st.pyplot(fig)

# --- Footer ---
st.markdown("<footer>📅 INTERSOFT FLM Tracker • {} </footer>".format(datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')), unsafe_allow_html=True)
