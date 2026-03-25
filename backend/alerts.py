import json
import os
import smtplib
import sqlite3
import ssl
import logging
from datetime import datetime
from email.message import EmailMessage
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user
from market import fetch_market_data
from user_data import DEFAULT_COMMODITIES

router = APIRouter(prefix="/api")


def _load_user_commodities(username: str) -> List[str]:
    """从 user_settings 里读取当前用户的自选品种 key（如 gold/oil）。"""
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT commodities FROM user_settings WHERE username=?", (username,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            arr = json.loads(row[0])
            if isinstance(arr, list) and arr:
                return [k for k in arr if isinstance(k, str) and k]
    except Exception as e:
        logging.warning(f"load user commodities failed: {e}")
    return DEFAULT_COMMODITIES


def _compute_symbol_alerts(symbol_key: str) -> List[Dict]:
    """基于技术指标对单个品种生成简要告警。

    symbol_key: 前端使用的小写 key，例如 gold / oil
    """
    symbol = symbol_key.upper()
    try:
        df = fetch_market_data(symbol)
    except Exception as e:
        logging.warning(f"fetch_market_data for alerts failed: {symbol}, {e}")
        return []

    if df is None or df.empty:
        return []

    # 只看最近两根 K 线
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) >= 2 else None

    alerts: List[Dict] = []

    # RSI 超买/超卖
    rsi = float(last.get("RSI14")) if last.get("RSI14") is not None else None
    if rsi is not None:
        if rsi >= 70:
            alerts.append({
                "symbol": symbol,
                "key": symbol_key,
                "type": "RSI_OVERBOUGHT",
                "level": "warning",
                "message": f"RSI 已进入超买区({rsi:.1f} > 70)，短期回调风险上升",
                "indicators": {"RSI14": rsi},
            })
        elif rsi <= 30:
            alerts.append({
                "symbol": symbol,
                "key": symbol_key,
                "type": "RSI_OVERSOLD",
                "level": "info",
                "message": f"RSI 已进入超卖区({rsi:.1f} < 30)，存在技术性反弹机会",
                "indicators": {"RSI14": rsi},
            })

    # MACD 金叉 / 死叉
    macd = last.get("MACD")
    signal = last.get("MACD_SIGNAL")
    if prev is not None and macd is not None and signal is not None:
        prev_diff = float(prev.get("MACD")) - float(prev.get("MACD_SIGNAL"))
        curr_diff = float(macd) - float(signal)
        if prev_diff <= 0 <= curr_diff:
            alerts.append({
                "symbol": symbol,
                "key": symbol_key,
                "type": "MACD_GOLDEN_CROSS",
                "level": "info",
                "message": "MACD 出现金叉，趋势有走强迹象（需结合量价与基本面确认）",
                "indicators": {"MACD": float(macd), "MACD_SIGNAL": float(signal)},
            })
        elif prev_diff >= 0 >= curr_diff:
            alerts.append({
                "symbol": symbol,
                "key": symbol_key,
                "type": "MACD_DEAD_CROSS",
                "level": "warning",
                "message": "MACD 出现死叉，短期趋势偏弱（注意回撤风险）",
                "indicators": {"MACD": float(macd), "MACD_SIGNAL": float(signal)},
            })

    # 布林带突破
    close = float(last.get("Close")) if last.get("Close") is not None else None
    upper = last.get("BOLL_UPPER")
    lower = last.get("BOLL_LOWER")
    if close is not None and upper is not None and lower is not None:
        upper = float(upper)
        lower = float(lower)
        if close > upper:
            alerts.append({
                "symbol": symbol,
                "key": symbol_key,
                "type": "BOLL_BREAK_UPPER",
                "level": "warning",
                "message": "价格向上突破布林带上轨，短期可能存在冲高回落风险",
                "indicators": {"Close": close, "BOLL_UPPER": upper},
            })
        elif close < lower:
            alerts.append({
                "symbol": symbol,
                "key": symbol_key,
                "type": "BOLL_BREAK_LOWER",
                "level": "info",
                "message": "价格跌破布林带下轨，存在超跌反弹可能",
                "indicators": {"Close": close, "BOLL_LOWER": lower},
            })

    for a in alerts:
        a["time"] = df.index[-1].isoformat()

    return alerts


def _get_user_email(username: str) -> str:
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT email FROM users WHERE username=?", (username,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception as e:
        logging.warning(f"load user email failed: {e}")
    return ""


def _send_alert_email(to_email: str, subject: str, content: str) -> bool:
    """使用环境变量配置的 SMTP 发送告警邮件，配置缺失时静默失败。"""
    host = os.getenv("ALERT_SMTP_HOST")
    if not host:
        logging.warning("ALERT_SMTP_HOST 未配置，跳过邮件发送")
        return False

    port = int(os.getenv("ALERT_SMTP_PORT", "587"))
    user = os.getenv("ALERT_SMTP_USERNAME")
    password = os.getenv("ALERT_SMTP_PASSWORD")
    from_email = os.getenv("ALERT_EMAIL_FROM", user or "no-reply@example.com")
    use_tls = os.getenv("ALERT_SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(content)

    try:
        if use_tls:
            context = ssl.create_default_context()
            with smtplib.SMTP(host, port) as server:
                server.starttls(context=context)
                if user and password:
                    server.login(user, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port) as server:
                if user and password:
                    server.login(user, password)
                server.send_message(msg)
        return True
    except Exception as e:
        logging.error(f"send alert email failed: {e}")
        return False


@router.get("/alerts")
async def get_alerts(send_email: bool = False, current_user: str = Depends(get_current_user)):
    """为当前用户自选品种生成技术面智能预警，可选邮件推送。"""
    keys = _load_user_commodities(current_user)

    all_alerts: List[Dict] = []
    for key in keys:
        all_alerts.extend(_compute_symbol_alerts(key))

    email_status = None
    if send_email and all_alerts:
        to_email = _get_user_email(current_user)
        if to_email:
            # 无论预警级别如何，只要本次有预警就整体发送给用户
            lines = [
                f"[{a['key'].upper()}] {a['message']} (时间: {a['time']})" for a in all_alerts
            ]
            body = "\n".join(lines)
            ok = _send_alert_email(
                to_email,
                subject="AI 投研终端 - 智能预警通知",
                content=body,
            )
            email_status = "sent" if ok else "failed"
        else:
            email_status = "no_email"

    return {
        "alerts": all_alerts,
        "email_status": email_status,
        "generated_at": datetime.utcnow().isoformat(),
    }
