from fastapi import APIRouter, HTTPException, Depends
import os
import sqlite3
from datetime import datetime
from typing import Optional
from openai import OpenAI

from models import ReportRequest, ChatRequest
from news import get_news
from auth import get_current_user
from alerts import _get_user_email, _send_alert_email

router = APIRouter(prefix="/api")


_deepseek_client = None


def get_deepseek_client() -> OpenAI:
    """延迟初始化 DeepSeek 客户端，仅在实际调用 AI 接口时检查配置。

    这样即便未配置 DEEPSEEK_API_KEY，其它路由（行情、新闻等）也能正常工作，
    仅在访问 AI 相关接口时返回清晰的错误信息。
    """
    global _deepseek_client
    if _deepseek_client is not None:
        return _deepseek_client

    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    if not api_key:
        # 仅在实际调用 AI 时才报错
        raise HTTPException(
            status_code=500,
            detail="AI Agent Error: DeepSeek API Key 未设置，请在后端环境中配置后再使用研报/对话功能。",
        )

    _deepseek_client = OpenAI(api_key=api_key, base_url=base_url)
    return _deepseek_client


# 预设人物风格（投研机构风格 + 不同“股神”人设）
PERSONA_PRESETS = {
    "default": {
        "display_name": "机构首席策略分析师",
        "system": (
            "你是一名大型券商/投行的首席大类资产策略分析师，"
            "擅长自上而下梳理宏观-资产-行业-标的逻辑，风格严谨、克制，不追逐情绪。")
    },
    "buffett": {
        "display_name": "价值投资型股神",
        "system": (
            "你是一位偏好长期价值投资的顶级投资人，极度重视公司/资产内在价值、安全边际和现金流，"
            "不做短线博弈，强调在合理甚至便宜的估值下长期持有优质资产。"
        )
    },
    "soros": {
        "display_name": "宏观对冲型高手",
        "system": (
            "你是一位擅长宏观对冲和趋势交易的投资大师，对全球流动性、利率、汇率、风险偏好极为敏感，"
            "善于捕捉宏观拐点与趋势反转，风格相对激进，但非常重视风险控制和止损。"
        )
    },
    "dalio": {
        "display_name": "全天候资产配置专家",
        "system": (
            "你是一位擅长全天候资产配置的桥水型投资人，强调在不同经济环境（通胀/通缩、繁荣/衰退）下的风险平衡，"
            "注重相关性、风险分散和组合层面的稳定收益。"
        )
    },
}


def build_persona_system_prompt(
    persona: Optional[str],
    custom_persona_name: Optional[str] = None,
    custom_persona_prompt: Optional[str] = None,
) -> str:
    """根据 persona / 自定义人设，构建系统提示词，供研报和对话复用。"""
    # 自定义人物优先
    if persona == "custom" and (custom_persona_name or custom_persona_prompt):
        name = custom_persona_name or "自定义投资顾问"
        desc = custom_persona_prompt or ""
        return (
            f"你现在扮演一位名为『{name}』的顶级投资顾问。"  # 人设名称
            f"下面是该人物的性格与投资风格设定：{desc}\n"  # 自定义风格
            "你的任务是站在该角色视角，结合宏观、基本面和技术面，给出审慎、专业且可执行的投资建议，"
            "同时保持语言清晰、结构化，适合普通投资者理解。"
        )

    # 预设人物
    key = (persona or "default").lower()
    preset = PERSONA_PRESETS.get(key, PERSONA_PRESETS["default"])
    display_name = preset["display_name"]
    system_core = preset["system"]
    return (
        f"你现在扮演：{display_name}。"  # 人物标签
        f"{system_core}"
        "在分析时要做到：\n"
        "1）先给出结论再给出推理依据；\n"
        "2）用通俗但不低俗的语言解释专业概念；\n"
        "3）特别强调风险点和不确定性来源，不做绝对化表述。"
    )


