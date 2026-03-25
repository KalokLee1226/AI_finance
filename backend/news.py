
from fastapi import APIRouter
from bs4 import BeautifulSoup
import asyncio
import httpx
import os
import logging
from datetime import datetime
from typing import List, Dict, Any

router = APIRouter(prefix="/api")

HEADERS = {"User-Agent": "Mozilla/5.0"}

# 第三方新闻 API 配置（通过环境变量注入）
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")

# 可选：在某些公司内网/自签名证书环境下，https 校验可能导致抓取失败。
# 如需跳过证书校验，可在 .env 中设置：NEWS_VERIFY_SSL=false
VERIFY_SSL = os.getenv("NEWS_VERIFY_SSL", "true").lower() != "false"

# 聚合新闻的简易内存缓存，减少频繁爬取导致的整体响应延迟
NEWS_CACHE: Dict[str, Any] = {"data": None, "ts": 0.0}
NEWS_CACHE_TTL = int(os.getenv("NEWS_CACHE_TTL", "180"))  # 默认缓存 3 分钟

# 扩展后的新闻源配置（部分网站如付费墙/反爬较强，需后续定制解析）
# 同时包含海外和国内站点，保证在跨境网络不稳定时，至少能拿到一部分国内财经标题。
NEWS_SOURCES = [
    # 海外英文财经/宏观
    {"name": "BBC News", "url": "https://www.bbc.com/news/business", "main_tag": "h3"},
    {"name": "Reuters", "url": "https://www.reuters.com/business", "main_tag": "h2"},
    {"name": "CNBC", "url": "https://www.cnbc.com", "main_tag": "a"},
    {"name": "Yahoo Finance", "url": "https://finance.yahoo.com", "main_tag": "h3"},
    {"name": "CoinDesk", "url": "https://www.coindesk.com", "main_tag": "h4"},
    # 国内中文财经站点（仅抓取标题+链接，不抓正文）
    {"name": "新浪财经要闻", "url": "https://finance.sina.com.cn/roll/index.d.html?cid=56588&page=1", "main_tag": "a"},
    {"name": "东方财富要闻", "url": "https://finance.eastmoney.com/a/cgnjj.html", "main_tag": "a"},
]


async def async_scrape_news(client: httpx.AsyncClient, source: Dict, limit: int = 5) -> List[Dict]:
    """通用 HTML 抓取型新闻源。"""
    news_list: List[Dict] = []
    try:
        resp = await client.get(source["url"], headers=HEADERS, timeout=8.0)
        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.find_all(source["main_tag"], limit=limit)
        for a in articles:
            title = a.get_text().strip()
            link_tag = a.find_parent("a") or a if a.name == "a" else None
            url_link = link_tag["href"] if link_tag and link_tag.has_attr("href") else None
            if url_link and url_link.startswith("/"):
                # 补全相对链接
                if "bbc.com" in source["url"]:
                    url_link = f"https://www.bbc.com{url_link}"
                elif "theguardian.com" in source["url"]:
                    url_link = f"https://www.theguardian.com{url_link}"
                elif "reuters.com" in source["url"]:
                    url_link = f"https://www.reuters.com{url_link}"
                elif "ft.com" in source["url"]:
                    url_link = f"https://www.ft.com{url_link}"
                elif "cnn.com" in source["url"]:
                    url_link = f"https://edition.cnn.com{url_link}"
                elif "sina.com.cn" in source["url"]:
                    url_link = f"https://finance.sina.com.cn{url_link}"
                elif "eastmoney.com" in source["url"]:
                    url_link = f"https://finance.eastmoney.com{url_link}"
            if title and len(title) > 10:
                news_list.append(
                    {
                        "title": title,
                        "source": source["name"],
                        "url": url_link,
                        "time": None,
                    }
                )
    except Exception as e:
        # 单个站点抓取失败不视为错误，只做轻量日志，避免刷屏
        logging.info(f"News scrape failed for {source.get('name')}: {type(e).__name__}")
    return news_list


