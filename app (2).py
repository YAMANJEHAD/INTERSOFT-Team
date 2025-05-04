# الكود الأصلي من دون تعديل كما هو ...

# 🆕 الميزات الجديدة بعد الكود الأصلي

import os
import json
import uuid

HISTORY_FILE = "upload_history.json"

# Load history
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        upload_history = json.load(f)
else:
    upload_history = []

st.markdown("---")
st.header("📂 File Upload History")

# Input uploader name and date before uploading
with st.form("upload_form"):
    uploader_name = st.text_input("Enter your name", "")
    upload_date = st.date_input("Select upload date", datetime.today())
    submitted = st.form_submit_button("Submit Info")

if submitted and not uploader_name:
    st.warning("Please enter your name before uploading a file.")
    st.stop()

# Save upload log after successful file upload
if uploaded_file and uploader_name:
    file_id = str(uuid.uuid4())  # unique identifier for the file
    filename = uploaded_file.name
    log_entry = {
        "id": file_id,
        "filename": filename,
        "uploader": uploader_name,
        "date": str(upload_date)
    }
    if not any(item["filename"] == filename for item in upload_history):
        upload_history.append(log_entry)
        with open(HISTORY_FILE, "w") as f:
            json.dump(upload_history, f)

# Show history table
if upload_history:
    st.subheader("📝 Uploaded Files")
    df_history = pd.DataFrame(upload_history)
    selected_row = st.radio("Select a file", df_history["filename"])

    st.dataframe(df_history)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🧾 Preview File"):
            try:
                df_selected = pd.read_excel(selected_row)
                st.dataframe(df_selected.head())
            except Exception as e:
                st.error(f"Could not open file: {e}")

    with col2:
        if st.button("❌ Delete File"):
            upload_history = [entry for entry in upload_history if entry["filename"] != selected_row]
            try:
                os.remove(selected_row)
            except FileNotFoundError:
                pass
            with open(HISTORY_FILE, "w") as f:
                json.dump(upload_history, f)
            st.success(f"File '{selected_row}' deleted successfully.")
            st.experimental_rerun()
