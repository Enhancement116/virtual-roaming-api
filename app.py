import streamlit as st
import requests
import pandas as pd

# 1. 頁面初始化
st.set_page_config(layout="wide", page_title="GNSS Mission Control")

# 2. 樣式注入：切換主題、移除浮水印、全螢幕風格
def inject_styles(is_light):
    theme_css = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { transition: background 0.3s ease; }
    """
    if is_light:
        theme_css += """
        .stApp { background-color: #ffffff; color: #1e1e1e; }
        h1, h2 { color: #005bb5; }
        """
    else:
        theme_css += """
        .stApp { background-color: #050505; color: #00ff41; }
        h1, h2 { color: #00d2ff; }
        """
    st.markdown(theme_css + "</style>", unsafe_allow_html=True)

# 主題狀態管理
if "light_mode" not in st.session_state: st.session_state.light_mode = False
is_light = st.sidebar.toggle("☀️ SWITCH THEME", key="light_mode")
inject_styles(is_light)

# 3. 身分驗證 (放在 Sidebar 以保持介面乾淨)
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛰️ SYSTEM ACCESS REQUIRED")
    code = st.text_input("ENTER ACCESS CODE", type="password")
    if st.button("LOGIN"):
        if code == "1234": # 可自訂密碼
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 4. 儀表板主體
st.title("🛰️ GNSS & SDR MISSION CONTROL CENTER")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ MISSION CONFIGURATION")
    
    # 地點輸入 (自由輸入，預設 F459)
    region = st.text_input("📍 TARGET REGION", placeholder="高雄美術館")
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
            st.error(f"連線失敗: {e}")

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

# 底部狀態列
st.markdown("---")
st.write("STATUS: ONLINE | NETWORK: SECURE")
