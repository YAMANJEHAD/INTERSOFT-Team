import streamlit as st
import pandas as pd
import io
import plotly.express as px
import streamlit.components.v1 as components
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Note Analyzer", layout="wide")

# الشريط الجانبي
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

    st.markdown(f"**📅 Logged in at:** `{st.session_state.login_time}`")

    if st.session_state.login_time:
        now = datetime.now()
        start_time = datetime.strptime(st.session_state.login_time, "%Y-%m-%d %H:%M:%S")
        duration = now - start_time
        st.markdown(f"⏱️ **Time spent:** `{str(duration).split('.')[0]}`")

    if st.session_state.uploaded_files_log:
        st.markdown("**📂 Uploaded Files:**")
        for log in st.session_state.uploaded_files_log:
            st.markdown(f"- `{log}`")
    else:
        st.info("No files uploaded yet.")

    st.markdown("---")
    st.markdown("### 🔗 Navigation")
    st.markdown("[🔝 Top Technicians](#top-5-technicians-with-most-notes)", unsafe_allow_html=True)
    st.markdown("[📊 Notes by Type](#notes-by-type)", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.info("Upload Excel file (Sheet2). Required columns: NOTE, Terminal_Id, Technician_Name, Ticket_Type.")

    if st.button("🔓 Logout"):
        st.session_state.clear()
        st.experimental_rerun()

# الساعة
clock_html = """<div style="background: transparent;">
<style>.clock-container {
    font-family: 'Courier New', monospace; font-size: 22px; color: #fff;
    background: linear-gradient(135deg, #1abc9c, #16a085); padding: 12px 25px;
    border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    animation: pulse 2s infinite; position: fixed; top: 15px; right: 25px;
    z-index: 9999; display: flex; flex-direction: column; align-items: flex-end;}
.clock-time { font-size: 22px; font-weight: bold; }
.clock-date { font-size: 16px; margin-top: 4px; }
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(26, 188, 156, 0.4); }
    70% { box-shadow: 0 0 0 15px rgba(26, 188, 156, 0); }
    100% { box-shadow: 0 0 0 0 rgba(26, 188, 156, 0); }
}</style>
<div class="clock-container">
    <div class="clock-time" id="clock"></div>
    <div class="clock-date" id="date"></div></div>
<script>
function updateClock() {
    const now = new Date();
    document.getElementById('clock').innerText = now.toLocaleTimeString();
    document.getElementById('date').innerText = now.toLocaleDateString(undefined, {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'});
}
setInterval(updateClock, 1000); updateClock();
</script></div>"""
components.html(clock_html, height=130, scrolling=False)

# رفع الملف وتحليله
st.title("📊 INTERSOFT Analyzer")
uploaded_file = st.file_uploader("📤 Upload Excel File", type=["xlsx"])
required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

def classify_note(note):
    note = str(note).strip().upper()
    keywords = {
        "TERMINAL ID - WRONG DATE", "NO IMAGE FOR THE DEVICE", "IMAGE FOR THE DEVICE ONLY",
        "WRONG DATE", "TERMINAL ID", "NO J.O", "DONE", "NO RETAILERS SIGNATURE", 
        "UNCLEAR IMAGE", "NO ENGINEER SIGNATURE", "NO SIGNATURE", "PENDING", 
        "NO INFORMATIONS", "MISSING INFORMATION", "NO BILL", "NOT ACTIVE", 
        "NO RECEIPT", "ANOTHER TERMINAL RECEIPT", "UNCLEAR RECEIPT"
    }
    for k in keywords:
        if k in note:
            return k
    return "MISSING INFORMATION"

if uploaded_file:
    st.session_state.uploaded_files_log.append(uploaded_file.name)

    try:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
    except:
        df = pd.read_excel(uploaded_file)

    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ Missing required columns. Found: {list(df.columns)}")
        st.stop()

    df['Note_Type'] = df['NOTE'].apply(classify_note)

    # ملخص سريع
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        st.markdown(f"- Total Rows: **{len(df)}**")
        st.markdown(f"- Unique Technicians: **{df['Technician_Name'].nunique()}**")
        st.markdown(f"- Note Types: **{df['Note_Type'].nunique()}**")
        selected_tech = st.selectbox("🎯 Track Technician", df['Technician_Name'].unique())
        tech_data = df[df['Technician_Name'] == selected_tech]
        st.markdown(f"- Notes: **{len(tech_data)}**")
        st.markdown(f"- Unique Terminals: **{tech_data['Terminal_Id'].nunique()}**")

    # تحليل كامل
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

    st.subheader("✅ Terminal IDs for 'DONE' Notes")
    done_df = df[df['Note_Type'] == 'DONE']
    st.dataframe(done_df[['Technician_Name', 'Terminal_Id', 'Ticket_Type']])

    st.subheader("📑 Detailed Notes for Top 5 Technicians")
    for tech in top_5.index:
        st.markdown(f"### 🧑‍🔧 {tech}")
        st.dataframe(filtered_df[filtered_df['Technician_Name'] == tech][['Terminal_Id', 'Note_Type', 'Ticket_Type']])

    # تصدير Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="All Notes")
        df['Note_Type'].value_counts().reset_index().to_excel(writer, index=False, sheet_name="Note Type Count")
    st.download_button("📥 Download Excel Summary", output.getvalue(), "note_summary.xlsx")

    # تصدير PDF
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 50, "INTERSOFT - Summary Report")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 80
         c.setFont("Helvetica", 12)
    c.drawString(100, height - 80, f"Top 5 Technicians:")
    y = height - 100
    for tech in top_5.index:
        c.drawString(120, y, f"{tech}: {top_5[tech]} Notes")
        y -= 20

    c.drawString(100, y - 20, "Note Types Count:")
    y -= 40
    note_counts = df['Note_Type'].value_counts()
    for note_type, count in note_counts.items():
        c.drawString(120, y, f"{note_type}: {count}")
        y -= 20
        if y < 100:
            c.showPage()
            y = height - 100
            c.setFont("Helvetica", 12)

    c.drawImage("https://raw.githubusercontent.com/username/repository/branch/logoChip.png", 100, height - 170, width=50, height=50)  # الشعار في التقرير
    c.save()

    st.download_button("📥 Download PDF Report", pdf_buffer.getvalue(), "summary_report.pdf", "application/pdf")
            