def build_report_prompt(commodity: str, news_context: str, mode: Optional[str] = None) -> str:
    """根据生成模式构建研报提示词。

    - detailed（默认）：结构完整、章节较多，用于深度研报；
    - fast：压缩结构与篇幅，优先给出结论和操作建议，追求响应速度。
    """
    mode_normalized = (mode or "detailed").lower()

    # 快速模式：结构收敛、字数更短，适合比赛/实盘中快速获取结论
    if mode_normalized == "fast":
        return f"""
你正在为关注【{commodity}】的普通投资者快速生成一份精简版投研点评，重点是**结论和可执行的操作建议**，而不是长篇大论。

以下是最新的宏观与新闻摘要（可能不完全覆盖全部信息，仅供参考）：
{news_context}

请用 Markdown 中文输出一份**控制在约 400–700 字**的简洁报告，结构如下：

1. **一句话核心结论**
   - 用 1 句话给出当前对【{commodity}】的总体判断，并在“买入 / 分批买入 / 观望 / 减仓 / 卖出”中明确倾向（可加粗标记）。

2. **关键驱动因素（尽量不超过 3 点）**
   - 概括 2–3 个当前最重要的宏观或基本面因素，并用非常简短的语句说明其如何影响【{commodity}】的方向或性价比；
   - 不需要铺陈背景故事，只强调“逻辑链条”和“当下状态”。

3. **操作建议与风险提示**
   - 面向中等风险偏好投资者，给出一句可执行的操作建议：例如分批建仓/暂时观望/逢高减仓等，并给出大致持有周期；
   - 用 2–3 条短句列出最主要的风险或会推翻当前结论的触发条件。

请注意：
- 严禁使用“必然、一定”等绝对化措辞，应使用“概率更大、更可能”等表述；
- 不要给出具体价格点位，只用“上行/下行空间有限”“震荡区间”等定性描述；
- 语言保持专业但简洁，确保在手机端阅读也能快速抓住重点。
"""

    # 详尽模式：使用完整的机构化结构，适合深度阅读
    return f"""
你正在为关注【{commodity}】的普通投资者撰写一份专业级投研报告，帮助他们判断当前是否适合买入/加仓/减仓或观望该标的（可以理解为该商品或相关基金/ETF）。

以下是最新的宏观与新闻摘要（可能不完全覆盖全部信息，仅供参考）：
{news_context}

请严格按照下面结构，用 Markdown 格式输出报告（使用中文标题和小结）：

1. **结论先行（1 段）**
    - 用 2-3 句话给出对【{commodity}】当前的总体判断，以及“现在更偏向：买入 / 分批买入 / 观望 / 减仓 / 卖出”中的哪一种，并简要给出 1-2 个核心理由。

2. **宏观环境与流动性**
    - 概括全球/主要经济体在增长、通胀、利率、流动性、风险偏好等维度的大致状态；
    - 说明这些宏观变量与【{commodity}】之间的典型传导路径。

3. **商品/标的基本面与资金面**
    - 从供给、需求、库存、成本、替代品、政策等角度，分析当前基本面偏强还是偏弱；
    - 如果适用，可以简要提及资金面（如机构持仓、期现结构、ETF 资金进出等）。

4. **技术面与波动诊断**
    - 假设你已经看过近期 K 线、成交量以及均线/RSI/MACD/BOLL 等指标走势，请用文字概括：趋势强弱、支撑/压力区域、大致波动区间，以及是否存在超买/超卖或趋势衰竭信号；
    - 说明技术面与基本面是否一致，还是存在背离。

5. **交易策略与仓位建议**
    - 面向普通投资者，给出清晰可执行的策略建议：包括建仓节奏（一次性 vs 分批）、建议仓位区间（如中低风险投资者不超过总资产 X%）、以及大致的参考持有周期；
    - 说明在哪些价格或情形下，应该考虑“加仓”或“减仓/止损”。

6. **主要风险点与触发条件**
    - 用条目形式列出 3-5 个最关键的风险：包括宏观、政策、流动性、地缘政治、黑天鹅等；
    - 尽量给出每个风险大致的触发条件或监测指标（例如“若未来几个月通胀显著回落且央行提前转向宽松，则…”）。

7. **情景分析与应对**
    - 构造至少两种未来 3-6 个月的情景（如“温和复苏 + 通胀黏性”“衰退担忧升温”“地缘冲突升级”等），
    - 对每种情景下【{commodity}】可能的价格区间/方向做定性判断，并给出相应的操作思路。

8. **最终操作建议（重点）**
    - 用单独一小节，总结一句清晰的话，例如：
      - “在当前价格与环境下，更适合**分批买入**该标的，建议仓位不超过 ××%”；
      - 或“当前性价比一般，建议**耐心观望**，等待更好的价格/信号”；
      - 或“短期风险较大，建议**逢高减仓或暂时退出**”。

请注意：
- 不要给出任何保证型或绝对化措辞（如“必然”“一定会”），而是使用“概率更大”“更可能”等表述；
- 你可以合理想象技术面形态，但不要捏造具体价格数字，只用“上/下行空间有限”“大致震荡区间”等定性描述；
- 全文使用中文输出，并保持结构清晰、逻辑严谨，适合中等经验的个人投资者阅读。
"""