async def fetch_newsapi(client: httpx.AsyncClient, page_size: int = 10) -> List[Dict]:
    """通过 NewsAPI 获取全球权威媒体的财经类新闻。

    依赖环境变量 NEWSAPI_KEY；若未配置则返回空列表。
    """
    if not NEWSAPI_KEY:
        return []
    url = "https://newsapi.org/v2/everything"
    params = {
        # 关键词可以按需调整，这里偏向大宗商品 / 宏观市场
        "q": "commodities OR gold OR oil OR macro economy",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
        # 尝试聚焦路透、彭博、新华社等域名（具体取决于 NewsAPI 授权范围）
        "domains": "reuters.com,bloomberg.com,xinhuanet.com,finance.yahoo.com",
        "apiKey": NEWSAPI_KEY,
    }
    news_list: List[Dict] = []
    try:
        resp = await client.get(url, params=params, timeout=8.0)
        if resp.status_code != 200:
            print("NewsAPI 调用失败:", resp.status_code, resp.text[:200])
            return []
        data = resp.json()
        for a in data.get("articles", []):
            title = (a.get("title") or "").strip()
            if not title or len(title) <= 10:
                continue
            source_name = (a.get("source") or {}).get("name") or "NewsAPI"
            url_link = a.get("url")
            published = a.get("publishedAt")
            news_list.append(
                {
                    "title": title,
                    "source": source_name,
                    "url": url_link,
                    "time": published,
                }
            )
    except Exception as e:
        print("NewsAPI 抓取失败:", e)
    return news_list


async def fetch_gnews(client: httpx.AsyncClient, max_items: int = 10) -> List[Dict]:
    """通过 GNews 获取商业 / 财经头条。

    依赖环境变量 GNEWS_API_KEY；若未配置则返回空列表。
    """
    if not GNEWS_API_KEY:
        return []
    url = "https://gnews.io/api/v4/top-headlines"
    params = {
        "topic": "business",
        # 使用中文频道，输出更贴近你的阅读习惯
        "lang": "zh",
        "token": GNEWS_API_KEY,
        "max": max_items,
    }
    news_list: List[Dict] = []
    try:
        resp = await client.get(url, params=params, timeout=8.0)
        if resp.status_code != 200:
            print("GNews 调用失败:", resp.status_code, resp.text[:200])
            return []
        data = resp.json()
        for a in data.get("articles", []):
            title = (a.get("title") or "").strip()
            if not title or len(title) <= 10:
                continue
            source_name = (a.get("source") or {}).get("name") or "GNews"
            url_link = a.get("url")
            published = a.get("publishedAt")
            news_list.append(
                {
                    "title": title,
                    "source": source_name,
                    "url": url_link,
                    "time": published,
                }
            )
    except Exception as e:
        print("GNews 抓取失败:", e)
    return news_list


