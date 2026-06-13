from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
import hashlib
from datetime import datetime, timezone

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

@app.get("/")
def read_root():
    return {"status": "api_online"}

# --- 認證路由 ---
@app.post("/auth/register")
async def register_user(user_data: dict):
    username = user_data.get("username")
    password = user_data.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="請提供帳號與密碼")
    try:
        supabase.table("users").insert({
            "username": username,
            "password_hash": hash_password(password),
            "is_active": True, # 根據你的設定預設為 True
            "weight": 0 
        }).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
async def login(user_data: dict):
    username = user_data.get("username")
    password = user_data.get("password")
    user = supabase.table("users").select("*").eq("username", username).execute()
    if not user.data or hash_password(password) != user.data[0]["password_hash"]:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    return {"status": "success", "username": username}

# --- 任務路由 (動態點位 + UTC 時間 + 優先權重) ---
@app.post("/tasks/")
async def create_task(task: dict):
    # 確保每個欄位都有值，如果沒有則給予預設值 (避免 NULL)
    task_data = {
        "region_name": task.get("region_name", "Unknown"),
        "gnss_system": task.get("gnss_system", "GPS"),
        "sampling_rate": task.get("sampling_rate", 20.8),
        "speed_kmh": task.get("speed_kmh", 16.5),
        "priority": task.get("priority", 1),
        "weight": task.get("weight", 0),
        "waypoints": task.get("waypoints", []),
        "start_time": task.get("start_time", datetime.now(timezone.utc).isoformat())
    }
    
    try:
        response = supabase.table("roaming_tasks").insert(task_data).execute()
        return {"status": "success", "data": response.data}
    except Exception as e:
        print(f"DEBUG ERROR: {e}") # 檢查這裡的錯誤
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tasks/")
async def get_tasks():
    # 依據 weight 排序實現插隊機制
    response = supabase.table("roaming_tasks").select("region_name, weight, start_time").order("weight", desc=True).execute()
    
    # 隱私過濾：WHO (隱碼) + TIME (UTC) + Priority (權重)
    sanitized_data = [
        {
            "WHO": "User_****", 
            "TIME": t.get("start_time", "")[:19].replace("T", " "), 
            "Priority": t.get("weight")
        }
        for t in response.data
    ]
    return {"data": sanitized_data}
