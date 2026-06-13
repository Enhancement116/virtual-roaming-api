import streamlit as st
import hashlib
import requests
import pandas as pd
from datetime import datetime, timezone

# 頁面配置
st.set_page_config(page_title="Mission Control", layout="wide")

# 加密函式
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 狀態管理
if "auth" not in st.session_state: st.session_state.auth = False
if "username" not in st.session_state: st.session_state.username = None
if "user_weight" not in st.session_state: st.session_state.user_weight = 0
if "waypoints" not in st.session_state: st.session_state.waypoints = [""]

# --- 認證頁面 ---
if not st.session_state.auth:
    st.title("🛰️ MISSION CONTROL ACCESS")
    tab = st.radio("選擇模式", ["Login", "Register"], horizontal=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button(tab):
        if not username or not password:
            st.warning("⚠️ 請輸入帳號與密碼")
        else:
            try:
                endpoint = "register" if tab == "Register" else "login"
                response = requests.post(f"https://api.enhancement-social.org/auth/{endpoint}", 
                                       json={"username": username, "password": password})
                if response.status_code == 200:
                    if tab == "Login":
                        st.session_state.auth = True
                        st.session_state.username = username
                        # 登入成功後，請 API 獲取一次權重存入狀態
                        # 假設 API 有一個 /user/weight/{username} 路由
                        try:
                            w_res = requests.get(f"https://api.enhancement-social.org/user/weight/{username}")
                            st.session_state.user_weight = w_res.json().get("weight", 0)
                        except:
                            st.session_state.user_weight = 0
                        st.rerun()
                    else:
                        st.success("註冊成功！")
                else:
                    st.error(f"操作失敗: {response.json().get('detail', '未知錯誤')}")
            except Exception as e:
                st.error(f"連線失敗: {e}")
    st.stop()

# --- 儀表板主體 ---
st.title("🛰️ GNSS & SDR MISSION CONTROL CENTER")

# 動態計算可輸入點位 (權重 * 0.2)
max_waypoints = max(3, round(st.session_state.user_weight * 0.2))

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ MISSION CONFIGURATION")
    region = st.text_input("📍 TARGET REGION", value="F459")
    system = st.selectbox("📡 GNSS SYSTEM", ["BDS+GPS", "GPS", "BDS", "GLONASS"])
    sampling = st.slider("📊 SAMPLING RATE (MHz)", 1.0, 50.0, 20.8)
    speed = st.number_input("🏃 VELOCITY (km/h)", value=16.5)
    priority = st.slider("⭐ MISSION PRIORITY", 1, 10, 1)
    
    st.markdown(f"**📍 WAYPOINTS (Allowed: {max_waypoints})**")
    for i in range(len(st.session_state.waypoints)):
        st.session_state.waypoints[i] = st.text_input(f"點位 {i+1}", value=st.session_state.waypoints[i], key=f"wp_{i}")
    
    if len(st.session_state.waypoints) < max_waypoints:
        if st.button("➕ 新增點位"):
            st.session_state.waypoints.append("")
            st.rerun()

    if st.button("🚀 INITIATE SIGNAL SIMULATION"):
        payload = {
            "username": st.session_state.username,
            "region_name": region,
            "gnss_system": system,
            "sampling_rate": sampling,
            "speed_kmh": speed,
            "priority": priority,
            "waypoints": [w for w in st.session_state.waypoints if w],
            "start_time": datetime.now(timezone.utc).isoformat()
        }
        # 405 修正：確保網址最後有 /，方法為 POST
        try:
            response = requests.post("https://api.enhancement-social.org/tasks/", json=payload)
            if response.status_code == 200:
                st.success("任務部署成功")
            else:
                st.error(f"伺服器回應錯誤: {response.status_code}")
        except Exception as e:
            st.error(f"連線失敗: {e}")

with col2:
    st.subheader("📊 LIVE DATA TELEMETRY")
    try:
        response = requests.get("https://api.enhancement-social.org/tasks/")
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                st.table(pd.DataFrame(data))
    except:
        st.error("API 連線錯誤")

if st.button("🚪 LOGOUT"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()
