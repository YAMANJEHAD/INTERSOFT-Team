import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit.components.v1 as components
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import shutil
from PIL import Image
import zipfile

# إعداد صفحة Streamlit
st.set_page_config(page_title="Note Analyzer", layout="wide")

# ✅ HTML + CSS لعرض الساعة والتاريخ
clock_html = """<div style="background: transparent;">
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
</div>"""
components.html(clock_html, height=130, scrolling=False)

st.markdown("""<h1 style='color:#ffffff; text-align:center;'>📊 INTERSOFT Analyzer</h1>""", unsafe_allow_html=True)

st.info("✅ تمت إضافة تصنيفات جديدة: WRONG RECEIPT و NO RECEIPT")

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])
required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

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
    elif "NO RETAILERS SIGNATURE" in note or ("RETAILER" in note and "SIGNATURE" in note):
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
    elif "NO RECEIPT" in note:
        return "NO RECEIPT"
    elif "WRONG RECEIPT" in note:
        return "WRONG RECEIPT"
    elif "ANOTHER TERMINAL RECEIPT" in note:
        return "ANOTHER TERMINAL RECEIPT"
    elif "UNCLEAR RECEIPT" in note:
        return "UNCLEAR RECEIPT"
    else:
        return "MISSING INFORMATION"

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
    except:
        df = pd.read_excel(uploaded_file)

    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ Missing required columns. Available: {list(df.columns)}")
    else:
        progress_bar = st.progress(0)
        note_types = []
        for i, note in enumerate(df['NOTE']):
            note_types.append(classify_note(note))
            if i % 10 == 0 or i == len(df['NOTE']) - 1:
                progress_bar.progress((i + 1) / len(df['NOTE']))
        df['Note_Type'] = note_types
        progress_bar.empty()

        st.success("✅ File processed successfully!")

        # التحليلات
        st.markdown("### 📈 Notes per Technician")
        tech_counts = df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
        st.bar_chart(tech_counts)

        st.markdown("### 🔝 Top 5 Technicians with Most Notes")
        filtered_df = df[~df['Note_Type'].isin(['DONE', 'NO J.O'])]
        tech_counts_filtered = filtered_df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
        top_5_technicians = tech_counts_filtered.head(5)
        top_5_data = filtered_df[filtered_df['Technician_Name'].isin(top_5_technicians.index.tolist())]
        technician_notes_table = top_5_data[['Technician_Name', 'Note_Type', 'Terminal_Id', 'Ticket_Type']]
        technician_notes_count = top_5_technicians.reset_index()
        technician_notes_count.columns = ['Technician_Name', 'Notes_Count']
        tech_note_group = df.groupby(['Technician_Name', 'Note_Type']).size().reset_index(name='Count')

        st.dataframe(technician_notes_count, use_container_width=True)
        st.markdown("### 🧾 Technician Notes Details")
        st.dataframe(technician_notes_table, use_container_width=True)

        st.markdown("### 📊 Notes by Type")
        note_counts = df['Note_Type'].value_counts()
        st.bar_chart(note_counts)

        st.markdown("### 🥧 Note Types Distribution")
        pie_data = note_counts.reset_index()
        pie_data.columns = ['Note_Type', 'Count']
        fig = px.pie(pie_data, names='Note_Type', values='Count', title='Note Type Distribution')
        fig.update_traces(textinfo='percent+label')
        st.plotly_chart(fig)

        st.markdown("### ✅ Terminal IDs for 'DONE' Notes")
        done_terminals = df[df['Note_Type'] == 'DONE'][['Technician_Name', 'Terminal_Id', 'Ticket_Type']]
        done_terminals_counts = done_terminals['Technician_Name'].value_counts()
        done_terminals_table = done_terminals[done_terminals['Technician_Name'].isin(done_terminals_counts.head(5).index)]
        done_terminals_summary = done_terminals_counts.head(5).reset_index()
        done_terminals_summary.columns = ['Technician_Name', 'DONE_Notes_Count']
        st.dataframe(done_terminals_summary, use_container_width=True)

        st.markdown("### 📑 Detailed Notes for Top 5 Technicians")
        for tech in top_5_technicians.index:
            st.markdown(f"#### Notes for Technician: {tech}")
            technician_data = top_5_data[top_5_data['Technician_Name'] == tech]
            technician_data_filtered = technician_data[~technician_data['Note_Type'].isin(['DONE', 'NO J.O'])]
            st.dataframe(technician_data_filtered[['Technician_Name', 'Note_Type', 'Terminal_Id', 'Ticket_Type']], use_container_width=True)

        # تصدير إلى Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for note_type in df['Note_Type'].unique():
                subset = df[df['Note_Type'] == note_type]
                subset[['Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type']].to_excel(writer, sheet_name=note_type[:31], index=False)
            note_counts.reset_index().rename(columns={'index': 'Note_Type', 'Note_Type': 'Count'}).to_excel(writer, sheet_name="Note Type Count", index=False)
            tech_note_group.to_excel(writer, sheet_name="Technician Notes Count", index=False)
            done_terminals_table.to_excel(writer, sheet_name="DONE_Terminals", index=False)

        st.download_button("📥 Download Summary Excel", output.getvalue(), "summary.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # تصدير PDF
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, height - 50, "Summary Report")
        c.setFont("Helvetica", 12)
        c.drawString(100, height - 100, f"Top 5 Technicians: {', '.join(top_5_technicians.index)}")
        c.showPage()
        c.save()
        st.download_button("📥 Download PDF Report", pdf_buffer.getvalue(), "summary_report.pdf", "application/pdf")

        # إدارة مجلدات الفنيين والصور
        st.markdown("## 📸 إدارة ملفات الفنيين")
        base_dir = "Technician_Files"
        os.makedirs(base_dir, exist_ok=True)

        for tech in df['Technician_Name'].unique():
            tech_folder = os.path.join(base_dir, tech.replace(" ", "_"))
            os.makedirs(tech_folder, exist_ok=True)

            with st.expander(f"📂 ملفات: {tech}"):
                uploaded_images = st.file_uploader(f"📤 أضف صور لـ {tech}", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key=tech)
                if uploaded_images:
                    for img_file in uploaded_images:
                        img_path = os.path.join(tech_folder, img_file.name)
                        with open(img_path, "wb") as f:
                            f.write(img_file.getbuffer())
                    st.success("✅ تم رفع الصور!")

                existing_images = [f for f in os.listdir(tech_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                if existing_images:
                    st.markdown("### 🖼 الصور المرفوعة:")
                    cols = st.columns(4)
                    for idx, img_name in enumerate(existing_images):
                        img_path = os.path.join(tech_folder, img_name)
                        with cols[idx % 4]:
                            st.image(img_path, caption=img_name, use_column_width=True)
                            if st.button(f"🗑 حذف {img_name}", key=f"del_{tech}_{img_name}"):
                                os.remove(img_path)
                                st.warning(f"❌ تم حذف {img_name}")
                                st.experimental_rerun()

                # ضغط المجلد وتحميله
                zip_filename = f"{tech.replace(' ', '_')}_images.zip"
                zip_path = os.path.join(base_dir, zip_filename)
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for root, _, files in os.walk(tech_folder):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, arcname=os.path.relpath(file_path, tech_folder))

                with open(zip_path, "rb") as f:
                    st.download_button("📥 تحميل الصور كمجلد مضغوط", f, file_name=zip_filename, mime="application/zip")
