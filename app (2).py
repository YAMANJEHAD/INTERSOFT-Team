import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
from datetime import datetime

# Page config
st.set_page_config(page_title="Note Analyzer", layout="wide")

# Clock and animation styles
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

# App title
st.title("📊 INTERSOFT Analyzer")

# Upload file
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

# Default known cases
default_known_cases = [
    "TERMINAL ID - WRONG DATE",
    "NO IMAGE FOR THE DEVICE",
    "WRONG DATE",
    "TERMINAL ID",
    "NO J.O",
    "DONE",
    "NO RETAILERS SIGNATURE",
    "UNCLEAR IMAGE",
    "NO ENGINEER SIGNATURE",
    "NO SIGNATURE",
    "PENDING",
    "NO INFORMATIONS",
    "MISSING INFORMATION",
    "NOT ACTIVE"
]

# Show editable table
st.subheader("✏️ Edit Known Cases Before Analysis")
known_cases_df = pd.DataFrame(default_known_cases, columns=["Known_Cases"])
edited_cases_df = st.data_editor(known_cases_df, num_rows="dynamic", use_container_width=True)
known_cases = edited_cases_df["Known_Cases"].dropna().str.upper().tolist()

# Note classification function
def classify_note(note):
    note = str(note).strip().upper()
    for case in known_cases:
        if case in note:
            return case
    return "OTHERS"

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name=None)
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")

    if isinstance(df, dict):
        sheet_names = list(df.keys())
        st.write(f"Sheets found: {sheet_names}")
        df = df[sheet_names[0]]

    df.columns = [col.upper() for col in df.columns]

    note_columns = [col for col in df.columns if 'NOTE' in col]

    if not note_columns:
        st.error("No 'NOTE' columns found in the file.")
    else:
        note_column = note_columns[0]
        df['Note_Type'] = df[note_column].apply(classify_note)

        st.success("✅ File processed successfully!")

        st.subheader("📈 Notes per Technician")
        if 'TECHNICIAN_NAME' in df.columns:
            tech_counts = df.groupby('TECHNICIAN_NAME')['Note_Type'].count().sort_values(ascending=False)
            st.bar_chart(tech_counts)

        st.subheader("📊 Notes by Type")
        note_counts = df['Note_Type'].value_counts()
        st.bar_chart(note_counts)

        st.subheader("📋 Data Table")
        display_cols = ['TECHNICIAN_NAME', 'Note_Type'] if 'TECHNICIAN_NAME' in df.columns else ['Note_Type']
        st.dataframe(df[display_cols])

        st.subheader("📑 Notes per Technician by Type")
        if 'TECHNICIAN_NAME' in df.columns:
            tech_note_group = df.groupby(['TECHNICIAN_NAME', 'Note_Type']).size().reset_index(name='Count')
            st.dataframe(tech_note_group)

        # Prepare Excel output
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for note_type in df['Note_Type'].unique():
                subset = df[df['Note_Type'] == note_type]
                subset[display_cols].to_excel(writer, sheet_name=note_type[:31], index=False)
            note_counts.reset_index().rename(columns={'index': 'Note_Type', 'Note_Type': 'Count'}).to_excel(writer, sheet_name="Note Type Count", index=False)
            if 'TECHNICIAN_NAME' in df.columns:
                tech_note_group.to_excel(writer, sheet_name="Technician Notes Count", index=False)

        st.download_button("📥 Download Summary Excel", output.getvalue(), "summary.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
