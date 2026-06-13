import streamlit as st
import hashlib
import requests
import pandas as pd
from datetime import datetime, timezone

st.set_page_config(page_title="Mission Control", layout="wide")

# 初始化 Session State
if "auth" not in st.session_state: st.session_state.auth = False
if "username" not in st.session_state: st.session_state.username = None
if "waypoints" not in st.session_state: st.session_state.waypoints = [""]

# --- 認證頁面 (保持原邏輯) ---
if not st.session_state.auth:
    # ... (登入/註冊邏輯保持不變) ...
    st.stop()

# --- 儀表板主體 ---
st.title("🛰️ GNSS & SDR MISSION CONTROL CENTER")

# 獲取權重 (假設後端有提供 GET /user/weight 或從 login 取得)
# 這裡簡單模擬：實際開發時請從 API 獲取
user_weight = 15 # 假設從 API 取得
max_waypoints = round(user_weight * 0.2) if user_weight >= 10 else 1

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ MISSION CONFIGURATION")
    
    # 動態點位輸入
    st.markdown(f"**📍 WAYPOINTS (Max: {max_waypoints})**")
    for i in range(len(st.session_state.waypoints)):
        st.session_state.waypoints[i] = st.text_input(f"點位 {i+1}", 
                                                      value=st.session_state.waypoints[i], 
                                                      key=f"wp_{i}")
    
    if len(st.session_state.waypoints) < max_waypoints:
        if st.button("➕ 新增點位"):
            st.session_state.waypoints.append("")
            st.rerun()

    if st.button("🚀 INITIATE SIGNAL SIMULATION"):
        payload = {
            "username": st.session_state.username,
            "region_name": "Dynamic_Region",
            "waypoints": [w for w in st.session_state.waypoints if w],
            "start_time": datetime.now(timezone.utc).isoformat()
        }
        try:
            response = requests.post("https://api.enhancement-social.org/tasks/", json=payload)
            if response.status_code == 200:
                st.success("任務部署成功")
            else:
                st.error("伺服器回應錯誤")
        except Exception as e:
            st.error(f"連線失敗: {e}")

with col2:
    st.subheader("📊 LIVE DATA TELEMETRY")
    # 顯示隱私過濾後的數據
    try:
        response = requests.get("https://api.enhancement-social.org/tasks/")
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                st.table(pd.DataFrame(data)) # 顯示 WHO | TIME | Priority
            else:
                st.info("目前無活動任務")
    except:
        st.error("API 連線錯誤")

if st.button("🚪 LOGOUT"):
    st.session_state.auth = False
    st.rerun()
