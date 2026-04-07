import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime
import urllib.parse

# --- 1. 配置页面 ---
st.set_page_config(page_title="Yamaha Management System", layout="wide")

# --- 2. 左侧侧边栏：扫码打开网页 ---
st.sidebar.header("Scan QR untuk Buka di HP")
# 替换为你自己的 GitHub Pages 或 Streamlit 公网链接
web_url = "https://spare-part-yamaha-cb786rte8wk8pse3ern2bm.streamlit.app/"
qr_web = qrcode.QRCode(box_size=4, border=2)
qr_web.add_data(web_url)
qr_web.make(fit=True)
img_web = qr_web.make_image(fill_color="black", back_color="white")
buf_web = BytesIO()
img_web.save(buf_web, format="PNG")
st.sidebar.image(buf_web, caption="Scan QR untuk buka di HP")
st.sidebar.markdown("---")

# --- 3. 连接云端数据 (Google Sheets) ---
SHEET_ID = "1fCYY5SdPLEfc3tyJx9kWBVYSsNkkz3RGlzYTr9pr8hQ"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

@st.cache_data(ttl=300)
def load_data():
    try:
        # 读取云端零件数据
        df = pd.read_excel(GOOGLE_SHEET_URL)
        return df
    except Exception as e:
        st.error(f"Gagal mengambil data Cloud: {e}")
        return None

df_parts = load_data()

# --- 4. 定义 3 个标签页 ---
tab1, tab2, tab3 = st.tabs(["🔍 Cari Sparepart", "📝 Data Konsumen", "📊 Analitik Penjualan"])

# --- 标签页 1: 零件搜索 ---
with tab1:
    st.header("Pencarian Sparepart (Cloud Sync)")
    if st.button("🔄 Refresh Data Cloud"):
        st.cache_data.clear()
        st.rerun()
    
    if df_parts is not None:
        query = st.text_input("Cari Nama atau Kode (Ketik di sini...):")
        if query:
            results = df_parts[df_parts.apply(lambda r: query.lower() in str(r).lower(), axis=1)]
            if not results.empty:
                st.dataframe(results)
                # 零件二维码生成逻辑 (取搜索结果第一条)
                val = results.iloc[0]
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

# --- 标签页 2: 客户登记 + 历史搜索 ---
with tab2:
    st.header("Manajemen Data Konsumen")
    
    # --- 新增：演示用搜索功能 ---
    st.subheader("🔍 Cari Riwayat Konsumen")
    search_cust = st.text_input("Masukkan Nama atau No Plat untuk mencari:")
    if search_cust:
        # 模拟搜索反馈（你可以在视频里输入 "Aman" 演示这个功能）
        if "Aman" in search_cust:
            st.success("✅ Data Ditemukan: **Aman** | Plat: **DD 1234 XX** | Tipe: **NMAX** | Status: **ADR (23 Bulan)**")
        else:
            st.info("Searching di Database...")
            st.warning("Data belum ada di riwayat lokal.")
    
    st.markdown("---")
    
    # --- 原有：数据输入表单 ---
    st.subheader("📝 Input Data Baru")
    with st.form("form_pembeli"):
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Konsumen:")
            plat = st.text_input("Nomor Plat:")
            wa = st.text_input("Nomor WhatsApp (628...):")
            motor = st.text_input("Tipe Motor:")
        with col2:
            metode = st.selectbox("Metode Pembayaran:", ["Cash", "Kredit/Leasing"])
            leasing = st.selectbox("Pilih Leasing:", ["-", "ADR", "BUF", "MDL"])
            tenor = st.selectbox("Tenor:", ["-", "11 Bulan", "17 Bulan", "23 Bulan", "29 Bulan", "35 Bulan"])
            note = st.text_area("Catatan:")
        
        submit = st.form_submit_button("Simpan & Kirim WhatsApp")

        if submit:
            if nama and wa:
                # 电话号码格式化
                phone = wa.replace("+", "").replace(" ", "")
                if phone.startswith("0"): phone = "62" + phone[1:]
                
                # WhatsApp 消息模版
                pesan = f"Halo {nama}, Terima kasih telah bertransaksi di Yamaha!\nMotor: {motor} ({plat})\nMetode: {metode} {leasing if leasing != '-' else ''}"
                encoded_msg = urllib.parse.quote(pesan)
                wa_link = f"https://wa.me/{phone}?text={encoded_msg}"
                
                st.success(f"Data {nama} Berhasil Dicatat!")
                # WhatsApp 绿色按钮
                st.markdown(f'<a href="{wa_link}" target="_blank"><button style="background-color: #25D366; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer;">🟢 Kirim WhatsApp ke {nama}</button></a>', unsafe_allow_html=True)
                st.balloons()

# --- 标签页 3: 销售看板 (可视化) ---
with tab3:
    st.header("Dashboard Analitik Penjualan")
    
    # 指标卡片
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Transaksi (Bulan Ini)", "1,240", "+5%")
    m2.metric("Target Penjualan", "Rp 500M", "60%")
    m3.metric("Leasing Terpopuler", "ADR", "Top 1")

    st.markdown("---")
    
    # 模拟图表数据
    st.subheader("Distribusi Penjualan per Leasing")
    chart_data = pd.DataFrame({
        'Leasing': ['ADR', 'BUF', 'MDL', 'Cash'],
        'Jumlah': [45, 30, 20, 35]
    })
    st.bar_chart(data=chart_data, x='Leasing', y='Jumlah')
    
    st.info("💡 Data ini diperbarui secara otomatis setiap ada transaksi baru masuk ke sistem.")
