import streamlit as st
import pandas as pd
import io
import os
import zipfile
from PIL import Image
import plotly.express as px
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import streamlit.components.v1 as components

# Set up Streamlit page
st.set_page_config(page_title="Technician Note Analyzer", layout="wide")

# HTML Clock Widget
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

st.markdown("""<h1 style='color:#ffffff; text-align:center;'>📊 Technician Note Analyzer</h1>""", unsafe_allow_html=True)

# Sidebar navigation for easy access
st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Select a page", ["Dashboard", "Manage Images"])

# Upload section
uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])
required_columns = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

# Classification function
def classify_note(note):
    note = str(note).strip().upper()
    keywords = {
        "TERMINAL ID - WRONG DATE": "TERMINAL ID - WRONG DATE",
        "NO IMAGE FOR THE DEVICE": "NO IMAGE FOR THE DEVICE",
        "IMAGE FOR THE DEVICE ONLY": "IMAGE FOR THE DEVICE ONLY",
        "WRONG DATE": "WRONG DATE",
        "TERMINAL ID": "TERMINAL ID",
        "NO J.O": "NO J.O",
        "DONE": "DONE",
        "NO RETAILERS SIGNATURE": "NO RETAILERS SIGNATURE",
        "RETAILER": "NO RETAILERS SIGNATURE",
        "SIGNATURE": "NO RETAILERS SIGNATURE",
        "UNCLEAR IMAGE": "UNCLEAR IMAGE",
        "NO ENGINEER SIGNATURE": "NO ENGINEER SIGNATURE",
        "NO SIGNATURE": "NO SIGNATURE",
        "PENDING": "PENDING",
        "NO INFORMATIONS": "NO INFORMATIONS",
        "MISSING INFORMATION": "MISSING INFORMATION",
        "NO BILL": "NO BILL",
        "NOT ACTIVE": "NOT ACTIVE",
        "NO RECEIPT": "NO RECEIPT",
        "WRONG RECEIPT": "WRONG RECEIPT",
        "ANOTHER TERMINAL RECEIPT": "ANOTHER TERMINAL RECEIPT",
        "UNCLEAR RECEIPT": "UNCLEAR RECEIPT",
    }
    for key in keywords:
        if key in note:
            return keywords[key]
    return "MISSING INFORMATION"

# Main process for the Dashboard
if page == "Dashboard":
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
        except:
            df = pd.read_excel(uploaded_file)

        if not all(col in df.columns for col in required_columns):
            st.error(f"Missing required columns. Found columns: {list(df.columns)}")
        else:
            df['Note_Type'] = df['NOTE'].apply(classify_note)

            # Visualizations
            st.subheader("📊 Notes Count by Technician")
            st.bar_chart(df['Technician_Name'].value_counts())

            st.subheader("🧾 Top 5 Technicians with Most Notes (Excluding DONE/NO J.O)")
            filtered_df = df[~df['Note_Type'].isin(['DONE', 'NO J.O'])]
            top_techs = filtered_df['Technician_Name'].value_counts().head(5)
            top_tech_df = filtered_df[filtered_df['Technician_Name'].isin(top_techs.index)]
            st.dataframe(top_tech_df[['Technician_Name', 'Note_Type', 'Terminal_Id', 'Ticket_Type']])

            st.subheader("🥧 Note Type Distribution")
            note_counts = df['Note_Type'].value_counts().reset_index()
            note_counts.columns = ['Note_Type', 'Count']
            fig = px.pie(note_counts, names='Note_Type', values='Count', title='Distribution of Notes by Type')
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig)

            # Export Excel
            excel_output = io.BytesIO()
            with pd.ExcelWriter(excel_output, engine='xlsxwriter') as writer:
                for note_type in df['Note_Type'].unique():
                    df[df['Note_Type'] == note_type][['Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type']].to_excel(writer, sheet_name=note_type[:31], index=False)
                note_counts.to_excel(writer, sheet_name="Note Summary", index=False)
            st.download_button("📥 Download Summary Excel", data=excel_output.getvalue(), file_name="summary.xlsx")

            # Export PDF
            pdf_output = io.BytesIO()
            c = canvas.Canvas(pdf_output, pagesize=A4)
            width, height = A4
            c.setFont("Helvetica-Bold", 14)
            c.drawString(100, height - 50, "Summary Report")
            c.setFont("Helvetica", 12)
            c.drawString(100, height - 100, f"Top Technicians: {', '.join(top_techs.index)}")
            c.showPage()
            c.save()
            st.download_button("📥 Download PDF Report", data=pdf_output.getvalue(), file_name="summary.pdf")

# Manage Images page
if page == "Manage Images":
    st.subheader("🗂 Manage Technician Images")
    base_folder = "technician_files"
    os.makedirs(base_folder, exist_ok=True)

    all_technicians = df['Technician_Name'].dropna().unique()
    for tech in all_technicians:
        folder_name = os.path.join(base_folder, tech.replace(" ", "_"))
        os.makedirs(folder_name, exist_ok=True)

        with st.expander(f"📁 Technician: {tech}"):
            # Image Upload Section for each Technician
            images = st.file_uploader(f"Upload images for {tech}", accept_multiple_files=True, type=["png", "jpg", "jpeg"], key=tech)
            if images:
                for img in images:
                    img_path = os.path.join(folder_name, img.name)
                    with open(img_path, "wb") as f:
                        f.write(img.getbuffer())
                st.success("Images uploaded successfully!")

            # Displaying existing images
            existing = [f for f in os.listdir(folder_name) if f.endswith(('.png', '.jpg', '.jpeg'))]
            if existing:
                cols = st.columns(4)
                for idx, img_name in enumerate(existing):
                    img_path = os.path.join(folder_name, img_name)
                    with cols[idx % 4]:
                        st.image(img_path, caption=img_name, use_column_width=True)
                        if st.button(f"Delete {img_name}", key=f"del_{tech}_{img_name}"):
                            os.remove(img_path)
                            st.warning(f"{img_name} deleted.")
                            st.experimental_rerun()

    # Global ZIP for all technician folders
    st.subheader("📦 Download All Technicians' Images in a ZIP")
    all_zip_path = "All_Technician_Images.zip"
    with zipfile.ZipFile(all_zip_path, 'w') as zipf:
        for tech in all_technicians:
            tech_folder = os.path.join(base_folder, tech.replace(" ", "_"))
            for img in os.listdir(tech_folder):
                img_path = os.path.join(tech_folder, img)
                arcname = os.path.join(tech.replace(" ", "_"), img)
                zipf.write(img_path, arcname=arcname)
    with open(all_zip_path, "rb") as f:
        st.download_button("📥 Download All Technicians ZIP", data=f, file_name=all_zip_path, mime="application/zip")
