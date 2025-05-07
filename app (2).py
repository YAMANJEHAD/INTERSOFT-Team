import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit.components.v1 as components
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# إعداد صفحة Streamlit
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

# عنوان الصفحة
st.title("📊 INTERSOFT Analyzer")

# رفع ملف Excel
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

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
    elif "NOT ACTIVE" in note:
        return "NOT ACTIVE"
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

        # حذف بعض الأنواع غير المرغوبة
        df = df[~df['Note_Type'].isin(['DONE', 'NO J.O'])]

        st.success("✅ File processed successfully!")

        # 📈 عدد الملاحظات حسب الفني
        st.subheader("📈 Notes per Technician")
        tech_counts = df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
        st.bar_chart(tech_counts)

        # 🔝 أعلى 5 فنيين
        st.subheader("🔝 Top 5 Technicians with Most Notes")
        top_5 = tech_counts.head(5).reset_index()
        st.dataframe(top_5.rename(columns={'Technician_Name': 'Technician', 'Note_Type': 'Note Count'}))

        # 📊 عدد كل نوع من الملاحظات
        st.subheader("📊 Notes by Type")
        note_counts = df['Note_Type'].value_counts()
        st.bar_chart(note_counts)

        # 🥧 رسم دائري لتوزيع الأنواع
        st.subheader("🥧 Note Types Distribution (Pie Chart)")
        pie_data = note_counts.reset_index()
        pie_data.columns = ['Note_Type', 'Count']
        fig = px.pie(pie_data, names='Note_Type', values='Count', title='Note Type Distribution')
        st.plotly_chart(fig)

        # 📋 جدول البيانات
        st.subheader("📋 Data Table")
        st.dataframe(df[['Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type']])

        # 📑 جدول ملاحظات لكل فني حسب النوع
        st.subheader("📑 Notes per Technician by Type")
        tech_note_group = df.groupby(['Technician_Name', 'Note_Type']).size().reset_index(name='Count')
        st.dataframe(tech_note_group)

        # 📥 تصدير إلى Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for note_type in df['Note_Type'].unique():
                subset = df[df['Note_Type'] == note_type]
                subset[['Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type']].to_excel(writer, sheet_name=note_type[:31], index=False)
            note_counts.reset_index().rename(columns={'index': 'Note_Type', 'Note_Type': 'Count'}).to_excel(writer, sheet_name="Note Type Count", index=False)
            tech_note_group.to_excel(writer, sheet_name="Technician Notes Count", index=False)

        st.download_button("📥 Download Summary Excel", output.getvalue(), "summary.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # 📄 تصدير تقرير PDF
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "INERSOFT Notes Summary Report")

        c.setFont("Helvetica", 12)
        c.drawString(50, height - 100, f"Total Notes: {len(df)}")
        c.drawString(50, height - 120, f"Unique Technicians: {df['Technician_Name'].nunique()}")

        c.drawString(50, height - 160, "Top 5 Note Types:")
        for i, (note, count) in enumerate(note_counts.head(5).items()):
            c.drawString(70, height - 180 - i * 20, f"{note}: {count}")

        c.drawString(50, height - 300, "Top 5 Technicians:")
        for i, (tech, count) in enumerate(top_5.values):
            c.drawString(70, height - 320 - i * 20, f"{tech}: {count}")

        c.showPage()
        c.save()
        pdf_buffer.seek(0)

        st.download_button("📄 Download PDF Report", pdf_buffer.getvalue(), file_name="report.pdf", mime="application/pdf")
