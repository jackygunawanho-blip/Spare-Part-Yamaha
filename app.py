import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime
import os

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
