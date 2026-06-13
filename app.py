import streamlit as st
import hashlib # 用於加密密碼

# 簡易密碼加密函式
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 狀態管理
if "auth" not in st.session_state: st.session_state.auth = False
if "mode" not in st.session_state: st.session_state.mode = "Login"

if not st.session_state.auth:
    st.title("🛰️ MISSION CONTROL ACCESS")
    
    # 模式切換
    tab = st.radio("選擇模式", ["Login", "Register"], horizontal=True)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if tab == "Login":
        if st.button("LOGIN"):
            # 這裡呼叫你的 API 去驗證帳密
            # response = requests.post("https://api.enhancement-social.org/auth/login", ...)
            st.success("登入驗證中...")
            
    elif tab == "Register":
        if st.button("REGISTER"):
            # 這裡呼叫你的 API 去寫入新使用者
            # hashed_pw = hash_password(password)
            # response = requests.post("https://api.enhancement-social.org/auth/register", ...)
            st.info("註冊請求已發送至資料庫")
            
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
