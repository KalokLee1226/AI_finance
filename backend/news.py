from fastapi import APIRouter
import requests
from bs4 import BeautifulSoup

router = APIRouter(prefix="/api")


@router.get("/news")
async def get_news():
    """
    获取最新大宗商品相关新闻
    """

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    news_list = []

    try:
        url = "https://finance.yahoo.com/topic/commodities"

        response = requests.get(url, headers=headers, timeout=5)

        soup = BeautifulSoup(response.text, "html.parser")

        articles = soup.find_all("h3", limit=10)

        for act in articles:
            title = act.get_text().strip()

            if len(title) > 15:
                news_list.append({
                    "title": title,
                    "source": "Yahoo Finance"
                })

    except Exception as e:
        print("Scraping error:", e)

    # 如果爬取失败，用备用数据
    if len(news_list) < 3:
        news_list = [
            {"title": "OPEC+ keeps oil output cuts in place as global demand concerns persist", "source": "Reuters"},
            {"title": "Gold surges to near all-time highs amid geopolitical tensions in the Middle East", "source": "Bloomberg"},
            {"title": "Silver prices mirror gold rally as industrial demand remains steady", "source": "CNBC"}
        ]

    return {"news": news_list}