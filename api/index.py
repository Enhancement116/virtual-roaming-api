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
        supabase.table("users").insert({
            "username": username,
            "password_hash": hash_password(password),
            "is_active": False
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
        
    return {"status": "success"}

# --- 任務路由 ---
@app.post("/tasks/")
async def create_task(task: dict):
    try:
        response = supabase.table("roaming_tasks").insert(task).execute()
        return {"status": "success", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tasks/")
async def get_tasks():
    response = supabase.table("roaming_tasks").select("*").execute()
    return {"data": response.data}
