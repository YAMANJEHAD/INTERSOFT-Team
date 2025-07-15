import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar
import re
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# --- Page Configuration ---
st.set_page_config(
    page_title="⏱ FLM Task Tracker | INTERSOFT POS",
    layout="wide",
    page_icon="⏱"
)

# --- Enhanced Styling with Inter Font ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #4f46e5;
        --secondary: #a855f7;
        --background: linear-gradient(135deg, #0f172a, #1e293b);
        --surface: #1e293b;
        --text: #f1f5f9;
        --accent: #22d3ee;
        --gradient: linear-gradient(135deg, #4f46e5, #a855f7);
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background: var(--background);
        color: var(--text);
    }
    
    .header {
        background: var(--gradient);
        color: var(--text);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1rem;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
        animation: fadeIn 1s ease-in-out;
    }
    
    .card {
        background: var(--surface);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
        animation: fadeIn 1s ease-in-out;
    }
    
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    .stSelectbox, .stTextInput, .stTextArea, .stTextInput > div > div > input, .stDateInput > div > div > input {
        background-color: #2d3748 !important;
        border-radius: 8px !important;
        border: none !important;
        color: var(--text) !important;
        padding: 0.5rem !important;
        transition: box-shadow 0.3s ease;
    }
    
    .stSelectbox:hover, .stTextInput:hover, .stTextArea:hover, .stDateInput:hover {
        box-shadow: 0 0 6px rgba(34, 211, 238, 0.3);
    }
    
    .stButton>button {
        background: var(--gradient) !important;
        color: var(--text) !important;
        border-radius: 16px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #3730a3, #7e22ce) !important;
        transform: scale(1.05);
        box-shadow: 0 0 10px rgba(79, 70, 229, 0.5);
    }
    
    .stDataFrame {
        border-radius: 12px !important;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .login-container {
        max-width: 350px;
        margin: 2rem auto;
        padding: 1rem;
        background: var(--surface);
        border-radius: 12px;
        animation: fadeIn 1s ease-in-out;
    }
    
    .sidebar .sidebar-content {
        background: var(--surface);
        padding: 0.5rem;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 0.25rem 0.75rem;
        margin-right: 0.25rem;
        transition: all 0.3s ease;
        background: var(--surface);
        color: var(--text);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--gradient);
        color: var(--text);
        border-bottom: 2px solid var(--accent);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #3730a3, #7e22ce);
        color: var(--text);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .card, .login-container, .stDataFrame {
            margin: 0.25rem;
            padding: 0.75rem;
        }
        .header {
            padding: 1rem;
        }
        .stButton>button {
            padding: 0.25rem 0.75rem;
        }
        .sidebar .sidebar-content {
            width: 100%;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- Authentication System ---
def check_login(username, password):
    CREDENTIALS = {
        "Yaman": "YAMAN1",
        "Hatem": "HATEM2",
        "Mahmoud": "MAHMOUD3",
        "Qusai": "QUSAI4"
    }
    return CREDENTIALS.get(username) == password

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

if not st.session_state.logged_in:
    with st.container():
        st.markdown("""
            <div class="header">
                <h1>⏱ INTERSOFT POS - FLM</h1>
                <h3>Login to Task Tracker</h3>
            </div>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.markdown("### Login")
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            if st.button("Login", use_container_width=True):
                if check_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.user_role = username
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- Header with Personalized Greeting ---
st.markdown(f"""
    <div class="header">
        <h1>Hi, {st.session_state.user_role}! Welcome to FLM Task Tracker</h1>
        <h3>Daily Task Dashboard</h3>
    </div>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

# --- Shift Options ---
SHIFTS = ["Morning Shift", "Evening Shift", "Night Shift", "Custom Shift"]

# --- Task Categories ---
TASK_CATEGORIES = {
    "TOMS Operations": {"icon": "💻"},
    "Paper Management": {"icon": "📄"},
    "Job Order Processing": {"icon": "🛠"},
    "CRM Activities": {"icon": "👥"},
    "Meetings": {"icon": "📅"}
}

# --- Priority Levels ---
PRIORITY_LEVELS = {
    "Low": {"emoji": "\U0001F7E2"},  # 🟢
    "Medium": {"emoji": "\U0001F7E1"},  # 🟡
    "High": {"emoji": "\U0001F534"}  # 🔴
}

# --- Status Options ---
STATUS_OPTIONS = {
    "Not Started": {"color": "#9e9e9e", "icon": "\U000023F8"},  # ⏸
    "In Progress": {"color": "#3b82f6", "icon": "\U0001F504"},  # 🔄
    "Completed": {"color": "#22c55e", "icon": "\U00002705"}  # ✅
}

# --- Simplified Sidebar ---
with st.sidebar:
    st.markdown(f"<h3>Hi, {st.session_state.user_role}</h3>", unsafe_allow_html=True)
    st.markdown("### Filters")
    date_range = st.date_input("Date Range", value=(datetime.today(), datetime.today()), format="YYYY-MM-DD", key="sidebar_date")
    start_date, end_date = date_range if isinstance(date_range, tuple) else (date_range, date_range)
    filter_category = st.multiselect("Task Category", list(TASK_CATEGORIES.keys()), 
                                   format_func=lambda x: f"{TASK_CATEGORIES[x]['icon']} {x}", key="sidebar_cat")
    filter_status = st.multiselect("Status", list(STATUS_OPTIONS.keys()), 
                                 format_func=lambda x: f"{STATUS_OPTIONS[x]['icon']} {x}", key="sidebar_status")
    st.markdown("### Quick Stats")
    total_entries = len([r for r in st.session_state.timesheet if r.get("Employee") == st.session_state.user_role])
    st.markdown(f"<p>Total Tasks: <strong>{total_entries}</strong></p>", unsafe_allow_html=True)
    st.markdown("### Actions")
    if st.button("Refresh", key="sidebar_refresh"):
        st.rerun()
    if st.button("Clear Filters", key="sidebar_clear"):
        st.session_state.start_date = datetime.today()
        st.session_state.end_date = datetime.today()
        st.session_state.filter_category = []
        st.session_state.filter_status = []
        st.rerun()

# --- Quick Add Task Form (Moved to Main Content) ---
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Quick Add Task")
    with st.form("quick_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            quick_category = st.selectbox("Category *", list(TASK_CATEGORIES.keys()), 
                                        format_func=lambda x: f"{TASK_CATEGORIES[x]['icon']} {x}", key="quick_cat")
        with col2:
            quick_date = st.date_input("Date *", value=datetime.today(), key="quick_date")
        quick_description = st.text_input("Description *", placeholder="Brief task description", key="quick_desc")
        if st.form_submit_button("Add Task", use_container_width=True):
            if not (quick_category and quick_description):
                st.error("Please fill all required fields (*)")
            else:
                entry = {
                    "Employee": st.session_state.user_role,
                    "Department": "FLM Team",
                    "Date": quick_date.strftime("%Y-%m-%d"),
                    "Day": calendar.day_name[quick_date.weekday()],
                    "Shift Type": "Custom Shift",
                    "Task Category": f"{TASK_CATEGORIES[quick_category]['icon']} {quick_category}",
                    "Priority": f"{PRIORITY_LEVELS['Low']['emoji']} Low",
                    "Status": f"{STATUS_OPTIONS['Not Started']['icon']} Not Started",
                    "Work Description": quick_description,
                    "Recorded At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.timesheet.append(entry)
                st.success(f"Task added by {st.session_state.user_role}!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Dashboard Layout ---
st.markdown("## Daily Task Dashboard")
tab1, tab2 = st.tabs(["Add Task", "Analytics"])

with tab1:
    with st.form("task_entry_form", clear_on_submit=True):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"### Task Entry for {st.session_state.user_role}")
        col1, col2 = st.columns(2)
        with col1:
            department = st.selectbox("Department *", ["FLM Team", "Field Operations", "Technical Support", "Customer Service"])
            shift_type = st.selectbox("Shift *", SHIFTS)
            date = st.date_input("Date *", value=datetime.today())
        with col2:
            task_category = st.selectbox("Category *", list(TASK_CATEGORIES.keys()), 
                                       format_func=lambda x: f"{TASK_CATEGORIES[x]['icon']} {x}")
            status = st.selectbox("Status *", list(STATUS_OPTIONS.keys()), 
                                format_func=lambda x: f"{STATUS_OPTIONS[x]['icon']} {x}")
            priority = st.selectbox("Priority *", list(PRIORITY_LEVELS.keys()), 
                                  format_func=lambda x: f"{PRIORITY_LEVELS[x]['emoji']} {x}")
        work_description = st.text_area("Description *", placeholder="Describe the task", height=80)
        if st.form_submit_button("Submit", use_container_width=True):
            if not (department and shift_type and task_category and work_description):
                st.error("Please fill all required fields (*)")
            else:
                entry = {
                    "Employee": st.session_state.user_role,
                    "Department": department,
                    "Date": date.strftime("%Y-%m-%d"),
                    "Day": calendar.day_name[date.weekday()],
                    "Shift Type": shift_type,
                    "Task Category": f"{TASK_CATEGORIES[task_category]['icon']} {task_category}",
                    "Priority": f"{PRIORITY_LEVELS[priority]['emoji']} {priority}",
                    "Status": f"{STATUS_OPTIONS[status]['icon']} {status}",
                    "Work Description": work_description,
                    "Recorded At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.timesheet.append(entry)
                st.success(f"Task added by {st.session_state.user_role}!")
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    if st.session_state.timesheet:
        df = pd.DataFrame(st.session_state.timesheet)
        filtered_df = df[df['Employee'] == st.session_state.user_role]
        if start_date and end_date:
            filtered_df = filtered_df[(filtered_df['Date'] >= start_date.strftime("%Y-%m-%d")) & (filtered_df['Date'] <= end_date.strftime("%Y-%m-%d"))]
        if filter_category:
            filtered_df = filtered_df[filtered_df['Task Category'].isin(filter_category)]
        if filter_status:
            filtered_df = filtered_df[filtered_df['Status'].isin(filter_status)]

        if not filtered_df.empty:
            # --- Styling DataFrame ---
            def get_priority_color(priority_str):
                priority_key = priority_str.split(' ')[-1]
                for key in PRIORITY_LEVELS:
                    if priority_key in key:
                        return '#ff5252' if PRIORITY_LEVELS[key]['emoji'] == '\U0001F534' else '#ffd740' if PRIORITY_LEVELS[key]['emoji'] == '\U0001F7E1' else '#22c55e'
                return '#22c55e'

            def get_status_color(status_str):
                status_key = status_str.split(' ')[0]
                return STATUS_OPTIONS.get(status_key, {}).get('color', '#f1f5f9')

            styled_df = filtered_df.sort_values("Date", ascending=False).style
            styled_df = styled_df.applymap(lambda x: f"color: {get_status_color(x)}", subset=["Status"])
            styled_df = styled_df.applymap(lambda x: f"color: {get_priority_color(x)}", subset=["Priority"])
            styled_df = styled_df.set_properties(**{
                'background-color': '#1e293b',
                'color': '#f1f5f9',
                'border': 'none',
                'font-family': 'Inter',
                'text-align': 'center'
            })

            # --- Metrics ---
            st.markdown("### Task Overview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Tasks", len(filtered_df))
            with col2:
                st.metric("Completed", filtered_df[filtered_df['Status'].str.contains("Completed")].shape[0])
            with col3:
                st.metric("In Progress", filtered_df[filtered_df['Status'].str.contains("In Progress")].shape[0])

            # --- Visualization ---
            st.markdown("### Task Trends")
            fig = px.bar(
                filtered_df.groupby('Date').size().reset_index(name='Count'),
                x='Date',
                y='Count',
                title="Tasks by Date",
                color='Date',
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig.update_layout(paper_bgcolor="#1e293b", font_color="#f1f5f9", plot_bgcolor="#1e293b")
            st.plotly_chart(fig, use_container_width=True)

            # --- Data Table ---
            st.markdown("### Task List")
            st.dataframe(styled_df, use_container_width=True, hide_index=True)

            # --- Report Generation ---
            st.markdown("### Export Report")
            col1, col2 = st.columns(2)
            with col1:
                report_format = st.selectbox("Format", ["PDF", "Excel"], key="report_format")
            with col2:
                if st.button("Export", key="report_button"):
                    with st.spinner("Generating report..."):
                        def remove_emojis(text):
                            emoji_pattern = re.compile("["
                                u"\U0001F600-\U0001F64F"
                                u"\U0001F300-\U0001F5FF"
                                u"\U0001F680-\U0001F6FF"
                                u"\U0001F1E0-\U0001F1FF"
                                u"\U00002700-\U000027BF"
                                u"\U0001F900-\U0001F9FF"
                                "]+", flags=re.UNICODE)
                            return emoji_pattern.sub(r'', str(text))

                        export_df = filtered_df.copy()
                        export_df['Task Category'] = export_df['Task Category'].apply(remove_emojis)
                        export_df['Priority'] = export_df['Priority'].apply(remove_emojis)
                        export_df['Status'] = export_df['Status'].apply(remove_emojis)

                        if report_format == "Excel":
                            excel_buffer = BytesIO()
                            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                                export_df.to_excel(writer, index=False, sheet_name="Tasks")
                                workbook = writer.book
                                worksheet = writer.sheets["Tasks"]
                                header_format = workbook.add_format({
                                    'bold': True, 'fg_color': '#4f46e5', 'font_color': '#f1f5f9', 'border': 1
                                })
                                for col_num, value in enumerate(export_df.columns.values):
                                    worksheet.write(0, col_num, value, header_format)
                            st.download_button(
                                label="Download Excel",
                                data=excel_buffer.getvalue(),
                                file_name=f"FLM_Tasks_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        else:
                            pdf_buffer = BytesIO()
                            doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
                            styles = getSampleStyleSheet()
                            styles['Title'].fontName = 'Helvetica-Bold'
                            styles['Normal'].fontName = 'Helvetica'
                            elements = []

                            elements.append(Paragraph(f"FLM Task Report - {st.session_state.user_role}", styles['Title']))
                            elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
                            elements.append(Spacer(1, 12))

                            data = [["Metric", "Value"], ["Total Tasks", str(len(export_df))]]
                            table = Table(data, colWidths=[2.5*inch, 1.5*inch])
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), '#4f46e5'),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black)
                            ]))
                            elements.append(table)
                            elements.append(Spacer(1, 12))

                            pdf_data = [list(export_df.columns)] + [list(row) for row in export_df.itertuples(index=False)]
                            pdf_table = Table(pdf_data)
                            pdf_table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), '#4f46e5'),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('FONTSIZE', (0, 0), (-1, -1), 8)
                            ]))
                            elements.append(pdf_table)

                            doc.build(elements)
                            st.download_button(
                                label="Download PDF",
                                data=pdf_buffer.getvalue(),
                                file_name=f"FLM_Tasks_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf"
                            )
        else:
            st.info("No tasks available based on filters.")
    else:
        st.markdown("""
            <div style="text-align:center; padding:1.5rem; border-radius:12px; background:#1e293b; max-width:800px; margin-left:auto; margin-right:auto;">
                <h3>No Tasks Yet</h3>
                <p>Add your first task using the 'Add Task' tab or Quick Add form.</p>
            </div>
        """, unsafe_allow_html=True)

# --- Footer ---
current_time = "06:02 PM +03"
st.markdown(f"""
    <center>
        <small style="color:#a855f7;">INTERSOFT POS - FLM Task Tracker • {datetime.now().strftime('%Y-%m-%d')} {current_time}</small>
    </center>
""", unsafe_allow_html=True)
