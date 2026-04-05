import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="摩托车管理系统", layout="wide")

# 文件配置
PARTS_FILE = "data.xlsx"
CUSTOMER_FILE = "clients.csv"

# 初始化客户文件（如果不存在）
if not os.path.exists(CUSTOMER_FILE):
    columns = ["Tanggal", "Nama", "No.plat", "NoFaktur", "No mesin", "No Rangka", "warna", "Type", "Alamat", "No.hp", "Payment", "Leasing", "Tenor"]
    pd.DataFrame(columns=columns).to_csv(CUSTOMER_FILE, index=False, encoding='utf-8-sig')

st.title("🏍️ 摩托车综合管理系统")

# 顶部导航标签
tab1, tab2 = st.tabs(["🔍 零件/价格查询", "📝 客户资料登记与查询"])

# --- 部分一：零件搜索 ---
with tab1:
    st.header("零件库存与价格搜索")
    if os.path.exists(PARTS_FILE):
        df_parts = pd.read_excel(PARTS_FILE)
        search_part = st.text_input("请输入零件名称或编码进行查询：", key="part_search")
        
        if search_part:
            mask = df_parts.astype(str).apply(lambda x: x.str.contains(search_part, case=False)).any(axis=1)
            result = df_parts[mask]
            st.success(f"找到 {len(result)} 条相关零件信息")
            st.dataframe(result, use_container_width=True)
            
            # 如果你的Excel里有“图片链接”列，可以取消下面注释来显示图片
            # st.image(result['图片列名'].iloc[0]) 
        else:
            st.info("💡 请输入关键词（如：Engine, Gear, 编码等）")
            st.write("数据预览：", df_parts.head(5))
    else:
        st.error(f"❌ 找不到零件表：请确保文件名是 {PARTS_FILE}")

# --- 部分二：摩托车客户信息 ---
with tab2:
    st.header("客户资料管理")
    
    # 子选项：登记新客户 或 查询旧客户
    menu = st.radio("请选择操作：", ["填入新客户信息", "搜索现有客户资料"], horizontal=True)
    
    if menu == "填入新客户信息":
        with st.form("client_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                tgl = st.date_input("Tanggal (日期)", datetime.now())
                nama = st.text_input("Nama (姓名)")
                plat = st.text_input("No.plat (车牌)")
                faktur = st.text_input("NoFaktur (发票号)")
                mesin = st.text_input("No mesin (发动机号)")
            with col2:
                rangka = st.text_input("No Rangka (车架号)")
                warna = st.text_input("Warna (颜色)")
                ctype = st.text_input("Type (型号)")
                alamat = st.text_input("Alamat (地址)")
                hp = st.text_input("No.hp (电话)")

            st.divider()
            
            # 付款逻辑
            pay = st.selectbox("付款方式", ["Cash", "Kredit"])
            leasing = "N/A"
            tenor = "N/A"
            
            if pay == "Kredit":
                l_col1, l_col2 = st.columns(2)
                with l_col1:
                    leasing = st.selectbox("融资渠道 (Leasing)", ["ADR", "BAF", "MOI", "WOM"])
                with l_col2:
                    tenor = st.text_input("期数 (Tenor)", placeholder="例如: 12个月")

            submitted = st.form_submit_button("✅ 确认保存客户资料")
            
            if submitted:
                if nama:
                    new_client = pd.DataFrame([[tgl, nama, plat, faktur, mesin, rangka, warna, ctype, alamat, hp, pay, leasing, tenor]])
                    new_client.to_csv(CUSTOMER_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
                    st.success(f"成功登记客户: {nama}")
                else:
                    st.error("请至少输入客户姓名！")

    else:
        # 客户搜索功能
        search_c = st.text_input("输入姓名或车牌号查询客户：")
        df_clients = pd.read_csv(CUSTOMER_FILE)
        if search_c:
            res_c = df_clients[df_clients.astype(str).apply(lambda x: x.str.contains(search_c, case=False)).any(axis=1)]
            if not res_c.empty:
                st.dataframe(res_c, use_container_width=True)
            else:
                st.warning("未找到该客户资料")
        else:
            st.write("最近登记记录：", df_clients.tail(5))