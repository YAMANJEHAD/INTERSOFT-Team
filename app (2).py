import streamlit as st
import pandas as pd
import io
import plotly.express as px
import streamlit.components.v1 as components
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Page setup
st.set_page_config(page_title="Note Analyzer", layout="wide")

# Clock widget
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

# Classification function
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

# Choose mode
analysis_mode = st.radio("🔍 Select Mode:", ["📊 Single File Analysis", "📁 Compare Multiple Files"])

# Multi-file comparison mode
if analysis_mode == "📁 Compare Multiple Files":
    uploaded_files = st.file_uploader("📁 Upload Excel Files to Compare", type=["xlsx"], accept_multiple_files=True)
    if uploaded_files:
        file_dfs = {}
        for uploaded_file in uploaded_files:
            try:
                df = pd.read_excel(uploaded_file)
                if 'NOTE' in df.columns:
                    df['Note_Type'] = df['NOTE'].apply(classify_note)
                    counts = df['Note_Type'].value_counts().rename(uploaded_file.name)
                    file_dfs[uploaded_file.name] = counts
                else:
                    st.warning(f"⚠️ Skipped file {uploaded_file.name}: missing 'NOTE' column.")
            except Exception as e:
                st.error(f"❌ Error processing file {uploaded_file.name}: {e}")

        if file_dfs:
            compare_df = pd.DataFrame(file_dfs).fillna(0).astype(int)
            st.markdown("### 📋 Comparison of Note Types Across Files")
            st.dataframe(compare_df, use_container_width=True)

            fig_comp = px.bar(compare_df.T, barmode='group', title="Note Type Comparison Across Files")
            st.plotly_chart(fig_comp, use_container_width=True)

            # ✅ Add Excel download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                compare_df.to_excel(writer, sheet_name="Comparison", index=True)
            st.download_button("📥 Download Comparison Excel", output.getvalue(), "comparison_summary.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
