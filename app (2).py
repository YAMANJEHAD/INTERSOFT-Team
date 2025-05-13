import streamlit as st
import pandas as pd
import os
import io
import base64
import plotly.express as px
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="Note Analyzer", layout="wide")

UPLOAD_DIR = "uploaded_files"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Sidebar
with st.sidebar:
    st.header("🧑‍💼 User Info")
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "login_time" not in st.session_state:
        st.session_state.login_time = None
    if "uploaded_files_log" not in st.session_state:
        st.session_state.uploaded_files_log = []

    username = st.text_input("👤 Enter your name", value=st.session_state.username)
    if username and not st.session_state.login_time:
        st.session_state.username = username
        st.session_state.login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not st.session_state.username:
        st.warning("⚠️ Please enter your name to use the application.")
        st.stop()

    st.markdown(f"*📅 Logged in at:* {st.session_state.login_time}")
    now = datetime.now()
    start_time = datetime.strptime(st.session_state.login_time, "%Y-%m-%d %H:%M:%S")
    duration = now - start_time
    st.markdown(f"⏱️ *Time spent:* {str(duration).split('.')[0]}")

    # ملف مرفوع
    if st.session_state.uploaded_files_log:
        st.markdown("### 📂 Uploaded Files")
        for file_path in st.session_state.uploaded_files_log:
            file_name = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">📄 {file_name}</a>'
                st.markdown(href, unsafe_allow_html=True)
    else:
        st.info("No files uploaded yet.")

    # الثيم
    theme = st.selectbox("🎨 Select Theme", ["Light", "Dark"])
    if theme == "Dark":
        st.markdown("""<style>body { background-color: #111; color: #eee; }</style>""", unsafe_allow_html=True)

    # تنقل وروابط
    st.markdown("---")
    st.markdown("### 🔗 Navigation")
    st.markdown("[🔝 Top Technicians](#top-5-technicians-with-most-notes)", unsafe_allow_html=True)
    st.markdown("[📊 Notes by Type](#notes-by-type)", unsafe_allow_html=True)

    # تسجيل خروج
    if st.button("🔓 Logout"):
        st.session_state.clear()
        st.experimental_rerun()

# مرفقات وتحميل
st.title("📊 INTERSOFT Analyzer")
uploaded_file = st.file_uploader("📤 Upload Excel File", type=["xlsx"])
required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type', 'Closed_Date']

def classify_note(note):
    note = str(note).strip().upper()
    keywords = {"TERMINAL ID - WRONG DATE", "NO IMAGE FOR THE DEVICE", "IMAGE FOR THE DEVICE ONLY", "WRONG DATE", "TERMINAL ID", "NO J.O", "DONE", "NO RETAILERS SIGNATURE", "UNCLEAR IMAGE", "NO ENGINEER SIGNATURE", "NO SIGNATURE", "PENDING", "NO INFORMATIONS", "MISSING INFORMATION", "NO BILL", "NOT ACTIVE", "NO RECEIPT", "ANOTHER TERMINAL RECEIPT", "UNCLEAR RECEIPT"}
    for k in keywords:
        if k in note:
            return k
    return "MISSING INFORMATION"

if uploaded_file:
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.session_state.uploaded_files_log.append(file_path)

    try:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
    except:
        df = pd.read_excel(uploaded_file)

    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ Missing required columns. Found: {list(df.columns)}")
        st.stop()

    df['Note_Type'] = df['NOTE'].apply(classify_note)

    # فلترة بالتاريخ
    st.subheader("📆 Filter by Date")
    df['Closed_Date'] = pd.to_datetime(df['Closed_Date'], errors='coerce')
    start = st.date_input("From", df['Closed_Date'].min().date())
    end = st.date_input("To", df['Closed_Date'].max().date())
    df = df[(df['Closed_Date'].dt.date >= start) & (df['Closed_Date'].dt.date <= end)]

    # إحصائيات سريعة
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Quick Stats")
    st.sidebar.markdown(f"- Total Rows: *{len(df)}*")
    st.sidebar.markdown(f"- Unique Technicians: *{df['Technician_Name'].nunique()}*")
    st.sidebar.markdown(f"- Note Types: *{df['Note_Type'].nunique()}*")
    selected_tech = st.sidebar.selectbox("🎯 Track Technician", df['Technician_Name'].unique())
    tech_data = df[df['Technician_Name'] == selected_tech]
    st.sidebar.markdown(f"- Notes: *{len(tech_data)}*")

    # تحذيرات ذكية
    if df[df['Note_Type'] == 'PENDING'].shape[0] > 0:
        st.warning(f"⚠️ There are {df[df['Note_Type'] == 'PENDING'].shape[0]} PENDING notes.")

    st.success("✅ File processed successfully!")

    st.subheader("📈 Notes per Technician")
    st.bar_chart(df['Technician_Name'].value_counts())

    st.subheader("🔝 Top 5 Technicians with Most Notes")
    filtered_df = df[~df['Note_Type'].isin(['DONE', 'NO J.O'])]
    top_5 = filtered_df['Technician_Name'].value_counts().head(5)
    st.dataframe(top_5.reset_index().rename(columns={'index': 'Technician_Name', 'Technician_Name': 'Notes_Count'}))

    st.subheader("📊 Notes by Type")
    st.bar_chart(df['Note_Type'].value_counts())

    st.subheader("🥧 Note Types Distribution (Pie Chart)")
    pie_data = df['Note_Type'].value_counts().reset_index()
    pie_data.columns = ['Note_Type', 'Count']
    fig = px.pie(pie_data, names='Note_Type', values='Count', title='Note Type Distribution')
    st.plotly_chart(fig)

    st.subheader("📑 Detailed Notes for Top 5 Technicians")
    for tech in top_5.index:
        st.markdown(f"### 🧑‍🔧 {tech}")
        st.dataframe(filtered_df[filtered_df['Technician_Name'] == tech][['Terminal_Id', 'Note_Type', 'Ticket_Type']])

    # تصدير Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="All Notes")
    st.download_button("📥 Download Excel Summary", output.getvalue(), "note_summary.xlsx")

    # تصدير PDF
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 50, "INTERSOFT - Summary Report")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 80, "Top 5 Technicians:")
    y = height - 100
    for tech in top_5.index:
        c.drawString(120, y, f"{tech}: {top_5[tech]} Notes")
        y -= 20
    c.save()
    st.download_button("📥 Download PDF Report", pdf_buffer.getvalue(), "summary_report.pdf", "application/pdf")

    # ملاحظات المستخدم
    st.subheader("✍️ Add Your Notes or Suggestions")
    feedback = st.text_area("Leave a note for developer:")
    if feedback:
        with open("feedback_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - {st.session_state.username}: {feedback}\n")
        st.success("Thanks! Your feedback was saved.")
