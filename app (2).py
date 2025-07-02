import streamlit as st
import pandas as pd
import io
import plotly.express as px
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import os
import hashlib
import re
from PIL import Image

# Configuration
st.set_page_config(
    page_title="INTERSOFT Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Mode Switch
def set_dark_mode():
    st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E1E;
        color: white;
    }
    .css-1d391kg, .css-1y4p8pa, .css-1oe5cao {
        background-color: #2E2E2E !important;
    }
    .st-bb, .st-at, .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

if st.sidebar.checkbox('🌙 Dark Mode'):
    set_dark_mode()

# Custom CSS for responsive design
st.markdown("""
<style>
@media (max-width: 768px) {
    .metric-card {
        padding: 10px !important;
        margin: 5px 0 !important;
    }
    .stDataFrame {
        width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Clock HTML Component
clock_html = """<div style="background: transparent;"><style>
.clock-container {
    font-family: 'Courier New', monospace;
    font-size: 22px;
    color: #fff;
    background: linear-gradient(135deg, #1abc9c, #16a085);
    padding: 12px 25px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    animation: pulse 2s infinite;
    position: fixed;
    top: 15px;
    right: 25px;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(26, 188, 156, 0.4); }
    70% { box-shadow: 0 0 0 15px rgba(26, 188, 156, 0); }
    100% { box-shadow: 0 0 0 0 rgba(26, 188, 156, 0); }
}
</style>
<div class="clock-container">
    <div class="clock-time" id="clock"></div>
    <div class="clock-date" id="date"></div>
</div>
<script>
function updateClock() {
    const now = new Date();
    const time = now.toLocaleTimeString();
    const date = now.toLocaleDateString(undefined, {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    document.getElementById('clock').innerText = time;
    document.getElementById('date').innerText = date;
}
setInterval(updateClock, 1000);
updateClock();
</script>
</div>"""
components.html(clock_html, height=130, scrolling=False)


with col2:
    st.markdown("<h1 style='color:#ffffff; margin-top:15px;'>📊 INTERSOFT Analyzer</h1>", unsafe_allow_html=True)

# Pending Tickets Analysis - First Section
st.markdown("<h2 style='color:#ffffff;'>📌 Pending Tickets Analysis</h2>", unsafe_allow_html=True)

with st.expander("🧮 Filter Unprocessed Tickets Based on Ticket_ID", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        all_file = st.file_uploader("🔄 Upload ALL Tickets File", type=["xlsx"], key="all_file")
    with col2:
        done_file = st.file_uploader("✅ Upload DONE Tickets File", type=["xlsx"], key="done_file")

    if all_file and done_file:
        try:
            all_df = pd.read_excel(all_file)
            done_df = pd.read_excel(done_file)

            if 'Ticket_ID' not in all_df.columns or 'Ticket_ID' not in done_df.columns:
                st.error("❌ Both files must contain a 'Ticket_ID' column.")
            else:
                # Remove duplicates
                all_df = all_df.drop_duplicates(subset=['Ticket_ID'], keep='first')
                done_df = done_df.drop_duplicates(subset=['Ticket_ID'], keep='first')
                
                pending_df = all_df[~all_df['Ticket_ID'].isin(done_df['Ticket_ID'])]
                
                # KPI Metrics
                st.markdown("### 📊 Performance Metrics")
                kpi1, kpi2, kpi3 = st.columns(3)
                
                with kpi1:
                    st.markdown(f"""
                    <div class='metric-card' style='background:#1f77b4; padding:20px; border-radius:10px; color:white;'>
                    <h3>Total Tickets</h3>
                    <h1>{len(all_df)}</h1>
                    </div>
                    """, unsafe_allow_html=True)
                
                with kpi2:
                    st.markdown(f"""
                    <div class='metric-card' style='background:#2ca02c; padding:20px; border-radius:10px; color:white;'>
                    <h3>Completed</h3>
                    <h1>{len(done_df)}</h1>
                    </div>
                    """, unsafe_allow_html=True)
                
                with kpi3:
                    pending_percent = (len(pending_df) / len(all_df)) * 100
                    st.markdown(f"""
                    <div class='metric-card' style='background:#ff7f0e; padding:20px; border-radius:10px; color:white;'>
                    <h3>Pending</h3>
                    <h1>{len(pending_df)} <small>({pending_percent:.1f}%)</small></h1>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Quick Filters
                st.markdown("### 🔍 Quick Filters")
                filter_col1, filter_col2, filter_col3 = st.columns(3)
                
                with filter_col1:
                    date_filter = st.selectbox("Filter by Date Range", ["All", "Last 7 Days", "Last 30 Days", "Custom"])
                
                with filter_col2:
                    if 'Technician_Name' in pending_df.columns:
                        tech_filter = st.multiselect("Filter by Technician", pending_df['Technician_Name'].unique())
                
                with filter_col3:
                    if 'Ticket_Type' in pending_df.columns:
                        type_filter = st.multiselect("Filter by Ticket Type", pending_df['Ticket_Type'].unique())
                
                # Apply filters
                if date_filter == "Last 7 Days":
                    pending_df = pending_df[pending_df['Date'] >= (datetime.now() - timedelta(days=7))]
                elif date_filter == "Last 30 Days":
                    pending_df = pending_df[pending_df['Date'] >= (datetime.now() - timedelta(days=30))]
                
                if 'Technician_Name' in pending_df.columns and tech_filter:
                    pending_df = pending_df[pending_df['Technician_Name'].isin(tech_filter)]
                
                if 'Ticket_Type' in pending_df.columns and type_filter:
                    pending_df = pending_df[pending_df['Ticket_Type'].isin(type_filter)]
                
                # Display filtered results
                st.dataframe(pending_df, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error processing files: {e}")

# Main Analyzer Section
st.markdown("<h2 style='color:#ffffff; margin-top:30px;'>📊 Full Analysis Dashboard</h2>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📁 Upload Excel File for Full Analysis", type=["xlsx"])
required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

# ... [Rest of your existing functions like normalize, classify_note, etc.] ...

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
    except:
        df = pd.read_excel(uploaded_file)

    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ Missing required columns. Available: {list(df.columns)}")
    else:
        # Remove duplicates if Ticket_ID exists
        if 'Ticket_ID' in df.columns:
            df = df.drop_duplicates(subset=['Ticket_ID'], keep='first')
        
        df['Note_Type'] = df['NOTE'].apply(classify_note)
        df['Problem_Severity'] = df['Note_Type'].apply(problem_severity)
        df['Suggested_Solution'] = df['Note_Type'].apply(suggest_solutions)
        
        # Severity Color Coding
        severity_colors = {
            "Critical": "#ff0000",
            "High": "#ff7f0e",
            "Medium": "#ffff00",
            "Low": "#00ff00",
            "Unclassified": "#cccccc"
        }
        
        # Dashboard KPIs
        st.markdown("### 📈 Performance Overview")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        with kpi1:
            total_tickets = len(df)
            st.markdown(f"""
            <div class='metric-card' style='background:#1f77b4; padding:15px; border-radius:10px; color:white;'>
            <h4>Total Tickets</h4>
            <h2>{total_tickets}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with kpi2:
            done_tickets = len(df[df['Note_Type'] == 'DONE'])
            st.markdown(f"""
            <div class='metric-card' style='background:#2ca02c; padding:15px; border-radius:10px; color:white;'>
            <h4>Completed</h4>
            <h2>{done_tickets}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with kpi3:
            critical_issues = len(df[df['Problem_Severity'] == 'Critical'])
            st.markdown(f"""
            <div class='metric-card' style='background:#d62728; padding:15px; border-radius:10px; color:white;'>
            <h4>Critical Issues</h4>
            <h2>{critical_issues}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with kpi4:
            avg_resolution = "N/A"  # You would calculate this from your data
            st.markdown(f"""
            <div class='metric-card' style='background:#9467bd; padding:15px; border-radius:10px; color:white;'>
            <h4>Avg Resolution Time</h4>
            <h2>{avg_resolution}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Quick Filters
        st.markdown("### 🔍 Filter Data")
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
        
        with filter_col1:
            date_range = st.selectbox("Date Range", ["All", "Last Week", "Last Month", "Custom"])
        
        with filter_col2:
            severity_filter = st.multiselect("Severity Level", df['Problem_Severity'].unique())
        
        with filter_col3:
            tech_filter = st.multiselect("Technician", df['Technician_Name'].unique())
        
        with filter_col4:
            note_filter = st.multiselect("Note Type", df['Note_Type'].unique())
        
        # Apply filters
        if date_range == "Last Week":
            df = df[df['Date'] >= (datetime.now() - timedelta(days=7))]
        elif date_range == "Last Month":
            df = df[df['Date'] >= (datetime.now() - timedelta(days=30))]
        
        if severity_filter:
            df = df[df['Problem_Severity'].isin(severity_filter)]
        
        if tech_filter:
            df = df[df['Technician_Name'].isin(tech_filter)]
        
        if note_filter:
            df = df[df['Note_Type'].isin(note_filter)]
        
        # Visualization
        st.markdown("### 📊 Data Visualization")
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            severity_counts = df['Problem_Severity'].value_counts().reset_index()
            severity_counts.columns = ['Severity', 'Count']
            severity_counts['Color'] = severity_counts['Severity'].map(severity_colors)
            
            fig_severity = px.bar(severity_counts, x='Severity', y='Count', color='Severity',
                                 color_discrete_map=severity_colors, title='Issues by Severity')
            st.plotly_chart(fig_severity, use_container_width=True)
        
        with viz_col2:
            note_counts = df['Note_Type'].value_counts().reset_index()
            note_counts.columns = ['Note_Type', 'Count']
            
            fig_notes = px.pie(note_counts, names='Note_Type', values='Count', 
                              title='Note Type Distribution')
            st.plotly_chart(fig_notes, use_container_width=True)
        
        # ... [Rest of your existing tabs and analysis code] ...

# Mobile Responsive Notice
st.markdown("""
<div style='text-align: center; margin-top: 20px; padding: 10px; background: #f0f2f6; border-radius: 5px;'>
<small>This dashboard is optimized for both desktop and mobile devices. For best experience on mobile, use landscape orientation.</small>
</div>
""", unsafe_allow_html=True)
