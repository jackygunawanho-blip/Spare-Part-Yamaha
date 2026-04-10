import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime
import urllib.parse

# --- 1. 页面基本配置 ---
st.set_page_config(page_title="Yamaha Pro Management", layout="wide", page_icon="🏍️")

# --- 2. 注入自定义 CSS (专业黑红配色) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #f8f9fa; }

    /* 侧边栏美化 */
    [data-testid="stSidebar"] { background-color: #111111; color: white; }
    
    /* 标签页 (Tabs) 样式增强 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #eeeeee;
        border-radius: 10px 10px 0px 0px;
        padding: 0px 25px;
        font-weight: bold;
        color: #555555;
        transition: 0.3s;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF0000 !important;
        color: white !important;
    }

    /* 统一按钮样式 */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.2em;
        background-color: #FF0000;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #CC0000;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(255,0,0,0.3);
    }

    /* 维修状态卡片样式 */
    .service-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #FF0000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 侧边栏内容 ---
st.sidebar.title("Yamaha Dashboard")
st.sidebar.markdown("Selamat datang, **Admin**")
st.sidebar.markdown("---")

# 二维码快速访问
web_url = "https://spare-part-yamaha-cb786rte8wk8pse3ern2bm.streamlit.app/"
qr_web = qrcode.make(web_url)
buf_web = BytesIO()
qr_web.save(buf_web, format="PNG")
st.sidebar.image(buf_web, caption="Scan QR untuk buka di HP", width=150)

st.sidebar.markdown("---")
# 模拟库存预警展示
st.sidebar.subheader("⚠️ Stok Menipis")
st.sidebar.error("B6H-E2170-00 (Sisa 2)")
st.sidebar.warning("2DP-E4411-00 (Sisa 4)")

# --- 4. 云端数据连接 ---
SHEET_ID = "1fCYY5SdPLEfc3tyJx9kWBVYSsNkkz3RGlzYTr9pr8hQ"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

@st.cache_data(ttl=300)
def load_data():
    try:
        return pd.read_excel(GOOGLE_SHEET_URL)
    except:
        return None

df_parts = load_data()

# --- 5. 定义 4 个功能标签页 ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Cari Part", 
    "📝 Konsumen", 
    "🛠️ Service Tracker",
    "📊 Analitik"
])

# --- TAB 1: 零件查询 ---
with tab1:
    st.header("Database Sparepart Yamaha")
    col_search, col_ref = st.columns([4, 1])
    with col_search:
        query = st.text_input("Input Nama atau Kode Part:", placeholder="Cari...")
    with col_ref:
        st.write("##")
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    if df_parts is not None and query:
        results = df_parts[df_parts.apply(lambda r: query.lower() in str(r).lower(), axis=1)]
        if not results.empty:
            st.dataframe(results, use_container_width=True)
            # 详情展示
            it = results.iloc[0]
            st.info(f"**Item Teratas:** {it.iloc[3]} | **Harga:** Rp {it.iloc[5]}")
        else:
            st.warning("Data tidak ditemukan.")

# --- TAB 2: 客户登记 ---
with tab2:
    st.header("Registrasi Konsumen Baru")
    with st.form("cust_form"):
        c1, c2 = st.columns(2)
        with c1:
            nama = st.text_input("Nama:")
            wa = st.text_input("WhatsApp:")
        with c2:
            motor = st.text_input("Tipe Motor:")
            plat = st.text_input("No Plat:")
        
        note = st.text_area("Catatan:")
        sub = st.form_submit_button("Simpan Data")
        
        if sub:
            st.success(f"Data {nama} Berhasil Tersimpan!")
            st.balloons()

# --- TAB 3: 维修工单追踪 ---
with tab3:
    st.header("🛠️ Service & Repair Progress")
    
    # 顶部状态统计
    s1, s2, s3 = st.columns(3)
    s1.metric("Dalam Antrian", "5 Unit")
    s2.metric("Sedang Dikerjakan", "3 Unit", delta="Aktif", delta_color="normal")
    s3.metric("Selesai Hari Ini", "12 Unit")

    st.markdown("---")
    
    # 输入新工单
    with st.expander("➕ Tambah Antrian Service Baru"):
        with st.form("service_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                s_plat = st.text_input("Plat Nomor:")
                s_issue = st.text_input("Keluhan Utama:")
            with col_b:
                s_mech = st.selectbox("Pilih Mekanik:", ["Agus", "Budi", "Samsul"])
                s_stat = st.selectbox("Status Awal:", ["Antrian", "Pengerjaan"])
            if st.form_submit_button("Daftarkan Service"):
                st.toast(f"Motor {s_plat} telah masuk ke daftar {s_stat}")

    # 模拟当前的维修看板
    st.subheader("Papan Monitor Bengkel")
    col_list = st.columns(2)
    
    with col_list[0]:
        st.markdown("""
        <div class="service-card">
            <h4>DD 4455 AB (NMAX)</h4>
            <p>🔧 <b>Mekanik:</b> Agus<br>
            📝 <b>Keluhan:</b> Ganti Oli & CVT<br>
            ⏳ <b>Status:</b> <span style='color:orange'>Pengerjaan</span></p>
        </div>
        """, unsafe_allow_html=True)

    with col_list[1]:
        st.markdown("""
        <div class="service-card" style="border-left-color: green;">
            <h4>DD 1234 XX (AEROX)</h4>
            <p>🔧 <b>Mekanik:</b> Samsul<br>
            📝 <b>Keluhan:</b> Kelistrikan<br>
            ⏳ <b>Status:</b> <span style='color:green'>Selesai (Siap Ambil)</span></p>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 4: 销售分析 ---
with tab4:
    st.header("Visualisasi Performa Toko")
    m1, m2, m3 = st.columns(3)
    m1.metric("Revenue (Est)", "Rp 45.2M", "+12%")
    m2.metric("Target", "75%", "On Track")
    m3.metric("Part Terlaris", "Oli Yamalube")
    
    chart_data = pd.DataFrame({
        'Leasing': ['ADR', 'BUF', 'MDL', 'Cash'],
        'Jumlah': [45, 30, 20, 35]
    })
    st.bar_chart(data=chart_data, x='Leasing', y='Jumlah', color="#FF0000")
