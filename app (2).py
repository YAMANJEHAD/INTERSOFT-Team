import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
from datetime import datetime
import numpy as np

# إعداد الصفحة
st.set_page_config(page_title="FLM Smart Dashboard", layout="wide")
st.title("🧠 FLM Intelligent POS Dashboard")

# تحميل البيانات الفعلية
@st.cache_data
def load_data():
    df = pd.read_csv("processed_flm_data.csv", parse_dates=["Ticket_Create_Date", "Closed_Date"])
    df["duration_minutes"] = (df["Closed_Date"] - df["Ticket_Create_Date"]).dt.total_seconds() // 60
    return df

df = load_data()

# قائمة التنقل الجانبية
page = st.sidebar.selectbox("📁 اختر صفحة", [
    "لوحة التحكم العامة",
    "تقييم الفنيين",
    "خريطة الأعطال",
    "تحليل الأعطال والملاحظات",
    "تحليل أوقات الذروة",
    "تنبيهات ذكية",
    "تنبؤ الأعطال (قريبًا)",
    "تصدير التقارير"
])

if page == "لوحة التحكم العامة":
    st.subheader("📊 نظرة عامة على الأعطال")
    col1, col2, col3 = st.columns(3)
    col1.metric("عدد التذاكر", len(df))
    col2.metric("متوسط مدة الإنجاز (دقيقة)", round(df["duration_minutes"].mean(), 1))
    col3.metric("نسبة المرفوض", f"{(df[df['decision'] == 'rejected'].shape[0]/len(df))*100:.1f}%")

    st.plotly_chart(px.histogram(df, x="Technician_Name", color="decision", barmode="group",
                                  title="توزيع التذاكر حسب الفني"))

elif page == "تقييم الفنيين":
    st.subheader("🧑‍🔧 تقييم أداء الفنيين")
    summary = df.groupby("Technician_Name").agg(
        total_tickets=("Ticket_Id", "count"),
        approved_tickets=("decision", lambda x: (x == "approved").sum()),
        rejected_tickets=("decision", lambda x: (x == "rejected").sum()),
        avg_duration=("duration_minutes", "mean")
    ).reset_index()

    summary["approval_rate"] = round(summary["approved_tickets"] / summary["total_tickets"] * 100, 1)
    summary["norm_duration"] = 1 - (summary["avg_duration"] / summary["avg_duration"].max())
    summary["final_score"] = round(
        (summary["approval_rate"] * 0.6) + (summary["norm_duration"] * 100 * 0.4), 2
    )

    st.dataframe(summary)
    st.plotly_chart(px.bar(summary, x="Technician_Name", y="final_score", title="🏅 التقييم النهائي للفنيين"))

elif page == "خريطة الأعطال":
    st.subheader("📍 عرض الأعطال على الخريطة")
    df["lat"] = np.random.uniform(24.5, 26.5, size=len(df))
    df["lon"] = np.random.uniform(50.0, 52.0, size=len(df))
    m = folium.Map(location=[25.3, 51.5], zoom_start=6)
    for i, row in df.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=f"{row['Technician_Name']} | {row['decision']}",
            tooltip=row["Ticket_Id"]
        ).add_to(m)
    folium_static(m)

elif page == "تحليل الأعطال والملاحظات":
    st.subheader("🛠️ تحليل أنواع الملاحظات")
    top_notes = df["NOTE"].value_counts().reset_index()
    top_notes.columns = ["Note", "Count"]
    st.write("📌 أكثر الملاحظات تكرارًا:")
    st.dataframe(top_notes.head(10))
    st.plotly_chart(px.bar(top_notes.head(10), x="Note", y="Count", title="الملاحظات الأكثر شيوعًا"))

elif page == "تحليل أوقات الذروة":
    st.subheader("🕒 تحليل ساعات الذروة")
    df["hour"] = df["Ticket_Create_Date"].dt.hour
    st.plotly_chart(px.histogram(df, x="hour", nbins=24, title="عدد التذاكر حسب الساعة"))

elif page == "تنبيهات ذكية":
    st.subheader("⚠️ التنبيهات الذكية")
    alert_df = df.groupby(["Technician_Name", df["Ticket_Create_Date"].dt.date]).size().reset_index(name="count")
    alerts = alert_df[alert_df["count"] > 3]
    if not alerts.empty:
        st.warning("تم الكشف عن عدد تذاكر مرتفع لفنيين معينين:")
        st.dataframe(alerts)
    else:
        st.success("لا توجد تنبيهات حالياً")

elif page == "تنبؤ الأعطال (قريبًا)":
    st.subheader("🤖 التنبؤ بالأعطال")
    st.info("هذه الميزة تحت التطوير، سيتم إطلاقها قريبًا.")

elif page == "تصدير التقارير":
    st.subheader("📥 تحميل تقرير PDF")
    st.info("سيتم قريبًا إضافة خيار تصدير التقرير الكامل بصيغة PDF تلقائيًا.")
