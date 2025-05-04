import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Note Analyzer", layout="wide")

# Animated Clock HTML/CSS
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

st.title("📊 INTERSOFT Note Analyzer")

# Input form for name, date, and file upload
with st.form("upload_form", clear_on_submit=False):
    name = st.text_input("Your Name")
    date = st.date_input("Upload Date", datetime.today())
    uploaded_file = st.file_uploader("📁 Select Excel File", type=["xlsx"])
    submit = st.form_submit_button("🔼 Upload")

# Initialize session log
if 'upload_log' not in st.session_state:
    st.session_state.upload_log = []

# Note classification function
def classify_note(note):
    note = str(note).strip().upper()
    if "TERMINAL ID - WRONG DATE" in note:
        return "TERMINAL ID - WRONG DATE"
    elif "NO IMAGE FOR THE DEVICE" in note:
        return "NO IMAGE FOR THE DEVICE"
    elif "WRONG DATE" in note:
        return "WRONG DATE"
    elif "TERMINAL ID" in note:
        return "TERMINAL ID"
    elif "NO J.O" in note:
        return "NO J.O"
    elif "DONE" in note:
        return "DONE"
    elif "NO RETAILERS SIGNATURE" in note:
        return "NO RETAILERS SIGNATURE"
    elif "UNCLEAR IMAGE" in note:
        return "UNCLEAR IMAGE"
    elif "NO ENGINEER SIGNATURE" in note:
        return "NO ENGINEER SIGNATURE"
    elif "NO SIGNATURE" in note:
        return "NO SIGNATURE"
    elif "PENDING" in note:
        return "PENDING"
    elif "NO INFORMATIONS" in note:
        return "NO INFORMATIONS"
    elif "MISSING INFORMATION" in note:
        return "MISSING INFORMATION"
    else:
        return "MISSING INFORMATION"

required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

# Process upload
if submit and uploaded_file and name:
    try:
        df = pd.read_excel(uploaded_file)
    except:
        st.error("❌ Failed to read the Excel file.")
        df = None

    if df is not None and all(col in df.columns for col in required_cols):
        df['Note_Type'] = df['NOTE'].apply(classify_note)
        df = df[~df['Note_Type'].isin(['DONE', 'NO J.O'])]

        tech_counts = df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
        note_counts = df['Note_Type'].value_counts()
        tech_note_group = df.groupby(['Technician_Name', 'Note_Type']).size().reset_index(name='Count')

        # Create Excel summary
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for note_type in df['Note_Type'].unique():
                subset = df[df['Note_Type'] == note_type]
                subset[['Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type']].to_excel(writer, sheet_name=note_type[:31], index=False)
            note_counts.reset_index().rename(columns={'index': 'Note_Type', 'Note_Type': 'Count'}).to_excel(writer, sheet_name="Note Type Count", index=False)
            tech_note_group.to_excel(writer, sheet_name="Technician Notes Count", index=False)

        excel_bytes = output.getvalue()
        if isinstance(excel_bytes, str):
            excel_bytes = excel_bytes.encode()

        # Save to log
        st.session_state.upload_log.append({
            "Name": name,
            "Date": date.strftime("%Y-%m-%d"),
            "File Name": uploaded_file.name,
            "Uploaded File Content": excel_bytes
        })

        st.success("✅ File uploaded and processed successfully.")

    else:
        st.error("❌ The file does not contain the required columns!")

# Upload history
st.subheader("📂 Upload History")
if st.session_state.upload_log:
    log_df = pd.DataFrame([
        {
            "Name": entry["Name"],
            "Date": entry["Date"],
            "File Name": entry["File Name"]
        }
        for entry in st.session_state.upload_log
    ])
    selected_index = st.selectbox("Select file", options=range(len(log_df)), format_func=lambda i: f'{log_df.iloc[i]["File Name"]} - {log_df.iloc[i]["Name"]} ({log_df.iloc[i]["Date"]})')

    st.dataframe(log_df)

    selected_entry = st.session_state.upload_log[selected_index]

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️ Download selected file",
            data=selected_entry["Uploaded File Content"] if isinstance(selected_entry["Uploaded File Content"], bytes)
            else selected_entry["Uploaded File Content"].encode(),
            file_name=selected_entry["File Name"],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with col2:
        if st.button("🗑️ Delete selected file"):
            st.session_state.upload_log.pop(selected_index)
            st.experimental_rerun()
else:
    st.info("📭 No files uploaded yet.")
