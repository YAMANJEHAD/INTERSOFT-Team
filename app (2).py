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
                    <h2>{stats['duplicate_percentage']:.1f}%</h2>
                </div>
                """, unsafe_allow_html=True)

            # Duplicate Analysis
            st.markdown("---")
            st.markdown('<div class="header-style">🔍 Duplicate Analysis</div>', unsafe_allow_html=True)
            
            if stats['all_duplicates'] > 0 or stats['completed_duplicates'] > 0:
                tab1, tab2 = st.tabs(["All Tickets Duplicates", "Completed Tickets Duplicates"])
                
                with tab1:
                    if stats['all_duplicates'] > 0:
                        st.subheader(f"All Tickets Duplicates ({stats['all_duplicates']} records)")
                        st.dataframe(all_duplicates.sort_values('Ticket_Id'), height=300)
                        
                        # Show duplicate details for selected ticket
                        selected_ticket = st.selectbox(
                            "Select a Ticket_Id to view duplicate details:",
                            list(all_dup_details.keys()),
                            key="all_dup_select"
                        )
                        
                        dup_df = pd.DataFrame(all_dup_details[selected_ticket])
                        st.dataframe(dup_df)
                    else:
                        st.info("No duplicates found in All Tickets")
                
                with tab2:
                    if stats['completed_duplicates'] > 0:
                        st.subheader(f"Completed Tickets Duplicates ({stats['completed_duplicates']} records)")
                        st.dataframe(done_duplicates.sort_values('Ticket_Id'), height=300)
                        
                        # Show duplicate details for selected ticket
                        selected_ticket = st.selectbox(
                            "Select a Ticket_Id to view duplicate details:",
                            list(done_dup_details.keys()),
                            key="done_dup_select"
                        )
                        
                        dup_df = pd.DataFrame(done_dup_details[selected_ticket])
                        st.dataframe(dup_df)
                    else:
                        st.info("No duplicates found in Completed Tickets")
            else:
                st.success("🎉 No duplicates found in any files")

            # Pending Tickets
            st.markdown("---")
            st.markdown('<div class="header-style">📋 Pending Tickets (Ready to Work)</div>', unsafe_allow_html=True)
            
            # Filters
            st.markdown("### 🔍 Filter Options")
            filter_cols = st.columns(3)
            
            if 'Date' in pending_df.columns:
                with filter_cols[0]:
                    date_options = ["All", "Last Week", "Last Month"]
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
            
            st.dataframe(pending_df, height=400)

            # Export Results
            st.markdown("---")
            st.markdown('<div class="header-style">💾 Export Results</div>', unsafe_allow_html=True)
            
            # Create Excel file in memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pending_df.to_excel(writer, index=False, sheet_name="Pending_Tickets")
                all_df_clean.to_excel(writer, index=False, sheet_name="Cleaned_All_Tickets")
                done_df_clean.to_excel(writer, index=False, sheet_name="Cleaned_Completed")
                
                if not all_duplicates.empty:
                    all_duplicates.to_excel(writer, index=False, sheet_name="All_Tickets_Duplicates")
                if not done_duplicates.empty:
                    done_duplicates.to_excel(writer, index=False, sheet_name="Completed_Duplicates")
                
                # Save statistics
                stats_df = pd.DataFrame.from_dict(stats, orient='index', columns=['Count'])
                stats_df.to_excel(writer, sheet_name="Statistics")
            
            # Download button
            st.download_button(
                label="📥 Download Full Report (Excel)",
                data=output.getvalue(),
                file_name=f"ticket_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Includes all cleaned data, duplicates, and statistics"
            )

        except Exception as e:
            st.error(f"❌ Error processing files: {str(e)}")

# ========== Main Analysis Dashboard ==========
st.markdown('<div class="header-style">📊 Comprehensive Analysis Dashboard</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📁 Upload Data File for Full Analysis", type=["xlsx"])
required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        
        if not all(col in df.columns for col in required_cols):
            st.error(f"❌ Required columns missing. Available columns: {list(df.columns)}")
        else:
            # Analyze duplicates
            duplicates, dup_counts, dup_details = analyze_duplicates(df, 'Ticket_Id')
            
            # Clean data (keep first occurrence)
            df_clean = df.drop_duplicates(subset=['Ticket_Id'], keep='first')
            
            # Classify data
            df_clean['Note_Type'] = df_clean['NOTE'].apply(classify_note)
            df_clean['Problem_Severity'] = df_clean['Note_Type'].apply(problem_severity)
            df_clean['Suggested_Solution'] = df_clean['Note_Type'].apply(suggest_solutions)
            
            # Calculate statistics
            stats = {
                'total_tickets': len(df),
                'duplicate_tickets': len(duplicates),
                'unique_tickets': len(df_clean),
                'duplicate_percentage': (len(duplicates)/len(df))*100 if len(df) > 0 else 0,
                'done_tickets': len(df_clean[df_clean['Note_Type'] == 'DONE']),
                'critical_issues': len(df_clean[df_clean['Problem_Severity'] == 'Critical'])
            }
            
            # Severity colors
            severity_colors = {
                "Critical": "#FF0000",  # Red
                "High": "#FFA500",      # Orange
                "Medium": "#FFFF00",    # Yellow
                "Low": "#00FF00",       # Green
                "Unclassified": "#808080" # Gray
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
                    <h2>{stats['total_tickets']:,}</h2>
                    <div style="margin-top: 10px;">
                        <span class="unique-badge">{stats['unique_tickets']:,} unique</span>
                        <span class="duplicate-badge">{stats['duplicate_tickets']:,} duplicates</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with cols[1]:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Completed Tickets</h3>
                    <h2>{stats['done_tickets']:,}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with cols[2]:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Critical Issues</h3>
                    <h2>{stats['critical_issues']:,}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with cols[3]:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Duplicate Rate</h3>
                    <h2>{stats['duplicate_percentage']:.1f}%</h2>
                </div>
                """, unsafe_allow_html=True)

            # Duplicate Analysis
            if stats['duplicate_tickets'] > 0:
                st.markdown("---")
                st.markdown('<div class="header-style">🔍 Duplicate Tickets Analysis</div>', unsafe_allow_html=True)
                
                st.dataframe(duplicates.sort_values('Ticket_Id'), height=300)
                
                # Show duplicate details for selected ticket
                selected_ticket = st.selectbox(
                    "Select a Ticket_Id to view duplicate details:",
                    list(dup_details.keys()),
                    key="main_dup_select"
                )
                
                dup_df = pd.DataFrame(dup_details[selected_ticket])
                st.dataframe(dup_df)
            else:
                st.markdown("---")
                st.success("🎉 No duplicate tickets found in the data")

            # Data Visualizations
            st.markdown("---")
            st.markdown('<div class="header-style">📊 Data Visualizations</div>', unsafe_allow_html=True)
            
            viz_col1, viz_col2 = st.columns(2)
            
            with viz_col1:
                # Note Type Distribution
                note_counts = df_clean['Note_Type'].value_counts().reset_index()
                note_counts.columns = ['Note_Type', 'Count']
                fig1 = px.pie(
                    note_counts,
                    names='Note_Type',
                    values='Count',
                    title="Note Type Distribution",
                    hole=0.3
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with viz_col2:
                # Problem Severity Distribution
                severity_counts = df_clean['Problem_Severity'].value_counts().reset_index()
                severity_counts.columns = ['Severity', 'Count']
                fig2 = px.bar(
                    severity_counts,
                    x='Severity',
                    y='Count',
                    color='Severity',
                    color_discrete_map=severity_colors,
                    title="Problems by Severity Level"
                )
                st.plotly_chart(fig2, use_container_width=True)

            # Technician Performance
            st.markdown("---")
            st.markdown('<div class="header-style">👨‍🔧 Technician Performance Analysis</div>', unsafe_allow_html=True)
            
            tech_df = df_clean.groupby('Technician_Name').agg({
                'Ticket_Type': 'count',
                'Problem_Severity': lambda x: (x == 'Critical').sum()
            }).rename(columns={
                'Ticket_Type': 'Total_Tickets',
                'Problem_Severity': 'Critical_Issues'
            }).sort_values('Total_Tickets', ascending=False)
            
            st.dataframe(tech_df.style.background_gradient(
                cmap='YlOrRd', 
                subset=['Critical_Issues']
            ), use_container_width=True)

            # Export Results
            st.markdown("---")
            st.markdown('<div class="header-style">💾 Export Results</div>', unsafe_allow_html=True)
            
            # Create Excel file in memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_clean.to_excel(writer, index=False, sheet_name="Clean_Data")
                tech_df.to_excel(writer, sheet_name="Technician_Performance")
                
                if not duplicates.empty:
                    duplicates.to_excel(writer, index=False, sheet_name="Duplicate_Tickets")
                
                # Save statistics
                stats_df = pd.DataFrame.from_dict(stats, orient='index', columns=['Count'])
                stats_df.to_excel(writer, sheet_name="Statistics")
            
            # Download button
            st.download_button(
                label="📥 Download Full Analysis Report",
                data=output.getvalue(),
                file_name=f"full_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Includes cleaned data, technician performance, and statistics"
            )

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")

# User Guide
with st.expander("ℹ️ System User Guide"):
    st.markdown("""
    ## INTERSOFT Analyzer Pro - User Guide
    
    ### How to Use:
    1. **Upload Files**:
       - For Pending Tickets Analysis: Upload both All Tickets and Completed Tickets files
       - For Comprehensive Analysis: Upload a single data file
       - All files must contain a 'Ticket_Id' column
    
    2. **Automatic Processing**:
       - System will identify and count all duplicate tickets
       - Clean data by keeping only first occurrence of each ticket
       - Generate comprehensive statistics and visualizations
    
    3. **Review Results**:
       - View key metrics in the dashboard
       - Examine duplicate tickets in detail
       - Analyze pending tickets ready for work
       - Explore data visualizations
    
    4. **Export Data**:
       - Download complete reports in Excel format
       - Includes all cleaned data, duplicates, and statistics
    
    ### Key Features:
    - **Advanced Duplicate Detection**: Identifies exact duplicates based on Ticket_Id
    - **Detailed Reporting**: Shows exactly which tickets are duplicated
    - **Visual Analytics**: Interactive charts for data exploration
    - **Data Cleaning**: Automatically removes duplicates while preserving originals
    - **Comprehensive Export**: All results in organized Excel files
    
    ### Technical Notes:
    - System handles large datasets efficiently
    - Preserves all original columns from your files
    - Timestamped reports for version control
    """)

# Footer
st.markdown("""
<div style="text-align:center; margin-top:50px; padding:20px; background:#f0f2f6;">
    <p>INTERSOFT Analyzer Pro - Version 2.0</p>
    <p>© 2023 All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
