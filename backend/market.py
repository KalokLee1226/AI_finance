from fastapi import APIRouter, HTTPException
import yfinance as yf
import pandas as pd
import logging
from cachetools import TTLCache, cached

router = APIRouter(prefix="/api")

# 缓存（10分钟）
market_cache = TTLCache(maxsize=10, ttl=600)

# 商品映射
mapping = {
    "GOLD": "GC=F",
    "OIL": "CL=F",
    "SILVER": "SI=F"
}


@cached(market_cache)
def fetch_market_data(symbol: str) -> pd.DataFrame:
    """
    从 Yahoo Finance 获取商品数据
    """

    ticker_symbol = mapping[symbol]

    try:
        data = yf.download(
            ticker_symbol,
            period="3mo",
            interval="1d",
            progress=False
        )
    except Exception as e:
        logging.error(f"Yahoo Finance 网络错误: {ticker_symbol}, {str(e)}")
        raise HTTPException(status_code=502, detail="数据源连接失败")

    if data is None or data.empty:
        raise HTTPException(status_code=404, detail="数据为空")

    # 处理 MultiIndex
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # 检查必要列
    required_cols = ['Open', 'Close', 'High', 'Low', 'Volume']
    for col in required_cols:
        if col not in data.columns:
            raise HTTPException(status_code=500, detail=f"缺少列: {col}")

    # 计算均线
    data['MA5'] = data['Close'].rolling(5).mean().round(2)
    data['MA10'] = data['Close'].rolling(10).mean().round(2)
    data['MA20'] = data['Close'].rolling(20).mean().round(2)

    return data


def analyze_trend(data: pd.DataFrame):
    """
    根据均线判断趋势
    """
    ma5 = data['MA5'].iloc[-1]
    ma20 = data['MA20'].iloc[-1]

    if pd.isna(ma5) or pd.isna(ma20):
        return {
            "trend": "Unknown",
            "reason": "Not enough data"
        }

    if ma5 > ma20:
        return {
            "trend": "Bullish",
            "reason": "MA5 above MA20"
        }
    elif ma5 < ma20:
        return {
            "trend": "Bearish",
            "reason": "MA5 below MA20"
        }
    else:
        return {
            "trend": "Sideways",
            "reason": "MA5 equals MA20"
        }


@router.get("/market-data/{symbol}")
async def get_market_data(symbol: str):

    symbol = symbol.upper()

    if symbol not in mapping:
        raise HTTPException(status_code=400, detail=f"不支持的商品: {symbol}")

    try:
        data = fetch_market_data(symbol)

        dates = data.index.strftime("%Y-%m-%d").tolist()
        kline = data[['Open', 'Close', 'Low', 'High']].round(2).values.tolist()
        volumes = data['Volume'].fillna(0).astype(int).tolist()
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
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/market-signal/{symbol}")
async def get_market_signal(symbol: str):

    symbol = symbol.upper()

    if symbol not in mapping:
        raise HTTPException(status_code=400, detail=f"不支持的商品: {symbol}")

    try:
        data = fetch_market_data(symbol)
        signal = analyze_trend(data)

        return {
            "symbol": symbol,
            "trend": signal["trend"],
            "reason": signal["reason"]
        }

    except Exception as e:
        logging.error(f"Signal Error: {symbol}, {str(e)}")
        raise HTTPException(status_code=500, detail="趋势分析失败")