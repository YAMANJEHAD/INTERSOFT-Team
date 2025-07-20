# FLM Task Tracker – Full Version with Admin Panel, Roles, Alerts, Calendar

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import calendar
from io import BytesIO
import uuid

# --- Page Config ---
st.set_page_config("⚡ INTERSOFT Dashboard | FLM", layout="wide", page_icon="🚀")

# --- Styling ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: radial-gradient(circle at top left, #0f172a, #1e293b);
    color: #f8fafc;
}
.top-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0 2rem; margin-top: 1rem;
}
.greeting { font-size: 1rem; font-weight: 500; color: #fcd34d; text-align: right; }
.company { font-size: 1.2rem; font-weight: 600; color: #60a5fa; }
.date-box {
    font-size: 1rem; font-weight: 500; color: #f8fafc; text-align: center;
    background: #1e293b; padding: 0.5rem 1rem; border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3); margin-bottom: 1.5rem; display: inline-block;
}
.overview-box {
    background: linear-gradient(to bottom right, #1e3a8a, #3b82f6);
    padding: 1.5rem; border-radius: 18px; text-align: center;
    margin: 1rem 0; transition: transform 0.4s ease;
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
}
.overview-box:hover { transform: translateY(-5px) scale(1.02); }
.overview-box span { font-size: 2.2rem; font-weight: 800; color: #fcd34d; }
footer { text-align: center; color: #94a3b8; padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- Users & Roles ---
USERS = {
    "Yaman": {"pass": "YAMAN1", "role": "Admin"},
    "Hatem": {"pass": "HATEM2", "role": "Supervisor"},
    "Qusai": {"pass": "QUSAI4", "role": "Employee"},
}

# --- Session Init ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_role_type = None
    st.session_state.timesheet = []
    st.session_state.login_log = []

if "login_log" not in st.session_state:
    st.session_state.login_log = []

# --- Authentication ---
if not st.session_state.logged_in:
    st.markdown("<div class='top-header'><div class='company'>INTERSOFT<br>International Software Company</div><div class='greeting'>🔐 INTERSOFT Task Tracker</div></div>", unsafe_allow_html=True)
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    if st.button("Login 🚀"):
        user = USERS.get(username)
        if user and user["pass"] == password:
            st.session_state.logged_in = True
            st.session_state.user_role = username
            st.session_state.user_role_type = user["role"]
            st.session_state.login_log.append({"user": username, "time": datetime.now().strftime("%Y-%m-%d %I:%M %p")})
            st.rerun()
        else:
            st.error("❌ Invalid credentials")
    st.stop()

# (Rest of the code remains unchanged...)
