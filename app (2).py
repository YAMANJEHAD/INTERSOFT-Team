import streamlit as st
import pandas as pd
import io
import plotly.express as px
import streamlit.components.v1 as components
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# إعداد الصفحة
st.set_page_config(page_title="Note Analyzer", layout="wide")

# الساعة والتاريخ
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
        "TERMINAL ID - WRONG DATE", "NO IMAGE FOR THE DEVICE", "IMAGE FOR THE DEVICE ONLY",
        "WRONG DATE", "TERMINAL ID", "NO J.O", "DONE", "NO RETAILERS SIGNATURE",
        "UNCLEAR IMAGE", "NO ENGINEER SIGNATURE", "NO SIGNATURE", "PENDING",
        "NO INFORMATIONS", "MISSING INFORMATION", "NO BILL", "NOT ACTIVE", "NO RECEIPT",
        "ANOTHER TERMINAL RECEIPT", "UNCLEAR RECEIPT", "WRONG RECEIPT", "REJECTED RECEIPT"
    ]
    matches = [kw for kw in known_keywords if kw in note]
    if len(matches) == 0:
        return "MISSING INFORMATION"
    elif len(matches) == 1:
        return matches[0]
    else:
        return "MULTIPLE ISSUES"

# ✅ المعالجة الرئيسية بعد رفع الملف
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
    except:
        df = pd.read_excel(uploaded_file)

    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ Missing required columns. Available: {list(df.columns)}")
    else:
        df['Note_Type'] = df['NOTE'].apply(classify_note)
        st.success("✅ File processed successfully!")

        # ✅ النسب وعدد التكرار
        note_counts = df['Note_Type'].value_counts().reset_index()
        note_counts.columns = ["Note_Type", "Count"]

        # ✅ تنبيه MULTIPLE ISSUES دائم
        if 'MULTIPLE ISSUES' in note_counts['Note_Type'].values:
            percent = (note_counts[note_counts['Note_Type'] == 'MULTIPLE ISSUES']['Count'].values[0] / note_counts['Count'].sum()) * 100
            if percent > 5:
                st.warning(f"🔴 MULTIPLE ISSUES are high: {percent:.2f}%")
            else:
                st.info(f"🟢 All good! MULTIPLE ISSUES under control: {percent:.2f}%")

        # ✅ تبويبات العرض
        tab1, tab2, tab3, tab4, tab5, tab6, tab7= st.tabs([
            "📊 Note Type Summary", "👨‍🔧 Notes per Technician", "🚨 Top 5 Technicians",
            "🥧 Note Type Distribution", "✅ DONE Terminals", "📑 Detailed Notes"])

        with tab1:
            st.markdown("### 🔢 Count of Each Note Type")
            st.dataframe(note_counts, use_container_width=True)
            fig_bar = px.bar(note_counts, x="Note_Type", y="Count", title="Note Type Frequency")
            st.plotly_chart(fig_bar, use_container_width=True)

        with tab2:
            st.markdown("### 📈 Notes per Technician")
            tech_counts = df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
            st.bar_chart(tech_counts)

        with tab3:
            st.markdown("### 🚨 Technician With Most Wrong Notes!")
            filtered_df = df[~df['Note_Type'].isin(['DONE', 'NO J.O'])]
            tech_counts_filtered = filtered_df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
            top_5_technicians = tech_counts_filtered.head(5)
            top_5_data = filtered_df[filtered_df['Technician_Name'].isin(top_5_technicians.index.tolist())]
            technician_notes_table = top_5_data[['Technician_Name', 'Note_Type', 'Terminal_Id', 'Ticket_Type']]
            technician_notes_count = top_5_technicians.reset_index()
            technician_notes_count.columns = ['Technician_Name', 'Notes_Count']
            tech_note_group = df.groupby(['Technician_Name', 'Note_Type']).size().reset_index(name='Count')
            st.dataframe(technician_notes_count, use_container_width=True)

        with tab4:
            st.markdown("### 🥧 Note Types Distribution")
            fig = px.pie(note_counts, names='Note_Type', values='Count', title='Note Type Distribution')
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig)

        with tab5:
            st.markdown("### ✅'DONE' Notes")
            done_terminals = df[df['Note_Type'] == 'DONE'][['Technician_Name', 'Terminal_Id', 'Ticket_Type']]
            done_terminals_counts = done_terminals['Technician_Name'].value_counts()
            done_terminals_table = done_terminals[done_terminals['Technician_Name'].isin(done_terminals_counts.head(5).index)]
            done_terminals_summary = done_terminals_counts.head(5).reset_index()
            done_terminals_summary.columns = ['Technician_Name', 'DONE_Notes_Count']
            st.dataframe(done_terminals_summary, use_container_width=True)

        with tab6:
            st.markdown("### 📑 Detailed Notes for Top 5 Technicians")
            for tech in top_5_technicians.index:
                st.markdown(f"#### 🧑 Technician: {tech}")
                technician_data = top_5_data[top_5_data['Technician_Name'] == tech]
                technician_data_filtered = technician_data[~technician_data['Note_Type'].isin(['DONE', 'NO J.O'])]
                st.dataframe(technician_data_filtered[['Technician_Name', 'Note_Type', 'Terminal_Id', 'Ticket_Type']], use_container_width=True)
                tab7 = st.tabs(["🛠️ J.O Improvement Suggestions & Analysis"])[0]
        with tab7:
            st.markdown("---")
            st.markdown("## 🔍 Deep Dive: Analyze Common J.O Problems")

            # أكثر نوع ملاحظة تكراراً
            top_issue = note_counts.iloc[0]
            st.markdown(f"### 🏆 Top Issue Type: **{top_issue['Note_Type']}** with {top_issue['Count']} occurrences")

            # أكثر فني عليه ملاحظات
            tech_note_summary = df[df['Note_Type'] != 'DONE'].groupby('Technician_Name')['Note_Type'].count().reset_index(name="Issue_Count")
            tech_note_summary = tech_note_summary.sort_values(by="Issue_Count", ascending=False)
            top_tech = tech_note_summary.iloc[0]
            st.markdown(f"### 👨‍🔧 Technician with Most Issues: **{top_tech['Technician_Name']}** - {top_tech['Issue_Count']} issues")

            # توزيع الأعطال حسب نوع التذكرة
            st.markdown("### 📊 Note Type Breakdown by Ticket Type")
            type_ticket_group = df.groupby(['Note_Type', 'Ticket_Type']).size().reset_index(name="Count")
            fig_ticket_breakdown = px.bar(type_ticket_group, x="Note_Type", y="Count", color="Ticket_Type", title="Note Type by Ticket Type", barmode="group")
            st.plotly_chart(fig_ticket_breakdown, use_container_width=True)

            # جدول كامل للمشاكل
            st.markdown("### 📋 Full Issue Table (excluding DONE & NO J.O)")
            issue_table = df[~df['Note_Type'].isin(['DONE', 'NO J.O'])][['Technician_Name', 'Note_Type', 'Terminal_Id', 'Ticket_Type']]
            st.dataframe(issue_table, use_container_width=True)

            # نسبة المشاكل إلى جميع الفنيين
            st.markdown("### 📌 Technician Issue Rate (%)")
            total_jobs = df.groupby('Technician_Name')['Note_Type'].count().reset_index(name="Total_Jobs")
            issues_only = df[~df['Note_Type'].isin(['DONE', 'NO J.O'])].groupby('Technician_Name')['Note_Type'].count().reset_index(name="Issues")
            merged = pd.merge(total_jobs, issues_only, on='Technician_Name', how='left').fillna(0)
            merged['Issue_Rate (%)'] = (merged['Issues'] / merged['Total_Jobs']) * 100
            merged = merged.sort_values(by='Issue_Rate (%)', ascending=False)
            st.dataframe(merged[['Technician_Name', 'Total_Jobs', 'Issues', 'Issue_Rate (%)']], use_container_width=True)
        

        # ✅ تصدير البيانات
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for note_type in df['Note_Type'].unique():
                subset = df[df['Note_Type'] == note_type]
                subset[['Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type']].to_excel(writer, sheet_name=note_type[:31], index=False)
            note_counts.to_excel(writer, sheet_name="Note Type Count", index=False)
            tech_note_group.to_excel(writer, sheet_name="Technician Notes Count", index=False)
            done_terminals_table.to_excel(writer, sheet_name="DONE_Terminals", index=False)

        st.download_button("📥 Download Summary Excel", output.getvalue(), "summary.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
