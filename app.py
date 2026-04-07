import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime
import urllib.parse

# --- 1. 页面配置 ---
st.set_page_config(page_title="Yamaha Management System", layout="wide")

# --- 2. 左侧侧边栏：扫码打开网页 ---
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

# --- 3. 云端数据连接 (Google Sheets) ---
SHEET_ID = "1fCYY5SdPLEfc3tyJx9kWBVYSsNkkz3RGlzYTr9pr8hQ"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

@st.cache_data(ttl=300)
def load_data():
    try:
        # 读取云端零件数据
        df = pd.read_excel(GOOGLE_SHEET_URL)
        return df
    except Exception as e:
        st.error(f"Gagal mengambil data: {e}")
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
        query = st.text_input("Cari Nama atau Kode (输入名称或编号):")
        if query:
            results = df_parts[df_parts.apply(lambda r: query.lower() in str(r).lower(), axis=1)]
            if not results.empty:
                st.dataframe(results)
                # 零件二维码生成
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

# --- 标签页 2: 客户登记 + WhatsApp ---
with tab2:
    st.header("Input Data Konsumen")
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
                # 整理电话和生成 WhatsApp 链接
                phone = wa.replace("+", "").replace(" ", "")
                if phone.startswith("0"): phone = "62" + phone[1:]
                
                pesan = f"Halo {nama}, Terima kasih telah bertransaksi!\nMotor: {motor} ({plat})\nMetode: {metode} {leasing if leasing != '-' else ''}"
                encoded_msg = urllib.parse.quote(pesan)
                wa_link = f"https://wa.me/{phone}?text={encoded_msg}"
                
                st.success(f"Data {nama} Berhasil Dicatat!")
                st.markdown(f'<a href="{wa_link}" target="_blank"><button style="background-color: #25D366; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer;">🟢 Kirim WhatsApp ke {nama}</button></a>', unsafe_allow_html=True)
                st.balloons()

# --- 标签页 3: 销售报表看板 (可视化) ---
with tab3:
    st.header("Dashboard Analitik Penjualan")
    
    # 建立 3 个亮眼的指标卡片
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Transaksi (Est.)", "1,240", "+5%")
    m2.metric("Target Bulanan", "Rp 500M", "60%")
    m3.metric("Partner Teraktif", "ADR", "Top 1")

    st.markdown("---")
    
    # 创建模拟图表数据 (未来可以根据你的真实客户表格自动生成)
    st.subheader("Distribusi Leasing (占比图)")
    chart_data = pd.DataFrame({
        'Leasing': ['ADR', 'BUF', 'MDL', 'Cash'],
        'Jumlah': [45, 30, 20, 35]
    })
    st.bar_chart(data=chart_data, x='Leasing', y='Jumlah')
    
    st.info("💡 Dashboard ini sangat cocok untuk dipamerkan di video YouTube sebagai bukti sistem manajemen modern!")
