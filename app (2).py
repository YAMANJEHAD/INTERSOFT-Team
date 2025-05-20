import streamlit as st
import pandas as pd
import io
import plotly.express as px
import streamlit.components.v1 as components
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# إعداد الصفحة
st.set_page_config(page_title="Note Analyzer", layout="wide")

# ✅ الساعة والتاريخ
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
.clock-time { font-size: 22px; font-weight: bold; }
.clock-date { font-size: 16px; margin-top: 4px; }
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

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])
required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

# ✅ التصنيف مع دعم MULTIPLE ISSUES
def classify_note(note):
    note = str(note).strip().upper()
    known_keywords = [
        "TERMINAL ID - WRONG DATE",
        "NO IMAGE FOR THE DEVICE",
        "IMAGE FOR THE DEVICE ONLY",
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
        "NO BILL",
        "NOT ACTIVE",
        "NO RECEIPT",
        "ANOTHER TERMINAL RECEIPT",
        "UNCLEAR RECEIPT",
        "WRONG RECEIPT",
        "REJECTED RECEIPT"
    ]
    matches = [kw for kw in known_keywords if kw in note]
    if len(matches) == 0:
        return "MISSING INFORMATION"
    elif len(matches) == 1:
        return matches[0]
    else:
        return "MULTIPLE ISSUES"

# ✅ بعد رفع الملف
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
    except:
        df = pd.read_excel(uploaded_file)

    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ Missing required columns. Available: {list(df.columns)}")
    else:
        df['Note_Type'] = df['NOTE'].apply(classify_note)

        # ✅ فلترة بالتاريخ (إن وُجد)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            st.markdown("### 📅 Filter by Date Range")
            min_date = df['Date'].min().date()
            max_date = df['Date'].max().date()
            start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
            end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)
            df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]

        st.success("✅ File processed successfully!")

        # ✅ النسب وعدد التكرار
        note_counts = df['Note_Type'].value_counts()
        note_percentage = (note_counts / note_counts.sum()) * 100
        note_percentage_df = pd.DataFrame({
            "Note_Type": note_counts.index,
            "Count": note_counts.values,
            "Percentage (%)": note_percentage.round(2).values
        })

        # ✅ تنبيه MULTIPLE ISSUES
        if 'MULTIPLE ISSUES' in note_percentage_df['Note_Type'].values:
            percent = note_percentage_df[note_percentage_df['Note_Type'] == 'MULTIPLE ISSUES']['Percentage (%)'].values[0]
            if percent > 10:
                st.error(f"🚨 High rate of MULTIPLE ISSUES: {percent:.2f}%")
            else:
                st.success(f"✅ All good! MULTIPLE ISSUES are under control: {percent:.2f}%")

        # ✅ متوسط عدد الملاحظات لكل فني
        avg_notes = df.groupby("Technician_Name")["Note_Type"].count().mean()
        st.markdown(f"### 📊 Average Notes per Technician: **{avg_notes:.2f}**")

        # ✅ Tabs
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📊 Note Type Summary",
            "👨‍🔧 Notes per Technician",
            "🏆 Top 5 Technicians",
            "🥧 Note Distribution",
            "✅ DONE Terminals",
            "📑 Detailed Notes",
            "📅 Notes Timeline"
        ])

        with tab1:
            st.dataframe(note_percentage_df, use_container_width=True)

        with tab2:
            tech_counts = df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
            st.bar_chart(tech_counts)

        with tab3:
            filtered_df = df[~df['Note_Type'].isin(['DONE', 'NO J.O'])]
            top_5_techs = filtered_df['Technician_Name'].value_counts().head(5)
            top_5_data = filtered_df[filtered_df['Technician_Name'].isin(top_5_techs.index)]
            st.dataframe(top_5_data[['Technician_Name', 'Note_Type', 'Terminal_Id', 'Ticket_Type']], use_container_width=True)

        with tab4:
            pie_data = note_counts.reset_index()
            pie_data.columns = ['Note_Type', 'Count']
            fig = px.pie(pie_data, names='Note_Type', values='Count', title='Note Type Distribution')
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig)

        with tab5:
            done_df = df[df['Note_Type'] == 'DONE']
            done_summary = done_df['Technician_Name'].value_counts().reset_index()
            done_summary.columns = ['Technician_Name', 'DONE Count']
            st.dataframe(done_summary, use_container_width=True)

        with tab6:
            for tech in df['Technician_Name'].unique():
                st.markdown(f"#### 🧑 Technician: {tech}")
                tech_data = df[df['Technician_Name'] == tech]
                st.dataframe(tech_data[['Technician_Name', 'Note_Type', 'Terminal_Id', 'Ticket_Type']], use_container_width=True)

        with tab7:
            if 'Date' in df.columns:
                timeline = df.groupby(['Date', 'Note_Type']).size().reset_index(name='Count')
                fig_time = px.line(timeline, x='Date', y='Count', color='Note_Type', title='Timeline of Notes by Type')
                st.plotly_chart(fig_time, use_container_width=True)

        # ✅ تصدير البيانات
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for note_type in df['Note_Type'].unique():
                subset = df[df['Note_Type'] == note_type]
                subset[['Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type']].to_excel(writer, sheet_name=note_type[:31], index=False)
            note_percentage_df.to_excel(writer, sheet_name="Note Type Summary", index=False)
        st.download_button("📥 Download Summary Excel", output.getvalue(), "summary.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 800, "Summary Report")
        c.setFont("Helvetica", 12)
        c.drawString(100, 770, f"Average Notes per Technician: {avg_notes:.2f}")
        c.showPage()
        c.save()
        st.download_button("📥 Download PDF Report", pdf_buffer.getvalue(), "summary_report.pdf", "application/pdf")