async def gather_all_news(limit_per_source: int = 3, max_total: int = 30) -> List[Dict]:
    """聚合本地 HTML 抓取源 + NewsAPI + GNews 的新闻，统一去重。"""
    # 优先使用缓存，避免每次都全量爬取，降低 /news、/generate-report、/ai-chat 的整体耗时
    now_ts = datetime.utcnow().timestamp()
    if NEWS_CACHE["data"] is not None and now_ts - NEWS_CACHE["ts"] < NEWS_CACHE_TTL:
        return NEWS_CACHE["data"]

    all_news: List[Dict] = []
    async with httpx.AsyncClient(follow_redirects=True, headers=HEADERS, verify=VERIFY_SSL) as client:
        tasks = [async_scrape_news(client, src, limit=limit_per_source) for src in NEWS_SOURCES]
        # 第三方 API 源（按需增加）
        tasks.append(fetch_newsapi(client, page_size=10))
        tasks.append(fetch_gnews(client, max_items=10))
        results = await asyncio.gather(*tasks)
        for news in results:
            all_news.extend(news)

    # 去重（按标题+来源）
    seen = set()
    unique_news: List[Dict] = []
    for n in all_news:
        key = (n.get("title"), n.get("source"))
        if key not in seen and n.get("title"):
            seen.add(key)
            unique_news.append(n)
    # 按时间字段做一个粗略排序（越新的越靠前）。
    # 注意：不同来源的时间字段可能带/不带时区信息，直接返回 datetime
    # 容易触发“can't compare offset-naive and offset-aware datetimes”错误。
    # 这里统一转成时间戳浮点数进行排序，避免类型不一致导致的异常。
    def _parse_time(item: Dict) -> float:
        t = item.get("time")
        if not t:
            return 0.0
        try:
            dt = datetime.fromisoformat(str(t).replace("Z", "+00:00"))
            return dt.timestamp()
        except Exception:
            return 0.0

    try:
        unique_news.sort(key=_parse_time, reverse=True)
    except Exception:
        # 排序失败不应影响主流程，保留原顺序返回
        pass
    # 若所有新闻源都失败，返回一条友好的占位提示，避免前端误以为接口异常
    if not unique_news:
        result = [
            {
                "title": "当前外部新闻源访问异常，暂未获取到最新资讯，请稍后重试。",
                "source": "系统提示",
                "url": None,
                "time": datetime.utcnow().isoformat() + "Z",
            }
        ]
    else:
        result = unique_news[:max_total]

    # 写入缓存
    NEWS_CACHE["data"] = result
    NEWS_CACHE["ts"] = now_ts

    return result


@router.get("/news")
async def get_news():
    news = await gather_all_news()
    return {"news": news}


@router.get("/news-debug")
async def news_debug():
    """新闻源连通性自检接口。

    - 逐个测试 HTML 源（只发 HEAD/GET 请求，不做解析）；
    - 测试 NewsAPI / GNews 接口可用性（若配置了 key）。
    """
    results: Dict[str, Any] = {"verify_ssl": VERIFY_SSL}

    async with httpx.AsyncClient(follow_redirects=True, headers=HEADERS, verify=VERIFY_SSL) as client:
        html_checks = []
        for src in NEWS_SOURCES:
            item = {"name": src.get("name"), "url": src.get("url"), "ok": False, "status": None, "error": None}
            try:
                resp = await client.get(src["url"], timeout=6.0)
                item["status"] = resp.status_code
                item["ok"] = resp.status_code < 400
            except Exception as e:
                item["error"] = f"{type(e).__name__}: {str(e)[:120]}"
            html_checks.append(item)
        results["html_sources"] = html_checks

        # NewsAPI 调试（若配置了 KEY）
        newsapi_result: Dict[str, Any] = {"configured": bool(NEWSAPI_KEY), "ok": False, "status": None, "error": None}
        if NEWSAPI_KEY:
            try:
                resp = await client.get(
                    "https://newsapi.org/v2/top-headlines",
                    params={"apiKey": NEWSAPI_KEY, "pageSize": 1, "language": "en", "category": "business"},
                    timeout=6.0,
                )
                newsapi_result["status"] = resp.status_code
                newsapi_result["ok"] = resp.status_code == 200
                if resp.status_code != 200:
                    # 返回部分错误信息帮助排查（如 401/429）
                    newsapi_result["error"] = resp.text[:200]
            except Exception as e:
                newsapi_result["error"] = f"{type(e).__name__}: {str(e)[:200]}"
        results["newsapi"] = newsapi_result

        # GNews 调试（若配置了 KEY）
        gnews_result: Dict[str, Any] = {"configured": bool(GNEWS_API_KEY), "ok": False, "status": None, "error": None}
        if GNEWS_API_KEY:
            try:
                resp = await client.get(
                    "https://gnews.io/api/v4/top-headlines",
                    params={"token": GNEWS_API_KEY, "max": 1, "topic": "business", "lang": "zh"},
                    timeout=6.0,
                )
                gnews_result["status"] = resp.status_code
                gnews_result["ok"] = resp.status_code == 200
                if resp.status_code != 200:
                    gnews_result["error"] = resp.text[:200]
            except Exception as e:
                gnews_result["error"] = f"{type(e).__name__}: {str(e)[:200]}"
        results["gnews"] = gnews_result

    return results