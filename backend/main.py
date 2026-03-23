import sqlite3
import hashlib
from fastapi import FastAPI, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
import json
import pandas as pd

app = FastAPI(title="Global Commodity AI Agent API") #创建 FastAPI 实例

# 初始化 SQLite 数据库
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 配置跨域访问（CORS）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration & Keys ---
# User provided Deepseek Key
# 配置 API Key / OpenAI 客户端
DEEPSEEK_API_KEY = "sk-0a2b77e7cb9f469eaa2c585e1013a2df" 
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

# --- Models ---
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ReportRequest(BaseModel):   
    commodity: str


# --- 初始化数据库 ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # 多加一个 salt 字段
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, 
            password TEXT,
            salt TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- 密码哈希函数，带盐 ---
def hash_password(password: str, salt=None):
    # 如果没有提供 salt，就生成一个随机盐
    if not salt:
        salt = os.urandom(16).hex()  # 16 字节随机盐
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed, salt

# --- 注册接口 ---
@app.post("/api/register")
async def register(req: RegisterRequest):
    if len(req.username) < 3 or len(req.password) < 6:
        raise HTTPException(status_code=400, detail="用户名至少3个字符，密码至少6个字符")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (req.username,))
    if c.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    hashed_pw, salt = hash_password(req.password)
    c.execute("INSERT INTO users (username, password, salt) VALUES (?, ?, ?)", 
              (req.username, hashed_pw, salt))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "注册成功，请登录"}

# --- 登录接口 ---
@app.post("/api/login")
async def login(req: LoginRequest):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password, salt FROM users WHERE username=?", (req.username,))
    row = c.fetchone()
    conn.close()
    
    if row:
        stored_hash, salt = row
        if hash_password(req.password, salt)[0] == stored_hash:
            return {"status": "success", "message": "登录成功"}
    
    raise HTTPException(status_code=401, detail="用户名或密码错误")


# 获取市场数据
@app.get("/api/market-data/{symbol}")
async def get_market_data(symbol: str):
    """
    Fetch K-Line data for charts. 
    Symbols mapping: 'GOLD' -> 'GC=F', 'OIL' -> 'CL=F', 'SILVER' -> 'SI=F'
    """
    mapping = {
        "GOLD": "GC=F",
        "OIL": "CL=F",
        "SILVER": "SI=F"
    }
    ticker = mapping.get(symbol.upper())
    if not ticker:
        raise HTTPException(status_code=400, detail="Unsupported symbol")
    
    # Get 3 months of daily data for K-line
    data = yf.download(ticker, period="3mo", interval="1d")
    
    # Calculate Moving Averages for better analysis
    data['MA5'] = data['Close'].rolling(window=5).mean()
    data['MA10'] = data['Close'].rolling(window=10).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()
    
    # Format for ECharts
    kline_data = []
    dates = []
    ma5, ma10, ma20 = [], [], []
    volumes = []
    
    for index, row in data.iterrows():
        dates.append(index.strftime("%Y-%m-%d"))
        # ECharts order: [open, close, lowest, highest]
        kline_data.append([
            round(float(row['Open'].iloc[0] if isinstance(row['Open'], pd.Series) else row['Open']), 2),
            round(float(row['Close'].iloc[0] if isinstance(row['Close'], pd.Series) else row['Close']), 2),
            round(float(row['Low'].iloc[0] if isinstance(row['Low'], pd.Series) else row['Low']), 2),
            round(float(row['High'].iloc[0] if isinstance(row['High'], pd.Series) else row['High']), 2)
        ])
        v_ma5 = row['MA5'].iloc[0] if isinstance(row['MA5'], pd.Series) else row['MA5']
        v_ma10 = row['MA10'].iloc[0] if isinstance(row['MA10'], pd.Series) else row['MA10']
        v_ma20 = row['MA20'].iloc[0] if isinstance(row['MA20'], pd.Series) else row['MA20']
        v_vol = row['Volume'].iloc[0] if isinstance(row['Volume'], pd.Series) else row['Volume']
        
        ma5.append(round(float(v_ma5), 2) if pd.notna(v_ma5) else None)
        ma10.append(round(float(v_ma10), 2) if pd.notna(v_ma10) else None)
        ma20.append(round(float(v_ma20), 2) if pd.notna(v_ma20) else None)
        volumes.append(int(v_vol))
        
    return {
        "dates": dates, 
        "kline": kline_data, 
        "volumes": volumes,
        "ma5": ma5, 
        "ma10": ma10, 
        "ma20": ma20
    }

# 获取新闻
@app.get("/api/news")
async def get_news():
    """
    Simple Web Scraper to get latest global financial news headlines.
    In a real app, you would rotate proxies or use APIs. 
    Here we scrape a public source or return fallback data if blocked.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    news_list = []
    try:
        # Example scraping investing.com commodities news (simplified)
        # Using a reliable fallback if scraping fails due to anti-bot
        url = "https://finance.yahoo.com/topic/commodities"
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Yahoo Finance title tags
        articles = soup.find_all("h3", limit=10)
        for act in articles:
            title = act.get_text().strip()
            if len(title) > 15:
                news_list.append({"title": title, "source": "Yahoo Finance"})
    except Exception as e:
        print(f"Scraping error: {e}")
    
    # Fallback / Mock News (to ensure the dashboard always has data for the AI)
    if len(news_list) < 3:
        news_list = [
            {"title": "OPEC+ keeps oil output cuts in place as global demand concerns persist", "source": "Reuters"},
            {"title": "Gold surges to near all-time highs amid geopolitical tensions in the Middle East", "source": "Bloomberg"},
            {"title": "Silver prices mirror gold rally as industrial demand remains steady", "source": "CNBC"}
        ]
        
    return {"news": news_list}

# AI分析报告
@app.post("/api/generate-report")
async def generate_ai_report(req: ReportRequest):
    """
    Uses Deepseek AI to evaluate news and predict price trends.
    """
    # 1. Fetch latest news
    news_data = await get_news()
    news_titles = [n["title"] for n in news_data["news"]]
    news_context = "\n".join(news_titles)
    
    # 2. Construct AI Prompt
    prompt = f"""
作为一个专业的国际政治与经济分析师（AI智能体），请根据以下最新的国际新闻头条，分析并预测【{req.commodity}】的大宗商品价格走势。

最新新闻素材：
{news_context}

请生成一份结构化的综合分析报告，包括以下部分：
1. **当前宏观局势概览**：基于以上新闻总结当前国际局势与经济情绪。
2. **{req.commodity}市场焦点**：新闻对该商品的直接或间接影响（供需、避险情绪等）。
3. **价格走势预测**：短期（未来1周）和中期（未来1-3个月）的价格走势预判（看涨/看跌/震荡）。
4. **交易建议与风险提示**：给投资者的操作建议及潜在的黑天鹅风险。

要求：分析要有深度，逻辑清晰，行文专业，用中文排版，使用Markdown格式。
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个资深的金融大宗商品分析师智能体。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        report_content = response.choices[0].message.content
        return {"report": report_content, "commodity": req.commodity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Agent Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
