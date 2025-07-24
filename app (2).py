import streamlit as st
import pandas as pd
import io
import plotly.express as px
import streamlit.components.v1 as components
from datetime import datetime
from collections import Counter
import os
import hashlib
import re

# Set page configuration
st.set_page_config(page_title="INTERSOFT Analyzer", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a cohesive design
st.markdown("""
<style>
    .stApp {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2563eb;
        transform: scale(1.05);
    }
    .stFileUploader {
        background-color: var(--card-bg);
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .stExpander {
        background-color: var(--card-bg);
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .stDataFrame {
        border-radius: 8px;
        padding: 10px;
        background-color: var(--card-bg);
    }
    .sidebar .sidebar-content {
        background-color: var(--sidebar-bg);
        color: var(--text-color);
    }
    h1, h2, h3, h4 {
        color: var(--text-color);
        margin-top: 10px;
    }
    .stMetric {
        background-color: var(--card-bg);
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .sidebar-metric {
        background-color: var(--card-bg);
        border-radius: 6px;
        padding: 8px;
        margin-bottom: 8px;
        font-size: 14px;
    }
    .clock-container {
        font-family: 'Segoe UI', monospace;
        font-size: 14px;
        color: var(--text-color);
        background: rgba(0,0,0,0.2);
        padding: 6px 12px;
        border-radius: 6px;
        position: fixed;
        top: 10px;
        right: 15px;
        z-index: 9999;
    }
</style>
""", unsafe_allow_html=True)

# Theme detection (existing JavaScript, no new additions)
theme_html = """
<script>
    function setTheme() {
        const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        document.documentElement.style.setProperty('--background', prefersDark ? 
            'linear-gradient(135deg, #1e3a8a, #3b82f6)' : 
            'linear-gradient(135deg, #e0f2fe, #f8fafc)');
        document.documentElement.style.setProperty('--text-color', prefersDark ? '#ffffff' : '#1e293b');
        document.documentElement.style.setProperty('--card-bg', prefersDark ? 'rgba(255,255,255,0.15)' : '#ffffff');
        document.documentElement.style.setProperty('--sidebar-bg', prefersDark ? '#1e293b' : '#f1f5f9');
    }
    setTheme();
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", setTheme);
</script>
<style>
    .stApp {
        background: var(--background);
        color: var(--text-color);
    }
    h1, h2, h3, h4 { color: var(--text-color); }
    .stMetric, .stDataFrame, .stFileUploader, .stExpander { background-color: var(--card-bg); }
</style>
"""
components.html(theme_html, height=0)

# Clock (existing, unchanged)
clock_html = """
<div class="clock-container">
    <div id="clock"></div>
</div>
<script>
function updateClock() {
    const now = new Date();
    const time = now.toLocaleTimeString();
    const date = now.toLocaleDateString(undefined, { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' });
    document.getElementById('clock').innerText = `${time} | ${date}`;
}
setInterval(updateClock, 1000);
updateClock();
</script>
"""
components.html(clock_html, height=40)

# Sidebar with detailed metrics
with st.sidebar:
    st.markdown("<h2 style='color:var(--text-color);'>INTERSOFT Analyzer</h2>", unsafe_allow_html=True)
    st.markdown("Real-time data analysis for operational insights.")

# Main title
with st.container():
    st.markdown("""
    <h1 style='text-align:center;'>📊 INTERSOFT Analyzer</h1>
    <div style='text-align:center; font-size:16px; margin-bottom:15px;'>
        Optimize operations with data-driven insights
    </div>
    """, unsafe_allow_html=True)

# File uploader
with st.container():
    uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"], help="Upload an Excel file with columns: NOTE, Terminal_Id, Technician_Name, Ticket_Type")
    if uploaded_file:
        progress_bar = st.progress(0)
        progress_bar.progress(20)

# Data processing functions
required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

def normalize(text):
    text = str(text).upper()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def classify_note(note):
    note = normalize(note)
    patterns = {
        "TERMINAL ID - WRONG DATE": ["TERMINAL ID WRONG DATE"],
        "NO IMAGE FOR THE DEVICE": ["NO IMAGE FOR THE DEVICE"],
        "IMAGE FOR THE DEVICE ONLY": ["IMAGE FOR THE DEVICE ONLY"],
        "WRONG DATE": ["WRONG DATE"],
        "TERMINAL ID": ["TERMINAL ID"],
        "NO J.O": ["NO JO", "NO J O"],
        "DONE": ["DONE"],
        "NO RETAILERS SIGNATURE": ["NO RETAILERS SIGNATURE", "NO RETAILER SIGNATURE"],
        "UNCLEAR IMAGE": ["UNCLEAR IMAGE"],
        "NO ENGINEER SIGNATURE": ["NO ENGINEER SIGNATURE"],
        "NO SIGNATURE": ["NO SIGNATURE", "NO SIGNATURES"],
        "PENDING": ["PENDING"],
        "NO INFORMATIONS": ["NO INFORMATION", "NO INFORMATIONS"],
        "MISSING INFORMATION": ["MISSING INFORMATION"],
        "NO BILL": ["NO BILL"],
        "NOT ACTIVE": ["NOT ACTIVE"],
        "NO RECEIPT": ["NO RECEIPT"],
        "ANOTHER TERMINAL RECEIPT": ["ANOTHER TERMINAL RECEIPT"],
        "UNCLEAR RECEIPT": ["UNCLEAR RECEIPT"],
        "WRONG RECEIPT": ["WRONG RECEIPT"],
        "REJECTED RECEIPT": ["REJECTED RECEIPT"],
        "MULTIPLE ISSUES": ["MULTIPLE ISSUES"]
    }
    if "+" in note:
        return "MULTIPLE ISSUES"
    matched_labels = []
    for label, keywords in patterns.items():
        for keyword in keywords:
            if keyword in note:
                matched_labels.append(label)
                break
    return matched_labels[0] if len(matched_labels) == 1 else "MULTIPLE ISSUES" if matched_labels else "MISSING INFORMATION"

def problem_severity(note_type):
    critical = ["WRONG DATE", "TERMINAL ID - WRONG DATE", "REJECTED RECEIPT"]
    high = ["NO IMAGE", "UNCLEAR IMAGE", "NO RECEIPT"]
    medium = ["NO SIGNATURE", "NO ENGINEER SIGNATURE"]
    low = ["NO J.O", "PENDING"]
    if note_type in critical: return "Critical"
    if note_type in high: return "High"
    if note_type in medium: return "Medium"
    if note_type in low: return "Low"
    return "Unclassified"

# File processing
if uploaded_file:
    progress_bar.progress(40)
    uploaded_bytes = uploaded_file.read()
    uploaded_file.seek(0)
    file_hash = hashlib.md5(uploaded_bytes).hexdigest()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ARCHIVE_DIR = "uploaded_archive"
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    archive_path = os.path.join(ARCHIVE_DIR, f"{timestamp}_{file_hash}.xlsx")
    with open(archive_path, "wb") as f:
        f.write(uploaded_bytes)

    try:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
    except:
        df = pd.read_excel(uploaded_file)
    progress_bar.progress(60)

    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ Missing required columns: {list(set(required_cols) - set(df.columns))}")
    else:
        df['Note_Type'] = df['NOTE'].apply(classify_note)
        df['Problem_Severity'] = df['Note_Type'].apply(problem_severity)
        st.success("✅ File processed successfully!")
        progress_bar.progress(100)

        # Sidebar metrics
        with st.sidebar:
            st.markdown("### 📊 Key Metrics")
            st.markdown(f"<div class='sidebar-metric'><strong>Total Notes:</strong> {len(df)}</div>", unsafe_allow_html=True)
            critical_count = (df['Problem_Severity'] == 'Critical').sum()
            st.markdown(f"<div class='sidebar-metric'><strong>Critical Issues:</strong> {critical_count}</div>", unsafe_allow_html=True)
            done_count = (df['Note_Type'] == 'DONE').sum()
            st.markdown(f"<div class='sidebar-metric'><strong>Completed Tasks:</strong> {done_count}</div>", unsafe_allow_html=True)
            top_problem = df['Note_Type'].value_counts().index[0] if not df['Note_Type'].empty else "N/A"
            st.markdown(f"<div class='sidebar-metric'><strong>Top Problem:</strong> {top_problem}</div>", unsafe_allow_html=True)
            total_technicians = df['Technician_Name'].nunique()
            st.markdown(f"<div class='sidebar-metric'><strong>Total Technicians:</strong> {total_technicians}</div>", unsafe_allow_html=True)

        # Metrics dashboard
        with st.container():
            st.markdown("### 📈 Overview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Total Notes", value=len(df))
            with col2:
                st.metric(label="Critical Issues", value=critical_count)
            with col3:
                st.metric(label="Completed Tasks", value=done_count)

        # Tabs for analysis
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Summary", "👨‍🔧 Technicians", "🚨 Top Issues",
            "🥧 Distribution", "✅ Completed", "📑 Details"
        ])

        with tab1:
            st.markdown("### 🔢 Note Type Summary")
            note_counts = df['Note_Type'].value_counts().reset_index()
            note_counts.columns = ["Note_Type", "Count"]
            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(note_counts, use_container_width=True)
            with col2:
                fig_bar = px.bar(note_counts, x="Note_Type", y="Count", title="Note Type Frequency",
                                 color="Note_Type", color_continuous_scale="Blues")
                st.plotly_chart(fig_bar, use_container_width=True)

        with tab2:
            st.markdown("### 📈 Notes per Technician")
            tech_counts = df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(tech_counts.reset_index(), use_container_width=True)
            with col2:
                fig_tech = px.bar(tech_counts.reset_index(), x="Technician_Name", y="Note_Type",
                                  title="Notes per Technician", color="Note_Type", color_continuous_scale="Blues")
                st.plotly_chart(fig_tech, use_container_width=True)

        with tab3:
            st.markdown("### 🚨 Top 5 Technicians with Issues")
            filtered_df = df[~df['Note_Type'].isin(['DONE', 'NO J.O'])]
            tech_counts_filtered = filtered_df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
            top_5_technicians = tech_counts_filtered.head(5)
            technician_notes_count = top_5_technicians.reset_index()
            technician_notes_count.columns = ['Technician_Name', 'Notes_Count']
            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(technician_notes_count, use_container_width=True)
            with col2:
                fig_top = px.bar(technician_notes_count, x="Technician_Name", y="Notes_Count",
                                 title="Top 5 Technicians with Issues", color="Notes_Count", color_continuous_scale="Blues")
                st.plotly_chart(fig_top, use_container_width=True)

        with tab4:
            st.markdown("### 🥧 Note Type Distribution")
            fig_pie = px.pie(note_counts, names='Note_Type', values='Count', title='Note Type Distribution',
                             color_discrete_sequence=px.colors.sequential.Blues)
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

        with tab5:
            st.markdown("### ✅ Completed Terminals")
            done_terminals = df[df['Note_Type'] == 'DONE'][['Technician_Name', 'Terminal_Id', 'Ticket_Type']]
            done_terminals_counts = done_terminals['Technician_Name'].value_counts()
            done_terminals_summary = done_terminals_counts.head(5).reset_index()
            done_terminals_summary.columns = ['Technician_Name', 'DONE_Notes_Count']
            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(done_terminals_summary, use_container_width=True)
            with col2:
                fig_done = px.bar(done_terminals_summary, x="Technician_Name", y="DONE_Notes_Count",
                                  title="Top 5 Technicians with Completed Tasks", color="DONE_Notes_Count",
                                  color_continuous_scale="Blues")
                st.plotly_chart(fig_done, use_container_width=True)

        with tab6:
            st.markdown("### 📑 Detailed Notes for Top 5 Technicians")
            for tech in top_5_technicians.index:
                st.markdown(f"#### 🧑 Technician: {tech}")
                technician_data = filtered_df[filtered_df['Technician_Name'] == tech]
                st.dataframe(technician_data[['Technician_Name', 'Note_Type', 'Terminal_Id', 'Ticket_Type']],
                             use_container_width=True)

        # Download full report
        with st.container():
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for note_type in df['Note_Type'].unique():
                    subset = df[df['Note_Type'] == note_type]
                    subset[['Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type']].to_excel(writer, sheet_name=note_type[:31], index=False)
                note_counts.to_excel(writer, sheet_name="Note Type Count", index=False)
                tech_counts_filtered.reset_index().to_excel(writer, sheet_name="Technician Notes Count", index=False)
                done_terminals.to_excel(writer, sheet_name="DONE_Terminals", index=False)
            st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
            st.download_button("📥 Download Full Report", output.getvalue(), "FULL_SUMMARY.xlsx",
                              mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
