import streamlit as st
import pandas as pd
import io
import plotly.express as px
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import os
import hashlib
import re
from PIL import Image, ImageDraw, ImageFont

# تهيئة الصفحة
st.set_page_config(
    page_title="INTERSOFT Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== وظائف مساعدة ==========

def create_default_logo():
    """إنشاء شعار افتراضي إذا لم يوجد ملف الصورة"""
    img = Image.new('RGB', (100, 100), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    d.text((10,10), "LOGO", fill=(255,255,0), font=font)
    return img

def load_logo():
    """تحميل شعار التطبيق"""
    try:
        return Image.open("logo.png")
    except:
        return create_default_logo()

def set_dark_mode():
    """تفعيل الوضع الليلي"""
    st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E1E;
        color: white;
    }
    .sidebar .sidebar-content {
        background-color: #2E2E2E;
    }
    .widget-label, .st-bb, .st-at, .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

def normalize(text):
    """توحيد تنسيق النص"""
    text = str(text).upper()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def classify_note(note):
    """تصنيف الملاحظات"""
    note = normalize(note)
    patterns = {
        "TERMINAL ID - WRONG DATE": ["TERMINAL ID WRONG DATE"],
        "NO IMAGE FOR THE DEVICE": ["NO IMAGE FOR THE DEVICE"],
        "IMAGE FOR THE DEVICE ONLY": ["IMAGE FOR THE DEVICE ONLY"],
        "WRONG DATE": ["WRONG DATE"],
        "TERMINAL ID": ["TERMINAL ID"],
        "NO J.O": ["NO JO", "NO J O"],
        "DONE": ["DONE"],
        "NO RETAILERS SIGNATURE": ["NO RETAILERS SIGNATURE", "NO RETAILER SIGNATURE"],
        "UNCLEAR IMAGE": ["UNCLEAR IMAGE"],
        "NO ENGINEER SIGNATURE": ["NO ENGINEER SIGNATURE"],
        "NO SIGNATURE": ["NO SIGNATURE","NO SIGNATURES"],
        "PENDING": ["PENDING"],
        "NO INFORMATIONS": ["NO INFORMATION", "NO INFORMATIONS"],
        "MISSING INFORMATION": ["MISSING INFORMATION"],
        "NO BILL": ["NO BILL"],
        "NOT ACTIVE": ["NOT ACTIVE"],
        "NO RECEIPT": ["NO RECEIPT"],
        "ANOTHER TERMINAL RECEIPT": ["ANOTHER TERMINAL RECEIPT"],
        "UNCLEAR RECEIPT": ["UNCLEAR RECEIPT"],
        "WRONG RECEIPT": ["WRONG RECEIPT"],
        "REJECTED RECEIPT": ["REJECTED RECEIPT"],
        "MULTIPLE ISSUES":["MULTIPLE ISSUES"]
    }
    if "+" in note: return "MULTIPLE ISSUES"
    matched_labels = []
    for label, keywords in patterns.items():
        if any(keyword in note for keyword in keywords):
            matched_labels.append(label)
    return matched_labels[0] if matched_labels else "MISSING INFORMATION"

def problem_severity(note_type):
    """تحديد خطورة المشكلة"""
    severity_map = {
        "Critical": ["WRONG DATE", "TERMINAL ID - WRONG DATE", "REJECTED RECEIPT"],
        "High": ["NO IMAGE", "UNCLEAR IMAGE", "NO RECEIPT"],
        "Medium": ["NO SIGNATURE", "NO ENGINEER SIGNATURE"],
        "Low": ["NO J.O", "PENDING"]
    }
    for severity, types in severity_map.items():
        if note_type in types: return severity
    return "Unclassified"

def suggest_solutions(note_type):
    """اقتراح حلول للمشاكل"""
    solutions = {
        "WRONG DATE": "تحقق من تاريخ الجهاز ومزامنته مع الخادم",
        "TERMINAL ID - WRONG DATE": "تحقق من رقم الجهاز وإعدادات التاريخ",
        "NO IMAGE FOR THE DEVICE": "التقاط صورة للجهاز ورفعها",
        "NO RETAILERS SIGNATURE": "تأكد من توقيع التاجر على النموذج",
        "NO ENGINEER SIGNATURE": "يجب على المهندس التوقيع قبل التسليم",
        "NO SIGNATURE": "التقاط التوقيعات المطلوبة من جميع الأطراف",
        "UNCLEAR IMAGE": "إعادة التقاط الصورة بإضاءة أفضل",
        "NOT ACTIVE": "تحقق من عملية التفعيل وحاول مرة أخرى",
        "NO BILL": "إرفاق فاتورة صالحة",
        "NO RECEIPT": "رفع صورة واضحة لإيصال المعاملة",
        "ANOTHER TERMINAL RECEIPT": "تأكد من رفع إيصال الجهاز الصحيح",
        "WRONG RECEIPT": "تحقق ورفع الإيصال الصحيح",
        "REJECTED RECEIPT": "متابعة سبب الرفض وتصحيحه",
        "MULTIPLE ISSUES": "حل جميع المشاكل المذكورة وتحديث الملاحظة",
        "NO J.O": "توفير رقم أو تفاصيل أمر العمل",
        "PENDING": "إكمال وإتمام المهمة المعلقة",
        "MISSING INFORMATION": "مراجعة الملاحظة وتوفير التفاصيل الكاملة",
    }
    return solutions.get(note_type, "لا يوجد حل متاح")

# ========== واجهة المستخدم ==========

# شريط الأدوات الجانبي
with st.sidebar:
    st.title("الإعدادات")
    dark_mode = st.checkbox('🌙 الوضع الليلي')
    if dark_mode: set_dark_mode()

# رأس الصفحة
col1, col2 = st.columns([1, 4])
with col1:
    try:
        logo = load_logo()
        st.image(logo, width=80)
    except:
        st.markdown("### 🏢")
with col2:
    st.markdown("<h1 style='color:#ffffff; margin-top:15px;'>📊 نظام تحليل إنترسوفت</h1>", unsafe_allow_html=True)

# ساعة رقمية
components.html("""
<div style="text-align:right; font-family:monospace; font-size:20px; margin-bottom:20px;">
    <div id="datetime"></div>
</div>
<script>
function updateTime() {
    const now = new Date();
    document.getElementById("datetime").innerHTML = 
        now.toLocaleDateString('ar-EG') + " | " + now.toLocaleTimeString('ar-EG');
}
setInterval(updateTime, 1000);
updateTime();
</script>
""", height=50)

# ========== قسم التذاكر المعلقة ==========
st.markdown("## 📌 تحليل التذاكر المعلقة")

with st.expander("🧮 تصفية التذاكر غير المكتملة حسب رقم التذكرة", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        all_file = st.file_uploader("🔄 رفع ملف كل التذاكر", type=["xlsx"])
    with col2:
        done_file = st.file_uploader("✅ رفع ملف التذاكر المكتملة", type=["xlsx"])

    if all_file and done_file:
        try:
            all_df = pd.read_excel(all_file)
            done_df = pd.read_excel(done_file)

            if 'Ticket_ID' not in all_df.columns or 'Ticket_ID' not in done_df.columns:
                st.error("❌ يجب أن يحتوي الملفان على عمود 'Ticket_ID'")
            else:
                # إزالة التكرارات
                all_df = all_df.drop_duplicates(subset=['Ticket_ID'], keep='first')
                done_df = done_df.drop_duplicates(subset=['Ticket_ID'], keep='first')
                
                pending_df = all_df[~all_df['Ticket_ID'].isin(done_df['Ticket_ID'])]
                
                # مؤشرات الأداء
                st.markdown("### 📊 مقاييس الأداء")
                cols = st.columns(4)
                with cols[0]:
                    st.metric("إجمالي التذاكر", len(all_df))
                with cols[1]:
                    st.metric("المكتملة", len(done_df))
                with cols[2]:
                    st.metric("المعلقة", len(pending_df))
                with cols[3]:
                    percent = (len(pending_df)/len(all_df))*100 if len(all_df)>0 else 0
                    st.metric("النسبة المعلقة", f"{percent:.1f}%")

                # الفلترة
                st.markdown("### 🔍 تصفية النتائج")
                filter_cols = st.columns(3)
                filters = {}
                
                if 'Date' in pending_df.columns:
                    with filter_cols[0]:
                        date_options = ["كل الفترات", "أسبوع", "شهر"]
                        date_sel = st.selectbox("الفترة الزمنية", date_options)
                        if date_sel == "أسبوع":
                            pending_df = pending_df[pending_df['Date'] >= (datetime.now() - timedelta(days=7))]
                        elif date_sel == "شهر":
                            pending_df = pending_df[pending_df['Date'] >= (datetime.now() - timedelta(days=30))]
                
                if 'Technician_Name' in pending_df.columns:
                    with filter_cols[1]:
                        techs = st.multiselect("الفني", pending_df['Technician_Name'].unique())
                        if techs:
                            pending_df = pending_df[pending_df['Technician_Name'].isin(techs)]
                
                if 'Ticket_Type' in pending_df.columns:
                    with filter_cols[2]:
                        types = st.multiselect("نوع التذكرة", pending_df['Ticket_Type'].unique())
                        if types:
                            pending_df = pending_df[pending_df['Ticket_Type'].isin(types)]
                
                # عرض النتائج
                st.dataframe(pending_df, use_container_width=True)
                
                # خيارات التصدير
                st.download_button(
                    "📥 تحميل التذاكر المعلقة (Excel)",
                    pending_df.to_excel(index=False),
                    "pending_tickets.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"❌ خطأ في معالجة الملفات: {str(e)}")

# ========== التحليل الرئيسي ==========
st.markdown("## 📊 لوحة التحليل الشاملة")

uploaded_file = st.file_uploader("📁 رفع ملف البيانات للتحليل", type=["xlsx"])
required_cols = ['NOTE', 'Terminal_Id', 'Technician_Name', 'Ticket_Type']

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        
        if not all(col in df.columns for col in required_cols):
            st.error(f"❌ الأعمدة المطلوبة غير موجودة. الأعمدة المتاحة: {list(df.columns)}")
        else:
            # تنظيف البيانات
            if 'Ticket_ID' in df.columns:
                df = df.drop_duplicates(subset=['Ticket_ID'], keep='first')
            
            df['Note_Type'] = df['NOTE'].apply(classify_note)
            df['Problem_Severity'] = df['Note_Type'].apply(problem_severity)
            df['Suggested_Solution'] = df['Note_Type'].apply(suggest_solutions)
            
            # ألوان مستوى الخطورة
            severity_colors = {
                "Critical": "#FF0000",  # أحمر
                "High": "#FFA500",      # برتقالي
                "Medium": "#FFFF00",    # أصفر
                "Low": "#00FF00",       # أخضر
                "Unclassified": "#808080" # رمادي
            }
            
            # مؤشرات الأداء
            st.markdown("### 📈 نظرة عامة على الأداء")
            kpi_cols = st.columns(4)
            
            with kpi_cols[0]:
                st.metric("إجمالي التذاكر", len(df))
            with kpi_cols[1]:
                done = len(df[df['Note_Type'] == 'DONE'])
                st.metric("المكتملة", done)
            with kpi_cols[2]:
                critical = len(df[df['Problem_Severity'] == 'Critical'])
                st.metric("مشاكل حرجة", critical)
            with kpi_cols[3]:
                st.metric("متوسط وقت الحل", "3 أيام")  # يمكن استبدالها بحساب حقيقي
            
            # التصورات البيانية
            st.markdown("### 📊 التصورات البيانية")
            
            # رسم بياني للأنواع
            fig1 = px.pie(
                df['Note_Type'].value_counts().reset_index(),
                names='Note_Type',
                values='count',
                title="توزيع أنواع الملاحظات"
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # رسم بياني لمستوى الخطورة
            severity_df = df['Problem_Severity'].value_counts().reset_index()
            fig2 = px.bar(
                severity_df,
                x='Problem_Severity',
                y='count',
                color='Problem_Severity',
                color_discrete_map=severity_colors,
                title="توزيع المشاكل حسب مستوى الخطورة"
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # تحليل الفنيين
            st.markdown("### 👨‍🔧 تحليل أداء الفنيين")
            
            tech_df = df.groupby('Technician_Name').agg({
                'Ticket_Type': 'count',
                'Problem_Severity': lambda x: (x == 'Critical').sum()
            }).rename(columns={
                'Ticket_Type': 'Total_Tickets',
                'Problem_Severity': 'Critical_Issues'
            }).sort_values('Total_Tickets', ascending=False)
            
            st.dataframe(tech_df, use_container_width=True)
            
            # تصدير التقرير النهائي
            st.markdown("### 📤 تصدير النتائج")
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name="البيانات الكاملة", index=False)
                tech_df.to_excel(writer, sheet_name="أداء الفنيين", index=True)
            
            st.download_button(
                "📥 تحميل التقرير الكامل",
                output.getvalue(),
                "full_report.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء معالجة الملف: {str(e)}")

# تذييل الصفحة
st.markdown("""
<div style="text-align:center; margin-top:50px; padding:20px; background:#f0f2f6;">
    <p>نظام تحليل إنترسوفت - الإصدار 1.0</p>
    <p>© 2023 جميع الحقوق محفوظة</p>
</div>
""", unsafe_allow_html=True)
