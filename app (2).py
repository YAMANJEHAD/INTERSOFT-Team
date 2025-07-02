import streamlit as st
import pandas as pd
import io
import plotly.express as px
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import os
import hashlib
import re
from PIL import Image, ImageDraw, ImageFont

# Page Configuration
st.set_page_config(
    page_title="INTERSOFT Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== Helper Functions ==========

def create_default_logo():
    """Create default logo if image file doesn't exist"""
    img = Image.new('RGB', (100, 100), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    d.text((10,10), "LOGO", fill=(255,255,0), font=font)
    return img

def load_logo():
    """Load application logo"""
    try:
        return Image.open("logo.png")
    except:
        return create_default_logo()

def set_dark_mode():
    """Enable dark mode"""
    st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E1E;
        color: white;
    }
    .sidebar .sidebar-content {
        background-color: #2E2E2E;
    }
    .widget-label, .st-bb, .st-at, .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

def normalize(text):
    """Normalize text format"""
    text = str(text).upper()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def classify_note(note):
    """Classify notes"""
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
        "NO SIGNATURE": ["NO SIGNATURE","NO SIGNATURES"],
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
        "MULTIPLE ISSUES":["MULTIPLE ISSUES"]
    }
    if "+" in note: return "MULTIPLE ISSUES"
    matched_labels = []
    for label, keywords in patterns.items():
        if any(keyword in note for keyword in keywords):
            matched_labels.append(label)
    return matched_labels[0] if matched_labels else "MISSING INFORMATION"

def problem_severity(note_type):
    """Determine problem severity"""
    severity_map = {
        "Critical": ["WRONG DATE", "TERMINAL ID - WRONG DATE", "REJECTED RECEIPT"],
        "High": ["NO IMAGE", "UNCLEAR IMAGE", "NO RECEIPT"],
        "Medium": ["NO SIGNATURE", "NO ENGINEER SIGNATURE"],
        "Low": ["NO J.O", "PENDING"]
    }
    for severity, types in severity_map.items():
        if note_type in types: return severity
    return "Unclassified"

def suggest_solutions(note_type):
    """Suggest solutions for problems"""
    solutions = {
        "WRONG DATE": "Verify device timestamp and sync with server",
        "TERMINAL ID - WRONG DATE": "Recheck terminal ID and date configuration",
        "NO IMAGE FOR THE DEVICE": "Capture and upload device image",
        "NO RETAILERS SIGNATURE": "Ensure retailer signs the form",
        "NO ENGINEER SIGNATURE": "Engineer must sign before submission",
        "NO SIGNATURE": "Capture required signatures from all parties",
        "UNCLEAR IMAGE": "Retake photo with better lighting",
        "NOT ACTIVE": "Check activation process and retry",
        "NO BILL": "Attach valid billing document",
        "NO RECEIPT": "Upload clear transaction receipt image",
        "ANOTHER TERMINAL RECEIPT": "Ensure correct terminal's receipt is uploaded",
        "WRONG RECEIPT": "Verify and re-upload correct receipt",
        "REJECTED RECEIPT": "Follow up on rejection reason and correct",
        "MULTIPLE ISSUES": "Resolve all mentioned issues and update note",
        "NO J.O": "Provide Job Order number/details",
        "PENDING": "Complete and finalize pending task",
        "MISSING INFORMATION": "Review note and provide complete details",
    }
    return solutions.get(note_type, "No solution available")

# ========== UI Components ==========

# Sidebar
with st.sidebar:
    st.title("Settings")
    dark_mode = st.checkbox('🌙 Dark Mode')
    if dark_mode: set_dark_mode()

# Header
col1, col2 = st.columns([1, 4])
with col1:
    try:
        logo = load_logo()
        st.image(logo, width=80)
    except:
        st.markdown("### 🏢")
with col2:
    st.markdown("<h1 style='color:#ffffff; margin-top:15px;'>📊 INTERSOFT Analyzer</h1>", unsafe_allow_html=True)

# Digital Clock
components.html("""
<div style="text-align:right; font-family:monospace; font-size:20px; margin-bottom:20px;">
    <div id="datetime"></div>
</div>
<script>
function updateTime() {
    const now = new Date();
    document.getElementById("datetime").innerHTML = 
        now.toLocaleDateString() + " | " + now.toLocaleTimeString();
}
setInterval(updateTime, 1000);
updateTime();
</script>
""", height=50)

# ========== Pending Tickets Section ==========
st.markdown("## 📌 Pending Tickets Analysis")

