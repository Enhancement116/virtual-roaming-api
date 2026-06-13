import streamlit as st
import requests
import pandas as pd

# 1. 頁面初始化
st.set_page_config(layout="wide", page_title="GNSS Mission Control")

# 2. 強制樣式注入：鎖定亮色系 + 徹底移除浮水印與選單
st.markdown("""
<style>
    /* 徹底隱藏 Streamlit 品牌標記 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* 亮色科技感配色 */
    .stApp { 
        background-color: #ffffff; 
        color: #1e1e1e; 
        transition: background 0.3s ease; 
    }
    h1, h2 { color: #2563eb; text-transform: uppercase; letter-spacing: 1px; }
    .stButton>button { 
        background-color: #2563eb; 
        color: white; 
        font-weight: bold; 
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 3. 身分驗證 (隱藏於頁面頂端)
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛰️ SYSTEM ACCESS REQUIRED")
    code = st.text_input("ENTER ACCESS CODE", type="password")
    if st.button("LOGIN"):
        if code == "1234":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 4. 儀表板主體
st.title("🛰️ GNSS & SDR MISSION CONTROL CENTER")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ MISSION CONFIGURATION")
    
    # 區域自由輸入 (預設 F459)
    region = st.text_input("📍 TARGET REGION", placeholder="例如：高雄美術館")
    target_region = region if region else "F459"
    
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
            requests.post("https://api.enhancement-social.org/tasks/", json=payload)
            st.success(f"任務已部署至: {target_region}")
        except Exception as e:
            st.error(f"API 連線失敗: {e}")

with col2:
    st.subheader("📊 LIVE DATA TELEMETRY")
    try:
        response = requests.get("https://api.enhancement-social.org/tasks/")
        if response.status_code == 200:
            data = response.json().get("data", [])
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.write("No active tasks.")
    except:
        st.write("API unreachable.")

st.markdown("---")
st.caption("INTERNAL MISSION CONTROL - AUTHORIZED ACCESS ONLY")