@router.post("/generate-report")
async def generate_ai_report(req: ReportRequest, current_user: str = Depends(get_current_user)):
    """使用 AI 分析新闻并预测大宗商品价格"""

    # 获取新闻
    news_data = await get_news()
    # 只取一部分最新、最关键的标题，减少 Prompt 体积和 LLM 推理耗时
    raw_news = news_data.get("news", []) if isinstance(news_data, dict) else []
    news_titles = [n.get("title", "") for n in raw_news][:12]

    news_context = "\n".join(f"- {t}" for t in news_titles)

    # 根据模式构建不同复杂度的提示词
    user_prompt = build_report_prompt(
        commodity=req.commodity,
        news_context=news_context,
        mode=getattr(req, "mode", None),
    )

    try:

        system_prompt = build_persona_system_prompt(
            persona=req.persona,
            custom_persona_name=req.custom_persona_name,
            custom_persona_prompt=req.custom_persona_prompt,
        )

        client = get_deepseek_client()

        # 根据模式控制返回长度，兼顾信息量与响应时间
        mode_normalized = (getattr(req, "mode", None) or "detailed").lower()
        max_tokens = 600 if mode_normalized == "fast" else 1000

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=max_tokens,
        )

        report = response.choices[0].message.content

        # 将研报写入用户历史
        try:
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            c.execute(
                "INSERT INTO user_reports (username, commodity, report, created_at) VALUES (?, ?, ?, ?)",
                (current_user, req.commodity, report, datetime.utcnow().isoformat())
            )
            conn.commit()
            conn.close()
        except Exception:
            # 历史写入失败不影响主流程
            pass

        return {
            "commodity": req.commodity,
            "report": report
        }

    except Exception as e:
        # 这里进一步拆分错误信息，便于前端做更友好的提示
        msg = str(e)
        if "401" in msg or "invalid_api_key" in msg.lower():
            detail = "AI Agent Error: DeepSeek API Key 无效或未授权，请检查后端环境变量配置。"
        elif "timed out" in msg.lower() or "timeout" in msg.lower():
            detail = "AI Agent Error: 与 DeepSeek 通信超时，请稍后重试。"
        else:
            detail = f"AI Agent Error: {msg}"

        raise HTTPException(
            status_code=500,
            detail=detail
        )


@router.get("/user-reports")
async def get_user_reports(
    commodity: Optional[str] = None,
    limit: int = 10,
    current_user: str = Depends(get_current_user),
):
    """查询当前用户的历史研报列表，可按商品名称过滤。"""
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        params = [current_user]
        query = "SELECT id, commodity, report, created_at FROM user_reports WHERE username = ?"
        if commodity:
            query += " AND commodity = ?"
            params.append(commodity)
        query += " ORDER BY datetime(created_at) DESC LIMIT ?"
        params.append(limit)
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        items = [
            {
                "id": r[0],
                "commodity": r[1],
                "report": r[2],
                "created_at": r[3],
            }
            for r in rows
        ]
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询研报历史失败: {e}")


@router.post("/user-reports/{report_id}/send-email")
async def send_user_report_email(report_id: int, current_user: str = Depends(get_current_user)):
    """将指定历史研报发送到当前用户邮箱。"""
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute(
            "SELECT commodity, report, created_at FROM user_reports WHERE id = ? AND username = ?",
            (report_id, current_user),
        )
        row = c.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="未找到对应的历史研报，或该研报不属于当前用户。")

        commodity, report, created_at = row
        to_email = _get_user_email(current_user)
        if not to_email:
            return {"status": "no_email", "report_id": report_id}

        subject = f"AI 投研终端 - {commodity} 策略研报"
        header = f"标的：{commodity}\n生成时间：{created_at}\n\n================= 以下为完整研报内容 =================\n\n"
        content = header + (report or "")

        ok = _send_alert_email(to_email, subject=subject, content=content)
        return {"status": "sent" if ok else "failed", "report_id": report_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送历史研报邮件失败: {e}")


@router.post("/ai-chat")
async def ai_chat(req: ChatRequest, current_user: str = Depends(get_current_user)):
    """基于当前人设与新闻/历史对话，进行多轮 AI 问答。"""
    try:
        # 构建人设
        system_prompt = build_persona_system_prompt(
            persona=req.persona,
            custom_persona_name=req.custom_persona_name,
            custom_persona_prompt=req.custom_persona_prompt,
        )

        client = get_deepseek_client()

        # 聚合最新新闻，给对话提供宏观/事件背景
        news_data = await get_news()
        raw_news = news_data.get("news", []) if isinstance(news_data, dict) else []
        news_titles = [n.get("title", "") for n in raw_news][:8]
        news_context = "\n".join(f"- {t}" for t in news_titles)

        messages = [
            {"role": "system", "content": system_prompt},
        ]
        # 追加历史对话（若有），仅保留最近若干轮，避免上下文过长拖慢响应
        if req.history:
            history_tail = req.history[-6:]
            for m in history_tail:
                if m.role in {"user", "assistant", "system"} and m.content:
                    messages.append({"role": m.role, "content": m.content})

        commodity_text = req.commodity or "未指定具体标的"
        user_content = f"""
你正在以专业投资顾问的身份，继续为投资者解答关于【{commodity_text}】的后续问题。

下面是近期与该标的相关的宏观/新闻摘要（可能并不完整，仅供参考）：
{news_context}

请结合以上背景信息和前文对话，用清晰、结构化的中文回答用户的新问题：
{req.question}
"""
        messages.append({"role": "user", "content": user_content})

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
            max_tokens=600,
        )
        answer = response.choices[0].message.content
        return {
            "commodity": commodity_text,
            "answer": answer,
            "created_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        msg = str(e)
        if "401" in msg or "invalid_api_key" in msg.lower():
            detail = "AI Agent Error: DeepSeek API Key 无效或未授权，请检查后端环境变量配置。"
        elif "timed out" in msg.lower() or "timeout" in msg.lower():
            detail = "AI Agent Error: 与 DeepSeek 通信超时，请稍后重试。"
        else:
            detail = f"AI Agent Error: {msg}"
        raise HTTPException(status_code=500, detail=detail)