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
import time
from PIL import Image

# ========== Splash Screen ==========
if "splash_shown" not in st.session_state:
    st.session_state.splash_shown = False

if not st.session_state.splash_shown:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;800&display=swap');

    .splash-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100vh;
        background: linear-gradient(135deg, #0f172a, #1e293b);
        animation: fadeIn 1s ease-in-out;
    }

    .splash-logo {
        width: 120px;
        opacity: 0;
        animation: slideDown 1.2s ease-out forwards;
    }

    .splash-title {
        font-size: 2.8rem;
        font-weight: 800;
        margin-top: 1rem;
        color: #4ade80;
        opacity: 0;
        animation: fadeSlideUp 1.2s ease-out 0.6s forwards;
    }

    .splash-sub {
        font-size: 1.1rem;
        color: #e2e8f0;
        margin-top: 0.5rem;
        opacity: 0;
        animation: fadeSlideUp 1s ease-out 1s forwards;
    }

    .loader {
        border: 6px solid #f3f3f3;
        border-top: 6px solid #4ade80;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        margin-top: 30px;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    @keyframes fadeIn {
        0% {opacity: 0;}
        100% {opacity: 1;}
    }

    @keyframes slideDown {
        0% { transform: translateY(-30px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }

    @keyframes fadeSlideUp {
        0% { transform: translateY(20px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown(f"""
        <div class="splash-container">
            <img src="logoChip.png" class="splash-logo" />
            <div class="splash-title">INTERSOFT Analyzer</div>
            <div class="splash-sub">Your Smart Ticket Tracker</div>
            <div class="loader"></div>
        </div>
        """, unsafe_allow_html=True)

    time.sleep(3)
    st.session_state.splash_shown = True
    st.experimental_rerun()

# ========== Continue with your main application logic here ==========
# 🟢 الآن حط باقي تطبيقك Streamlit اللي بيبدأ مثلاً بـ:
# st.set_page_config(...)
# uploaded_file = st.file_uploader(...)
# df = pd.read_excel(...) 
# ... إلخ


# ---------------------- 🧠 APP TITLE ----------------------
st.markdown("<h1>📊 INTERSOFT Analyzer</h1>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])
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
        "NO RETAILERS SIGNATURE": ["NO RETAILERS SIGNATURE", "NO RETAILER SIGNATURE", "NO RETAILERS SIGNATURE", "NO RETAILER'S SIGNATURE"],
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

ARCHIVE_DIR = "uploaded_archive"
os.makedirs(ARCHIVE_DIR, exist_ok=True)

if uploaded_file:
    # Create unique filename with hash and upload timestamp
    uploaded_bytes = uploaded_file.read()
    uploaded_file.seek(0)
    file_hash = hashlib.md5(uploaded_bytes).hexdigest()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_filename = f"{timestamp}_{file_hash}.xlsx"
    archive_path = os.path.join(ARCHIVE_DIR, archive_filename)

    # Save a copy of the file
    with open(archive_path, "wb") as f:
        f.write(uploaded_bytes)

    try:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
    except:
        df = pd.read_excel(uploaded_file)

    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ Missing required columns. Available: {list(df.columns)}")
    else:
        df['Note_Type'] = df['NOTE'].apply(classify_note)
        df['Problem_Severity'] = df['Note_Type'].apply(problem_severity)
        df['Suggested_Solution'] = df['Note_Type'].apply(suggest_solutions)
        st.success("✅ File processed successfully!")

        note_counts = df['Note_Type'].value_counts().reset_index()
        note_counts.columns = ["Note_Type", "Count"]

       
        if 'Note_Type' in df.columns:
            filtered_df_not_done = df[df['Note_Type'] != 'DONE']
            total_notes = len(filtered_df_not_done)
            note_type_counts = filtered_df_not_done['Note_Type'].value_counts()

            if total_notes > 0:
                with st.expander("❗Note Types Overview", expanded=False):
                    for note_type, count in note_type_counts.items():
                        percent = (count / total_notes) * 100
                        color_box = "#f8d7da" if percent > 5 else "#d4edda"
                        color_border = "#f5c6cb" if percent > 5 else "#c3e6cb"
                        color_text = "#721c24" if percent > 5 else "#155724"
                        icon = "🔴" if percent > 5 else "🟢"

                        st.markdown(f"""
                        <div style='background-color:{color_box}; color:{color_text}; padding:8px 15px;
                                    border-left: 6px solid {color_border}; border-radius: 6px;
                                    font-size:14px; margin-bottom:8px'>
                        {icon} <strong>{note_type}</strong>: {percent:.2f}%
                        </div>
                        """, unsafe_allow_html=True)

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

       
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "📊 Note Type Summary", "👨‍🔧 Notes per Technician", "🚨 Top 5 Technicians",
            "🥧 Note Type Distribution", "✅ DONE Terminals", "📑 Detailed Notes", 
            "✍️ Signature Issues", "🔍 Deep Problem Analysis"])

        with tab1:
            st.markdown("### 🔢 Count of Each Note Type")
            st.dataframe(note_counts, use_container_width=True)
            fig_bar = px.bar(note_counts, x="Note_Type", y="Count", title="Note Type Frequency")
            st.plotly_chart(fig_bar, use_container_width=True)

        with tab2:
            st.markdown("### 📈 Notes per Technician")
            tech_counts = df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
            st.bar_chart(tech_counts)

        with tab3:
            st.markdown("### 🚨 Technician With Most Wrong Notes!")
            filtered_df = df[~df['Note_Type'].isin(['DONE', 'NO J.O'])]
            tech_counts_filtered = filtered_df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
            top_5_technicians = tech_counts_filtered.head(5)
            top_5_data = filtered_df[filtered_df['Technician_Name'].isin(top_5_technicians.index.tolist())]
            technician_notes_table = top_5_data[['Technician_Name', 'Note_Type', 'Terminal_Id', 'Ticket_Type']]
            technician_notes_count = top_5_technicians.reset_index()
            technician_notes_count.columns = ['Technician_Name', 'Notes_Count']
            tech_note_group = df.groupby(['Technician_Name', 'Note_Type']).size().reset_index(name='Count')
            st.dataframe(technician_notes_count, use_container_width=True)

        with tab4:
            st.markdown("### 🥧 Note Types Distribution")
            fig = px.pie(note_counts, names='Note_Type', values='Count', title='Note Type Distribution')
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig)

        with tab5:
            st.markdown("### ✅'DONE' Notes")
            done_terminals = df[df['Note_Type'] == 'DONE'][['Technician_Name', 'Terminal_Id', 'Ticket_Type']]
            done_terminals_counts = done_terminals['Technician_Name'].value_counts()
            done_terminals_table = done_terminals[done_terminals['Technician_Name'].isin(done_terminals_counts.head(5).index)]
            done_terminals_summary = done_terminals_counts.head(5).reset_index()
            done_terminals_summary.columns = ['Technician_Name', 'DONE_Notes_Count']
            st.dataframe(done_terminals_summary, use_container_width=True)

        with tab6:
            st.markdown("### 📑 Detailed Notes for Top 5 Technicians")
            for tech in top_5_technicians.index:
                st.markdown(f"#### 🧑 Technician: {tech}")
                technician_data = top_5_data[top_5_data['Technician_Name'] == tech]
                technician_data_filtered = technician_data[~technician_data['Note_Type'].isin(['DONE', 'NO J.O'])]
                st.dataframe(technician_data_filtered[['Technician_Name', 'Note_Type', 'Terminal_Id', 'Ticket_Type']], use_container_width=True)

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

        with tab8:
            st.markdown("## 🔍 Deep Problem Analysis")
            
            # Common problems analysis
            st.markdown("### 📌 Common Problems and Patterns")
            common_problems = df[~df['Note_Type'].isin(['DONE'])]
            
            # Problem frequency
            problem_freq = common_problems['Note_Type'].value_counts().reset_index()
            problem_freq.columns = ["Problem", "Count"]
            
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(problem_freq, use_container_width=True)
            
            with col2:
                fig_problems = px.pie(problem_freq, names='Problem', values='Count', 
                                     title='Problem Distribution')
                st.plotly_chart(fig_problems, use_container_width=True)
            
            # Ticket type vs problem analysis
            st.markdown("### 🎫 Ticket Type vs Problem Type")
            ticket_problem = pd.crosstab(df['Ticket_Type'], df['Note_Type'])
            st.dataframe(ticket_problem.style.background_gradient(cmap='Blues'), 
                        use_container_width=True)
            
            # Suggested solutions
            st.markdown("### 💡 Suggested Solutions for Common Problems")
            solutions_df = df[['Note_Type', 'Suggested_Solution']].drop_duplicates()
            st.dataframe(solutions_df, use_container_width=True)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for note_type in df['Note_Type'].unique():
                subset = df[df['Note_Type'] == note_type]
                subset[['Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type']].to_excel(writer, sheet_name=note_type[:31], index=False)
            note_counts.to_excel(writer, sheet_name="Note Type Count", index=False)
            tech_note_group.to_excel(writer, sheet_name="Technician Notes Count", index=False)
            done_terminals_table.to_excel(writer, sheet_name="DONE_Terminals", index=False)
            solutions_df.to_excel(writer, sheet_name="Suggested Solutions", index=False)

st.download_button("📥 Download Summary Excel", output.getvalue(), "FULL_SUMMARY.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


       
