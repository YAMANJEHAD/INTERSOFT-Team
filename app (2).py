
import streamlit as st
import pandas as pd
import io
import re
import base64
import plotly.express as px
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import streamlit.components.v1 as components

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

# تدريب نموذج ML للتصنيف
training_data = pd.DataFrame({
    'NOTE': [
        "terminal id - wrong date", "no image for the device", "image for the device only", "wrong date",
        "terminal id", "no j.o", "done", "no retailers signature", "unclear image",
        "no engineer signature", "no signature", "pending", "no informations", "missing information",
        "no bill", "not active", "no receipt", "another terminal receipt", "unclear receipt"
    ],
    'Label': [
        "TERMINAL ID - WRONG DATE", "NO IMAGE FOR THE DEVICE", "IMAGE FOR THE DEVICE ONLY", "WRONG DATE",
        "TERMINAL ID", "NO J.O", "DONE", "NO RETAILERS SIGNATURE", "UNCLEAR IMAGE",
        "NO ENGINEER SIGNATURE", "NO SIGNATURE", "PENDING", "NO INFORMATIONS", "MISSING INFORMATION",
        "NO BILL", "NOT ACTIVE", "NO RECEIPT", "ANOTHER TERMINAL RECEIPT", "UNCLEAR RECEIPT"
    ]
})
model_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', LogisticRegression())
])
model_pipeline.fit(training_data['NOTE'], training_data['Label'])

def classify_note_ml(NOTE):
    return model_pipeline.predict([NOTE])[0]

# عند رفع الملف
st.title("📊 INTERSOFT Analyzer")
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']
    if not all(col in df.columns for col in required_cols):
        st.error("Missing columns in uploaded file.")
    else:
        # وقت التصنيف
        import time
        start = time.time()
        df['Note_Type'] = df['NOTE'].astype(str).apply(classify_note_ml)
        duration = time.time() - start
        st.success(f"✅ Classification done in {duration:.2f} seconds.")

        # رفع صور اختيارية
        st.subheader("📷 Upload Image (Optional)")
        df['Image_Link'] = ""
        for i in range(min(3, len(df))):
            img = st.file_uploader(f"Image for Note {i+1}", type=["png", "jpg"], key=f"img_{i}")
            if img:
                df.at[i, 'Image_Link'] = f"data:image/png;base64,{base64.b64encode(img.read()).decode()}"

        # فلاتر حسب نوع التذكرة والملاحظة
        st.subheader("🔍 Filters")
        tickets = st.multiselect("Filter by Ticket Type", df['Ticket_Type'].unique())
        notes = st.multiselect("Filter by Note Type", df['Note_Type'].unique())
        if tickets:
            df = df[df['Ticket_Type'].isin(tickets)]
        if notes:
            df = df[df['Note_Type'].isin(notes)]

        # عرض جدول ومخطط
        st.subheader("📊 Notes Count")
        note_counts = df['Note_Type'].value_counts()
        st.bar_chart(note_counts)

        st.subheader("📋 Data Table")
        st.dataframe(df)

        # تصدير Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 Download Excel", data=output.getvalue(), file_name="note_analysis.xlsx")

        # تصدير PDF
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        c.drawString(100, 800, "INTERSOFT - Note Summary Report")
        c.drawString(100, 780, f"Total Notes: {len(df)}")
        c.drawString(100, 760, f"Top Note Types:")
        top_notes = note_counts.head(5).to_dict()
        y = 740
        for k, v in top_notes.items():
            c.drawString(120, y, f"{k}: {v}")
            y -= 20
        c.showPage()
        c.save()
        st.download_button("📥 Download PDF", data=pdf_buffer.getvalue(), file_name="note_summary.pdf")
