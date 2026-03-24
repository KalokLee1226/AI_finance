from fastapi import APIRouter, HTTPException
from openai import OpenAI

from models import ReportRequest
from news import get_news

router = APIRouter(prefix="/api")

# DeepSeek API配置
DEEPSEEK_API_KEY = "你的key"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)


@router.post("/generate-report")
async def generate_ai_report(req: ReportRequest):
    """
    使用AI分析新闻并预测大宗商品价格
    """

    # 获取新闻
    news_data = await get_news()
    news_titles = [n["title"] for n in news_data["news"]]

    news_context = "\n".join(news_titles)

    prompt = f"""
作为一个专业的国际政治与经济分析师，请根据以下新闻预测【{req.commodity}】走势：

{news_context}

请生成：
1. 当前宏观局势
2. 商品市场影响
3. 短期与中期价格预测
4. 投资建议与风险
"""

    try:

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是资深金融分析师"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        report = response.choices[0].message.content

        return {
            "commodity": req.commodity,
            "report": report
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"AI Agent Error: {str(e)}"
        )