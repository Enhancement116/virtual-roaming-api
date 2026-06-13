from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from passlib.context import CryptContext
import os

app = FastAPI()
# 設定 CORS，確保你的前端 (Streamlit) 可以跨網域存取
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 Supabase 與加密套件
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 1. 任務管理路由
@app.post("/tasks/")
def create_task(task: dict):
    # 執行任務寫入邏輯
    try:
        response = supabase.table("roaming_tasks").insert(task).execute()
        return {"status": "success", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tasks/")
def get_tasks():
    response = supabase.table("roaming_tasks").select("*").execute()
    return {"data": response.data}

# 2. 註冊路由 (密碼加密)
@app.post("/auth/register")
def register_user(user_data: dict):
    username = user_data.get("username")
    password = user_data.get("password")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="請提供帳號與密碼")
    
    # 密碼 Hash 化
    hashed_password = pwd_context.hash(password)
    
    try:
        supabase.table("users").insert({
            "username": username,
            "password_hash": hashed_password,
            "is_active": False # 預設關閉，需管理員啟用
        }).execute()
        return {"status": "success", "message": "註冊成功，等待管理員審核"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="註冊失敗，帳號可能已存在")

# 3. 登入路由 (驗證 Hash)
@app.post("/auth/login")
def login(user_data: dict):
    username = user_data.get("username")
    password = user_data.get("password")
    
    # 撈取使用者
    user = supabase.table("users").select("*").eq("username", username).execute()
    if not user.data:
        raise HTTPException(status_code=401, detail="帳號不存在")
    
    stored_user = user.data[0]
    
    # 比對密碼
    if not pwd_context.verify(password, stored_user["password_hash"]):
        raise HTTPException(status_code=401, detail="密碼錯誤")
    
    if not stored_user.get("is_active"):
        raise HTTPException(status_code=403, detail="帳號尚未被啟用")
        
    return {"status": "success", "message": "登入成功"}
