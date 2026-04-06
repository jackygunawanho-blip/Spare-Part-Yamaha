import streamlit as st
import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import qrcode  # 新增：二维码库
from io import BytesIO

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Sistem Manajemen Motor", layout="wide")

# 2. Nama File
PARTS_FILE = "data.xlsx"
CUSTOMER_FILE = "clients.csv"

# 3. Inisialisasi file customer jika belum ada
if not os.path.exists(CUSTOMER_FILE):
    columns = ["Tanggal", "Nama", "No.plat", "NoFaktur", "No mesin", "No Rangka", "warna", "Type", "Alamat", "No.hp", "Payment", "Leasing", "Tenor"]
    pd.DataFrame(columns=columns).to_csv(CUSTOMER_FILE, index=False, encoding='utf-8-sig')

st.title("🏍️ Sistem Manajemen Sparepart & Penjualan")

tab1, tab2 = st.tabs(["🔍 Cari Sparepart & Harga", "📝 Data Konsumen & Notifikasi"])

# --- 新增：二维码生成函数 ---
def generate_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf.getvalue()

# --- BAGIAN 1: CARI SPAREPART ---
with tab1:
    st.header("Pencarian Sparepart")
    if os.path.exists(PARTS_FILE):
        try:
            df_parts = pd.read_excel(PARTS_FILE)
            # --- 修复：强制转换所有数据为字符串，解决 pyarrow 报错 ---
            df_parts = df_parts.astype(str) 
            
            search_part = st.text_input("Masukkan Nama atau Kode Sparepart:", key="part_search")
            if search_part:
                mask = df_parts.apply(lambda x: x.str.contains(search_part, case=False)).any(axis=1)
                found_df = df_parts[mask]
                st.dataframe(found_df, use_container_width=True)
                
                # --- 新增：显示二维码功能 ---
                if not found_df.empty:
                    st.divider()
                    st.subheader("🛠️ Quick QR Code")
                    # 取搜索到的第一个零件编号生成二维码
                    first_part_code = str(found_df.iloc[0, 0]) 
                    qr_img = generate_qr(first_part_code)
                    
                    col_qr1, col_qr2 = st.columns([1, 3])
                    with col_qr1:
                        st.image(qr_img, width=180)
                    with col_qr2:
                        st.write(f"**Kode Part:** {first_part_code}")
                        st.download_button(
                            label="📥 下载二维码用于打印",
                            data=qr_img,
                            file_name=f"QR_{first_part_code}.png",
                            mime="image/png"
                        )
            else:
                st.write("Data Sparepart (Top 10):", df_parts.head(10))
        except Exception as e:
            st.error(f"Gagal membaca data.xlsx: {e}")

# --- BAGIAN 2: DATA KONSUMEN & REMINDER ---
with tab2:
    st.header("Manajemen Konsumen")
    op = st.radio("Pilih Menu:", ["Input Data Baru", "Cari & Notifikasi Pembayaran"], horizontal=True)
    
    if op == "Input Data Baru":
        with st.form("client_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                tgl = st.date_input("Tanggal")
                nama = st.text_input("Nama Konsumen")
                plat = st.text_input("No. Plat")
                faktur = st.text_input("No. Faktur")
                mesin = st.text_input("No. Mesin")
            with c2:
                rangka = st.text_input("No. Rangka")
                warna = st.text_input("Warna")
                ctype = st.text_input("Type Motor")
                alamat = st.text_input("Alamat")
                hp = st.text_input("No. HP")

            st.markdown("---")
            pay = st.selectbox("Metode Pembayaran", ["Cash", "Kredit"])
            leasing = "N/A"
            tenor = "0"
            
            if pay == "Kredit":
                lc1, lc2 = st.columns(2)
                with lc1:
                    leasing = st.selectbox("Leasing", ["ADR", "BAF", "MDL", "WOM"])
                with lc2:
                    tenor = st.text_input("Tenor (Bulan)", value="11")

            if st.form_submit_button("💾 Simpan Data"):
                if nama:
                    new_row = [tgl, nama, plat, faktur, mesin, rangka, warna, ctype, alamat, hp, pay, leasing, tenor]
                    pd.DataFrame([new_row]).to_csv(CUSTOMER_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
                    st.success(f"✅ Data {nama} berhasil disimpan!")
                else:
                    st.warning("Mohon isi Nama!")

    else:
        if os.path.exists(CUSTOMER_FILE):
            df_clients = pd.read_csv(CUSTOMER_FILE)
            # --- 修复：同样强制转换为字符串防错 ---
            df_clients = df_clients.astype(str)
            
            def check_status(row):
                if row['Payment'] == 'Cash': return "🟢 Lunas (Cash)"
                try:
                    start_date = datetime.strptime(str(row['Tanggal']), '%Y-%m-%d')
                    tenor_months = int(row['Tenor'])
                    end_date = start_date + relativedelta(months=tenor_months)
                    today = datetime.now()
                    if today > end_date: return "🔴 Overdue (Lewat)"
                    elif today + relativedelta(months=1) >= end_date: return "🟡 Segera (Bulan ini)"
                    else: return "🔵 On Going"
                except: return "Data Error"
            
            if not df_clients.empty:
                df_clients['Status'] = df_clients.apply(check_status, axis=1)
                st.dataframe(df_clients, use_container_width=True)
