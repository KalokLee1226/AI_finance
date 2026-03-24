from fastapi import APIRouter
import requests
from bs4 import BeautifulSoup

router = APIRouter(prefix="/api")

HEADERS = {"User-Agent": "Mozilla/5.0"}

# 新闻源配置
NEWS_SOURCES = [
    {"name": "BBC News", "url": "https://www.bbc.com/news/business", "main_tag": "h3"},
    {"name": "The Guardian", "url": "https://www.theguardian.com/business", "main_tag": "h3"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/economy", "main_tag": "h3"},
    {"name": "DW", "url": "https://www.dw.com/en/business", "main_tag": "h2"},
    {"name": "Associated Press", "url": "https://apnews.com/business", "main_tag": "h3"}
]

def scrape_news(source, limit=5):
    news_list = []
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=5)
        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.find_all(source["main_tag"], limit=limit)
        for a in articles:
            title = a.get_text().strip()
            link_tag = a.find_parent("a")
            url_link = link_tag['href'] if link_tag else None
            if url_link and url_link.startswith("/"):
                # 补全相对链接
                if "bbc.com" in source["url"]:
                    url_link = f"https://www.bbc.com{url_link}"
                elif "theguardian.com" in source["url"]:
                    url_link = f"https://www.theguardian.com{url_link}"
            if len(title) > 15:
                news_list.append({
                    "title": title,
                    "source": source["name"],
                    "url": url_link,
                    "time": None  # 可以进一步解析发布时间
                })
    except Exception as e:
        print(f"{source['name']} 抓取失败:", e)
    return news_list

@router.get("/news")
async def get_news():
    all_news = []
    # 先抓主源（前两个）
    for src in NEWS_SOURCES[:2]:
        news = scrape_news(src)
        all_news.extend(news)
    # 如果新闻条数 <5，则用备用源填充
    if len(all_news) < 5:
        for src in NEWS_SOURCES[2:]:
            news = scrape_news(src)
            all_news.extend(news)
            if len(all_news) >= 5:
                break
    # 最终返回最多 10 条新闻
    return {"news": all_news[:10]}