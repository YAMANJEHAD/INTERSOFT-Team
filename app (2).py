import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime
import plotly.express as px
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="INTERSOFT Analyzer", layout="wide")

# بيانات المستخدمين
users_db = {
    "admin": {"password": "123456", "role": "supervisor"},
    "tech1": {"password": "123", "role": "technician"},
    "tech2": {"password": "123", "role": "technician"}
}

# صفحة الدخول
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.username = ""

if not st.session_state.authenticated:
    st.title("🔐 Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = users_db.get(username)
        if user and user["password"] == password:
            st.session_state.authenticated = True
            st.session_state.role = user["role"]
            st.session_state.username = username
            st.success("Login successful! Redirecting...")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

# زر تسجيل الخروج
if st.sidebar.button("🔓 Logout"):
    st.session_state.authenticated = False
    st.experimental_rerun()

st.sidebar.success(f"👋 Welcome, {st.session_state.username} ({st.session_state.role})")

# تحميل الملف
st.title("📊 INTERSOFT Note Analyzer")
uploaded_file = st.file_uploader("📤 Upload Excel File", type=["xlsx"])
required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type', 'Closed_Date']

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
    df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ Missing required columns. Found: {list(df.columns)}")
        st.stop()

    df['Note_Type'] = df['NOTE'].apply(classify_note)
    df['Closed_Date'] = pd.to_datetime(df['Closed_Date'], errors='coerce')

    # فلترة فنيين فقط على اسم المستخدم
    if st.session_state.role == "technician":
        df = df[df['Technician_Name'].str.lower().str.contains(st.session_state.username.lower())]

    st.subheader("📆 Filter by Date")
    start = st.date_input("From", df['Closed_Date'].min().date())
    end = st.date_input("To", df['Closed_Date'].max().date())
    df = df[(df['Closed_Date'].dt.date >= start) & (df['Closed_Date'].dt.date <= end)]

    st.success(f"✅ Showing {len(df)} records")

    st.subheader("📊 Notes by Technician")
    st.bar_chart(df['Technician_Name'].value_counts())

    st.subheader("📌 Notes by Type")
    st.bar_chart(df['Note_Type'].value_counts())

    st.subheader("🥧 Note Distribution")
    pie_data = df['Note_Type'].value_counts().reset_index()
    pie_data.columns = ['Note_Type', 'Count']
    st.plotly_chart(px.pie(pie_data, names='Note_Type', values='Count'))

    if st.session_state.role == "supervisor":
        st.subheader("🔝 Top Technicians with Most Notes")
        top_techs = df['Technician_Name'].value_counts().head(5)
        st.dataframe(top_techs.reset_index().rename(columns={'index': 'Technician_Name', 'Technician_Name': 'Notes_Count'}))

    st.subheader("📋 All Notes")
    st.dataframe(df[['Technician_Name', 'Terminal_Id', 'Note_Type', 'Ticket_Type', 'Closed_Date']])

    # تصدير PDF
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 50, f"INTERSOFT Summary Report - {st.session_state.username}")
    c.setFont("Helvetica", 12)
    y = height - 100
    note_counts = df['Note_Type'].value_counts()
    for note_type, count in note_counts.items():
        c.drawString(120, y, f"{note_type}: {count}")
        y -= 20
        if y < 100:
            c.showPage()
            y = height - 100
            c.setFont("Helvetica", 12)
    c.save()

    st.download_button("📥 Download PDF Report", pdf_buffer.getvalue(), "summary_report.pdf", "application/pdf")
