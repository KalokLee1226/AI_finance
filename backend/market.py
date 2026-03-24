from fastapi import APIRouter, HTTPException
import yfinance as yf
import pandas as pd
import logging
from cachetools import TTLCache, cached

# 初始化路由
router = APIRouter(prefix="/api")

# TTL 缓存：最多缓存 10 个商品，每个缓存 600 秒（10 分钟）
market_cache = TTLCache(maxsize=10, ttl=600)

# 商品映射
mapping = {
    "GOLD": "GC=F",
    "OIL": "CL=F",
    "SILVER": "SI=F"
}

@cached(market_cache)
def fetch_market_data(ticker_symbol: str) -> pd.DataFrame:
    """
    从 Yahoo Finance 下载数据，并返回 DataFrame。
    缓存保证同一商品 10 分钟内不会重复下载。
    """
    try:
        data = yf.download(ticker_symbol, period="3mo", interval="1d")
    except Exception as e:
        logging.error(f"Yahoo Finance 网络错误: {ticker_symbol}, {str(e)}")
        raise HTTPException(status_code=502, detail=f"无法获取 {ticker_symbol} 数据，网络异常")

    if data is None or data.empty:
        raise HTTPException(status_code=404, detail=f"{ticker_symbol} 数据为空")

    # 处理 MultiIndex 列
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # 确认关键列存在
    for col in ['Open', 'Close', 'High', 'Low', 'Volume']:
        if col not in data.columns:
            raise HTTPException(status_code=500, detail=f"数据列缺失: {col}")

    # 计算均线
    data['MA5'] = data['Close'].rolling(5).mean().round(2)
    data['MA10'] = data['Close'].rolling(10).mean().round(2)
    data['MA20'] = data['Close'].rolling(20).mean().round(2)

    return data

@router.get("/market-data/{symbol}")
async def get_market_data(symbol: str):
    """
    获取 K 线图数据，包含移动平均线 (MA)。
    返回格式：
    {
        "dates": [...],
        "kline": [[open, close, low, high], ...],
        "volumes": [...],
        "ma5": [...],
        "ma10": [...],
        "ma20": [...]
    }
    """
    ticker_symbol = mapping.get(symbol.upper())
    if not ticker_symbol:
        raise HTTPException(status_code=400, detail=f"不支持的商品符号: {symbol}")

    try:
        data = fetch_market_data(ticker_symbol)

        # 向量化构建 JSON
        dates = data.index.strftime("%Y-%m-%d").tolist()
        kline = data[['Open', 'Close', 'Low', 'High']].round(2).values.tolist()
        volumes = data['Volume'].astype(int).tolist()

        # 均线处理 NaN -> None
        ma5 = [v if pd.notna(v) else None for v in data['MA5']]
        ma10 = [v if pd.notna(v) else None for v in data['MA10']]
        ma20 = [v if pd.notna(v) else None for v in data['MA20']]

        return {
            "dates": dates,
            "kline": kline,
            "volumes": volumes,
            "ma5": ma5,
            "ma10": ma10,
            "ma20": ma20
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Market Data Error: {symbol}, {str(e)}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")