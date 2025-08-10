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
st.set_page_config(page_title="INTERSOFT Analyzer", layout="wide")

# Clock HTML for display
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
.clock-time { font-size: 22px; font-weight: bold; }
.clock-date { font-size: 16px; margin-top: 4px; }
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

# Title
st.markdown("<h1 style='color:#ffffff; text-align:center;'>📊 INTERSOFT Analyzer</h1>", unsafe_allow_html=True)

# Define tabs
tab_upload, tab_duplicate_analysis, tab_by_analysis, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📁 Upload File", "🔄 Duplicate Analysis", "👤 BY Column Analysis", "📊 Note Type Summary", 
    "👨‍🔧 Notes per Technician", "🚨 Top 5 Technicians", "🥧 Note Type Distribution", 
    "✅ DONE Terminals", "📑 Detailed Notes", "✍️ Signature Issues", "🔍 Deep Problem Analysis", 
    "🚪 Visit & Cancelled Analysis"
])

# Required columns
required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type', 'BY']

# Data normalization and classification functions
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
        "NO RETAILERS SIGNATURE": ["NO RETAILERS SIGNATURE", "NO RETAILER SIGNATURE", "NO RETAILERS SIGNATURE", "NO RETAILER'S SIGNATURE"],
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
    if len(matched_labels) == 0:
        return "MISSING INFORMATION"
    elif len(matched_labels) == 1:
        return matched_labels[0]
    else:
        return "MULTIPLE ISSUES"

def classify_visit_cancelled(note):
    note = normalize(note)
    visit_patterns = [
        "NEED TO VISIT", "NEEDS TO VISIT", "NEED TO VIST", "NEEDTOVISIT", "NEED TO VISSIT",
        "NEED VISIT", "NEEDTO VISIT", "NEED TOVISIT"
    ]
    cancel_patterns = [
        "CANCELLED", "CANCELED", "CANCEL", "CANCELL", "CANCLED", "CANCELE"
    ]
    if any(pattern in note for pattern in visit_patterns):
        return "NEED TO VISIT"
    elif any(pattern in note for pattern in cancel_patterns):
        return "CANCELLED"
    return None

def problem_severity(note_type):
    critical = ["WRONG DATE", "TERMINAL ID - WRONG DATE", "REJECTED RECEIPT"]
    high = ["NO IMAGE", "UNCLEAR IMAGE", "NO RECEIPT"]
    medium = ["NO SIGNATURE", "NO ENGINEER SIGNATURE"]
    low = ["NO J.O", "PENDING"]
    if note_type in critical: return "Critical"
    elif note_type in high: return "High"
    elif note_type in medium: return "Medium"
    elif note_type in low: return "Low"
    else: return "Unclassified"

