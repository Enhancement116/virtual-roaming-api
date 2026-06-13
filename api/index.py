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
    username = task.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="Missing username")
    
    # 從資料庫獲取權重
    user_res = supabase.table("users").select("weight").eq("username", username).execute()
    weight = user_res.data[0]["weight"] if user_res.data else 0
    
    # 這裡將時間補上，若前端沒給，則用 UTC 現在時間
    start_time = task.get("start_time") or datetime.now(timezone.utc).isoformat()
    
    task_data = {
        "username": username, # 存入 username 以便顯示
        "region_name": task.get("region_name", "Unknown"),
        "weight": weight,
        "start_time": start_time,
        "waypoints": task.get("waypoints", [])
    }
    
    try:
        supabase.table("roaming_tasks").insert(task_data).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@app.get("/tasks/")
async def get_tasks():
    response = supabase.table("roaming_tasks").select("username, weight, start_time").order("weight", desc=True).execute()
    
    sanitized_data = []
    for t in response.data:
        sanitized_data.append({
            "WHO": t.get("username", "Unknown"), # 顯示真實帳號名稱
            "TIME": str(t.get("start_time", ""))[:19].replace("T", " "), # 顯示格式化時間
            "Priority": t.get("weight", 0)
        })
    return {"data": sanitized_data}
