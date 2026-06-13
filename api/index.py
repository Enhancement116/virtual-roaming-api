import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 初始化 FastAPI
app = FastAPI()

# 初始化 Supabase 客戶端
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# --- 定義資料模型 ---
# 這裡定義了我們要接收的「漫遊任務」資料格式
class RoamingTask(BaseModel):
    region_name: str
    gnss_system: str
    sampling_rate: float
    speed_kmh: float

# --- API 路由 ---

@app.get("/")
def read_root():
    return {"message": "虛擬漫遊系統 API 運作中！"}

# 新增任務的 API (POST 請求)
@app.post("/tasks/")
def create_task(task: RoamingTask):
    try:
        # 將前端傳來的資料 (task) 轉換成字典，並寫入 supabase 的 roaming_tasks 表格
        # supabase-python 新版使用 model_dump() 來轉換 pydantic 模型
        data = supabase.table("roaming_tasks").insert(task.model_dump()).execute()
        
        return {
            "status": "success",
            "message": "漫遊任務已成功新增！",
            "data": data.data
        }
    except Exception as e:
        # 如果發生錯誤，回傳 400 錯誤碼與錯誤訊息
        raise HTTPException(status_code=400, detail=f"寫入資料庫失敗：{e}")
# 在 create_task 函式下方加入這個 GET 路由
@app.get("/tasks/")
def get_tasks():
    try:
        # 直接拿全部資料，不指定排序，或者你可以用 id 排序
        response = supabase.table("roaming_tasks").select("*").execute()
        return {
            "status": "success",
            "data": response.data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"讀取資料庫失敗：{e}")