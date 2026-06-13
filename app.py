import streamlit as st
import requests
import pandas as pd

# 頁面設定
st.set_page_config(layout="wide", page_title="GNSS Mission Control")

# 賽博龐克風格 CSS
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; font-family: 'Consolas', monospace; }
    h1, h2 { color: #00d2ff; text-transform: uppercase; }
    .stButton>button { background-color: #00ff41; color: #000; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 1. 身分驗證邏輯
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛰️ SYSTEM ACCESS REQUIRED")
    code = st.text_input("ENTER ACCESS CODE", type="password")
    if st.button("LOGIN"):
        if code == "1234": # 可更改為你的密碼
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 2. 儀表板主體
st.title("🛰️ GNSS & SDR MISSION CONTROL CENTER")
st.markdown("---")

left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("⚙️ MISSION CONFIGURATION")
    
    # 區域自由輸入 (預設值邏輯)
    region = st.text_input("📍 TARGET REGION", placeholder="例如：高雄美術館")
    if not region: region = "F459" # 若未輸入，強制設為 F459
    
    system = st.selectbox("📡 GNSS SYSTEM", ["BDS+GPS", "GPS", "BDS", "GLONASS"])
    sampling = st.slider("📊 SAMPLING RATE (MHz)", 1.0, 50.0, 20.8)
    speed = st.number_input("🏃 VELOCITY (km/h)", value=16.5)
    priority = st.slider("⭐ MISSION PRIORITY", 1, 10, 1)
    
    if st.button("🚀 INITIATE SIGNAL SIMULATION"):
        payload = {
            "region_name": region,
            "gnss_system": system,
            "sampling_rate": sampling,
            "speed_kmh": speed,
            "priority": priority
        }
        try:
            # 呼叫你的 API
            requests.post("https://api.enhancement-social.org/tasks/", json=payload)
            st.success(f"任務已發送至區域: {region} (權重: {priority})")
        except Exception as e:
            st.error(f"API 連線失敗: {e}")

with right_col:
    st.subheader("📊 LIVE DATA TELEMETRY")
    # 讀取任務列表
    try:
        response = requests.get("https://api.enhancement-social.org/tasks/")
        if response.status_code == 200:
            data = response.json().get("data", [])
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("無即時數據")
    except:
        st.error("無法連接 API")

st.markdown("---")
st.caption("SYSTEM OPERATIONAL - AUTHORIZED ACCESS ONLY")
