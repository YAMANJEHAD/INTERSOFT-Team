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
    
    .logo {
        position: absolute;
        top: 1rem;
        left: 1rem;
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text);
        opacity: 0.8;
        animation: fadeIn 1s ease-in-out;
    }
    
    .header {
        background: var(--gradient);
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 1.5rem;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
        animation: fadeIn 1s ease-in-out;
    }
    
    .card {
        background: var(--surface);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        max-width: 900px;
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
        border-radius: 12px !important;
        border: none !important;
        color: var(--text) !important;
        padding: 0.75rem !important;
        transition: box-shadow 0.3s ease;
    }
    
    .stSelectbox:hover, .stTextInput:hover, .stTextArea:hover, .stDateInput:hover {
        box-shadow: 0 0 8px rgba(34, 211, 238, 0.3);
    }
    
    .stButton>button {
        background: var(--gradient) !important;
        color: var(--text) !important;
        border-radius: 24px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #3730a3, #7e22ce) !important;
        transform: scale(1.05) translateY(-2px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.5);
    }
    
    .stDataFrame {
        border-radius: 16px !important;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .metric-card {
        background: var(--surface);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        animation: fadeIn 1s ease-in-out;
    }
    
    h1, h2, h3 {
        font-weight: 700 !important;
        color: var(--text) !important;
    }
    
    .login-container {
        max-width: 350px;
        margin: 2rem auto;
        padding: 1.5rem;
        background: var(--surface);
        border-radius: 16px;
        animation: fadeIn 1s ease-in-out;
        text-align: center;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #1e293b, #2d3748);
        max-width: 250px;
        min-width: 200px;
        padding: 1rem;
        border-radius: 12px;
        animation: slideIn 0.5s ease-in-out;
    }
    
    @keyframes slideIn {
        0% { transform: translateX(-20px); opacity: 0; }
        100% { transform: translateX(0); opacity: 1; }
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        margin-right: 0.5rem;
        transition: all 0.3s ease;
        background: var(--surface);
        color: var(--text);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--gradient);
        color: #ffffff;
        border-bottom: 3px solid var(--accent);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #3730a3, #7e22ce);
        color: #ffffff;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .card, .metric-card, .login-container, .stDataFrame {
            margin: 0.5rem;
            padding: 1rem;
        }
        .header {
            padding: 1rem;
        }
        .stButton>button {
            padding: 0.5rem 1rem;
        }
        .sidebar .sidebar-content {
            max-width: 100%;
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
    st.markdown('<div class="logo">INTERSOFT<br>International Software Company</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown("""
            <div class="header">
                <h2>Login</h2>
            </div>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
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
st.markdown('<div class="logo">INTERSOFT<br>International Software Company</div>', unsafe_allow_html=True)
st.markdown(f"""
    <div class="header">
        <h2>Hi, {st.session_state.user_role}! Welcome to FLM Task Tracker Daily Task Dashboard</h2>
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

# --- Priority Levels (Using Unicode escape sequences for safety) ---
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

# --- Sidebar Filters and Quick Actions ---
with st.sidebar:
    st.markdown(f"### Hi, {st.session_state.user_role}")
    st.markdown("### Filters")
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### Date Range")
        date_range = st.date_input("Select Date Range", value=(datetime.today(), datetime.today()), format="YYYY-MM-DD")
        start_date, end_date = date_range if isinstance(date_range, tuple) else (date_range, date_range)
        
        st.markdown("#### Department")
        filter_department = st.multiselect("Select Department", ["FLM Team", "Field Operations", "Technical Support", "Customer Service"], placeholder="All Departments")
        
        st.markdown("#### Task Category")
        filter_category = st.multiselect("Select Task Category", list(TASK_CATEGORIES.keys()), 
                                       format_func=lambda x: f"{TASK_CATEGORIES[x]['icon']} {x}", placeholder="All Categories")
        
        st.markdown("#### Status")
        filter_status = st.multiselect("Select Status", list(STATUS_OPTIONS.keys()), 
                                     format_func=lambda x: f"{STATUS_OPTIONS[x]['icon']} {x}", placeholder="All Statuses")
        
        st.markdown("#### Search Description")
        search_term = st.text_input("Search Task Description", placeholder="Enter keywords...")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Stats
    total_entries = len([r for r in st.session_state.timesheet if r.get("Employee") == st.session_state.user_role])
    st.markdown(f"""
        <div class="card">
            <p>Total Tasks: <strong>{total_entries}</strong></p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Quick Actions")
    if st.button("Refresh Data", use_container_width=True):
        st.rerun()
    if st.button("Clear Filters", use_container_width=True):
        st.session_state.filter_department = []
        st.session_state.filter_category = []
        st.session_state.filter_status = []
        st.session_state.search_term = ""
        st.session_state.start_date = datetime.today()
        st.session_state.end_date = datetime.today()
        st.rerun()
    
    # Quick Add Task Form
    st.markdown("### Quick Add Task")
    with st.form("quick_task_form", clear_on_submit=True):
        quick_category = st.selectbox("Task Category *", list(TASK_CATEGORIES.keys()), 
                                     format_func=lambda x: f"{TASK_CATEGORIES[x]['icon']} {x}", key="quick_category")
        quick_description = st.text_input("Task Description *", placeholder="Brief task description", key="quick_description")
        quick_date = st.date_input("Date *", value=datetime.today(), key="quick_date")
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
                st.balloons()

# --- Dashboard Layout ---
st.markdown("## Daily Task Dashboard")
tab1, tab2 = st.tabs(["Add Task", "Analytics"])

with tab1:
    with st.form("task_entry_form", clear_on_submit=True):
        st.markdown(f"### Daily Task Entry for {st.session_state.user_role}")
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("#### Task Assignment")
            department = st.selectbox("Department *", ["FLM Team", "Field Operations", "Technical Support", "Customer Service"])
            shift_type = st.selectbox("Shift Type *", SHIFTS)
            date = st.date_input("Date *", value=datetime.today())

            st.markdown("#### Task Details")
            col1, col2 = st.columns([1, 1])
            with col1:
                task_category = st.selectbox("Task Category *", list(TASK_CATEGORIES.keys()), 
                                           format_func=lambda x: f"{TASK_CATEGORIES[x]['icon']} {x}")
            with col2:
                status = st.selectbox("Status *", list(STATUS_OPTIONS.keys()), 
                                     format_func=lambda x: f"{STATUS_OPTIONS[x]['icon']} {x}")
            priority = st.selectbox("Priority *", list(PRIORITY_LEVELS.keys()), 
                                   format_func=lambda x: f"{PRIORITY_LEVELS[x]['emoji']} {x}")

            work_description = st.text_area("Task Description *", placeholder="Describe the task", height=100)
            st.markdown('</div>', unsafe_allow_html=True)

            submitted = st.form_submit_button("Submit Task", use_container_width=True)

        if submitted:
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
                st.balloons()

with tab2:
    if st.session_state.timesheet:
        df = pd.DataFrame(st.session_state.timesheet)

        # --- Filters ---
        st.markdown("### Filter Tasks")
        filtered_df = df[df['Employee'] == st.session_state.user_role]
        if start_date and end_date:
            filtered_df = filtered_df[(filtered_df['Date'] >= start_date.strftime("%Y-%m-%d")) & (filtered_df['Date'] <= end_date.strftime("%Y-%m-%d"))]
        if filter_department:
            filtered_df = filtered_df[filtered_df['Department'].isin(filter_department)]
        if filter_category:
            filtered_df = filtered_df[filtered_df['Task Category'].isin(filter_category)]
        if filter_status:
            filtered_df = filtered_df[filtered_df['Status'].isin(filter_status)]
        if search_term:
            filtered_df = filtered_df[filtered_df['Work Description'].str.contains(search_term, case=False, na=False)]

        if not filtered_df.empty:
            # --- Small Details ---
            st.markdown("### Task Overview")
            st.markdown(f"<p>Total Tasks: <strong>{len(filtered_df)}</strong></p>", unsafe_allow_html=True)
            status_summary = filtered_df['Status'].value_counts().to_dict()
            st.markdown("<p>Status: </p>", unsafe_allow_html=True)
            for status, count in status_summary.items():
                st.markdown(f"<p>  {status}: <strong>{count}</strong></p>", unsafe_allow_html=True)

            # --- Report Generation ---
            st.markdown("### Generate Report")
            col1, col2 = st.columns([1, 1])
            with col1:
                report_format = st.selectbox("Format", ["PDF", "Excel"])
            with col2:
                if st.button("Generate Report", use_container_width=True):
                    with st.spinner("Generating report..."):
                        # Remove emojis for Excel export
                        def remove_emojis(text):
                            emoji_pattern = re.compile("["
                                u"\U0001F600-\U0001F64F"  # emoticons
                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                u"\U0001F1E0-\U0001F1FF"  # flags
                                u"\U00002700-\U000027BF"  # dingbats
                                u"\U0001F900-\U0001F9FF"  # supplemental symbols
                                "]+", flags=re.UNICODE)
                            return emoji_pattern.sub(r'', str(text))

                        export_df = filtered_df.copy()
                        export_df['Task Category'] = export_df['Task Category'].apply(remove_emojis)
                        export_df['Priority'] = export_df['Priority'].apply(remove_emojis)
                        export_df['Status'] = export_df['Status'].apply(remove_emojis)

                        if report_format == "Excel":
                            excel_buffer = BytesIO()
                            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                                export_df.to_excel(writer, index=False, sheet_name="Task Entries")
                                workbook = writer.book
                                worksheet = writer.sheets["Task Entries"]
                                header_format = workbook.add_format({
                                    'bold': True,
                                    'fg_color': '#4f46e5',
                                    'font_color': '#f1f5f9',
                                    'border': 1
                                })
                                for col_num, value in enumerate(export_df.columns.values):
                                    worksheet.write(0, col_num, value, header_format)
                            st.download_button(
                                label="Download Excel",
                                data=excel_buffer.getvalue(),
                                file_name=f"FLM_Task_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        else:
                            pdf_buffer = BytesIO()
                            doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
                            styles = getSampleStyleSheet()
                            styles['Title'].fontName = 'Helvetica-Bold'
                            styles['Normal'].fontName = 'Helvetica'
                            elements = []

                            elements.append(Paragraph(f"FLM Task Report - Generated by {st.session_state.user_role}", styles['Title']))
                            elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
                            elements.append(Spacer(1, 12))

                            summary_data = [
                                ["Metric", "Value"],
                                ["Total Tasks", f"{len(filtered_df)}"]
                            ]
                            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
                            summary_table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), '#4f46e5'),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica')
                            ]))
                            elements.append(summary_table)
                            elements.append(Spacer(1, 12))

                            pdf_data = [list(filtered_df.columns)] + [list(row) for _, row in filtered_df.iterrows()]
                            pdf_table = Table(pdf_data)
                            pdf_table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), '#4f46e5'),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('FONTSIZE', (0, 0), (-1, -1), 8),
                                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica')
                            ]))
                            elements.append(pdf_table)

                            doc.build(elements)
                            st.download_button(
                                label="Download PDF",
                                data=pdf_buffer.getvalue(),
                                file_name=f"FLM_Task_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf"
                            )
        else:
            st.markdown("""
                <div style="text-align:center; padding:2rem; border-radius:16px; background:#1e293b; max-width:900px; margin-left:auto; margin-right:auto;">
                    <h3>No Tasks Yet</h3>
                    <p>Add your first task in the 'Add Task' tab or use the Quick Add Task form</p>
                </div>
            """, unsafe_allow_html=True)

# --- Footer ---
st.markdown(f"""
    <center>
        <small style="color:#ffffff;">INTERSOFT POS - FLM Task Tracker • 2025-07-15</small>
    </center>
""", unsafe_allow_html=True)
