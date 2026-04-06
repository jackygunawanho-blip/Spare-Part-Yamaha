import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime
import osimport streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime
import os

# --- 1. 页面配置 ---
st.set_page_config(page_title="Yamaha Management", layout="wide")

# --- 2. 左侧网页二维码 (始终显示) ---
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

# --- 3. 加载零件数据 ---
@st.cache_data(ttl=600)
def load_data():
    file_path = "data.xlsx"
    if os.path.exists(file_path):
        return pd.read_excel(file_path)
    return None

df = load_data()

# --- 4. 顶部标签页切换 ---
tab1, tab2 = st.tabs(["🔍 Cari Sparepart", "📝 Data Konsumen"])

# --- 标签页 1: 搜索零件 ---
with tab1:
    st.header("Pencarian Sparepart")
    if df is None:
        st.error("⚠️ File data.xlsx tidak terbaca.")
    else:
        query = st.text_input("Cari Nama atau Kode (输入名称或编号):")
        if query:
            results = df[df.apply(lambda r: query.lower() in str(r).lower(), axis=1)]
            if not results.empty:
                st.dataframe(results)
                # 零件详情二维码
                st.markdown("---")
                val = results.iloc[0]
                qr_txt = f"Kode: {val.iloc[1]}\nNama: {val.iloc[3]}\nHarga: Rp {val.iloc[5]}"
                img_qr = qrcode.make(qr_txt)
                buf = BytesIO()
                img_qr.save(buf, format="PNG")
                st.image(buf, width=200, caption="QR Code Detail Sparepart")

# --- 标签页 2: 消费者数据 (已加入 ADR, BUF, MDL) ---
with tab2:
    st.header("Input Data Konsumen")
    with st.form("form_pembeli"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Informasi Pribadi")
            nama = st.text_input("Nama Konsumen (客户姓名):")
            plat = st.text_input("Nomor Plat (车牌号):")
            wa = st.text_input("Nomor WhatsApp:")
            motor = st.text_input("Tipe Motor (摩托型号):")
        
        with col2:
            st.subheader("Detail Pembayaran")
            metode_bayar = st.selectbox("Metode Pembayaran (支付方式):", ["Cash", "Kredit/Leasing"])
            
            # 只有当选择 Kredit/Leasing 时，下面的选项才有效
            leasing = st.selectbox("Pilih Leasing (贷款公司):", ["-", "ADR", "BUF", "MDL"])
            tenor = st.selectbox("Tenor (分期期数):", ["-", "11 Bulan", "17 Bulan", "23 Bulan", "29 Bulan", "35 Bulan"])
            
            tgl = st.date_input("Tanggal Transaksi (日期)", datetime.now())
            note = st.text_area("Catatan Tambahan (备注):")
        
        submit = st.form_submit_button("Simpan Data (保存数据)")
        
        if submit:
            if nama and wa:
                st.success(f"Data {nama} Berhasil Dicatat!")
                # 显示汇总信息
                summary = f"**Metode:** {metode_bayar}"
                if metode_bayar == "Kredit/Leasing":
                    summary += f" | **Leasing:** {leasing} | **Tenor:** {tenor}"
                st.info(summary)
                st.balloons()
            else:
                st.error("Mohon isi Nama dan Nomor WhatsApp.")

# --- 页面配置 ---
st.set_page_config(page_title="Yamaha Management", layout="wide")

# --- 1. 左侧网页二维码 ---
st.sidebar.header("Scan QR untuk Buka di HP")
web_url = "https://spare-part-yamaha-cb786rte8wk8pse3ern2bm.streamlit.app/"
qr_web = qrcode.QRCode(box_size=4, border=2)
qr_web.add_data(web_url)
qr_web.make(fit=True)
img_web = qr_web.make_image(fill_color="black", back_color="white")
buf_web = BytesIO()
img_web.save(buf_web, format="PNG")
st.sidebar.image(buf_web, caption="Scan QR untuk buka di HP")

# --- 2. 强制读取数据 ---
@st.cache_data(ttl=600) # 每10分钟强制更新一次缓存
def load_data():
    file_name = "data.xlsx"
    if os.path.exists(file_name):
        return pd.read_excel(file_name)
    return None

df = load_data()

# --- 3. 标签页 ---
tab1, tab2 = st.tabs(["🔍 Cari Sparepart", "📝 Data Konsumen"])

with tab1:
    st.header("Pencarian Sparepart")
    if df is None:
        st.error("⚠️ File data.xlsx masih belum terbaca. Silakan klik 'Reboot App' di menu kanan atas.")
    else:
        query = st.text_input("Cari Nama/Kode:")
        if query:
            results = df[df.apply(lambda r: query.lower() in str(r).lower(), axis=1)]
            st.dataframe(results)
            # 自动生成零件二维码
            if not results.empty:
                val = results.iloc[0]
                qr_txt = f"Kode: {val.iloc[1]}\nHarga: {val.iloc[5]}"
                img_qr = qrcode.make(qr_txt)
                buf = BytesIO()
                img_qr.save(buf, format="PNG")
                st.image(buf, width=200)

with tab2:
    st.header("Input Konsumen")
    st.write("Silakan isi data di bawah ini...")
    # (此处省略表单代码，保持简洁)
