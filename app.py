import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="Sistem Manajemen Motor", layout="wide")

# Konfigurasi File
PARTS_FILE = "data.xlsx"
CUSTOMER_FILE = "clients.csv"

# Inisialisasi file customer jika belum ada
if not os.path.exists(CUSTOMER_FILE):
    columns = ["Tanggal", "Nama", "No.plat", "NoFaktur", "No mesin", "No Rangka", "warna", "Type", "Alamat", "No.hp", "Payment", "Leasing", "Tenor"]
    pd.DataFrame(columns=columns).to_csv(CUSTOMER_FILE, index=False, encoding='utf-8-sig')

st.title("🏍️ Sistem Manajemen Sparepart & Penjualan")

# Membuat Tab
tab1, tab2 = st.tabs(["🔍 Cari Sparepart & Harga", "📝 Data Konsumen Baru"])

# --- BAGIAN 1: CARI SPAREPART ---
with tab1:
    st.header("Pencarian Sparepart")
    if os.path.exists(PARTS_FILE):
        try:
            df_parts = pd.read_excel(PARTS_FILE)
            search_part = st.text_input("Masukkan Nama atau Kode Sparepart:", placeholder="Cari kode, nama, atau harga...")
            
            if search_part:
                mask = df_parts.astype(str).apply(lambda x: x.str.contains(search_part, case=False)).any(axis=1)
                result = df_parts[mask]
                st.success(f"Ditemukan {len(result)} hasil")
                st.dataframe(result, use_container_width=True)
            else:
                st.info("💡 Silakan masukkan kata kunci untuk mencari.")
                st.write("Pratinjau Data (10 baris pertama):", df_parts.head(10))
        except Exception as e:
            st.error(f"Gagal membaca file Excel: {e}")
    else:
        st.error(f"❌ File {PARTS_FILE} tidak ditemukan di server.")

# --- BAGIAN 2: DATA KONSUMEN ---
with tab2:
    st.header("Manajemen Data Konsumen")
    
    op = st.radio("Pilih Menu:", ["Input Data Baru", "Cari Data Lama"], horizontal=True)
    
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
            tenor = "N/A"
            if pay == "Kredit":
                lc1, lc2 = st.columns(2)
                with lc1:
                    leasing = st.selectbox("Leasing", ["ADR", "BAF", "MOI", "WOM"])
                with lc2:
                    tenor = st.text_input("Tenor (Bulan)", placeholder="Contoh: 11, 23, 35")

            if st.form_submit_button("💾 Simpan Data"):
                if nama:
                    new_row = [tgl, nama, plat, faktur, mesin, rangka, warna, ctype, alamat, hp, pay, leasing, tenor]
                    new_df = pd.DataFrame([new_row])
                    new_df.to_csv(CUSTOMER_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
                    st.success(f"✅ Data konsumen {nama} berhasil disimpan!")
                else:
                    st.warning("Mohon isi Nama Konsumen minimal!")

    else:
        search_c = st.text_input("Cari berdasarkan Nama, No Plat, atau No Rangka:")
        if os.path.exists(CUSTOMER_FILE):
            df_clients = pd.read_csv(CUSTOMER_FILE)
            if search_c:
                res_c = df_clients[df_clients.astype(str).apply(lambda x: x.str.contains(search_c, case=False)).any(axis=1)]
                if not res_c.empty:
                    st.dataframe(res_c, use_container_width=True)
                else:
                    st.warning("Data konsumen tidak ditemukan.")
            else:
                st.write("10 Data Terakhir:", df_clients.tail(10))
