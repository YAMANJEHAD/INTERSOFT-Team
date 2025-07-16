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
    page_title="Intersoft FLM Task Tracker",
    layout="wide",
    page_icon="📊"
)

# --- Professional Styling with Inter Font ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #1e3a8a;
        --secondary: #3b82f6;
        --background: #f8fafc;
        --surface: #ffffff;
        --text: #1f2937;
        --border: #e2e8f0;
        --shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        --gradient: linear-gradient(90deg, #1e3a8a, #2563eb);
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background: var(--background);
        color: var(--text);
    }
    
    .header {
        background: var(--gradient);
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 1.5rem;
        max-width: 1000px;
        margin-left: auto;
        margin-right: auto;
        box-shadow: var(--shadow);
    }
    
    .card {
        background: var(--surface);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        max-width: 1000px;
        margin-left: auto;
        margin-right: auto;
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
    }
    
    .stSelectbox, .stTextInput, .stTextArea, .stDateInput > div > div > input {
        background-color: #f1f5f9 !important;
        border-radius: 6px !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        padding: 0.5rem !important;
    }
    
    .stSelectbox:hover, .stTextInput:hover, .stTextArea:hover, .stDateInput:hover {
        border-color: var(--primary) !important;
        box-shadow: 0 0 5px rgba(30, 58, 138, 0.2);
    }
    
    .stButton>button {
        background: var(--primary) !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        border: none !important;
        transition: background-color 0.2s ease;
    }
    
    .stButton>button:hover {
        background: #1e40af !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }
    
    .stDataFrame {
        border-radius: 8px;
        max-width: 1000px;
        margin-left: auto;
        margin-right: auto;
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
    }
    
    .login-container {
        max-width: 400px;
        margin: 3rem auto;
        padding: 2rem;
        background: var(--surface);
        border-radius: 8px;
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
    }
    
    .sidebar {
        background: var(--surface);
        padding: 1rem;
        border-right: 1px solid var(--border);
    }
    
    .logo {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary);
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 0.5rem 1rem;
        margin-right: 0.5rem;
        background: var(--surface);
        color: var(--text);
        border: 1px solid var(--border);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--primary);
        color: #ffffff;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #e0e7ff;
        color: var(--text);
    }
    
    @media (max-width: 768px) {
        .card, .login-container, .stDataFrame {
            margin: 0.5rem;
            padding: 1rem;
        }
        .header {
            padding: 1rem;
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
    st.markdown('<div class="logo">Intersoft</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown("""
            <div class="header">
                <h1>Intersoft FLM Task Tracker</h1>
                <h3>Login</h3>
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

# --- Header ---
st.markdown('<div class="logo">Intersoft</div>', unsafe_allow_html=True)
st.markdown(f"""
    <div class="header">
        <h1>Welcome, {st.session_state.user_role}</h1>
        <h3>FLM Task Tracker</h3>
    </div>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "timesheet" not in st.session_state:
    st.session_state.timesheet = []

# --- Shift Options ---
SHIFTS = ["Morning Shift (8:30 - 5:30)", "Evening Shift (3:00 - 11:00)"]

# --- Task Categories ---
TASK_CATEGORIES = {
    "TOMS Operations": {"icon": "🖥️"},
    "Paper Management": {"icon": "📑"},
    "Job Order Processing": {"icon": "🔧"},
    "CRM Activities": {"icon": "🤝"},
    "Meetings": {"icon": "📅"}
}

# --- Priority Levels ---
PRIORITY_LEVELS = {
    "Low": {"emoji": "🟩"},
    "Medium": {"emoji": "🟨"},
    "High": {"emoji": "🟥"}
}

# --- Status Options ---
STATUS_OPTIONS = {
    "Not Started": {"color": "#9e9e9e", "icon": "⏳"},
    "In Progress": {"color": "#3b82f6", "icon": "🔄"},
    "Completed": {"color": "#22c55e", "icon": "✅"}
}

# --- Sidebar ---
with st.sidebar:
    st.markdown('<div class="logo">Intersoft</div>', unsafe_allow_html=True)
    st.markdown("### Filters")
    date_range = st.date_input("Date Range", value=(datetime(2025, 7, 15), datetime(2025, 7, 15)), format="YYYY-MM-DD", key="date_range")
    start_date, end_date = date_range if isinstance(date_range, tuple) else (date_range, date_range)
    task_category = st.selectbox("Task Category", ["All"] + list(TASK_CATEGORIES.keys()), 
                               format_func=lambda x: x if x == "All" else f"{TASK_CATEGORIES[x]['icon']} {x}", key="task_cat")
    status = st.selectbox("Status", ["All"] + list(STATUS_OPTIONS.keys()), 
                         format_func=lambda x: x if x == "All" else f"{STATUS_OPTIONS[x]['icon']} {x}", key="status")
    st.markdown("### Statistics")
    total_entries = len([r for r in st.session_state.timesheet if r.get("Employee") == st.session_state.user_role])
    st.markdown(f"<p>Total Tasks: <strong>{total_entries}</strong></p>", unsafe_allow_html=True)
    st.markdown("### Actions")
    if st.button("Refresh"):
        st.rerun()
    if st.button("Clear Filters"):
        st.session_state.date_range = (datetime.today(), datetime.today())
        st.session_state.task_category = "All"
        st.session_state.status = "All"
        st.rerun()

# --- Dashboard Layout ---
st.markdown("## Task Dashboard")
tab1, tab2 = st.tabs(["Add Task", "Analytics"])

with tab1:
    with st.form("task_entry_form", clear_on_submit=True):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Add Task")
        col1, col2 = st.columns(2)
        with col1:
            department = st.selectbox("Department", ["FLM Team", "Field Operations", "Technical Support", "Customer Service"])
            shift_type = st.selectbox("Shift", SHIFTS)
            date = st.date_input("Date", value=datetime.today())
        with col2:
            task_category = st.selectbox("Category", list(TASK_CATEGORIES.keys()), 
                                      format_func=lambda x: f"{TASK_CATEGORIES[x]['icon']} {x}")
            status = st.selectbox("Status", list(STATUS_OPTIONS.keys()), 
                                format_func=lambda x: f"{STATUS_OPTIONS[x]['icon']} {x}")
            priority = st.selectbox("Priority", list(PRIORITY_LEVELS.keys()), 
                                  format_func=lambda x: f"{PRIORITY_LEVELS[x]['emoji']} {x}")
        work_description = st.text_area("Description", placeholder="Enter task details", height=80)
        if st.form_submit_button("Submit", use_container_width=True):
            if not (department and shift_type and task_category and work_description):
                st.error("Please fill all required fields")
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
                st.success("Task added successfully!")
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    if st.session_state.timesheet:
        df = pd.DataFrame(st.session_state.timesheet)
        filtered_df = df[df['Employee'] == st.session_state.user_role]
        if start_date and end_date:
            filtered_df = filtered_df[(filtered_df['Date'] >= start_date.strftime("%Y-%m-%d")) & (filtered_df['Date'] <= end_date.strftime("%Y-%m-%d"))]
        if task_category != "All":
            filtered_df = filtered_df[filtered_df['Task Category'].str.contains(task_category.split(' ')[-1])]
        if status != "All":
            filtered_df = filtered_df[filtered_df['Status'].str.contains(status.split(' ')[-1])]

        if not filtered_df.empty:
            # --- Styling DataFrame ---
            def get_priority_color(priority_str):
                priority_key = priority_str.split(' ')[-1]
                return '#dc2626' if priority_key == 'High' else '#facc15' if priority_key == 'Medium' else '#16a34a'

            def get_status_color(status_str):
                status_key = status_str.split(' ')[-1]
                return STATUS_OPTIONS.get(status_key, {}).get('color', '#6b7280')

            styled_df = filtered_df.sort_values("Date", ascending=False).style
            styled_df = styled_df.applymap(lambda x: f"color: {get_status_color(x)}", subset=["Status"])
            styled_df = styled_df.applymap(lambda x: f"color: {get_priority_color(x)}", subset=["Priority"])
            styled_df = styled_df.set_properties(**{
                'background-color': 'var(--surface)',
                'color': 'var(--text)',
                'border': '1px solid var(--border)',
                'font-family': 'Inter',
                'text-align': 'left',
                'padding': '0.5rem'
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
                color_discreteSequence=px.colors.qualitative.Bold
            )
            fig.update_layout(
                paper_bgcolor="var(--surface)",
                plot_bgcolor="var(--surface)",
                font_color="var(--text)",
                title_font_size=16,
                margin=dict(l=40, r=40, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- Data Table ---
            st.markdown("### Task List")
            st.dataframe(styled_df, use_container_width=True, hide_index=True)

            # --- Report Generation ---
            st.markdown("### Export Report")
            shift_time = st.selectbox("Shift Time", SHIFTS, key="shift_time")
            if st.button("Export Excel"):
                with st.spinner("Preparing report..."):
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
                    for col in ['Task Category', 'Priority', 'Status']:
                        export_df[col] = export_df[col].apply(remove_emojis)
                    export_df['Shift Time'] = shift_time

                    excel_buffer = BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                        export_df.to_excel(writer, index=False, sheet_name="Tasks")
                        workbook = writer.book
                        worksheet = writer.sheets["Tasks"]
                        header_format = workbook.add_format({
                            'bold': True, 'bg_color': '#1e3a8a', 'font_color': '#ffffff',
                            'border': 1, 'text_wrap': True, 'align': 'center'
                        })
                        for col_num, value in enumerate(export_df.columns.values):
                            worksheet.set_column(col_num, col_num, 20)
                            worksheet.write(0, col_num, value, header_format)
                    st.download_button(
                        label="Download Excel",
                        data=excel_buffer.getvalue(),
                        file_name=f"Intersoft_FLM_Tasks_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        else:
            st.info("No tasks match the selected filters.")
    else:
        st.markdown("""
            <div class="card">
                <h3>No Tasks Available</h3>
                <p>Add a task using the 'Add Task' tab.</p>
            </div>
        """, unsafe_allow_html=True)

# --- Footer ---
st.markdown(f"""
    <div style="text-align: center; padding: 1rem; color: #6b7280;">
        <small>Intersoft FLM Task Tracker • {datetime.now().strftime('%Y-%m-%d')}</small>
    </div>
""", unsafe_allow_html=True)
