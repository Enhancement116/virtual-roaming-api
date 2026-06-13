import streamlit as st
import requests
from streamlit_lottie import st_lottie
import pandas as pd

st.set_page_config(layout="wide", page_title="GNSS Mission Control")

# --- 賽博龐克 CSS ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; font-family: 'Consolas', monospace; }
    .metric-card { background: #111; border: 1px solid #00ff41; padding: 20px; border-radius: 5px; }
    h1, h2 { color: #00d2ff; text-transform: uppercase; letter-spacing: 2px; }
    div[data-testid="stMetricValue"] { color: #00ff41; }
</style>
""", unsafe_allow_html=True)

st.title("🛰️ GNSS & SDR MISSION CONTROL CENTER")
st.markdown("---")

# --- 頂層指標列 (Metrics) ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("SIGNAL STRENGTH", "98.2 dBm", "+0.5")
col2.metric("SATELLITE LOCK", "12/24", "Stable")
col3.metric("LATENCY", "12ms", "-2ms")
col4.metric("SYSTEM LOAD", "42%", "Normal")

# --- 左右佈局 ---
left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("⚙️ MISSION CONFIGURATION")
    region = st.selectbox("📍 TARGET REGION", ["高雄都會公園", "高雄美術館", "台北大安森林公園"])
    speed = st.slider("🏃 VELOCITY (km/h)", 0.0, 50.0, 16.5)
    
    if st.button("🚀 INITIATE SIGNAL SIMULATION"):
        # 你的後端 API 呼叫
        payload = {"region_name": region, "gnss_system": "BDS+GPS", "sampling_rate": 20.8, "speed_kmh": speed}
        try:
            requests.post("https://api.enhancement-social.org/tasks/", json=payload)
            st.success("SIMULATION STREAM STARTING...")
        except:
            st.error("CONNECTION FAILED")

with right_col:
    st.subheader("📊 LIVE DATA TELEMETRY")
    
    # 即時表格
    response = requests.get("https://api.enhancement-social.org/tasks/")
    if response.status_code == 200:
        data = response.json().get("data", [])
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, height=300)
    
    # 虛擬日誌區 (看起來超專業)
    st.subheader("🖥️ SYSTEM LOG")
    log_area = st.empty()
    log_area.text("> INITIALIZING SDR CORE...\n> LOADING EPHEMERIS DATA...\n> BDS+GPS LINK ESTABLISHED...")

st.markdown("---")
st.caption("INTERNAL USE ONLY - AUTHORIZED ACCESS REQUIRED")