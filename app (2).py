import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="Note Analyzer", layout="wide")

# HTML للساعة المتحركة
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

st.title("📊 INTERSOFT Analyzer")

# حفظ سجل الملفات المرفوعة
if "upload_log" not in st.session_state:
    st.session_state.upload_log = []

# اسم المستخدم والتاريخ
st.subheader("👤 User Information")
user_name = st.text_input("Enter your name:")
upload_date = st.date_input("Select date:", value=datetime.today())

# رفع الملف
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

# تصنيف الملاحظات
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

if uploaded_file and user_name:
    file_bytes = uploaded_file.read()
    st.session_state["Uploaded File Content"] = file_bytes  # Save for download

    # سجل الرفع
    st.session_state.upload_log.append({
        "Name": user_name,
        "File Name": uploaded_file.name,
        "Date": str(upload_date)
    })

    try:
        excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
        df = pd.read_excel(io.BytesIO(file_bytes), sheet_name="Sheet2") if "Sheet2" in excel_file.sheet_names else pd.read_excel(io.BytesIO(file_bytes))
    except Exception as e:
        st.error(f"❌ Error reading Excel file: {e}")
        st.stop()

    if not all(col in df.columns for col in required_cols):
        st.error(f"Missing required columns. Available: {list(df.columns)}")
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

        # تنزيل Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for note_type in df['Note_Type'].unique():
                subset = df[df['Note_Type'] == note_type]
                subset[['Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type']].to_excel(writer, sheet_name=note_type[:31], index=False)
            note_counts.reset_index().rename(columns={'index': 'Note_Type', 'Note_Type': 'Count'}).to_excel(writer, sheet_name="Note Type Count", index=False)
            tech_note_group.to_excel(writer, sheet_name="Technician Notes Count", index=False)
        st.download_button("📥 Download Summary Excel", output.getvalue(), "summary.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# عرض سجل الملفات المرفوعة
if st.session_state.upload_log:
    st.subheader("📁 Uploaded Files Log")

    log_df = pd.DataFrame(st.session_state.upload_log)

    selected_row = st.selectbox(
        "Select a file to manage it:", 
        options=log_df.index, 
        format_func=lambda x: f"{log_df.loc[x, 'File Name']} (by {log_df.loc[x, 'Name']} on {log_df.loc[x, 'Date']})"
    )

    st.dataframe(log_df)

    if selected_row is not None:
        selected_entry = log_df.loc[selected_row]

        col1, col2 = st.columns(2)

        with col1:
            if "Uploaded File Content" in st.session_state:
                st.download_button(
                    "🔄 Download Selected File",
                    st.session_state["Uploaded File Content"],
                    selected_entry["File Name"],
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("⚠️ File not available in memory for download.")

        with col2:
            if st.button("❌ Delete Selected Entry"):
                st.session_state.upload_log.pop(selected_row)
                st.success("✅ Entry deleted from session history.")
                st.rerun()
