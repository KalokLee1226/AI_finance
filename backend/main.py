from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# 优先加载当前目录的 .env，确保 os.getenv 能读到配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path, override=False)

from database import init_db
from auth import router as auth_router
from market import router as market_router
from news import router as news_router
from ai_report import router as ai_router
from user_data import router as user_router
from alerts import router as alerts_router
from predict import router as predict_router

app = FastAPI(title="Global Commodity AI Agent API")

# 初始化数据库
init_db()

# CORS 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)
app.include_router(market_router)
app.include_router(news_router)
app.include_router(ai_router)
app.include_router(user_router)
app.include_router(alerts_router)
app.include_router(predict_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)