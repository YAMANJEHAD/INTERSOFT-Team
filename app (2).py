# app.py
import streamlit as st
import sqlite3
from datetime import datetime, time
import pandas as pd
import plotly.express as px
import os

# --- DB Functions ---
def init_connection():
    return sqlite3.connect("timesheet.db", check_same_thread=False)

def create_user_table():
    conn = init_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)
    conn.commit()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS timesheet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task TEXT,
            date TEXT,
            start_time TEXT,
            end_time TEXT,
            duration REAL,
            notes TEXT,
            file_path TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def get_user(username, password):
    conn = init_connection()
    result = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
    conn.close()
    return result

def get_user_by_name(username):
    conn = init_connection()
    result = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return result

def insert_timesheet(user_id, task, date, start_time, end_time, duration, notes, file_path):
    conn = init_connection()
    conn.execute("""
        INSERT INTO timesheet (user_id, task, date, start_time, end_time, duration, notes, file_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, task, date, start_time, end_time, duration, notes, file_path))
    conn.commit()
    conn.close()

def get_timesheets(role, user_id=None):
    conn = init_connection()
    if role == 'admin':
        df = pd.read_sql("SELECT t.*, u.username FROM timesheet t JOIN users u ON t.user_id=u.id", conn)
    else:
        df = pd.read_sql("SELECT t.*, u.username FROM timesheet t JOIN users u ON t.user_id=u.id WHERE user_id=?", conn, params=(user_id,))
    conn.close()
    return df

# --- App Start ---
st.set_page_config(page_title="🕒 Timesheet App", layout="wide")
st.title("🕒 Employee Timesheet System")
create_user_table()

# --- Authentication ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Register"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = get_user(username, password)
            if user:
                st.session_state.user = user
                st.success("Logged in successfully!")
            else:
                st.error("Invalid credentials")

    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        role = st.selectbox("Role", ["employee", "admin"])
        if st.button("Register"):
            if get_user_by_name(new_user):
                st.warning("User already exists")
            else:
                conn = init_connection()
                conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (new_user, new_pass, role))
                conn.commit()
                conn.close()
                st.success("User registered")

else:
    user_id, username, _, role = st.session_state.user
    st.sidebar.success(f"Logged in as: {username} ({role})")
    nav = st.sidebar.radio("Navigation", ["📝 Fill Timesheet", "📊 View Report"])

    if nav == "📝 Fill Timesheet":
        st.subheader("📝 Fill Timesheet")
        with st.form("timesheet_form"):
            task = st.text_input("Task Title")
            date = st.date_input("Date", value=datetime.today())
            start = st.time_input("Start Time", value=time(8, 30))
            end = st.time_input("End Time", value=time(17, 0))
            notes = st.text_area("Notes (Optional)")
            file = st.file_uploader("Upload File (Optional)")
            submitted = st.form_submit_button("Submit")

            if submitted:
                duration = (datetime.combine(date, end) - datetime.combine(date, start)).total_seconds() / 3600
                path = ""
                if file:
                    os.makedirs("uploads", exist_ok=True)
                    path = os.path.join("uploads", file.name)
                    with open(path, "wb") as f:
                        f.write(file.read())
                insert_timesheet(user_id, task, str(date), str(start), str(end), duration, notes, path)
                st.success("Timesheet submitted successfully")

    elif nav == "📊 View Report":
        st.subheader("📊 Timesheet Report")
        df = get_timesheets(role, user_id)

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime.today())
        with col2:
            end_date = st.date_input("End Date", value=datetime.today())

        df["date"] = pd.to_datetime(df["date"])
        mask = (df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))
        df_filtered = df[mask]

        st.dataframe(df_filtered)

        fig = px.bar(df_filtered, x="username", y="duration", color="task", title="Worked Hours per User")
        st.plotly_chart(fig, use_container_width=True)

        total_hours = df_filtered['duration'].sum()
        st.metric("Total Hours in Selected Period", f"{total_hours:.2f} hrs")
