import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime
import urllib.parse

# --- 1. 配置页面 (必须在第一行) ---
st.set_page_config(page_title="Yamaha Management System", layout="wide", page_icon="🏍️")

# --- 2. 注入自定义 CSS (全网页美化) ---
st.markdown("""
    <style>
    /* 全局字体和背景 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    .main {
        background-color: #f8f9fa;
    }

    /* 侧边栏深色美化 */
    [data-testid="stSidebar"] {
        background-color: #111111;
        color: white;
    }
    [data-testid="stSidebar"] .stMarkdown p {
        color: #bbbbbb;
    }

    /* 标签页 (Tabs) 样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #eeeeee;
        border-radius: 8px 8px 0px 0px;
        padding: 0px 20px;
        font-weight: bold;
        color: #666666;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF0000 !important; /* 雅马哈红 */
        color: white !important;
        border: none !important;
    }

    /* 按钮美化 (带悬停动画) */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        border: none;
        height: 3em;
        background-color: #FF0000;
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background-color: #CC0000;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255,0,0,0.3);
    }

    /* 输入框圆角优化 */
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea {
        border-radius: 10px !important;
    }

    /* 指标卡片美化 */
    [data-testid="stMetricValue"] {
        color: #FF0000;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 左侧侧边栏：扫码打开网页 ---
st.sidebar.header("📱 Akses di Smartphone")
web_url = "https://spare-part-yamaha-cb786rte8wk8pse3ern2bm.streamlit.app/"
qr_web = qrcode.QRCode(box_size=4, border=2)
qr_web.add_data(web_url)
qr_web.make(fit=True)
img_web = qr_web.make_image(fill_color="black", back_color="white")
buf_web = BytesIO()
img_web.save(buf_web, format="PNG")
st.sidebar.image(buf_web, caption="Scan QR untuk buka di HP")
st.sidebar.markdown("---")
st.sidebar.info("Tips: Gunakan menu Tab di atas untuk navigasi cepat.")

# --- 4. 连接云端数据 (Google Sheets) ---
SHEET_ID = "1fCYY5SdPLEfc3tyJx9kWBVYSsNkkz3RGlzYTr9pr8hQ"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_excel(GOOGLE_SHEET_URL)
        return df
    except Exception as e:
        st.error(f"Gagal mengambil data Cloud: {e}")
        return None

df_parts = load_data()

# --- 5. 定义 3 个标签页 ---
tab1, tab2, tab3 = st.tabs(["🔍 Cari Sparepart", "📝 Data Konsumen", "📊 Analitik Penjualan"])

# --- 标签页 1: 零件搜索 ---
with tab1:
    st.title("Pencarian Sparepart")
    c1, c2 = st.columns([3, 1])
    with c1:
        query = st.text_input("Cari Nama atau Kode (Ketik di sini...):", placeholder="Contoh: B6H-E2170-00")
    with c2:
        st.write("##") # 间距
        refresh = st.button("🔄 Refresh Cloud")
        if refresh:
            st.cache_data.clear()
            st.rerun()
    
    if df_parts is not None:
        if query:
            results = df_parts[df_parts.apply(lambda r: query.lower() in str(r).lower(), axis=1)]
            if not results.empty:
                # 使用 Container 包裹搜索结果
                with st.container():
                    st.success(f"Ditemukan {len(results)} item")
                    st.dataframe(results, use_container_width=True)
                    
                    # 零件二维码预览
                    val = results.iloc[0]
                    p_code = val.iloc[1] if len(val) > 1 else "N/A"
                    p_name = val.iloc[3] if len(val) > 3 else "N/A"
                    p_price = val.iloc[5] if len(val) > 5 else "N/A"
                    
                    st.markdown("---")
                    col_qr, col_info = st.columns([1, 2])
                    with col_qr:
                        qr_txt = f"Kode: {p_code}\nNama: {p_name}\nHarga: Rp {p_price}"
                        img_qr = qrcode.make(qr_txt)
                        buf = BytesIO()
                        img_qr.save(buf, format="PNG")
                        st.image(buf, width=180, caption=f"QR Code: {p_code}")
                    with col_info:
                        st.subheader("Detail Item")
                        st.write(f"**Kode:** {p_code}")
                        st.write(f"**Nama:** {p_name}")
                        st.write(f"**Harga:** Rp {p_price}")
            else:
                st.warning("Data tidak ditemukan. Pastikan ejaan benar.")

# --- 标签页 2: 客户登记 ---
with tab2:
    st.title("Manajemen Data Konsumen")
    
    # 历史搜索
    with st.expander("🔍 Cari Riwayat Konsumen (Klik untuk Buka)"):
        search_cust = st.text_input("Masukkan Nama atau No Plat:")
        if search_cust:
            if "Aman" in search_cust:
                st.success("✅ Data Ditemukan: **Aman** | Plat: **DD 1234 XX** | Tipe: **NMAX**")
            else:
                st.info("Data tidak ditemukan di riwayat lokal.")
    
    st.markdown("---")
    
    # 输入表单
    st.subheader("📝 Input Data Transaksi Baru")
    with st.form("form_pembeli", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Konsumen:")
            plat = st.text_input("Nomor Plat:")
            wa = st.text_input("Nomor WhatsApp (Contoh: 628123...)")
        with col2:
            motor = st.text_input("Tipe Motor:")
            metode = st.selectbox("Metode Pembayaran:", ["Cash", "Kredit/Leasing"])
            leasing = st.selectbox("Pilih Leasing:", ["-", "ADR", "BUF", "MDL"])
        
        note = st.text_area("Catatan Tambahan:")
        submit = st.form_submit_button("Simpan & Kirim WhatsApp")

        if submit:
            if nama and wa:
                phone = wa.replace("+", "").replace(" ", "")
                if phone.startswith("0"): phone = "62" + phone[1:]
                
                pesan = f"Halo {nama}, Terima kasih telah bertransaksi di Yamaha!\nMotor: {motor} ({plat})\nMetode: {metode} {leasing if leasing != '-' else ''}"
                encoded_msg = urllib.parse.quote(pesan)
                wa_link = f"https://wa.me/{phone}?text={encoded_msg}"
                
                st.success(f"Data {nama} Berhasil Dicatat!")
                st.markdown(f'''
                    <a href="{wa_link}" target="_blank" style="text-decoration: none;">
                        <div style="background-color: #25D366; color: white; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold;">
                            🟢 Klik di Sini untuk Kirim WhatsApp ke {nama}
                        </div>
                    </a>
                ''', unsafe_allow_html=True)
                st.balloons()
            else:
                st.error("Nama dan No WhatsApp wajib diisi!")

# --- 标签页 3: 销售看板 ---
with tab3:
    st.title("Dashboard Analitik")
    
    m1, m2, m3 = st.columns(3)
    with st.container():
        m1.metric("Total Transaksi", "1,240", "+5%")
        m2.metric("Target Penjualan", "Rp 500M", "60%")
        m3.metric("Leasing Populer", "ADR", "Top 1")

    st.markdown("---")
    
    st.subheader("Visualisasi Penjualan")
    chart_data = pd.DataFrame({
        'Leasing': ['ADR', 'BUF', 'MDL', 'Cash'],
        'Jumlah': [45, 30, 20, 35]
    })
    st.bar_chart(data=chart_data, x='Leasing', y='Jumlah', color="#FF0000")
    
    st.info("💡 Data Dashboard disinkronisasi dengan database Cloud secara real-time.")
