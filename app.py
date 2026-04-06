import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime
import os

# --- 页面配置 ---
st.set_page_config(page_title="Yamaha Sparepart & Penjualan", layout="wide")

# --- 1. 生成网页访问二维码 (始终显示在左侧边栏) ---
st.sidebar.header("Scan QR untuk Buka di HP")
web_url = "https://spare-part-yamaha-cb786rte8wk8pse3ern2bm.streamlit.app/"
qr_web = qrcode.QRCode(box_size=4, border=2)
qr_web.add_data(web_url)
qr_web.make(fit=True)
img_web = qr_web.make_image(fill_color="black", back_color="white")

buf_web = BytesIO()
img_web.save(buf_web, format="PNG")
st.sidebar.image(buf_web, caption="Scan QR ini untuk berbagi link ke karyawan")
st.sidebar.markdown("---")

# --- 2. 增强版加载数据 (解决文件名找不到的问题) ---
@st.cache_data
def load_data():
    # 依次尝试可能的文件名
    possible_files = ["data.xlsx", "Data.xlsx", "DATA.xlsx"]
    for file in possible_files:
        if os.path.exists(file):
            try:
                df = pd.read_excel(file)
                return df
            except Exception as e:
                st.error(f"Error membaca file {file}: {e}")
    return None

df = load_data()

# --- 3. 顶部标签页切换 ---
tab1, tab2 = st.tabs(["🔍 Cari Sparepart & Harga", "📝 Data Konsumen & Notifikasi"])

# --- 标签页 1: 搜索零件 ---
with tab1:
    st.header("Pencarian Sparepart")
    
    # 如果没找到文件，显示友好的提示
    if df is None:
        st.error("❌ File data.xlsx tidak ditemukan di GitHub. Pastikan Anda sudah mengupload file Excel dengan nama 'data.xlsx' (semua huruf kecil).")
    else:
        search_query = st.text_input("Masukkan Nama atau Kode Sparepart (输入零件名称或编号):")

        if search_query:
            # 兼容搜索，确保 Part Number 和 Part Name 存在
            results = df[
                df['Part Number'].astype(str).str.contains(search_query, case=False, na=False) |
                df['Part Name'].astype(str).str.contains(search_query, case=False, na=False)
            ]

            if not results.empty:
                st.write(f"Ditemukan {len(results)} item:")
                st.dataframe(results)

                # 生成零件详情二维码
                st.markdown("---")
                st.subheader("QR Code Detail Sparepart")
                first_item = results.iloc[0]
                p_number = first_item['Part Number']
                p_name = first_item['Part Name']
                # 自动获取价格列，防止列名变动报错
                p_price = first_item.get('HED 210625', first_item.get('Price', 'N/A'))

                qr_detail_text = f"Kode: {p_number}\nNama: {p_name}\nHarga: Rp {p_price}"
                qr_item = qrcode.QRCode(box_size=8, border=4)
                qr_item.add_data(qr_detail_text)
                qr_item.make(fit=True)
                img_item = qr_item.make_image(fill_color="black", back_color="white")

                buf_item = BytesIO()
                img_item.save(buf_item, format="PNG")
                
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(buf_item, caption=f"QR Code {p_number}")
                with c2:
                    st.info(f"**Informasi QR:**\n\n{qr_detail_text}")
            else:
                st.warning("Data tidak ditemukan.")

# --- 标签页 2: 消费者数据 ---
with tab2:
    st.header("Input Data Konsumen")
    with st.form("form_konsumen"):
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Konsumen:")
            plat = st.text_input("Nomor Plat Motor:")
            telepon = st.text_input("Nomor WhatsApp (62xxx):")
        with col2:
            tipe_motor = st.text_input("Tipe Motor:")
            tgl_service = st.date_input("Tanggal Service", datetime.now())
            catatan = st.text_area("Catatan Tambahan:")
        
        submitted = st.form_submit_button("Simpan Data")
        if submitted:
            st.success(f"Data untuk {nama} berhasil dicatat!")
            st.write({
                "Nama": nama,
                "Plat": plat,
                "WA": telepon,
                "Tipe": tipe_motor,
                "Tanggal": tgl_service,
                "Catatan": catatan
            })

# --- 侧边栏底部 ---
st.sidebar.info("Tips: Jika tabel tidak muncul, pastikan file Excel di GitHub bernama 'data.xlsx'")
