import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime

# --- 1. 页面配置 ---
st.set_page_config(page_title="Yamaha Cloud Management", layout="wide")

# --- 2. 左侧网页二维码 (保持不变) ---
st.sidebar.header("Scan QR untuk Buka di HP")
web_url = "https://spare-part-yamaha-cb786rte8wk8pse3ern2bm.streamlit.app/"
qr_web = qrcode.QRCode(box_size=4, border=2)
qr_web.add_data(web_url)
qr_web.make(fit=True)
img_web = qr_web.make_image(fill_color="black", back_color="white")
buf_web = BytesIO()
img_web.save(buf_web, format="PNG")
st.sidebar.image(buf_web, caption="Scan QR untuk buka di HP")
st.sidebar.markdown("---")

# --- 3. 连接 Google Sheets (云端同步核心) ---
# 这是你刚才提供的表格 ID
SHEET_ID = "1fCYY5SdPLEfc3tyJx9kWBVYSsNkkz3RGlzYTr9pr8hQ"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

@st.cache_data(ttl=300) # 每 5 分钟自动刷新一次云端数据
def load_data_from_cloud():
    try:
        # 直接从 Google Docs 链接下载并读取
        df = pd.read_excel(GOOGLE_SHEET_URL)
        return df
    except Exception as e:
        st.error(f"Gagal mengambil data dari Google Sheets: {e}")
        return None

df = load_data_from_cloud()

# --- 4. 顶部标签页切换 ---
tab1, tab2 = st.tabs(["🔍 Cari Sparepart (Live Cloud)", "📝 Data Konsumen"])

# --- 标签页 1: 搜索零件 (数据来自云端) ---
with tab1:
    st.header("Pencarian Sparepart (Sync: Google Sheets)")
    if st.button("🔄 Refresh Data Sekarang"):
        st.cache_data.clear()
        st.rerun()

    if df is not None:
        query = st.text_input("Cari Nama atau Kode (输入名称或编号):")
        if query:
            # 全文搜索逻辑
            results = df[df.apply(lambda r: query.lower() in str(r).lower(), axis=1)]
            if not results.empty:
                st.dataframe(results)
                
                # 生成详情二维码
                st.markdown("---")
                val = results.iloc[0]
                # 假设你的列顺序没变：1是编号，3是名称，5是价格
                p_code = val.iloc[1] if len(val) > 1 else "N/A"
                p_name = val.iloc[3] if len(val) > 3 else "N/A"
                p_price = val.iloc[5] if len(val) > 5 else "N/A"

                qr_txt = f"Kode: {p_code}\nNama: {p_name}\nHarga: Rp {p_price}"
                img_qr = qrcode.make(qr_txt)
                buf = BytesIO()
                img_qr.save(buf, format="PNG")
                st.image(buf, width=200, caption=f"QR Detail: {p_code}")
            else:
                st.warning("Data tidak ditemukan.")
    else:
        st.warning("Menunggu data dari Google Sheets...")

# --- 标签页 2: 消费者数据 (含租赁公司选项) ---
with tab2:
    st.header("Input Data Konsumen")
    with st.form("form_pembeli"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Informasi Pribadi")
            nama = st.text_input("Nama Konsumen:")
            plat = st.text_input("Nomor Plat:")
            wa = st.text_input("Nomor WhatsApp:")
            motor = st.text_input("Tipe Motor:")
        
        with col2:
            st.subheader("Detail Pembayaran")
            metode = st.selectbox("Metode Pembayaran:", ["Cash", "Kredit/Leasing"])
            leasing = st.selectbox("Pilih Leasing:", ["-", "ADR", "BUF", "MDL"])
            tenor = st.selectbox("Tenor:", ["-", "11 Bulan", "17 Bulan", "23 Bulan", "29 Bulan", "35 Bulan"])
            tgl = st.date_input("Tanggal Transaksi", datetime.now())
            note = st.text_area("Catatan:")
        
        if st.form_submit_button("Simpan Data"):
            if nama and wa:
                st.success(f"Data {nama} Berhasil Dicatat!")
                st.balloons()
            else:
                st.error("Mohon isi Nama dan Nomor WhatsApp.")

st.sidebar.info("Tips: Ubah harga di Google Sheets, lalu klik 'Refresh Data' di sini.")
