try:
    import investpy
except ImportError:
    investpy = None
from fastapi import APIRouter, HTTPException, Query
import yfinance as yf
import akshare as ak
import pandas as pd
import logging
from cachetools import TTLCache, cached


# 降低 yfinance 内部日志噪音：只保留严重错误
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

router = APIRouter(prefix="/api")

# 缓存（10分钟）
market_cache = TTLCache(maxsize=10, ttl=600)

# 商品映射
# 商品映射（支持多品种/多市场）
mapping = {
    # 大宗商品
    "GOLD": {"yahoo": "GC=F", "ak": "au0", "investpy": "gold"},
    "SILVER": {"yahoo": "SI=F", "ak": "ag0", "investpy": "silver"},
    "OIL": {"yahoo": "CL=F", "ak": "sc0", "investpy": "crude oil"},
    "COPPER": {"yahoo": "HG=F", "ak": "cu0", "investpy": "copper"},
    "ALUMINUM": {"yahoo": "ALI=F", "ak": "al0", "investpy": "aluminum"},
    "IRON": {"yahoo": None, "ak": "i0", "investpy": None},
    # 农产品
    "CORN": {"yahoo": "ZC=F", "ak": "c0", "investpy": "corn"},
    "SOYBEAN": {"yahoo": "ZS=F", "ak": "a0", "investpy": "soybeans"},
    # 加密货币
    "BTC": {"yahoo": "BTC-USD", "ak": None, "investpy": None},
    "ETH": {"yahoo": "ETH-USD", "ak": None, "investpy": None},
    # 外汇（已移除EURUSD、USDINDEX，因数据源不可用）
    # 股指
    "NDX": {"yahoo": "^NDX", "ak": None, "investpy": "nasdaq 100"},
    "SP500": {"yahoo": "^GSPC", "ak": None, "investpy": "s&p 500"},
    "HSI": {"yahoo": "^HSI", "ak": None, "investpy": "hang seng"},
}



