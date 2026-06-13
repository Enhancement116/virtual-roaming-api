import streamlit as st
import requests

# 設定 FastAPI 後端的網址
# ⚠️ 注意：這裡要換成你 Vercel 部署後的正式網址！
# 在本地測試時，先用 http://127.0.0.1:8000
API_URL = "https://virtual-roaming-api.vercel.app/tasks/"
# 設定網頁標題與圖示
st.set_page_config(page_title="虛擬定位漫遊系統", page_icon="🚶‍♂️", layout="centered")

st.title("🚶‍♂️ 虛擬定位漫遊服務")
st.markdown("專為 AR 遊戲玩家設計，設定你的散步計畫並開始自動漫遊！")

st.divider()

# --- 建立使用者介面 ---

# 1. 選擇區域
region_options = ["高雄都會公園", "高雄美術館", "台北大安森林公園", "台南奇美博物館"]
selected_region = st.selectbox("📍 選擇漫遊區域：", region_options)

# 2. 選擇 GNSS 系統
gnss_options = ["GPS", "BDS", "BDS+GPS"]
selected_gnss = st.selectbox("🛰️ 選擇定位星系：", gnss_options, index=2) # 預設選第三個 BDS+GPS

# 3. 設定移動速率 (滑桿)
st.markdown("🏃‍♂️ **設定移動速率 (km/h)**")
st.caption("建議步行速度約為 3~5 km/h，腳踏車約為 10~15 km/h。過快可能導致遊戲判定異常。")
selected_speed = st.slider("速率", min_value=1.0, max_value=20.0, value=4.5, step=0.5, label_visibility="collapsed")

# 4. 設定取樣率 (進階選項，預設折疊)
with st.expander("⚙️ 進階設定 (取樣率)"):
    selected_sampling_rate = st.number_input("取樣率 (MHz)", value=20.8, min_value=1.0, max_value=50.0, step=0.1)

st.divider()

# --- 提交按鈕與 API 呼叫 ---

if st.button("🚀 啟動漫遊任務", use_container_width=True, type="primary"):
    # 準備要傳送給 API 的資料
    payload = {
        "region_name": selected_region,
        "gnss_system": selected_gnss,
        "sampling_rate": selected_sampling_rate,
        "speed_kmh": selected_speed
    }
    
    with st.spinner('正在將任務發送至伺服器...'):
        try:
            # 發送 POST 請求到 FastAPI
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ {result['message']}")
                st.balloons() # 放個氣球慶祝一下
                
                # 顯示回傳的資料
                st.json(result["data"])
            else:
                st.error(f"❌ 錯誤：{response.status_code}")
                st.json(response.json())
                
        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ 無法連線到伺服器，請確認後端 API 是否已啟動。\n\n詳細錯誤：{e}")
# --- 歷史任務清單 ---
st.divider()
st.subheader("📋 歷史漫遊任務紀錄")

if st.button("🔄 重新整理清單"):
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            tasks = response.json().get("data", [])
            if tasks:
                st.table(tasks) # 這會自動幫你畫出一個漂亮的表格
            else:
                st.info("目前還沒有任務紀錄喔！")
        else:
            st.error("無法讀取清單")
    except Exception as e:
        st.error(f"連線錯誤：{e}")