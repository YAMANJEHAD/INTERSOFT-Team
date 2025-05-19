import streamlit as st
import pandas as pd
import plotly.express as px

# بيانات وهمية لاختبار الشكل
employee_name = st.session_state.username if "username" in st.session_state else "Yaman"
login_time = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
employee_role = "Field Engineer"

# تحميل ملف الملاحظات (Excel)
st.set_page_config(layout="wide")
st.markdown(f"<h2 style='text-align:center;'>Welcome, {employee_name.title()} 👋</h2>", unsafe_allow_html=True)

# تقسيم الصفحة إلى 3 أعمدة
left, center, right = st.columns([1.5, 3, 1.5])

# --- العمود الأيسر: معلومات البروفايل ---
with left:
    st.image("https://i.pravatar.cc/150?img=3", width=120)  # صورة بروفايل وهمية
    st.markdown(f"### {employee_name.title()}")
    st.markdown(f"*Role:* {employee_role}")
    st.markdown(f"*Login:* {login_time}")
    st.markdown("---")
    if st.button("📥 Start Work"):
        st.success("🕒 Work started!")
        # سجل وقت البدء بملف attendance.csv أو قاعدة البيانات

# --- العمود الأوسط: تحليل الملاحظات ---
with center:
    st.markdown("### 📊 Notes Overview")
    uploaded_file = st.file_uploader("Upload your notes Excel", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        if 'NOTE' in df.columns:
            def classify(note):
                note = str(note).upper()
                if "TERMINAL" in note: return "TERMINAL ID"
                if "DONE" in note: return "DONE"
                if "WRONG" in note: return "WRONG DATE"
                return "OTHER"

            df["Note_Type"] = df["NOTE"].apply(classify)
            fig = px.bar(df["Note_Type"].value_counts().reset_index(),
                         x="index", y="Note_Type",
                         labels={"index": "Note Type", "Note_Type": "Count"},
                         title="Note Type Summary")
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df, use_container_width=True)
        else:
            st.warning("NOTE column is missing in the file!")

# --- العمود الأيمن: قائمة موظفين وهمية ---
with right:
    st.markdown("### 👨‍💼 Team Members")
    team = ["Yaman", "Mahmud", "Hatem", "Qusi", "Mohammad"]
    for member in team:
        st.markdown(f"- {member}")
    st.markdown("---")
    st.info("You can view other members' reports and uploaded files.")
