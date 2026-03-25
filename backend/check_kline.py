# 可用品种K线可用性检测脚本
import requests

backend_url = "http://127.0.0.1:8000/api/market-data/"
commodities = [
    "GOLD", "OIL", "SILVER", "COPPER", "ALUMINUM", "CORN", "SOYBEAN", "BTC", "ETH", "NDX", "SP500", "HSI"
]

for symbol in commodities:
    url = backend_url + symbol
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("dates") and len(data["dates"]) > 0:
            print(f"{symbol}: OK, {len(data['dates'])} bars")
        else:
            print(f"{symbol}: NO DATA, error={data.get('error')}")
    except Exception as e:
        print(f"{symbol}: ERROR, {e}")
