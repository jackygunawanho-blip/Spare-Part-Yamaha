import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO

# --- 页面配置 ---
st.set_page_config(page_title="Yamaha Sparepart Management", layout="wide")

# --- 1. 生成网页访问二维码 (显示在左侧边栏) ---
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

# --- 2. 加载数据 ---
@st.cache_data
def load_data():
    # 确保你的 GitHub 仓库里有这个 data.xlsx 文件
    df = pd.read_excel("data.xlsx")
    return df

try:
    df = load_data()
except Exception as e:
    st.error("Gagal memuat data. Pastikan file 'data.xlsx' sudah diupload ke GitHub.")
    st.stop()

# --- 3. 界面标题 ---
st.title("🏍️ Sistem Manajemen Sparepart & Penjualan")

# --- 4. 搜索功能 ---
st.header("Pencarian Sparepart")
search_query = st.text_input("Masukkan Nama atau Kode Sparepart (输入零件名称或编号):")

if search_query:
    # 在 Part Number 或 Part Name 中搜索
    results = df[
        df['Part Number'].astype(str).str.contains(search_query, case=False, na=False) |
        df['Part Name'].astype(str).str.contains(search_query, case=False, na=False)
    ]

    if not results.empty:
        st.write(f"Ditemukan {len(results)} item:")
        st.dataframe(results)

        # --- 5. 为搜索到的第一个零件生成详情二维码 ---
        st.markdown("---")
        st.subheader("QR Code Detail Sparepart")
        
        # 获取第一个搜索结果的信息
        first_item = results.iloc[0]
        p_number = first_item['Part Number']
        p_name = first_item['Part Name']
        # 假设你的列名叫 'HED 210625' 或者类似的，根据你之前的截图调整
        p_price = first_item.get('HED 210625', 'N/A')

        # 二维码内容包含：编号、名称、价格
        qr_detail_text = f"Kode: {p_number}\nNama: {p_name}\nHarga: Rp {p_price}"
        
        qr_item = qrcode.QRCode(box_size=10, border=4)
        qr_item.add_data(qr_detail_text)
        qr_item.make(fit=True)
        img_item = qr_item.make_image(fill_color="black", back_color="white")

        buf_item = BytesIO()
        img_item.save(buf_item, format="PNG")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(buf_item, caption=f"QR Code untuk {p_number}")
        with col2:
            st.info(f"**Detail dari QR Code:**\n\n{qr_detail_text}")
    else:
        st.warning("Data tidak ditemukan.")

# --- 6. 底部信息 ---
st.sidebar.info("Tips: Gunakan fitur scan di atas untuk akses cepat melalui HP karyawan.")
