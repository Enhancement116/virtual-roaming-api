import streamlit as st
import hashlib
import requests
import pandas as pd

# 頁面配置
st.set_page_config(page_title="Mission Control", layout="wide")

# 加密函式
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 狀態管理
if "auth" not in st.session_state:
    st.session_state.auth = False

# --- 認證頁面 ---
if not st.session_state.auth:
    st.title("🛰️ MISSION CONTROL ACCESS")
    tab = st.radio("選擇模式", ["Login", "Register"], horizontal=True)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if tab == "Login":
        if st.button("LOGIN"):
            if not username or not password:
                st.warning("⚠️ 請輸入帳號與密碼")
            else:
                try:
                    response = requests.post("https://api.enhancement-social.org/auth/login", 
                                           json={"username": username, "password": password})
                    if response.status_code == 200:
                        st.session_state.auth = True
                        st.rerun()
                    else:
                        st.error(f"登入失敗: {response.json().get('detail', '未知錯誤')}")
                except Exception:
                    st.error("無法連接至認證伺服器")
    
    elif tab == "Register":
        if st.button("REGISTER"):
            if not username or not password:
                st.warning("⚠️ 請輸入帳號與密碼")
            else:
                with st.status("正在處理註冊請求...", expanded=True) as status:
                    try:
                        response = requests.post("https://api.enhancement-social.org/auth/register", 
                                               json={"username": username, "password": password})
                        if response.status_code == 200:
                            status.update(label="✅ 註冊申請已送出！", state="complete")
                            st.success("請聯繫系統管理員以獲取存取權限。")
                        else:
                            status.update(label="❌ 註冊失敗", state="error")
                            st.error(f"錯誤: {response.json().get('detail', '未知錯誤')}")
                    except Exception:
                        status.update(label="⚠️ 連線中斷", state="error")
                        st.error("無法連接至認證伺服器。")
    st.stop()

# --- 儀表板主體 (只有認證後可見) ---
st.title("🛰️ GNSS & SDR MISSION CONTROL CENTER")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ MISSION CONFIGURATION")
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
        response = requests.get("https://api.enhancement-social.org/tasks/")
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                st.dataframe(pd.DataFrame(data), use_container_width=True)
            else:
                st.info("目前無活動任務")
        else:
            st.error("無法取得數據")
    except:
        st.error("API 連線錯誤")

if st.button("🚪 LOGOUT"):
    st.session_state.auth = False
    st.rerun()

st.markdown("---")
st.caption("AUTHORIZED ACCESS ONLY | SYSTEM OPERATIONAL")
