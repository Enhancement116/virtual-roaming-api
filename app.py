import streamlit as st
import requests
import os
import pandas as pd

# 1. 頁面配置 (強制全寬)
st.set_page_config(layout="wide", page_title="GNSS Mission Control")

# 2. 強制隱藏 UI 與浮水印
# 這些 CSS 會強制移除所有 Streamlit 的品牌標誌與全螢幕按鈕
st.markdown("""
<style>
    #MainMenu, footer, header, .stDeployButton, button[title="View fullscreen"] { 
        visibility: hidden !important; 
        display: none !important; 
    }
    .stApp { 
        background-color: #ffffff; 
        color: #1e1e1e; 
    }
    h1, h2 { color: #2563eb; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# 3. 身分驗證 (從環境變數讀取密碼)
# 在 Vercel 環境變數設定 APP_PASSWORD，預設為空以確保安全性
SECRET_PASS = os.getenv("APP_PASSWORD", "1234") 

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛰️ SYSTEM ACCESS REQUIRED")
    code = st.text_input("ENTER ACCESS CODE", type="password")
    if st.button("LOGIN"):
        if code == SECRET_PASS:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Invalid Access Code")
    st.stop()

# 4. 儀表板主體
st.title("🛰️ GNSS & SDR MISSION CONTROL CENTER")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ MISSION CONFIGURATION")
    
    # 自由輸入區域，未輸入則預設為 F459
    region = st.text_input("📍 TARGET REGION", placeholder="例如：高雄美術館")
    target_region = region if region and region.strip() != "" else "F459"
    
    system = st.selectbox("📡 GNSS SYSTEM", ["BDS+GPS", "GPS", "BDS", "GLONASS"])
    sampling = st.slider("📊 SAMPLING RATE (MHz)", 1.0, 50.0, 20.8)
    speed = st.number_input("🏃 VELOCITY (km/h)", value=16.5)
    priority = st.slider("⭐ MISSION PRIORITY", 1, 10, 1)
    
    if st.button("🚀 INITIATE SIGNAL SIMULATION"):
        payload = {
            "region_name": target_region,
            "gnss_system": system,
            "sampling_rate": sampling,
            "speed_kmh": speed,
            "priority": priority
        }
        try:
            # 發送請求至你的後端
            response = requests.post("https://api.enhancement-social.org/tasks/", json=payload)
            if response.status_code == 200:
                st.success(f"任務已部署至: {target_region}")
            else:
                st.error("伺服器回應錯誤")
        except Exception as e:
            st.error(f"連線失敗: {e}")

with col2:
    st.subheader("📊 LIVE DATA TELEMETRY")
    try:
        # 從後端獲取數據
        response = requests.get("https://api.enhancement-social.org/tasks/")
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("目前無活動任務")
        else:
            st.error("無法取得數據")
    except:
        st.error("API 連線錯誤")

st.markdown("---")
st.caption("AUTHORIZED ACCESS ONLY | SYSTEM OPERATIONAL")
