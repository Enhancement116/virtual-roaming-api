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
                        
                        # 登入成功後，嚴格獲取權重並強制轉為整數
                        try:
                            w_res = requests.get(f"https://api.enhancement-social.org/user/weight/{username}", timeout=5)
                            if w_res.status_code == 200:
                                st.session_state.user_weight = int(w_res.json().get("weight", 0))
                            else:
                                st.session_state.user_weight = 0
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

# ==========================================
# --- ADMIN CONTROL PANEL (超級管理員區塊) ---
# ==========================================
if st.session_state.user_weight >= 999:
    st.divider()
    st.title("👑 SUPER ADMIN CONTROL PANEL")
    st.markdown("歡迎登入，您擁有最高系統權限。您可以在此監控營運數據並直接修改底層資料庫。")
    
    try:
        # 取得最詳細的資料 (呼叫後端 Admin 專屬路由)
        task_res = requests.get("https://api.enhancement-social.org/admin/tasks/")
        user_res = requests.get("https://api.enhancement-social.org/admin/users/")
        
        if task_res.status_code == 200 and user_res.status_code == 200:
            tasks_data = task_res.json().get("data", [])
            users_data = user_res.json().get("data", [])
            
            df_tasks = pd.DataFrame(tasks_data)
            df_users = pd.DataFrame(users_data)
            
            # --- 📊 數據分析區塊 ---
            st.subheader("📊 系統營運數據分析")
            if not df_tasks.empty:
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("**📡 使用者 GNSS 系統偏好**")
                    system_counts = df_tasks['gnss_system'].value_counts()
                    st.bar_chart(system_counts)
                    
                with col_b:
                    st.markdown("**🕒 任務執行時段熱區 (UTC 小時)**")
                    # 安全地解析時間並提取小時
                    df_tasks['parsed_time'] = pd.to_datetime(df_tasks['start_time'], errors='coerce')
                    df_tasks['hour'] = df_tasks['parsed_time'].dt.hour
                    hourly_counts = df_tasks['hour'].value_counts().sort_index()
                    st.line_chart(hourly_counts)
                    
                    # 清理暫時用來分析的欄位，以免干擾下方的編輯器
                    df_tasks = df_tasks.drop(columns=['parsed_time', 'hour'])
            else:
                st.info("目前尚無任務數據可供分析。")

            st.divider()

            # --- 📝 即時資料庫編輯區塊 ---
            st.subheader("📝 核心資料庫編輯 (Database Inline Editor)")
            
            tab1, tab2 = st.tabs(["🛰️ 任務管理 (roaming_tasks)", "👥 帳號管理 (users)"])
            
            with tab1:
                st.markdown("您可以直接修改數值、勾選左側刪除，或在最下方新增一筆資料。")
                edited_tasks = st.data_editor(df_tasks, num_rows="dynamic", use_container_width=True, key="task_editor")
                if st.button("💾 儲存任務修改 (Save Tasks)"):
                    payload = edited_tasks.to_dict(orient="records")
                    # 將時間格式轉回字串，避免 JSON 序列化報錯
                    for row in payload:
                        if isinstance(row.get('start_time'), pd.Timestamp):
                            row['start_time'] = row['start_time'].isoformat()
                            
                    res = requests.patch("https://api.enhancement-social.org/admin/tasks/upsert/", json=payload)
                    if res.status_code == 200:
                        st.success("✅ 任務資料庫已更新！")
                        st.rerun()
                    else:
                        st.error(f"更新失敗: {res.text}")

            with tab2:
                st.markdown("您可以修改使用者的權重 (weight) 或啟用狀態 (is_active)。")
                edited_users = st.data_editor(df_users, num_rows="dynamic", use_container_width=True, key="user_editor")
                if st.button("💾 儲存帳號修改 (Save Users)"):
                    payload = edited_users.to_dict(orient="records")
                    res = requests.patch("https://api.enhancement-social.org/admin/users/upsert/", json=payload)
                    if res.status_code == 200:
                        st.success("✅ 帳號資料庫已更新！")
                        st.rerun()
                    else:
                        st.error(f"更新失敗: {res.text}")

        else:
            st.error("無法取得管理員資料，請確認後端 API 是否已更新。")
    except Exception as e:
        st.error(f"管理面板發生錯誤: {e}")

st.divider()
if st.button("🚪 LOGOUT"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()