with st.expander("🧮 Filter Unprocessed Tickets by Ticket_Id", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        all_file = st.file_uploader("🔄 Upload ALL Tickets File", type=["xlsx"])
    with col2:
        done_file = st.file_uploader("✅ Upload DONE Tickets File", type=["xlsx"])

    if all_file and done_file:
        try:
            all_df = pd.read_excel(all_file)
            done_df = pd.read_excel(done_file)

            if 'Ticket_Id' not in all_df.columns or 'Ticket_Id' not in done_df.columns:
                st.error("❌ Both files must contain a 'Ticket_Id' column")
            else:
                # Remove duplicates
                all_df = all_df.drop_duplicates(subset=['Ticket_Id'], keep='first')
                done_df = done_df.drop_duplicates(subset=['Ticket_Id'], keep='first')
                
                pending_df = all_df[~all_df['Ticket_Id'].isin(done_df['Ticket_Id'])]
                
                # KPIs
                st.markdown("### 📊 Performance Metrics")
                cols = st.columns(4)
                with cols[0]:
                    st.metric("Total Tickets", len(all_df))
                with cols[1]:
                    st.metric("Completed", len(done_df))
                with cols[2]:
                    st.metric("Pending", len(pending_df))
                with cols[3]:
                    percent = (len(pending_df)/len(all_df))*100 if len(all_df)>0 else 0
                    st.metric("Pending Percentage", f"{percent:.1f}%")

                # Filters
                st.markdown("### 🔍 Filter Results")
                filter_cols = st.columns(3)
                filters = {}
                
                if 'Date' in pending_df.columns:
                    with filter_cols[0]:
                        date_options = ["All Periods", "Last Week", "Last Month"]
                        date_sel = st.selectbox("Time Period", date_options)
                        if date_sel == "Last Week":
                            pending_df = pending_df[pending_df['Date'] >= (datetime.now() - timedelta(days=7))]
                        elif date_sel == "Last Month":
                            pending_df = pending_df[pending_df['Date'] >= (datetime.now() - timedelta(days=30))]
                
                if 'Technician_Name' in pending_df.columns:
                    with filter_cols[1]:
                        techs = st.multiselect("Technician", pending_df['Technician_Name'].unique())
                        if techs:
                            pending_df = pending_df[pending_df['Technician_Name'].isin(techs)]
                
                if 'Ticket_Type' in pending_df.columns:
                    with filter_cols[2]:
                        types = st.multiselect("Ticket Type", pending_df['Ticket_Type'].unique())
                        if types:
                            pending_df = pending_df[pending_df['Ticket_Type'].isin(types)]
                
                # Display results
                st.dataframe(pending_df, use_container_width=True)
                
                # Export options
                st.download_button(
                    "📥 Download Pending Tickets (Excel)",
                    pending_df.to_excel(index=False),
                    "pending_tickets.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"❌ Error processing files: {str(e)}")

# ========== Main Analysis ==========
st.markdown("## 📊 Comprehensive Analysis Dashboard")

uploaded_file = st.file_uploader("📁 Upload Data File for Analysis", type=["xlsx"])
required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        
        if not all(col in df.columns for col in required_cols):
            st.error(f"❌ Required columns missing. Available columns: {list(df.columns)}")
        else:
            # Data cleaning
            if 'Ticket_Id' in df.columns:
                df = df.drop_duplicates(subset=['Ticket_Id'], keep='first')
            
            df['Note_Type'] = df['NOTE'].apply(classify_note)
            df['Problem_Severity'] = df['Note_Type'].apply(problem_severity)
            df['Suggested_Solution'] = df['Note_Type'].apply(suggest_solutions)
            
            # Severity colors
            severity_colors = {
                "Critical": "#FF0000",  # Red
                "High": "#FFA500",      # Orange
                "Medium": "#FFFF00",    # Yellow
                "Low": "#00FF00",       # Green
                "Unclassified": "#808080" # Gray
            }
            
            # KPIs
            st.markdown("### 📈 Performance Overview")
            kpi_cols = st.columns(4)
            
            with kpi_cols[0]:
                st.metric("Total Tickets", len(df))
            with kpi_cols[1]:
                done = len(df[df['Note_Type'] == 'DONE'])
                st.metric("Completed", done)
            with kpi_cols[2]:
                critical = len(df[df['Problem_Severity'] == 'Critical'])
                st.metric("Critical Issues", critical)
            with kpi_cols[3]:
                st.metric("Avg Resolution Time", "3 days")  # Replace with actual calculation
            
            # Visualizations
            st.markdown("### 📊 Data Visualizations")
            
            # Note types chart
            fig1 = px.pie(
                df['Note_Type'].value_counts().reset_index(),
                names='Note_Type',
                values='count',
                title="Note Type Distribution"
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Severity chart
            severity_df = df['Problem_Severity'].value_counts().reset_index()
            fig2 = px.bar(
                severity_df,
                x='Problem_Severity',
                y='count',
                color='Problem_Severity',
                color_discrete_map=severity_colors,
                title="Problems by Severity Level"
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # Technicians analysis
            st.markdown("### 👨‍🔧 Technician Performance Analysis")
            
            tech_df = df.groupby('Technician_Name').agg({
                'Ticket_Type': 'count',
                'Problem_Severity': lambda x: (x == 'Critical').sum()
            }).rename(columns={
                'Ticket_Type': 'Total_Tickets',
                'Problem_Severity': 'Critical_Issues'
            }).sort_values('Total_Tickets', ascending=False)
            
            st.dataframe(tech_df, use_container_width=True)
            
            # Export final report
            st.markdown("### 📤 Export Results")
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name="Complete Data", index=False)
                tech_df.to_excel(writer, sheet_name="Technician Performance", index=True)
            
            st.download_button(
                "📥 Download Full Report",
                output.getvalue(),
                "full_report.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")

# Footer
st.markdown("""
<div style="text-align:center; margin-top:50px; padding:20px; background:#f0f2f6;">
    <p>INTERSOFT Analyzer - Version 1.0</p>
    <p>© 2023 All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
