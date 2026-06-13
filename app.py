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
            if not username or not password:
                st.warning("⚠️ 請輸入帳號與密碼")
            else:
                try:
                    # 發送請求至後端登入路由
                    response = requests.post("https://api.enhancement-social.org/auth/login", 
                                           json={"username": username, "password": password})
                    if response.status_code == 200:
                        st.session_state.auth = True
                        st.rerun() # 驗證成功後直接進入儀表板
                    else:
                        st.error(f"登入失敗: {response.json().get('detail', '未知錯誤')}")
                except Exception as e:
                    st.error("無法連接至認證伺服器")
            
    # 註冊模式下的回饋機制
    elif tab == "Register":
        if st.button("REGISTER"):
            if not username or not password:
                st.warning("⚠️ 請輸入帳號與密碼")
            else:
                # 使用狀態容器提供明確的反饋
                with st.status("正在加密並上傳資料...", expanded=True) as status:
                    try:
                        response = requests.post("https://api.enhancement-social.org/auth/register", 
                                               json={"username": username, "password": password})
                        
                        if response.status_code == 200:
                            status.update(label="✅ 註冊申請已送出！", state="complete", expanded=False)
                            st.success("請聯繫系統管理員以獲取存取權限。")
                        else:
                            status.update(label="❌ 註冊失敗", state="error")
                            st.error(f"錯誤訊息: {response.json().get('detail', '未知錯誤')}")
                    except Exception as e:
                        status.update(label="⚠️ 連線中斷", state="error")
                        st.error("無法連接至認證伺服器。")
            
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
