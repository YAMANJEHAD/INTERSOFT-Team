import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
from datetime import datetime

st.set_page_config(page_title="Note Analyzer", layout="wide")

clock_html = """
<style>
.clock-container {
    font-family: 'Courier New', monospace;
    font-size: 24px;
    color: #ffffff;
    background: linear-gradient(90deg, #f39c12, #e67e22);
    padding: 10px 20px;
    border-radius: 12px;
    width: fit-content;
    animation: pulse 2s infinite;
    margin-bottom: 20px;
    position: absolute;
    top: 10px;
    right: 10px;
    z-index: 9999;
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(243, 156, 18, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(243, 156, 18, 0); }
    100% { box-shadow: 0 0 0 0 rgba(243, 156, 18, 0); }
}
@keyframes slideIn {
    0% { transform: translateX(100%); opacity: 0; }
    100% { transform: translateX(0); opacity: 1; }
}
.page-container {
    animation: slideIn 1s ease-out;
    overflow: hidden;
}
</style>
<div class="clock-container">
    <span id="clock"></span>
</div>
<script>
function updateClock() {
    const now = new Date();
    document.getElementById('clock').innerText = now.toLocaleTimeString();
}
setInterval(updateClock, 1000);
updateClock();
</script>
"""

components.html(clock_html, height=100)

st.title("📊 INTERSOFT Analyzer")

name = st.text_input("🧑‍💻 Enter Your Name:")
date = st.date_input("📅 Select Date:", datetime.today())

uploaded_file = st.file_uploader("📤 Upload Excel File", type=["xlsx"])

required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

def classify_note(note):
    note = str(note).strip().upper()
    cases = {
        "TERMINAL ID - WRONG DATE": "TERMINAL ID - WRONG DATE",
        "NO IMAGE FOR THE DEVICE": "NO IMAGE FOR THE DEVICE",
        "WRONG DATE": "WRONG DATE",
        "TERMINAL ID": "TERMINAL ID",
        "NO J.O": "NO J.O",
        "DONE": "DONE",
        "NO RETAILERS SIGNATURE": "NO RETAILERS SIGNATURE",
        "UNCLEAR IMAGE": "UNCLEAR IMAGE",
        "NO ENGINEER SIGNATURE": "NO ENGINEER SIGNATURE",
        "NO SIGNATURE": "NO SIGNATURE",
        "PENDING": "PENDING",
        "NO INFORMATIONS": "NO INFORMATIONS",
        "MISSING INFORMATION": "MISSING INFORMATION"
    }
    for key in cases:
        if key in note:
            return cases[key]
    return "MISSING INFORMATION"

if "upload_log" not in st.session_state:
    st.session_state.upload_log = []

if uploaded_file and name and date:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
    except:
        df = pd.read_excel(uploaded_file)

    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ Missing required columns. Found columns: {list(df.columns)}")
    else:
        df['Note_Type'] = df['NOTE'].apply(classify_note)
        df = df[~df['Note_Type'].isin(['DONE', 'NO J.O'])]

        st.success("✅ File processed successfully!")

        st.subheader("📈 Notes per Technician")
        tech_counts = df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
        st.bar_chart(tech_counts)

        st.subheader("📊 Notes by Type")
        note_counts = df['Note_Type'].value_counts()
        st.bar_chart(note_counts)

        st.subheader("📋 Data Table")
        st.dataframe(df[['Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type']])

        st.subheader("📑 Notes per Technician by Type")
        tech_note_group = df.groupby(['Technician_Name', 'Note_Type']).size().reset_index(name='Count')
        st.dataframe(tech_note_group)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for note_type in df['Note_Type'].unique():
                subset = df[df['Note_Type'] == note_type]
                subset[['Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type']].to_excel(writer, sheet_name=note_type[:31], index=False)
            note_counts.reset_index().rename(columns={'index': 'Note_Type', 'Note_Type': 'Count'}).to_excel(writer, sheet_name="Note Type Count", index=False)
            tech_note_group.to_excel(writer, sheet_name="Technician Notes Count", index=False)
        st.download_button("📥 Download Summary Excel", output.getvalue(), "summary.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        st.session_state.upload_log.append({
            "Name": name,
            "Date": date.strftime("%Y-%m-%d"),
            "File Name": uploaded_file.name,
            "Uploaded File Content": output.getvalue()
        })

if st.session_state.upload_log:
    st.subheader("📁 Uploaded Files Log")
    log_df = pd.DataFrame(st.session_state.upload_log)

    log_df['entry_id'] = log_df.apply(lambda row: f"{row['File Name']}_{row['Name']}_{row['Date']}", axis=1)
    unique_ids = log_df['entry_id'].tolist()

    selected_id = st.selectbox(
        "📌 Select a file to download/delete:",
        options=unique_ids,
        format_func=lambda x: f"{x.split('_')[0]} (by {x.split('_')[1]} on {x.split('_')[2]})"
    )

    st.dataframe(log_df.drop(columns='entry_id'))

    selected_entry = log_df[log_df['entry_id'] == selected_id].iloc[0]

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️ Download Selected File",
            selected_entry["Uploaded File Content"],
            selected_entry["File Name"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with col2:
        if st.button("🗑️ Delete Selected Entry"):
            st.session_state.upload_log = [
                entry for entry in st.session_state.upload_log
                if f"{entry['File Name']}_{entry['Name']}_{entry['Date']}" != selected_id
            ]
            st.success("✅ Entry deleted successfully.")
            st.rerun()
