# expert_views.py
import feedparser
import asyncio
import logging
from fastapi import APIRouter

logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/expert", tags=["Expert Views"])

# 可稳定抓取的 RSS 源
RSS_SOURCES = [
    {"name": "OilPrice", "url": "https://oilprice.com/rss/main"},
    # 可以继续添加其他源
]

async def fetch_single_source(source, limit=10):
    """抓取单个 RSS 源"""
    results = []
    try:
        feed = feedparser.parse(source["url"])
        if feed.bozo:
            logging.warning(f"RSS 解析异常: {source['name']} - {feed.bozo_exception}")

        for entry in feed.entries[:limit]:
            results.append({
                "source": source["name"],
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "published": entry.get("published", "")
            })
    except Exception as e:
        logging.error(f"抓取 {source['name']} 出错: {e}")
        results.append({
            "source": source["name"],
            "error": str(e)
        })
    return results

async def fetch_expert_opinions(limit=10):
    """异步抓取所有 RSS 源"""
    tasks = [fetch_single_source(source, limit) for source in RSS_SOURCES]
    results = await asyncio.gather(*tasks)
    # flatten list of lists
    all_results = [item for sublist in results for item in sublist]
    return all_results

@router.get("/latest")
async def get_expert_views(limit: int = 10):
    """
    GET /expert/latest?limit=10
    limit: 每个 RSS 源抓取条数，默认 10
    """
    data = await fetch_expert_opinions(limit)
    return {"count": len(data), "opinions": data}