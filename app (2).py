import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components

# Page setup
st.set_page_config(page_title="Note Analyzer", layout="wide")

# Clock
clock_html = """
<style>
.clock-container {
    font-family: 'Courier New', monospace;
    font-size: 24px;
    color: #ffffff;
    background: linear-gradient(90deg, #f39c12, #e67e22);
    padding: 10px 20px;
    border-radius: 12px;
    width: fit-content;
    animation: pulse 2s infinite;
    margin-bottom: 20px;
    position: absolute;
    top: 10px;
    right: 10px;
    z-index: 9999;
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(243, 156, 18, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(243, 156, 18, 0); }
    100% { box-shadow: 0 0 0 0 rgba(243, 156, 18, 0); }
}
</style>
<div class="clock-container">
    <span id="clock"></span>
</div>
<script>
function updateClock() {
    const now = new Date();
    document.getElementById('clock').innerText = now.toLocaleTimeString();
}
setInterval(updateClock, 1000);
updateClock();
</script>
"""
components.html(clock_html, height=100)

# Title
st.title("📊 INTERSOFT Analyzer")

# Upload Excel
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

# Default known cases
default_known_cases = [
    "TERMINAL ID - WRONG DATE",
    "NO IMAGE FOR THE DEVICE",
    "WRONG DATE",
    "TERMINAL ID",
    "NO J.O",
    "DONE",
    "NO RETAILERS SIGNATURE",
    "UNCLEAR IMAGE",
    "NO ENGINEER SIGNATURE",
    "NO SIGNATURE",
    "PENDING",
    "NO INFORMATIONS",
    "MISSING INFORMATION",
    "NOT ACTIVE"
]

# Editable known cases
st.subheader("✏️ Edit Known Note Types Before Analysis")
known_cases_df = pd.DataFrame(default_known_cases, columns=["Known_Cases"])
edited_cases_df = st.data_editor(known_cases_df, num_rows="dynamic", use_container_width=True)
known_cases = edited_cases_df["Known_Cases"].dropna().str.strip().str.upper().tolist()

# Note classification
def classify_note(note):
    note = str(note).strip().upper()
    for case in known_cases:
        if case in note:
            return case
    return "OTHERS"

# File processing
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name=None)
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")

    if isinstance(df, dict):
        sheet_names = list(df.keys())
        df = df[sheet_names[0]]

    df.columns = [col.upper() for col in df.columns]
    note_columns = [col for col in df.columns if 'NOTE' in col]

    if not note_columns:
        st.error("No 'NOTE' column found.")
    else:
        note_column = note_columns[0]
        df['Note_Type'] = df[note_column].apply(classify_note)

        # Separate out the "OTHERS" rows (ملاحظات غير معروفة)
        others_df = df[df['Note_Type'] == "OTHERS"].copy()  # تحديد الملاحظات غير المعروفة
        
        # Display the "OTHERS" notes in a styled table
        if not others_df.empty:
            st.subheader("🚨 Unknown Notes (OTHERS)")
            st.markdown("""
            <style>
            .unknown-notes {
                background-color: #fff3cd;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
                border-left: 5px solid #ffc107;
            }
            </style>
            <div class="unknown-notes">
                <h4 style='color: #856404;'>The following notes were not recognized and classified as 'OTHERS':</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # عرض الجدول مع خيارات التصفية
            cols_to_display = [note_column, 'Note_Type'] + [col for col in others_df.columns if col not in [note_column, 'Note_Type']]
            st.dataframe(
                others_df[cols_to_display],
                use_container_width=True,
                height=400,
                column_config={
                    note_column: st.column_config.TextColumn(
                        "Original Note",
                        help="The original note text that wasn't recognized"
                    ),
                    'Note_Type': st.column_config.TextColumn(
                        "Classification",
                        help="Automatically classified as 'OTHERS'"
                    )
                }
            )
            
            # إضافة إحصائية بعدد الملاحظات غير المعروفة
            st.markdown(f"""
            <div style="background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin: 10px 0;">
                <strong>Total Unknown Notes:</strong> {len(others_df)} ({(len(others_df)/len(df)*100):.1f}% of total notes)
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("🎉 All notes were successfully classified! No unknown notes found.")

        # باقي التحليلات...
        st.subheader("📈 Notes per Technician")
        if 'TECHNICIAN_NAME' in df.columns:
            tech_counts = df.groupby('TECHNICIAN_NAME')['Note_Type'].count().sort_values(ascending=False)
            st.bar_chart(tech_counts)

        st.subheader("📊 Notes by Type")
        note_counts = df['Note_Type'].value_counts()
        st.bar_chart(note_counts)

        # Excel export
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name="All Data", index=False)
            if not others_df.empty:
                others_df.to_excel(writer, sheet_name="Unknown Notes", index=False)
            note_counts.to_excel(writer, sheet_name="Note Counts")

        st.download_button("📥 Download Analysis Results", output.getvalue(), "note_analysis.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
