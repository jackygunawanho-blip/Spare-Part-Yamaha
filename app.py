import streamlit as st
import pandas as pd
import qrcode
import psycopg2
from io import BytesIO
from datetime import datetime
import urllib.parse

# --- 1. 页面基本配置 ---
st.set_page_config(page_title="Yamaha Pro Management", layout="wide", page_icon="🏍️")

# --- 2. 注入自定义 CSS (保持你原有的设计) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #111111; color: white; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #eeeeee; border-radius: 10px 10px 0px 0px;
        padding: 0px 25px; font-weight: bold; color: #555555;
    }
    .stTabs [aria-selected="true"] { background-color: #FF0000 !important; color: white !important; }
    .stButton>button {
        width: 100%; border-radius: 10px; height: 3.2em;
        background-color: #FF0000; color: white; font-weight: bold;
    }
    .service-card {
        background-color: white; padding: 20px; border-radius: 15px;
        border-left: 5px solid #FF0000; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 数据库连接函数 (替代原来的 Google Sheets) ---
def load_data_from_db():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="my_test_db",
            user="postgres",
            password="你的密码"  # <--- ⚠️ 这里填入你安装时设的密码
        )
        query = "SELECT * FROM employees ORDER BY id DESC;"
        # 使用 pandas 读取数据库数据
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"数据库连接失败: {e}")
        return pd.DataFrame(columns=["id", "name", "position", "salary", "joined_date"])

# 获取数据
df_parts = load_data_from_db()

# --- 4. 侧边栏内容 ---
st.sidebar.title("Yamaha Dashboard")
st.sidebar.markdown("Selamat datang, **Admin**")
st.sidebar.markdown("---")

# 二维码 (保持原样)
web_url = "https://your-app-url.streamlit.app/"
qr_web = qrcode.make(web_url)
buf_web = BytesIO()
qr_web.save(buf_web, format="PNG")
st.sidebar.image(buf_web, caption="Scan QR untuk buka di HP", width=150)

# --- 5. 功能标签页 ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 员工管理 (DB)", 
    "📝 注册新成员", 
    "🛠️ Service Tracker",
    "📊 业务分析"
])

# --- TAB 1: 从数据库搜索数据 ---
with tab1:
    st.header("PostgreSQL 实时员工列表")
    col_search, col_ref = st.columns([4, 1])
    with col_search:
        query = st.text_input("搜索姓名或职位:", placeholder="输入关键字...")
    with col_ref:
        st.write("##")
        if st.button("🔄 刷新数据库"):
            st.rerun()

    if not df_parts.empty:
        if query:
            # 简单的搜索过滤
            results = df_parts[df_parts.apply(lambda r: query.lower() in str(r).lower(), axis=1)]
            st.dataframe(results, use_container_width=True)
        else:
            st.dataframe(df_parts, use_container_width=True)
    else:
        st.warning("数据库中暂无数据。")

# --- TAB 2: 向数据库写入新数据 ---
with tab2:
    st.header("添加新员工到数据库")
    with st.form("db_form"):
        c1, c2 = st.columns(2)
        with c1:
            new_name = st.text_input("姓名:")
            new_pos = st.text_input("职位:")
        with c2:
            new_salary = st.number_input("工资:", min_value=0)
        
        submit_db = st.form_submit_button("保存到 PostgreSQL")
        
        if submit_db and new_name:
            try:
                # 写入数据的逻辑
                conn = psycopg2.connect(host="localhost", database="my_test_db", user="postgres", password="你的密码")
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO employees (name, position, salary) VALUES (%s, %s, %s)",
                    (new_name, new_pos, new_salary)
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"成功将 {new_name} 存入数据库！")
                st.balloons()
            except Exception as e:
                st.error(f"保存失败: {e}")

# --- TAB 3 & 4 (保持你原有的 UI 结构) ---
with tab3:
    st.header("🛠️ Service & Repair Progress")
    st.info("这里的逻辑也可以按照 TAB 2 的方式改为读取数据库。")

with tab4:
    st.header("📊 业务指标")
    m1, m2, m3 = st.columns(3)
    m1.metric("DB Records", f"{len(df_parts)} Rows", "+1")
    m2.metric("Status", "Local DB Active")
    st.bar_chart(df_parts, x="name", y="salary", color="#FF0000")
