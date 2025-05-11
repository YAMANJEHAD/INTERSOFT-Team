import os
import zipfile
import pandas as pd
import streamlit as st
import io
from datetime import datetime
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# إعداد الصفحة
st.set_page_config(page_title="Note Analyzer", layout="wide")

# ✅ HTML + CSS لعرض الساعة والتاريخ
clock_html = """
<div style="background: transparent;">
<style>
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
.clock-time {
    font-size: 22px;
    font-weight: bold;
}
.clock-date {
    font-size: 16px;
    margin-top: 4px;
}
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
</div>
"""
components.html(clock_html, height=130, scrolling=False)

# رفع ملف Excel
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

# الأعمدة المطلوبة
required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

# دالة تصنيف الملاحظات
def classify_note(note):
    note = str(note).strip().upper()
    if "TERMINAL ID - WRONG DATE" in note:
        return "TERMINAL ID - WRONG DATE"
    elif "NO IMAGE FOR THE DEVICE" in note:
        return "NO IMAGE FOR THE DEVICE"
    elif "IMAGE FOR THE DEVICE ONLY" in note:
        return "IMAGE FOR THE DEVICE ONLY"
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
    elif "NO BILL" in note:
        return "NO BILL"
    else:
        return "MISSING INFORMATION"

# عند رفع الملف
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
    except:
        df = pd.read_excel(uploaded_file)

    if not all(col in df.columns for col in required_cols):
        st.error(f"Missing required columns. Available: {list(df.columns)}")
    else:
        # ✅ شريط التقدم أثناء التصنيف
        from time import sleep
        progress_bar = st.progress(0)
        note_types = []

        for i, note in enumerate(df['NOTE']):
            note_types.append(classify_note(note))
            if i % 10 == 0 or i == len(df['NOTE']) - 1:
                progress_bar.progress((i + 1) / len(df['NOTE']))
        df['Note_Type'] = note_types
        progress_bar.empty()

        st.success("✅ File processed successfully!")

        # 🔥 اختيار نوع التذكرة
        selected_ticket_types = st.multiselect("Select Ticket Types", df['Ticket_Type'].unique())
        
        # فلترة البيانات حسب نوع التذكرة المحدد
        filtered_df = df[df['Ticket_Type'].isin(selected_ticket_types)] if selected_ticket_types else df

        # 🔥 اختيار نوع الملاحظات
        selected_note_types = st.multiselect("Select Note Types", df['Note_Type'].unique())
        
        # فلترة البيانات حسب نوع الملاحظات المحددة
        filtered_df = filtered_df[filtered_df['Note_Type'].isin(selected_note_types)] if selected_note_types else filtered_df

        # إنشاء ملفات لكل فني
        technician_groups = filtered_df.groupby('Technician_Name')

        # تنزيل التحليل الكامل
        st.subheader("📥 Download Complete Analysis")

        # إنشاء مجلدات لكل فني
        download_button = st.button("Download Technician Files as ZIP")

        if download_button:
            zip_filename = "technician_notes.zip"
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for technician_name, technician_data in technician_groups:
                    # إنشاء مجلد لكل فني داخل الـ ZIP
                    technician_folder = f"{technician_name.replace(' ', '_')}"
                    zip_file.writestr(f"{technician_folder}/info.txt", f"Technician: {technician_name}\nNotes Count: {technician_data.shape[0]}")

                    # إنشاء ملف Excel لكل فني
                    technician_data_to_excel = io.BytesIO()
                    with pd.ExcelWriter(technician_data_to_excel, engine='xlsxwriter') as writer:
                        technician_data.to_excel(writer, index=False)
                    technician_data_to_excel.seek(0)
                    zip_file.writestr(f"{technician_folder}/{technician_name.replace(' ', '_')}_notes.xlsx", technician_data_to_excel.read())

            # إرسال ملف ZIP للمستخدم
            zip_buffer.seek(0)
            st.download_button("Download Technician Files ZIP", zip_buffer, zip_filename, "application/zip")

        # تصدير التحليل الكامل إلى Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, sheet_name="Filtered Notes", index=False)

        st.download_button("📥 Download Filtered Analysis Excel", output.getvalue(), "filtered_analysis.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