@cached(market_cache)
def fetch_market_data(symbol: str, period: str = 'day') -> pd.DataFrame:
    '''Multi-market/multi-symbol market data API: yfinance > investpy > akshare fallback.'''
    code_ak = mapping[symbol]["ak"] if isinstance(mapping[symbol], dict) and "ak" in mapping[symbol] else None
    code_yahoo = mapping[symbol]["yahoo"] if isinstance(mapping[symbol], dict) and "yahoo" in mapping[symbol] else mapping[symbol]
    code_investpy = mapping[symbol]["investpy"] if isinstance(mapping[symbol], dict) and "investpy" in mapping[symbol] else None
    data = None
    # 1. yfinance 国际行情（代理环境下优先）
    try:
        data = yf.download(
            code_yahoo,
            period="3mo",
            interval="1d",
            progress=False
        )
    except Exception as e:
        # 非致命：后续会尝试 investpy/akshare 兜底
        logging.info(f"yfinance获取{symbol}失败: {str(e)}")
        data = None
    # 2. investpy 国际行情（如可用）
    if (data is None or data.empty) and investpy is not None and code_investpy:
        try:
            if symbol in ["GOLD", "SILVER", "OIL", "COPPER", "ALUMINUM", "CORN", "SOYBEAN"]:
                df = investpy.get_commodity_historical_data(commodity=code_investpy, from_date='01/01/2023', to_date=None, interval='Daily')
            elif symbol in ["NDX", "SP500", "HSI"]:
                df = investpy.get_index_historical_data(index=code_investpy, country=None, from_date='01/01/2023', to_date=None, interval='Daily')
            else:
                df = None
            if df is not None:
                df = df.rename(columns={"Open": "Open", "Close": "Close", "High": "High", "Low": "Low", "Volume": "Volume"})
                df["Date"] = pd.to_datetime(df.index)
                df = df.set_index("Date")
                data = df
        except Exception as e:
            logging.info(f"investpy获取{symbol}失败: {str(e)}")
            data = None
    # 3. akshare 国内合约兜底
    if data is None or data.empty:
        try:
            if code_ak:
                df = ak.futures_zh_daily_sina(symbol=code_ak)
                df = df.rename(columns={"date": "Date", "open": "Open", "close": "Close", "high": "High", "low": "Low", "volume": "Volume"})
                df["Date"] = pd.to_datetime(df["Date"])
                df = df.set_index("Date")
                data = df
            else:
                data = None
        except Exception as e:
            logging.info(f"akshare获取{symbol}失败: {str(e)}")
            data = None
    if data is None or data.empty:
        raise HTTPException(status_code=404, detail="数据为空")
    # 处理 MultiIndex
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    # 标准化字段顺序和类型
    data = data.sort_index()
    # 周期聚合
    if period == 'week':
        data = data.resample('W').agg({
            'Open': 'first',
            'Close': 'last',
            'High': 'max',
            'Low': 'min',
            'Volume': 'sum'
        })
    elif period == 'month':
        data = data.resample('M').agg({
            'Open': 'first',
            'Close': 'last',
            'High': 'max',
            'Low': 'min',
            'Volume': 'sum'
        })
    # 只取近90条
    if len(data) > 90:
        data = data.iloc[-90:]
    # 补齐Volume
    if 'Volume' not in data.columns:
        data['Volume'] = 0
    # 保证所有字段为float或int
    for col in ['Open', 'Close', 'High', 'Low', 'Volume']:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
        else:
            data[col] = 0
    # 检查必要列
    required_cols = ['Open', 'Close', 'High', 'Low', 'Volume']
    for col in required_cols:
        if col not in data.columns:
            raise HTTPException(status_code=500, detail=f"缺少列: {col}")
    # 计算均线
    data['MA5'] = data['Close'].rolling(5).mean().round(2)
    data['MA10'] = data['Close'].rolling(10).mean().round(2)
    data['MA20'] = data['Close'].rolling(20).mean().round(2)

    # 计算 RSI(14)
    try:
        delta = data['Close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14, min_periods=14).mean()
        avg_loss = loss.rolling(window=14, min_periods=14).mean()
        rs = avg_gain / avg_loss.replace(0, pd.NA)
        rsi = 100 - (100 / (1 + rs))
        data['RSI14'] = rsi.round(2)
    except Exception as e:
        logging.warning(f"计算RSI失败: {e}")
        data['RSI14'] = pd.NA

    # 计算 MACD(12,26,9)
    try:
        ema12 = data['Close'].ewm(span=12, adjust=False).mean()
        ema26 = data['Close'].ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        data['MACD'] = macd.round(4)
        data['MACD_SIGNAL'] = signal.round(4)
        data['MACD_HIST'] = hist.round(4)
    except Exception as e:
        logging.warning(f"计算MACD失败: {e}")
        data['MACD'] = pd.NA
        data['MACD_SIGNAL'] = pd.NA
        data['MACD_HIST'] = pd.NA

    # 计算 Bollinger Bands(20, 2σ)
    try:
        mid = data['Close'].rolling(window=20, min_periods=20).mean()
        std = data['Close'].rolling(window=20, min_periods=20).std()
        upper = mid + 2 * std
        lower = mid - 2 * std
        data['BOLL_UPPER'] = upper.round(2)
        data['BOLL_LOWER'] = lower.round(2)
    except Exception as e:
        logging.warning(f"计算BOLL失败: {e}")
        data['BOLL_UPPER'] = pd.NA
        data['BOLL_LOWER'] = pd.NA
    # 保证index为升序日期
    data = data.reset_index().set_index('Date')
    data = data.sort_index()
    return data



@router.get("/market-data/{symbol}")
async def get_market_data(symbol: str, period: str = Query('day', enum=['day','week','month'])):

    symbol = symbol.upper()

    if symbol not in mapping:
        return {
            "dates": [],
            "kline": [],
            "volumes": [],
            "ma5": [],
            "ma10": [],
            "ma20": [],
            "error": f"不支持的商品: {symbol}"
        }

    try:
        data = fetch_market_data(symbol, period)

        dates = data.index.strftime("%Y-%m-%d").tolist()
        kline = data[['Open', 'Close', 'Low', 'High']].round(2).values.tolist()
        volumes = data['Volume'].fillna(0).astype(int).tolist()
        ma5 = [v if pd.notna(v) else None for v in data['MA5']]
        ma10 = [v if pd.notna(v) else None for v in data['MA10']]
        ma20 = [v if pd.notna(v) else None for v in data['MA20']]

        # 额外技术指标
        rsi14 = [float(v) if pd.notna(v) else None for v in data.get('RSI14', pd.Series([pd.NA] * len(data)))]
        macd = [float(v) if pd.notna(v) else None for v in data.get('MACD', pd.Series([pd.NA] * len(data)))]
        macd_signal = [float(v) if pd.notna(v) else None for v in data.get('MACD_SIGNAL', pd.Series([pd.NA] * len(data)))]
        macd_hist = [float(v) if pd.notna(v) else None for v in data.get('MACD_HIST', pd.Series([pd.NA] * len(data)))]
        boll_upper = [float(v) if pd.notna(v) else None for v in data.get('BOLL_UPPER', pd.Series([pd.NA] * len(data)))]
        boll_lower = [float(v) if pd.notna(v) else None for v in data.get('BOLL_LOWER', pd.Series([pd.NA] * len(data)))]

        return {
            "dates": dates,
            "kline": kline,
            "volumes": volumes,
            "ma5": ma5,
            "ma10": ma10,
            "ma20": ma20,
            "rsi14": rsi14,
            "macd": macd,
            "macd_signal": macd_signal,
            "macd_hist": macd_hist,
            "boll_upper": boll_upper,
            "boll_lower": boll_lower,
            "error": None
        }

    except Exception as e:
        logging.error(f"Market Data Error: {symbol}, {str(e)}")
        return {
            "dates": [],
            "kline": [],
            "volumes": [],
            "ma5": [],
            "ma10": [],
            "ma20": [],
            "error": f"行情数据获取失败: {str(e)}"
        }


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