def suggest_solutions(note_type):
    solutions = {
        "NEED TO VISIT": "Schedule a visit to the terminal location.",
        "CANCELLED": "Review cancellation reason and reschedule if necessary.",
        "WRONG DATE": "Verify device timestamp and sync with server.",
        "TERMINAL ID - WRONG DATE": "Recheck terminal ID entry and date configuration.",
        "NO IMAGE FOR THE DEVICE": "Capture and upload image of the device.",
        "NO RETAILERS SIGNATURE": "Ensure the retailer signs the form.",
        "NO ENGINEER SIGNATURE": "Engineer must provide a signature before submission.",
        "NO SIGNATURE": "Capture necessary signatures from all parties.",
        "UNCLEAR IMAGE": "Retake photo with better clarity and lighting.",
        "NOT ACTIVE": "Check activation process and retry.",
        "NO BILL": "Attach a valid billing document.",
        "NO RECEIPT": "Upload a clear image of the transaction receipt.",
        "ANOTHER TERMINAL RECEIPT": "Ensure the correct terminal's receipt is uploaded.",
        "WRONG RECEIPT": "Verify and re-upload the correct receipt.",
        "REJECTED RECEIPT": "Follow up on why receipt was rejected and correct it.",
        "MULTIPLE ISSUES": "Resolve all mentioned issues and update note accordingly.",
        "NO J.O": "Provide the Job Order number or details.",
        "PENDING": "Complete and finalize the pending task.",
        "MISSING INFORMATION": "Review note and provide complete details.",
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

def text_analysis(notes):
    all_words = ' '.join(notes.dropna().astype(str)).upper().split()
    word_counts = Counter(all_words)
    return pd.DataFrame(word_counts.most_common(20), columns=['Word', 'Count'])

def analyze_by_column(df):
    if 'BY' not in df.columns:
        return pd.DataFrame(columns=['BY', 'Count'])
    by_counts = df['BY'].value_counts().reset_index()
    by_counts.columns = ['BY', 'Count']
    return by_counts

def analyze_visit_cancelled(df):
    vc_counts = df['Visit_Cancelled'].value_counts().reset_index()
    vc_counts.columns = ['Status', 'Count']
    vc_counts = vc_counts[vc_counts['Status'].notnull()]
    return vc_counts

def analyze_duplicates(df):
    duplicate_cols = ['Ticket_Id', 'Terminal_Id']
    duplicate_data = {'Ticket_Id': pd.DataFrame(), 'Terminal_Id': pd.DataFrame()}
    summary = {'Ticket_Id': 0, 'Terminal_Id': 0}
    
    for col in duplicate_cols:
        if col in df.columns:
            duplicates = df[df[col].duplicated(keep=False)]
            if not duplicates.empty:
                duplicate_data[col] = duplicates[['Ticket_Id', 'Terminal_Id', 'Technician_Name', 'Main_Area', 'Address', 'Note_Type', 'BY'] if 'Address' in df.columns else ['Ticket_Id', 'Terminal_Id', 'Technician_Name', 'Main_Area', 'Note_Type', 'BY']]
                summary[col] = len(duplicates[col].unique())
    
    return duplicate_data, summary

# File upload tab
with tab_upload:
    st.markdown("### 📁 Upload Excel File")
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"], key="uploader")
    
    if uploaded_file:
        uploaded_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        file_hash = hashlib.md5(uploaded_bytes).hexdigest()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archive_filename = f"{timestamp}_{file_hash}.xlsx"
        archive_path = os.path.join("uploaded_archive", archive_filename)
        os.makedirs("uploaded_archive", exist_ok=True)
        
        with open(archive_path, "wb") as f:
            f.write(uploaded_bytes)
        
        try:
            df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
        except:
            df = pd.read_excel(uploaded_file)
        
        if not all(col in df.columns for col in required_cols):
            st.error(f"❌ Missing required columns. Available: {list(df.columns)}")
        else:
            # Apply classifications and normalize BY column
            df['Note_Type'] = df['NOTE'].apply(classify_note)
            df['Problem_Severity'] = df['Note_Type'].apply(problem_severity)
            df['Suggested_Solution'] = df['Note_Type'].apply(suggest_solutions)
            df['Visit_Cancelled'] = df['NOTE'].apply(classify_visit_cancelled)
            if 'BY' in df.columns:
                df['BY'] = df['BY'].apply(normalize)
            # Validate Technician_Name and BY columns
            if df['Technician_Name'].isna().all():
                st.warning("⚠️ 'Technician_Name' column contains no valid data.")
            if df['BY'].isna().all():
                st.warning("⚠️ 'BY' column contains no valid data.")
            st.session_state['df'] = df
            st.success("✅ File uploaded and processed successfully! Switch to other tabs to view analysis.")

# Process data if available
if 'df' in st.session_state:
    df = st.session_state['df']
    note_counts = df['Note_Type'].value_counts().reset_index()
    note_counts.columns = ["Note_Type", "Count"]
    
    # Alerts
    alerts = generate_alerts(df)
    if alerts:
        with st.expander("🚨 Alerts", expanded=False):
            for alert in alerts:
                st.markdown(f"""
                <div style='background-color:#fff3cd; color:#856404; padding:8px 15px;
                            border-left: 6px solid #ffeeba; border-radius: 6px;
                            font-size:14px; margin-bottom:8px'>
                {alert}
                </div>
                """, unsafe_allow_html=True)

    # Duplicate Analysis Tab
    with tab_duplicate_analysis:
        st.markdown("## 🔄 Duplicate Analysis")
        duplicate_data, summary = analyze_duplicates(df)
        
        st.markdown("### 📊 Duplicate Summary")
        summary_df = pd.DataFrame({
            'Column': ['Ticket_Id', 'Terminal_Id'],
            'Duplicate Count': [summary['Ticket_Id'], summary['Terminal_Id']]
        })
        st.dataframe(summary_df, use_container_width=True)
        fig_summary = px.bar(summary_df, x='Column', y='Duplicate Count', title='Number of Duplicates by Column', color='Column')
        st.plotly_chart(fig_summary, use_container_width=True)
        
        if not duplicate_data['Ticket_Id'].empty:
            st.markdown("### 🔢 Duplicate Ticket_Id Entries")
            st.dataframe(duplicate_data['Ticket_Id'], use_container_width=True)
        
        if not duplicate_data['Terminal_Id'].empty:
            st.markdown("### 🔢 Duplicate Terminal_Id Entries")
            st.dataframe(duplicate_data['Terminal_Id'], use_container_width=True)
        
        if not (duplicate_data['Ticket_Id'].empty and duplicate_data['Terminal_Id'].empty):
            output_duplicates = io.BytesIO()
            with pd.ExcelWriter(output_duplicates, engine='xlsxwriter') as writer:
                if not duplicate_data['Ticket_Id'].empty:
                    duplicate_data['Ticket_Id'].to_excel(writer, sheet_name="Duplicate_Ticket_Id", index=False)
                if not duplicate_data['Terminal_Id'].empty:
                    duplicate_data['Terminal_Id'].to_excel(writer, sheet_name="Duplicate_Terminal_Id", index=False)
            st.download_button("📥 Download Duplicate Report", output_duplicates.getvalue(), "duplicate_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.success("✅ No duplicates found for Ticket_Id or Terminal_Id!")

    # BY Column Analysis Tab
    with tab_by_analysis:
        st.markdown("## 👤 Detailed BY Column Analysis")
        if 'BY' not in df.columns:
            st.warning("⚠️ No 'BY' column found in the uploaded file.")
        else:
            by_analysis = analyze_by_column(df)
            st.markdown("### 📊 Total Tickets per BY")
            st.dataframe(by_analysis, use_container_width=True)
            fig_by = px.bar(by_analysis, x='BY', y='Count', title='Ticket Count per BY', color='BY')
            st.plotly_chart(fig_by, use_container_width=True)

            # Detailed analysis for each unique BY value
            by_values = df['BY'].unique()
            for by_value in by_values:
                if pd.notna(by_value):
                    st.markdown(f"### 🧑 Analysis for BY: {by_value}")
                    by_df = df[df['BY'] == by_value]
                    
                    # Summary metrics
                    total_tickets = len(by_df)
                    active_tickets = len(by_df[by_df['Visit_Cancelled'] == 'NEED TO VISIT'])
                    cancelled_tickets = len(by_df[by_df['Visit_Cancelled'] == 'CANCELLED'])
                    
                    # Safely handle top technician
                    tech_counts = by_df['Technician_Name'].value_counts()
                    top_tech = tech_counts.index[0] if not tech_counts.empty else "N/A"
                    top_tech_count = tech_counts.iloc[0] if not tech_counts.empty else 0
                    
                    # Safely handle top area
                    top_area = "N/A"
                    top_area_count = 0
                    if 'Main_Area' in by_df.columns and not by_df['Main_Area'].empty:
                        area_counts = by_df['Main_Area'].value_counts()
                        top_area = area_counts.index[0] if not area_counts.empty else "N/A"
                        top_area_count = area_counts.iloc[0] if not area_counts.empty else 0
                    
                    st.markdown(f"""
                    - **Total Tickets**: {total_tickets}
                    - **Active Tickets (NEED TO VISIT)**: {active_tickets}
                    - **Cancelled Tickets**: {cancelled_tickets}
                    - **Top Technician**: {top_tech} ({top_tech_count} tickets)
                    - **Top Area**: {top_area} ({top_area_count} tickets)
                    """)
                    
                    # Visualizations
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Status distribution
                        vc_counts = by_df['Visit_Cancelled'].value_counts().reset_index()
                        vc_counts.columns = ['Status', 'Count']
                        vc_counts = vc_counts[vc_counts['Status'].notnull()]
                        if not vc_counts.empty:
                            fig_status = px.bar(vc_counts, x='Status', y='Count', title=f'Visit Status for {by_value}', color='Status')
                            st.plotly_chart(fig_status, use_container_width=True)
                    
                    with col2:
                        # Top 5 technicians
                        tech_counts = by_df['Technician_Name'].value_counts().head(5).reset_index()
                        tech_counts.columns = ['Technician_Name', 'Count']
                        if not tech_counts.empty:
                            fig_tech = px.bar(tech_counts, x='Technician_Name', y='Count', title=f'Top 5 Technicians for {by_value}', color='Technician_Name')
                            st.plotly_chart(fig_tech, use_container_width=True)
                    
                    # Top 5 areas (if Main_Area exists)
                    if 'Main_Area' in by_df.columns:
                        area_counts = by_df['Main_Area'].value_counts().head(5).reset_index()
                        area_counts.columns = ['Main_Area', 'Count']
                        other_count = by_df['Main_Area'].value_counts()[5:].sum()
                        if other_count > 0:
                            area_counts = pd.concat([area_counts, pd.DataFrame([{'Main_Area': 'Others', 'Count': other_count}])], ignore_index=True)
                        if not area_counts.empty:
                            fig_area = px.pie(area_counts, names='Main_Area', values='Count', title=f'Top 5 Areas for {by_value}')
                            st.plotly_chart(fig_area, use_container_width=True)
                    
                    # Detailed table
                    st.markdown(f"#### 📑 Detailed Tickets for {by_value}")
                    st.dataframe(by_df[['Ticket_Id', 'Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type', 'Main_Area', 'Address', 'Suggested_Solution']] if 'Address' in by_df.columns else by_df[['Ticket_Id', 'Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type', 'Main_Area', 'Suggested_Solution']], use_container_width=True)

    # Note Type Summary Tab
    with tab1:
        st.markdown("### 🔢 Count of Each Note Type")
        st.dataframe(note_counts, use_container_width=True)
        fig_bar = px.bar(note_counts, x="Note_Type", y="Count", title="Note Type Frequency")
        st.plotly_chart(fig_bar, use_container_width=True)

    # Notes per Technician Tab
    with tab2:
        st.markdown("### 📈 Notes per Technician")
        tech_counts = df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
        st.bar_chart(tech_counts)

    # Top 5 Technicians Tab
    with tab3:
        st.markdown("### 🚨 Technician With Most Wrong Notes!")
        filtered_df = df[~df['Note_Type'].isin(['DONE', 'NO J.O'])]
        tech_counts_filtered = filtered_df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
        top_5_technicians = tech_counts_filtered.head(5)
        top_5_data = filtered_df[filtered_df['Technician_Name'].isin(top_5_technicians.index.tolist())]
        technician_notes_table = top_5_data[['Technician_Name', 'Note_Type', 'Ticket_Id', 'Terminal_Id', 'Ticket_Type']]
        technician_notes_count = top_5_technicians.reset_index()
        technician_notes_count.columns = ['Technician_Name', 'Notes_Count']
        tech_note_group = df.groupby(['Technician_Name', 'Note_Type']).size().reset_index(name='Count')
        st.dataframe(technician_notes_count, use_container_width=True)

    # Note Type Distribution Tab
    with tab4:
        st.markdown("### 🥧 Note Types Distribution")
        fig = px.pie(note_counts, names='Note_Type', values='Count', title='Note Type Distribution')
        fig.update_traces(textinfo='percent+label')
        st.plotly_chart(fig)

    # DONE Terminals Tab
    with tab5:
        st.markdown("### ✅'DONE' Notes")
        done_terminals = df[df['Note_Type'] == 'DONE'][['Technician_Name', 'Ticket_Id', 'Terminal_Id', 'Ticket_Type']]
        done_terminals_counts = done_terminals['Technician_Name'].value_counts()
        done_terminals_table = done_terminals[done_terminals['Technician_Name'].isin(done_terminals_counts.head(5).index)]
        done_terminals_summary = done_terminals_counts.head(5).reset_index()
        done_terminals_summary.columns = ['Technician_Name', 'DONE_Notes_Count']
        st.dataframe(done_terminals_summary, use_container_width=True)

    # Detailed Notes Tab
    with tab6:
        st.markdown("### 📑 Detailed Notes for Top 5 Technicians")
        for tech in top_5_technicians.index:
            st.markdown(f"#### 🧑 Technician: {tech}")
            technician_data = top_5_data[top_5_data['Technician_Name'] == tech]
            technician_data_filtered = technician_data[~technician_data['Note_Type'].isin(['DONE', 'NO J.O'])]
            st.dataframe(technician_data_filtered[['Technician_Name', 'Note_Type', 'Ticket_Id', 'Terminal_Id', 'Ticket_Type']], use_container_width=True)

    # Signature Issues Tab
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
            fig_sig_bar = px.bar(sig_merged, x='Technician_Name', y='Signature_Issues', color='Signature_Issue_Rate (%)', title='Signature Issues per Technician')
            st.plotly_chart(fig_sig_bar, use_container_width=True)

            st.markdown("### 📈 Line Chart")
            fig_sig_line = px.line(sig_merged, x='Technician_Name', y='Signature_Issue_Rate (%)', markers=True, title='Signature Issue Rate')
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
            st.download_button("📥 Download Signature Issues Report", sig_output.getvalue(), "signature_issues.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Deep Problem Analysis Tab
    with tab8:
        st.markdown("## 🔍 Deep Problem Analysis")
        st.markdown("### 📌 Common Problems and Patterns")
        common_problems = df[~df['Note_Type'].isin(['DONE'])]
        problem_freq = common_problems['Note_Type'].value_counts().reset_index()
        problem_freq.columns = ["Problem", "Count"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(problem_freq, use_container_width=True)
        
        with col2:
            fig_problems = px.pie(problem_freq, names='Problem', values='Count', 
                                 title='Problem Distribution')
            st.plotly_chart(fig_problems, use_container_width=True)
        
        st.markdown("### 🎫 Ticket Type vs Problem Type")
        ticket_problem = pd.crosstab(df['Ticket_Type'], df['Note_Type'])
        st.dataframe(ticket_problem.style.background_gradient(cmap='Blues'), 
                    use_container_width=True)
        
        st.markdown("### 💡 Suggested Solutions for Common Problems")
        solutions_df = df[['Note_Type', 'Suggested_Solution']].drop_duplicates()
        st.dataframe(solutions_df, use_container_width=True)

    # Visit & Cancelled Analysis Tab
    with tab9:
        st.markdown("## 🚪 Visit & Cancelled Analysis")
        vc_analysis = analyze_visit_cancelled(df)
        if vc_analysis.empty:
            st.warning("⚠️ No 'NEED TO VISIT' or 'CANCELLED' entries found in the NOTE column.")
        else:
            st.markdown("### 📊 Visit & Cancelled Counts")
            st.dataframe(vc_analysis, use_container_width=True)
            fig_vc = px.bar(vc_analysis, x='Status', y='Count', title='NEED TO VISIT & CANCELLED Counts')
            st.plotly_chart(fig_vc, use_container_width=True)

        st.markdown("### 👤 BY Column Analysis")
        by_analysis = analyze_by_column(df)
        if by_analysis.empty:
            st.warning("⚠️ No 'BY' column found in the uploaded file.")
        else:
            st.dataframe(by_analysis, use_container_width=True)
            fig_by = px.bar(by_analysis, x='BY', y='Count', title='Activity Count per Technician (BY Column)')
            st.plotly_chart(fig_by, use_container_width=True)

    # Download summary Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for note_type in df['Note_Type'].unique():
            subset = df[df['Note_Type'] == note_type]
            subset[['Ticket_Id', 'Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type', 'BY']].to_excel(writer, sheet_name=note_type[:31], index=False)
        note_counts.to_excel(writer, sheet_name="Note Type Count", index=False)
        tech_note_group.to_excel(writer, sheet_name="Technician Notes Count", index=False)
        done_terminals_table.to_excel(writer, sheet_name="DONE_Terminals", index=False)
        solutions_df.to_excel(writer, sheet_name="Suggested Solutions", index=False)
        vc_analysis.to_excel(writer, sheet_name="Visit_Cancelled_Analysis", index=False)
        by_analysis.to_excel(writer, sheet_name="BY_Column_Analysis", index=False)
        if not duplicate_data['Ticket_Id'].empty:
            duplicate_data['Ticket_Id'].to_excel(writer, sheet_name="Duplicate_Ticket_Id", index=False)
        if not duplicate_data['Terminal_Id'].empty:
            duplicate_data['Terminal_Id'].to_excel(writer, sheet_name="Duplicate_Terminal_Id", index=False)
    st.download_button("📥 Download Summary Excel", output.getvalue(), "FULL_SUMMARY.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
