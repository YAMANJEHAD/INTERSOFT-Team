import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
import streamlit.components.v1 as components

# إعداد صفحة Streamlit
st.set_page_config(page_title="Note Analyzer", layout="wide")

# دالة تسجيل الدخول
def login_page():
    st.title("Login")
    username = st.text_input("Enter your username")
    password = st.text_input("Enter your password", type="password")

    # إذا كان المدير أو موظف، التحقق من البيانات
    if username == "admin" and password == "adminpassword":
        st.session_state.username = username
        st.success("Successfully logged in as Admin!")
    elif username in ["employee1", "employee2", "employee3", "employee4"] and password == "employee_password":
        st.session_state.username = username
        st.success(f"Successfully logged in as {username}!")
    else:
        st.error("Invalid username or password")

# إذا كان المستخدم قد سجل دخوله
if "username" in st.session_state:
    user_logged_in = True
    if st.session_state.username == "admin":
        # إذا كان المدير، يظهر صفحة المدير
        admin_page()
    else:
        # إذا كان موظفًا، يظهر صفحة الموظف
        employee_page()
else:
    login_page()

# دالة صفحة المدير
def admin_page():
    st.sidebar.header("Admin Dashboard")
    st.markdown("<h1 style='color:#ffffff; text-align:center;'>📊 Admin Dashboard</h1>", unsafe_allow_html=True)
    st.write("This is the Admin page. Here you can view reports, stats, and manage users.")
    st.markdown("### 🚀 User Management")
    st.write("Here, the admin can manage employee accounts, check reports, and more.")
    st.markdown("### 📈 Reports")
    st.write("Here, the admin can see performance reports of the employees.")

    # إمكانية رفع ملفات للمدير
    uploaded_file = st.file_uploader("Upload Employee Report", type=["xlsx"])
    if uploaded_file:
        st.success("File uploaded successfully!")
        df = pd.read_excel(uploaded_file)
        st.dataframe(df)  # عرض البيانات في جدول

# دالة صفحة الموظف
def employee_page():
    st.sidebar.header("Employee Dashboard")
    st.markdown("<h1 style='color:#ffffff; text-align:center;'>📊 Employee Dashboard</h1>", unsafe_allow_html=True)
    st.write(f"Welcome {st.session_state.username}! This is your personal dashboard.")

    st.markdown("### 📂 Upload your files or images")
    uploaded_file = st.file_uploader("📁 Upload Image File", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # عرض تقارير الموظف
    st.markdown("### 📝 Your Reports")
    st.write("Here, the employee can upload data, see personal performance reports, etc.")

    uploaded_excel = st.file_uploader("Upload Your Excel Report", type=["xlsx"])
    if uploaded_excel:
        df = pd.read_excel(uploaded_excel)
        st.dataframe(df)  # عرض بيانات الموظف

# تحليل البيانات والرسوم البيانية
uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])
required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

def classify_note(note):
    note = str(note).strip().upper()
    # تصنيف الملاحظات بناءً على النص
    if "TERMINAL ID - WRONG DATE" in note:
        return "TERMINAL ID - WRONG DATE"
    elif "NO IMAGE FOR THE DEVICE" in note:
        return "NO IMAGE FOR THE DEVICE"
    # إضافة المزيد من الحالات حسب الحاجة...
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

        st.markdown("### 📈 Notes per Technician")
        tech_counts = df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
        st.bar_chart(tech_counts)

        st.markdown("### 🔝 Top 5 Technicians with Most Notes")
        filtered_df = df[~df['Note_Type'].isin(['DONE', 'NO J.O'])]
        tech_counts_filtered = filtered_df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
        top_5_technicians = tech_counts_filtered.head(5)
        technician_notes_table = filtered_df[filtered_df['Technician_Name'].isin(top_5_technicians.index.tolist())]

        st.dataframe(technician_notes_table)

        st.markdown("### 🥧 Note Types Distribution")
        pie_data = df['Note_Type'].value_counts().reset_index()
        pie_data.columns = ['Note_Type', 'Count']
        fig = px.pie(pie_data, names='Note_Type', values='Count', title='Note Type Distribution')
        st.plotly_chart(fig)

        # تنزيل ملف Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 Download Summary Excel", output.getvalue(), "summary.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # تنزيل PDF
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
