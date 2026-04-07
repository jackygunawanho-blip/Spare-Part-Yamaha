import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime
import urllib.parse # 新增：用于处理文字转链接

# --- 1. 页面配置 ---
st.set_page_config(page_title="Yamaha Cloud Management", layout="wide")

# --- 2. 左侧网页二维码 ---
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

# --- 3. 连接 Google Sheets ---
SHEET_ID = "1fCYY5SdPLEfc3tyJx9kWBVYSsNkkz3RGlzYTr9pr8hQ"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

@st.cache_data(ttl=300)
def load_data_from_cloud():
    try:
        df = pd.read_excel(GOOGLE_SHEET_URL)
        return df
    except Exception as e:
        st.error(f"Gagal mengambil data: {e}")
        return None

df = load_data_from_cloud()

# --- 4. 标签页 ---
tab1, tab2 = st.tabs(["🔍 Cari Sparepart", "📝 Data Konsumen"])

# --- 标签页 1: 搜索零件 (保持不变) ---
with tab1:
    st.header("Pencarian Sparepart")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    if df is not None:
        query = st.text_input("Cari Nama atau Kode:")
        if query:
            results = df[df.apply(lambda r: query.lower() in str(r).lower(), axis=1)]
            if not results.empty:
                st.dataframe(results)
    else:
        st.warning("Menunggu data...")

# --- 标签页 2: 消费者数据 + WhatsApp 自动通知 ---
with tab2:
    st.header("Input Data Konsumen")
    with st.form("form_pembeli"):
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Konsumen:")
            plat = st.text_input("Nomor Plat:")
            wa = st.text_input("Nomor WhatsApp (Contoh: 62812345678):")
            motor = st.text_input("Tipe Motor:")
        with col2:
            metode = st.selectbox("Metode Pembayaran:", ["Cash", "Kredit/Leasing"])
            leasing = st.selectbox("Pilih Leasing:", ["-", "ADR", "BUF", "MDL"])
            tenor = st.selectbox("Tenor:", ["-", "11 Bulan", "17 Bulan", "23 Bulan", "29 Bulan", "35 Bulan"])
            note = st.text_area("Catatan:")
        
        submit = st.form_submit_button("Simpan & Siapkan WhatsApp")

        if submit:
            if nama and wa:
                # 1. 清理电话号码，确保以 62 开头
                phone = wa.replace("+", "").replace(" ", "")
                if phone.startswith("0"):
                    phone = "62" + phone[1:]
                
                # 2. 编写自动发送的文字内容
                pesan = f"Halo {nama},\n\nTerima kasih telah melakukan transaksi di Yamaha.\n"
                pesan += f"Motor: {motor} ({plat})\n"
                if metode == "Kredit/Leasing":
                    pesan += f"Pembayaran: {metode} via {leasing} ({tenor})\n"
                else:
                    pesan += f"Pembayaran: {metode}\n"
                pesan += f"\nCatatan: {note}\n\nSalam Hangat!"
                
                # 3. 转换成 WhatsApp 链接格式
                encoded_msg = urllib.parse.quote(pesan)
                wa_link = f"https://wa.me/{phone}?text={encoded_msg}"
                
                st.success(f"Data {nama} Berhasil Dicatat!")
                
                # 4. 显示 WhatsApp 发送按钮
                st.markdown(f"""
                    <a href="{wa_link}" target="_blank">
                        <button style="background-color: #25D366; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;">
                            🟢 Kirim WhatsApp ke {nama}
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
                st.balloons()
            else:
                st.error("Mohon isi Nama dan Nomor WhatsApp.")
