import streamlit as st
import pandas as pd
import io
import plotly.express as px
import streamlit.components.v1 as components
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from collections import Counter
import os
import hashlib
import re

# Set page configuration with a modern layout
st.set_page_config(page_title="INTERSOFT Analyzer", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a modern, sleek design
st.markdown("""
<style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: #ffffff;
    }
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1e40af;
        transform: scale(1.05);
    }
    .stFileUploader {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .stExpander {
        background-color: rgba(255,255,255,0.1);
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .stDataFrame {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 10px;
    }
    .sidebar .sidebar-content {
        background-color: #1e293b;
        color: #ffffff;
    }
    h1, h2, h3, h4 {
        color: #ffffff;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .metric-card {
        background-color: rgba(255,255,255,0.15);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.2);
    }
    .clock-container {
        font-family: 'Segoe UI', monospace;
        font-size: 18px;
        color: #fff;
        background: rgba(0,0,0,0.3);
        padding: 10px 20px;
        border-radius: 8px;
        position: fixed;
        top: 10px;
        right: 20px;
        z-index: 9999;
    }
</style>
""", unsafe_allow_html=True)

# Clock HTML with a simpler, modern design
clock_html = """
<div class="clock-container">
    <div id="clock"></div>
</div>
<script>
function updateClock() {
    const now = new Date();
    const time = now.toLocaleTimeString();
    const date = now.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    document.getElementById('clock').innerText = `${time} | ${date}`;
}
setInterval(updateClock, 1000);
updateClock();
</script>
"""
components.html(clock_html, height=50, scrolling=False)

# Sidebar for navigation and theme toggle
with st.sidebar:
    st.markdown("<h2 style='color:#ffffff;'>INTERSOFT Analyzer</h2>", unsafe_allow_html=True)
    theme = st.selectbox("Theme", ["Dark", "Light"])
    if theme == "Light":
        st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
                color: #1e293b;
            }
            h1, h2, h3, h4 { color: #1e293b; }
        </style>
        """, unsafe_allow_html=True)

# Main title with emoji and animation
st.markdown("""
<h1 style='text-align:center;'>
    📊 INTERSOFT Analyzer
</h1>
<div style='text-align:center; font-size:18px; color:#ffffff; margin-bottom:20px;'>
    Analyze and optimize your data with ease
</div>
""", unsafe_allow_html=True)

# File uploader with progress bar
uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"], help="Upload an Excel file with columns: NOTE, Terminal_Id, Technician_Name, Ticket_Type")
if uploaded_file:
    progress_bar = st.progress(0)
    progress_bar.progress(20)

# Required columns and data processing functions
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

def suggest_solutions(note_type):
    solutions = {
        "WRONG DATE": "Verify device timestamp and sync with server.",
        "TERMINAL ID - WRONG DATE": "Recheck terminal ID and date configuration.",
        "NO IMAGE FOR THE DEVICE": "Capture and upload device image.",
        "NO RETAILERS SIGNATURE": "Ensure retailer signs the form.",
        "NO ENGINEER SIGNATURE": "Engineer must sign before submission.",
        "NO SIGNATURE": "Capture all required signatures.",
        "UNCLEAR IMAGE": "Retake photo with better clarity.",
        "NOT ACTIVE": "Check and retry activation process.",
        "NO BILL": "Attach a valid billing document.",
        "NO RECEIPT": "Upload a clear transaction receipt.",
        "ANOTHER TERMINAL RECEIPT": "Upload the correct terminal's receipt.",
        "WRONG RECEIPT": "Verify and re-upload the correct receipt.",
        "REJECTED RECEIPT": "Correct and resubmit the receipt.",
        "MULTIPLE ISSUES": "Address all issues and update note.",
        "NO J.O": "Provide Job Order details.",
        "PENDING": "Finalize the pending task.",
        "MISSING INFORMATION": "Provide complete details."
    }
    return solutions.get(note_type, "No solution available.")

def generate_alerts(df):
    alerts = []
    critical_percent = (df['Problem_Severity'] == 'Critical').mean() * 100
    if critical_percent > 50:
        alerts.append(f"⚠️ High critical problems: {critical_percent:.1f}%")
    tech_problems = df.groupby('Technician_Name')['Problem_Severity'].apply(
        lambda x: (x != 'Low').mean() * 100)
    for tech, percent in tech_problems.items():
        if percent > 20:
            alerts.append(f"👨‍🔧 Technician {tech} has high problem rate: {percent:.1f}%")
    return alerts

# File processing
if uploaded_file:
    progress_bar.progress(40)
    uploaded_bytes = uploaded_file.read()
    uploaded_file.seek(0)
    file_hash = hashlib.md5(uploaded_bytes).hexdigest()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_filename = f"{timestamp}_{file_hash}.xlsx"
    ARCHIVE_DIR = "uploaded_archive"
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    archive_path = os.path.join(ARCHIVE_DIR, archive_filename)
    with open(archive_path, "wb") as f:
        f.write(uploaded_bytes)

    try:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
    except:
        df = pd.read_excel(uploaded_file)
    progress_bar.progress(60)

    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ Missing required columns. Available: {list(df.columns)}")
    else:
        df['Note_Type'] = df['NOTE'].apply(classify_note)
        df['Problem_Severity'] = df['Note_Type'].apply(problem_severity)
        df['Suggested_Solution'] = df['Note_Type'].apply(suggest_solutions)
        st.success("✅ File processed successfully!")
        progress_bar.progress(100)

        # Metrics dashboard
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='metric-card'><h3>Total Notes</h3><p>{len(df)}</p></div>", unsafe_allow_html=True)
        with col2:
            critical_count = (df['Problem_Severity'] == 'Critical').sum()
            st.markdown(f"<div class='metric-card'><h3>Critical Issues</h3><p>{critical_count}</p></div>", unsafe_allow_html=True)
        with col3:
            done_count = (df['Note_Type'] == 'DONE').sum()
            st.markdown(f"<div class='metric-card'><h3>Completed Tasks</h3><p>{done_count}</p></div>", unsafe_allow_html=True)

        # Alerts section
        alerts = generate_alerts(df)
        if alerts:
            with st.expander("🚨 Alerts", expanded=True):
                for alert in alerts:
                    st.markdown(f"""
                    <div style='background-color:#fef3c7; color:#78350f; padding:10px; border-radius:8px; margin-bottom:10px;'>
                        {alert}
                    </div>
                    """, unsafe_allow_html=True)

        # Tabs for analysis
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "📊 Note Summary", "👨‍🔧 Technician Notes", "🚨 Top Issues",
            "🥧 Distribution", "✅ Completed", "📑 Details", 
            "✍️ Signatures", "🔍 Deep Analysis"
        ])

        with tab1:
            st.markdown("### 🔢 Note Type Summary")
            note_counts = df['Note_Type'].value_counts().reset_index()
            note_counts.columns = ["Note_Type", "Count"]
            st.dataframe(note_counts, use_container_width=True)
            fig_bar = px.bar(note_counts, x="Note_Type", y="Count", title="Note Type Frequency",
                             color="Note_Type", template="plotly_dark" if theme == "Dark" else "plotly_white")
            st.plotly_chart(fig_bar, use_container_width=True)

        with tab2:
            st.markdown("### 📈 Notes per Technician")
            tech_counts = df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
            fig_tech = px.bar(tech_counts.reset_index(), x="Technician_Name", y="Note_Type",
                              title="Notes per Technician", color="Note_Type",
                              template="plotly_dark" if theme == "Dark" else "plotly_white")
            st.plotly_chart(fig_tech, use_container_width=True)

        with tab3:
            st.markdown("### 🚨 Top 5 Technicians with Issues")
            filtered_df = df[~df['Note_Type'].isin(['DONE', 'NO J.O'])]
            tech_counts_filtered = filtered_df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
            top_5_technicians = tech_counts_filtered.head(5)
            technician_notes_count = top_5_technicians.reset_index()
            technician_notes_count.columns = ['Technician_Name', 'Notes_Count']
            st.dataframe(technician_notes_count, use_container_width=True)
            fig_top = px.bar(technician_notes_count, x="Technician_Name", y="Notes_Count",
                             title="Top 5 Technicians with Issues", color="Notes_Count",
                             template="plotly_dark" if theme == "Dark" else "plotly_white")
            st.plotly_chart(fig_top, use_container_width=True)

        with tab4:
            st.markdown("### 🥧 Note Type Distribution")
            fig_pie = px.pie(note_counts, names='Note_Type', values='Count', title='Note Type Distribution',
                             template="plotly_dark" if theme == "Dark" else "plotly_white")
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

        with tab5:
            st.markdown("### ✅ Completed Terminals")
            done_terminals = df[df['Note_Type'] == 'DONE'][['Technician_Name', 'Terminal_Id', 'Ticket_Type']]
            done_terminals_counts = done_terminals['Technician_Name'].value_counts()
            done_terminals_summary = done_terminals_counts.head(5).reset_index()
            done_terminals_summary.columns = ['Technician_Name', 'DONE_Notes_Count']
            st.dataframe(done_terminals_summary, use_container_width=True)
            fig_done = px.bar(done_terminals_summary, x="Technician_Name", y="DONE_Notes_Count",
                              title="Top 5 Technicians with Completed Tasks", color="DONE_Notes_Count",
                              template="plotly_dark" if theme == "Dark" else "plotly_white")
            st.plotly_chart(fig_done, use_container_width=True)

        with tab6:
            st.markdown("### 📑 Detailed Notes for Top 5 Technicians")
            for tech in top_5_technicians.index:
                st.markdown(f"#### 🧑 Technician: {tech}")
                technician_data = filtered_df[filtered_df['Technician_Name'] == tech]
                st.dataframe(technician_data[['Technician_Name', 'Note_Type', 'Terminal_Id', 'Ticket_Type']],
                             use_container_width=True)

        with tab7:
            st.markdown("## ✍️ Signature Issues Analysis")
            signature_issues_df = df[df['NOTE'].str.upper().str.contains("SIGNATURE", na=False)]
            if signature_issues_df.empty:
                st.success("✅ No signature-related issues found!")
            else:
                st.markdown("### 📋 Summary Table")
                sig_group = signature_issues_df.groupby('Technician_Name')['NOTE'].count().reset_index(name='Signature_Issues')
                total_tech = df.groupby('Technician_Name')['NOTE'].count().reset_index(name='Total_Notes')
                sig_merged = pd.merge(sig_group, total_tech, on='Technician_Name')
                sig_merged['Signature_Issue_Rate (%)'] = (sig_merged['Signature_Issues'] / sig_merged['Total_Notes']) * 100
                st.dataframe(sig_merged, use_container_width=True)

                st.markdown("### 📊 Bar Chart")
                fig_sig_bar = px.bar(sig_merged, x='Technician_Name', y='Signature_Issues',
                                     color='Signature_Issue_Rate (%)', title='Signature Issues per Technician',
                                     template="plotly_dark" if theme == "Dark" else "plotly_white")
                st.plotly_chart(fig_sig_bar, use_container_width=True)

                st.markdown("### 📈 Line Chart")
                fig_sig_line = px.line(sig_merged, x='Technician_Name', y='Signature_Issue_Rate (%)',
                                       markers=True, title='Signature Issue Rate',
                                       template="plotly_dark" if theme == "Dark" else "plotly_white")
                st.plotly_chart(fig_sig_line, use_container_width=True)

                st.markdown("### 🗺️ Geo Map (Dummy Coordinates)")
                df_map = signature_issues_df.copy()
                df_map['lat'] = 24.7136 + (df_map.index % 10) * 0.03
                df_map['lon'] = 46.6753 + (df_map.index % 10) * 0.03
                st.map(df_map[['lat', 'lon']])

                sig_output = io.BytesIO()
                with pd.ExcelWriter(sig_output, engine='xlsxwriter') as writer:
                    signature_issues_df.to_excel(writer, index=False, sheet_name="Signature Issues")
                    sig_merged.to_excel(writer, index=False, sheet_name="Technician Summary")
                st.download_button("📥 Download Signature Issues Report", sig_output.getvalue(),
                                  "signature_issues.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        with tab8:
            st.markdown("## 🔍 Deep Problem Analysis")
            common_problems = df[~df['Note_Type'].isin(['DONE'])]
            problem_freq = common_problems['Note_Type'].value_counts().reset_index()
            problem_freq.columns = ["Problem", "Count"]

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📌 Common Problems")
                st.dataframe(problem_freq, use_container_width=True)
            with col2:
                st.markdown("### 🥧 Problem Distribution")
                fig_problems = px.pie(problem_freq, names='Problem', values='Count',
                                     title='Problem Distribution',
                                     template="plotly_dark" if theme == "Dark" else "plotly_white")
                st.plotly_chart(fig_problems, use_container_width=True)

            st.markdown("### 🎫 Ticket Type vs Problem Type")
            ticket_problem = pd.crosstab(df['Ticket_Type'], df['Note_Type'])
            st.dataframe(ticket_problem.style.background_gradient(cmap='Blues'), use_container_width=True)

            st.markdown("### 💡 Suggested Solutions")
            solutions_df = df[['Note_Type', 'Suggested_Solution']].drop_duplicates()
            st.dataframe(solutions_df, use_container_width=True)

        # Download full report
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for note_type in df['Note_Type'].unique():
                subset = df[df['Note_Type'] == note_type]
                subset[['Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type']].to_excel(writer, sheet_name=note_type[:31], index=False)
            note_counts.to_excel(writer, sheet_name="Note Type Count", index=False)
            tech_counts_filtered.reset_index().to_excel(writer, sheet_name="Technician Notes Count", index=False)
            done_terminals.to_excel(writer, sheet_name="DONE_Terminals", index=False)
            solutions_df.to_excel(writer, sheet_name="Suggested Solutions", index=False)
        st.download_button("📥 Download Full Report", output.getvalue(), "FULL_SUMMARY.xlsx",
                          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
