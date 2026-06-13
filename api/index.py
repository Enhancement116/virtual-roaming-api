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

# 初始化
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# 使用標準庫的 SHA-256 加密
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

@app.get("/")
def read_root():
    return {"status": "api_online"}

@app.post("/auth/register")
async def register_user(user_data: dict):
    username = user_data.get("username")
    password = user_data.get("password")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="請提供帳號與密碼")
    
    # 改用 hashlib 加密
    hashed_password = hash_password(password)
    
    try:
        supabase.table("users").insert({
            "username": username,
            "password_hash": hashed_password,
            "is_active": False
        }).execute()
        return {"status": "success", "message": "註冊成功"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
