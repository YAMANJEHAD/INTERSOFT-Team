import streamlit as st
import pandas as pd
import io
import os
import zipfile
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit.components.v1 as components
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# إعداد صفحة Streamlit
st.set_page_config(page_title="Note Analyzer", layout="wide")

# قائمة المستخدمين: يمكن إضافة المزيد من الحسابات أو ربطها بقاعدة بيانات
users = {"admin": "admin123", "employee": "employee123"}  # مدير - موظف
user_logged_in = False

# صفحة تسجيل الدخول
def login_page():
    global user_logged_in
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if username in users and users[username] == password:
            user_logged_in = True
            st.session_state.username = username
            st.success("✅ Successfully logged in!")
        else:
            st.error("❌ Invalid username or password.")

if "username" not in st.session_state:
    login_page()

# إذا كان المستخدم قد سجل دخوله، نعرض الصفحات
if user_logged_in:
    if st.session_state.username == "admin":
        # صفحة المدير
        admin_page()
    else:
        # صفحة الموظف
        employee_page()

# صفحة المدير
def admin_page():
    st.sidebar.header("Admin Dashboard")
    st.markdown("""<h1 style='color:#ffffff; text-align:center;'>📊 Admin Dashboard</h1>""", unsafe_allow_html=True)

    # تحميل ملف Excel
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

            # 📊 Analysis Section
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

            # 🧾 Technician Notes
            st.dataframe(technician_notes_count, use_container_width=True)
            st.markdown("### 🧾 Technician Notes Details")
            st.dataframe(technician_notes_table, use_container_width=True)

            # 📊 Distribution of Notes
            st.markdown("### 📊 Notes by Type")
            note_counts = df['Note_Type'].value_counts()
            st.bar_chart(note_counts)

            # 🥧 Pie Chart Distribution
            st.markdown("### 🥧 Note Types Distribution")
            pie_data = note_counts.reset_index()
            pie_data.columns = ['Note_Type', 'Count']
            fig = px.pie(pie_data, names='Note_Type', values='Count', title='Note Type Distribution')
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig)

            # 📑 Detailed Notes for Top 5 Technicians
            st.markdown("### 📑 Detailed Notes for Top 5 Technicians")
            for tech in top_5_technicians.index:
                st.markdown(f"#### Notes for Technician: {tech}")
                technician_data = top_5_data[top_5_data['Technician_Name'] == tech]
                technician_data_filtered = technician_data[~technician_data['Note_Type'].isin(['DONE', 'NO J.O'])]
                st.dataframe(technician_data_filtered[['Technician_Name', 'Note_Type', 'Terminal_Id', 'Ticket_Type']], use_container_width=True)

            # Export Excel File
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for note_type in df['Note_Type'].unique():
                    subset = df[df['Note_Type'] == note_type]
                    subset[['Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type']].to_excel(writer, sheet_name=note_type[:31], index=False)
                note_counts.reset_index().rename(columns={'index': 'Note_Type', 'Note_Type': 'Count'}).to_excel(writer, sheet_name="Note Type Count", index=False)
            st.download_button("📥 Download Summary Excel", output.getvalue(), "summary.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            # Export PDF File
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

# صفحة الموظف
def employee_page():
    st.sidebar.header("Employee Dashboard")
    st.markdown("""<h1 style='color:#ffffff; text-align:center;'>📊 Employee Dashboard</h1>""", unsafe_allow_html=True)

    # رفع الصور الخاصة بالفني
    technician_name = st.text_input("Enter Your Technician Name:")
    uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    
    if technician_name and uploaded_images:
        image_folder = os.path.join("images", technician_name)
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        
        for uploaded_image in uploaded_images:
            image_path = os.path.join(image_folder, uploaded_image.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_image.getbuffer())
        
        st.success("✅ Images uploaded successfully!")
    
    # عرض الصور السابقة
    if technician_name:
        technician_folder = os.path.join("images", technician_name)
        if os.path.exists(technician_folder):
            images = os.listdir(technician_folder)
            for image_name in images:
                image_path = os.path.join(technician_folder, image_name)
                st.image(image_path, caption=image_name, use_column_width=True)
            
            # تنزيل الصور في ملف ZIP
            zip_path = os.path.join(technician_folder, f"{technician_name}_images.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for image_name in images:
                    zipf.write(os.path.join(technician_folder, image_name), image_name)
            
            st.download_button("📥 Download All Images as ZIP", zip_path, f"{technician_name}_images.zip", mime="application/zip")
