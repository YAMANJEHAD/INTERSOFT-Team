import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# --- Page Config ---
st.set_page_config(page_title="INTERSOFT Task Tracker", layout="wide")
st.title("📋 INTERSOFT POS | FLM Task Tracker")

# --- Init Session State ---
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# --- Input Form ---
with st.expander("➕ Add New Task", expanded=True):
    with st.form("task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Employee Name *")
            category = st.selectbox("Task Category", ["TOMS", "Paper", "Job Order", "CRM", "Meeting"])
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        with col2:
            date = st.date_input("Date", datetime.today())
            status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
            description = st.text_area("Task Description", height=100)

        submit = st.form_submit_button("💾 Save Task")
        if submit:
            if not name or not description:
                st.warning("Please complete all required fields.")
            else:
                st.session_state.tasks.append({
                    "Name": name,
                    "Category": category,
                    "Priority": priority,
                    "Status": status,
                    "Date": date.strftime("%Y-%m-%d"),
                    "Description": description,
                    "Recorded At": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success("Task saved!")

# --- Task Display ---
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)

    st.markdown("### 🔍 Filter Tasks")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        filter_name = st.multiselect("Filter by Name", options=sorted(df["Name"].unique()))
        filter_status = st.multiselect("Filter by Status", options=sorted(df["Status"].unique()))
    with filter_col2:
        filter_priority = st.multiselect("Filter by Priority", options=sorted(df["Priority"].unique()))
        search = st.text_input("Search Description")

    filtered_df = df.copy()
    if filter_name:
        filtered_df = filtered_df[filtered_df["Name"].isin(filter_name)]
    if filter_status:
        filtered_df = filtered_df[filtered_df["Status"].isin(filter_status)]
    if filter_priority:
        filtered_df = filtered_df[filtered_df["Priority"].isin(filter_priority)]
    if search:
        filtered_df = filtered_df[filtered_df["Description"].str.contains(search, case=False, na=False)]

    st.dataframe(filtered_df, use_container_width=True)

    st.markdown("### 📈 Task Count by Status")
    fig = px.bar(filtered_df.groupby("Status").size().reset_index(name="Count"),
                 x="Status", y="Count", color="Status", title="Tasks by Status")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📤 Export Report")
    export_format = st.selectbox("Choose format", ["Excel", "PDF"])

    if st.button("Download Report"):
        if export_format == "Excel":
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
                filtered_df.to_excel(writer, index=False, sheet_name="Tasks")
            st.download_button("Download Excel", excel_buffer.getvalue(),
                               file_name="tasks_report.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = [
                Paragraph("INTERSOFT Task Report", styles["Title"]),
                Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]),
                Spacer(1, 12)
            ]
            table_data = [list(filtered_df.columns)] + [list(row) for _, row in filtered_df.iterrows()]
            table = Table(table_data)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black)
            ]))
            elements.append(table)
            doc.build(elements)
            st.download_button("Download PDF", data=pdf_buffer.getvalue(),
                               file_name="tasks_report.pdf", mime="application/pdf")

else:
    st.info("No tasks yet. Add your first task above.")
