from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
import hashlib

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 Supabase
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# 加密函式
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
        # 新增帳號時，預設權重 weight 為 0
        supabase.table("users").insert({
            "username": username,
            "password_hash": hash_password(password),
            "is_active": False,
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
    
    if not user.data[0]["is_active"]:
        raise HTTPException(status_code=403, detail="帳號尚未被啟用")
        
    return {"status": "success", "username": username}

# --- 任務路由 (具備插隊權重功能) ---
@app.post("/tasks/")
async def create_task(task: dict):
    username = task.get("username")
    
    # 1. 取得發起人的權重
    user_res = supabase.table("users").select("weight").eq("username", username).execute()
    weight = user_res.data[0]["weight"] if user_res.data else 0
    
    # 2. 將權重寫入任務資料中
    task_data = task.copy()
    task_data["weight"] = weight
    
    try:
        response = supabase.table("roaming_tasks").insert(task_data).execute()
        return {"status": "success", "assigned_weight": weight}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tasks/")
async def get_tasks():
    # 依據 weight 由大到小排序，權重最高者永遠在最上方 (插隊機制)
    response = supabase.table("roaming_tasks").select("region_name, weight").order("weight", desc=True).execute()
    
    # 隱私過濾：只傳回區域名稱與權重等級，不顯示發起人資訊
    sanitized_data = [
        {"region": t["region_name"], "priority": t["weight"]}
        for t in response.data
    ]
    return {"data": sanitized_data}
