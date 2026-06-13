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
            "is_active": True, 
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

# --- 取得使用者權重 (供前端動態解鎖管理員面板與點位) ---
@app.get("/user/weight/{username}")
async def get_user_weight(username: str):
    try:
        res = supabase.table("users").select("weight").eq("username", username).execute()
        weight = res.data[0]["weight"] if res.data else 0
        return {"weight": weight}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- 任務路由 (建立任務) ---
@app.post("/tasks/")
async def create_task(task: dict):
    username = task.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="Missing username")
    
    # 1. 從資料庫獲取真實權重
    user_res = supabase.table("users").select("weight").eq("username", username).execute()
    weight = user_res.data[0]["weight"] if user_res.data else 0
    
    # 2. 處理時間
    start_time = task.get("start_time") or datetime.now(timezone.utc).isoformat()
    
    # 3. 組裝資料 
    task_data = {
        "username": username,
        "region_name": task.get("region_name", "F459"),
        "gnss_system": task.get("gnss_system", "BDS+GPS"),
        "sampling_rate": task.get("sampling_rate", 20.8),
        "speed_kmh": task.get("speed_kmh", 16.5),
        "weight": weight, 
        "priority": task.get("priority", 1),
        "waypoints": task.get("waypoints", []),
        "start_time": start_time 
    }
    
    try:
        # 將資料寫入資料庫
        supabase.table("roaming_tasks").insert(task_data).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
# --- 任務路由 (讀取任務 Telemetry) ---
@app.get("/tasks/")
async def get_tasks():
    try:
        # 撈取所有需要的欄位
        response = supabase.table("roaming_tasks").select("username, weight, start_time").order("weight", desc=True).execute()
        
        sanitized_data = []
        if response.data:
            for t in response.data:
                raw_time = t.get("start_time")
                formatted_time = str(raw_time)[:19].replace("T", " ") if raw_time else "N/A"
                
                sanitized_data.append({
                    "WHO": t.get("username", "Unknown"),
                    "TIME": formatted_time,
                    "Priority": t.get("weight", 0)
                })
        
        return {"data": sanitized_data}
    except Exception as e:
        print(f"DEBUG ERROR: {e}") 
        raise HTTPException(status_code=500, detail=str(e))

# --- 任務路由 (超級管理員更新任務權重) ---
@app.patch("/tasks/update/")
async def update_tasks(data: list):
    try:
        # 遍歷前端傳來的所有資料列進行更新
        for item in data:
            username = item.get("WHO")
            new_weight = item.get("Priority")
            
            # 若有明確的帳號與權重，則更新對應使用者的任務
            if username is not None and new_weight is not None:
                supabase.table("roaming_tasks")\
                    .update({"weight": new_weight})\
                    .eq("username", username)\
                    .execute()
                    
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
