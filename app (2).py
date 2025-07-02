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
from collections import defaultdict

# Page Configuration
st.set_page_config(
    page_title="INTERSOFT Analyzer Pro",
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
    """Enable dark mode styling"""
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
    .metric-card {
        background-color: #2E2E2E;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 5px solid #4e79a7;
    }
    .duplicate-badge {
        color: white;
        background-color: #ff4b4b;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        margin-left: 10px;
    }
    .unique-badge {
        color: white;
        background-color: #59a14f;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        margin-left: 10px;
    }
    .header-style {
        border-bottom: 2px solid #4e79a7;
        padding-bottom: 5px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def analyze_duplicates(df, column_name):
    """Analyze duplicates and return detailed information"""
    duplicates = df[df.duplicated(subset=[column_name], keep=False)]
    duplicate_counts = duplicates[column_name].value_counts().to_dict()
    
    duplicate_details = defaultdict(list)
    for _, row in duplicates.iterrows():
        duplicate_details[row[column_name]].append(row.to_dict())
    
    return duplicates, duplicate_counts, duplicate_details

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
    st.markdown("<h1 style='color:#ffffff; margin-top:15px;'>📊 INTERSOFT Analyzer Pro</h1>", unsafe_allow_html=True)

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
st.markdown('<div class="header-style">📌 Pending Tickets Analysis</div>', unsafe_allow_html=True)

with st.expander("🧮 Filter Unprocessed Tickets by Ticket_Id", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        all_file = st.file_uploader("🔄 Upload ALL Tickets File", type=["xlsx"])
    with col2:
        done_file = st.file_uploader("✅ Upload DONE Tickets File", type=["xlsx"])

    if all_file and done_file:
        try:
            # Read files
            all_df = pd.read_excel(all_file)
            done_df = pd.read_excel(done_file)

            # Analyze duplicates
            all_duplicates, all_dup_counts, all_dup_details = analyze_duplicates(all_df, 'Ticket_Id')
            done_duplicates, done_dup_counts, done_dup_details = analyze_duplicates(done_df, 'Ticket_Id')

            # Clean data (keep first occurrence)
            all_df_clean = all_df.drop_duplicates(subset=['Ticket_Id'], keep='first')
            done_df_clean = done_df.drop_duplicates(subset=['Ticket_Id'], keep='first')
            
            # Find pending tickets
            pending_df = all_df_clean[~all_df_clean['Ticket_Id'].isin(done_df_clean['Ticket_Id'])]
            
            # Calculate statistics
            stats = {
                'total_all': len(all_df),
                'total_completed': len(done_df),
                'total_pending': len(pending_df),
                'all_duplicates': len(all_duplicates),
                'completed_duplicates': len(done_duplicates),
                'unique_all': len(all_df_clean),
                'unique_completed': len(done_df_clean),
                'duplicate_percentage': (len(all_duplicates)/len(all_df))*100 if len(all_df) > 0 else 0
            }

            # Display results
            st.success("✅ Data analyzed successfully")
            st.markdown("---")
            
            # Key Metrics
            st.markdown('<div class="header-style">📈 Key Metrics</div>', unsafe_allow_html=True)
            cols = st.columns(4)
            
            with cols[0]:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Total Tickets</h3>
                    <h2>{stats['total_all']:,}</h2>
                    <div style="margin-top: 10px;">
                        <span class="unique-badge">{stats['unique_all']:,} unique</span>
                        <span class="duplicate-badge">{stats['all_duplicates']:,} duplicates</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with cols[1]:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Completed Tickets</h3>
                    <h2>{stats['total_completed']:,}</h2>
                    <div style="margin-top: 10px;">
                        <span class="unique-badge">{stats['unique_completed']:,} unique</span>
                        <span class="duplicate-badge">{stats['completed_duplicates']:,} duplicates</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with cols[2]:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Pending Tickets</h3>
                    <h2>{stats['total_pending']:,}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with cols[3]:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Duplicate Rate</h3>
                    <h2>{stats
