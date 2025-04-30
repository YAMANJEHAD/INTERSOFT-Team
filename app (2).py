import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime
import uuid

st.set_page_config(page_title="Note Analyzer", layout="wide")
st.title("📊 INTERSOFT Analyzer")

# Ensure uploads folder exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")

logs_file = "logs.csv"
if not os.path.exists(logs_file):
    pd.DataFrame(columns=["username", "action", "timestamp", "filename", "saved_path"]).to_csv(logs_file, index=False)

# --- USERNAME INPUT AT TOP ---
st.markdown("""
    <div style='text-align: center;'>
        <h3>👤 Enter your name to start</h3>
    </div>
""", unsafe_allow_html=True)
username = st.text_input("Your Name:", key="user_input")

uploaded_file = st.file_uploader("📤 Upload Excel File", type=["xlsx"])

required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

def classify_note(note):
    note = str(note).strip().upper()
    if "TERMINAL ID - WRONG DATE" in note:
        return "TERMINAL ID - WRONG DATE"
    elif "NO IMAGE FOR THE DEVICE" in note:
        return "NO IMAGE FOR THE DEVICE"
    elif "WRONG DATE" in note:
        return "WRONG DATE"
    elif "TERMINAL ID" in note:
        return "TERMINAL ID"
    elif "NO J.O" in note:
        return "NO J.O"
    elif "DONE" in note:
        return "DONE"
    elif "NO RETAILERS SIGNATURE" in note:
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
    else:
        return "MISSING INFORMATION"

if uploaded_file and username.strip():
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet2")
    except:
        df = pd.read_excel(uploaded_file)

    if not all(col in df.columns for col in required_cols):
        st.error(f"Missing required columns. Available: {list(df.columns)}")
    else:
        df['Note_Type'] = df['NOTE'].apply(classify_note)
        df = df[~df['Note_Type'].isin(['DONE', 'NO J.O'])]
        st.success("✅ File processed successfully!")

        # Save uploaded file
        unique_filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
        saved_path = os.path.join("uploads", unique_filename)
        with open(saved_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Save log
        log_entry = pd.DataFrame([{
            "username": username,
            "action": "Uploaded and analyzed file",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filename": uploaded_file.name,
            "saved_path": saved_path
        }])
        log_entry.to_csv(logs_file, mode='a', header=False, index=False)

        # Charts
        st.subheader("📈 Notes per Technician")
        tech_counts = df.groupby('Technician_Name')['Note_Type'].count().sort_values(ascending=False)
        st.bar_chart(tech_counts)

        st.subheader("📊 Notes by Type")
        note_counts = df['Note_Type'].value_counts()
        st.bar_chart(note_counts)

        st.subheader("📋 All Notes")
        st.dataframe(df[['Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type']])

        st.subheader("📑 Notes per Technician by Type")
        tech_note_group = df.groupby(['Technician_Name', 'Note_Type']).size().reset_index(name='Count')
        st.dataframe(tech_note_group)

        # Export Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for note_type in df['Note_Type'].unique():
                subset = df[df['Note_Type'] == note_type]
                subset[['Terminal_Id', 'Technician_Name', 'Note_Type', 'Ticket_Type']].to_excel(writer, sheet_name=note_type[:31], index=False)
            note_counts.reset_index().rename(columns={'index': 'Note_Type', 'Note_Type': 'Count'}).to_excel(writer, sheet_name="Note Type Count", index=False)
            tech_note_group.to_excel(writer, sheet_name="Technician Notes Count", index=False)
        st.download_button("📥 Download Summary Excel", output.getvalue(), "summary.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- View Logs ---
if st.sidebar.checkbox("📚 View Upload History"):
    st.sidebar.subheader("📁 Uploaded Files Log")
    logs_df = pd.read_csv(logs_file)
    st.write("### 📜 Upload Log History")
    st.dataframe(logs_df)

    for idx, row in logs_df.iterrows():
        st.markdown(f"**🧍‍♂️ {row['username']}** | 🕒 {row['timestamp']} | 📄 {row['filename']}")
        if os.path.exists(row['saved_path']):
            with open(row['saved_path'], "rb") as f:
                st.download_button(
                    label=f"⬇️ Download {row['filename']}",
                    data=f,
                    file_name=row['filename'],
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    key=f"download_{idx}"
                )
        else:
            st.warning("File not found on server.")
