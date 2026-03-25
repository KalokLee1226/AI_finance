from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from market import fetch_market_data, mapping

router = APIRouter(prefix="/api")


def _safe_float(val) -> float | None:
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return None
        return float(val)
    except Exception:
        return None


def _build_short_term_view(df: pd.DataFrame) -> Dict[str, Any]:
    """基于日频数据给出未来 1–3 天的方向+区间+置信度（规则基线版）。"""
    close = df["Close"].astype(float)
    last_close = float(close.iloc[-1])

    rets = close.pct_change().dropna()
    if len(rets) < 5:
        raise HTTPException(status_code=500, detail="历史数据不足，无法进行短期预测")

    mean5 = float(rets.tail(5).mean())
    mean20 = float(rets.tail(20).mean()) if len(rets) >= 20 else mean5
    vol20 = float(rets.tail(20).std()) if len(rets) >= 20 else float(rets.std())

    rsi_series = df.get("RSI14")
    last_rsi = _safe_float(rsi_series.iloc[-1]) if rsi_series is not None else None

    macd_series = df.get("MACD")
    macd_signal_series = df.get("MACD_SIGNAL")
    last_macd = _safe_float(macd_series.iloc[-1]) if macd_series is not None else None
    last_macd_signal = _safe_float(macd_signal_series.iloc[-1]) if macd_signal_series is not None else None

    # 方向评分：[-2,2] 区间，>0 偏多，<0 偏空
    score = 0.0
    # 短期收益倾向
    if mean5 > 0:
        score += 0.7
    elif mean5 < 0:
        score -= 0.7
    # 中期收益倾向
    if mean20 > 0:
        score += 0.5
    elif mean20 < 0:
        score -= 0.5

    # RSI 信号：超卖偏多、超买偏空
    if last_rsi is not None:
        if last_rsi < 30:
            score += 0.7
        elif last_rsi > 70:
            score -= 0.7

    # MACD 多空结构
    if last_macd is not None and last_macd_signal is not None:
        if last_macd > last_macd_signal:
            score += 0.4
        else:
            score -= 0.4

    # 将 score 压缩到 [-2,2]
    score = max(-2.0, min(2.0, score))

    # 映射到方向
    if score >= 0.6:
        direction = "up"
    elif score <= -0.6:
        direction = "down"
    else:
        direction = "range"

    # 置信度：根据 |score| 与波动率一起给一个 0.2–0.9 的分值
    base_conf = min(1.0, abs(score) / 2.0)
    # 波动率越大，不确定性越高，适当打折
    vol_adj = 1.0
    if vol20 > 0.05:
        vol_adj = 0.7
    elif vol20 > 0.03:
        vol_adj = 0.8
    confidence = max(0.2, min(0.9, base_conf * vol_adj))

    # 预期收益区间（未来 1–3 天），只给出百分比，不给绝对价位
    expected_mean = mean5 * 3  # 线性放大，粗略估计
    band = (vol20 or 0.02) * 2.0
    range_low_pct = expected_mean - band
    range_high_pct = expected_mean + band

    # 文字解释（中文）
    reasons = []
    if mean5 > 0:
        reasons.append("近期 5 日平均收益为正，短线动能偏多")
    elif mean5 < 0:
        reasons.append("近期 5 日平均收益为负，短线动能偏空")

    if mean20 > 0:
        reasons.append("近 20 日总体偏上行")
    elif mean20 < 0:
        reasons.append("近 20 日总体偏下行")

    if last_rsi is not None:
        if last_rsi < 30:
            reasons.append(f"RSI≈{last_rsi:.1f}，处于超卖区，存在技术性反弹可能")
        elif last_rsi > 70:
            reasons.append(f"RSI≈{last_rsi:.1f}，处于超买区，短期回调风险上升")

    if last_macd is not None and last_macd_signal is not None:
        if last_macd > last_macd_signal:
            reasons.append("MACD 高于信号线，趋势偏多")
        else:
            reasons.append("MACD 低于信号线，趋势偏空")

    explanation = "；".join(reasons) or "样本较少，仅做方向性参考。"

    return {
        "horizon_days": [1, 3],
        "direction": direction,  # up / down / range
        "confidence": confidence,  # 0-1
        "expected_return_pct_mean": expected_mean,
        "expected_return_pct_range": [range_low_pct, range_high_pct],
        "explanation": explanation,
    }


def _build_arima_view(df: pd.DataFrame) -> Dict[str, Any] | None:
    """使用 ARIMA(1,1,1) 模型对未来 1–3 日做一个计量学预测视图。

    返回结构与 _build_short_term_view 一致，供多模型融合使用。
    若样本过少或拟合失败，返回 None 并由上层忽略该模型。
    """
    close = df["Close"].astype(float)
    if len(close) < 30:
        # 历史不足，放弃 ARIMA 模型
        return None

    # 为提升稳定性，仅使用最近最多 120 根 K 线
    series = close.tail(120)
    last_close = float(series.iloc[-1])

    try:
        model = ARIMA(series, order=(1, 1, 1))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=3)
    except Exception:
        # 拟合失败时忽略 ARIMA 视图
        return None

    # 将未来 1–3 日预期价格转为相对于当前收盘价的收益率
    rets = (forecast / last_close) - 1.0
    # 未来 1–3 天整体的平均收益率
    mean_ret = float(rets.mean())
    # 使用 min/max 构造一个覆盖 1–3 日的整体区间
    range_low_pct = float(rets.min())
    range_high_pct = float(rets.max())

    # 若未来路径非常平滑，则给一个最小带宽避免区间为 0
    if range_high_pct - range_low_pct < 0.01:
        center = mean_ret
        half_band = 0.01
        range_low_pct = center - half_band
        range_high_pct = center + half_band

    if mean_ret > 0.001:
        direction = "up"
    elif mean_ret < -0.001:
        direction = "down"
    else:
        direction = "range"

    # 计量模型本身不输出置信度，这里给一个中等偏保守的固定区间
    confidence = 0.6

    explanation = (
        "ARIMA(1,1,1) 模型基于最近价格序列，对未来 1–3 日的收盘价进行外推，"
        "该视图仅体现计量模型对方向与波动区间的判断。"
    )

    return {
        "horizon_days": [1, 3],
        "direction": direction,
        "confidence": confidence,
        # 这里直接使用 1–3 日整体平均收益率，不再额外放大
        "expected_return_pct_mean": mean_ret,
        "expected_return_pct_range": [range_low_pct, range_high_pct],
        "explanation": explanation,
    }


def _build_ultra_short_term_view(short_term: Dict[str, Any]) -> Dict[str, Any]:
    """基于日频波动给出 5–30 分钟的超短线波动判断（规则近似）。"""
    direction = short_term["direction"]
    base_conf = short_term["confidence"]
    # 超短线的不确定性更大，整体打个折扣
    confidence = max(0.15, min(0.7, base_conf * 0.7))

    # 用日度预期波动的 1/8 作为 30 分钟大致波动参考
    mean = short_term["expected_return_pct_mean"] or 0.0
    low, high = short_term["expected_return_pct_range"] or [0.0, 0.0]
    scale = 1.0 / 8.0
    us_mean = mean * scale
    us_band = ((high - low) / 2.0) * scale

    explanation = (
        "超短线判断仅基于当前日度趋势和波动率做缩放，"
        "未结合盘口和实时成交，仅做突发事件下的方向性参考。"
    )

    return {
        "horizon_minutes": [5, 30],
        "direction": direction,
        "confidence": confidence,
        "expected_return_pct_mean": us_mean,
        "expected_return_pct_range": [us_mean - us_band, us_mean + us_band],
        "explanation": explanation,
    }


@router.get("/predict-price/{symbol}")
async def predict_price(symbol: str):
    """对指定品种进行规则基线的短期价格量化预测（方向+波动区间+置信度）。"""
    symbol = symbol.upper()
    if symbol not in mapping:
        raise HTTPException(status_code=400, detail=f"不支持的商品: {symbol}")

    try:
        df = fetch_market_data(symbol, period="day")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"行情数据获取失败: {e}")

    if df is None or df.empty or len(df) < 10:
        raise HTTPException(status_code=500, detail="有效历史数据不足，无法进行预测")

    # 规则基线视图（技术面）
    technical_view = _build_short_term_view(df)

    # ARIMA 计量视图（若失败则返回 None）
    arima_view = _build_arima_view(df)

    # 多模型融合：规则技术面 + ARIMA
    fused_view = dict(technical_view)  # 默认退化为技术面
    fused_view["models"] = {"technical": technical_view, "arima": arima_view}

    if arima_view is not None:
        tech_dir = technical_view["direction"]
        ari_dir = arima_view["direction"]

        # 方向投票：一致则沿用方向并略微抬高置信度；不一致则视为震荡区间、降低置信度并放宽区间
        if tech_dir == ari_dir:
            direction = tech_dir
            confidence = min(0.95, (technical_view["confidence"] * 0.6) + (arima_view["confidence"] * 0.4))
            widen_factor = 1.0
        else:
            direction = "range"
            confidence = max(0.2, technical_view["confidence"] * 0.7)
            widen_factor = 1.3

        # 收益区间与中枢做加权融合（技术面 60%，ARIMA 40%）
        mean_comb = (
            technical_view["expected_return_pct_mean"] * 0.6
            + arima_view["expected_return_pct_mean"] * 0.4
        )
        low1, high1 = technical_view["expected_return_pct_range"]
        low2, high2 = arima_view["expected_return_pct_range"]
        range_low = (low1 * 0.6 + low2 * 0.4) * widen_factor
        range_high = (high1 * 0.6 + high2 * 0.4) * widen_factor

        explanation = (
            "多模型融合：技术指标规则引擎（60% 权重）与 ARIMA 计量模型（40% 权重）联合给出判断。"
            f" 技术面视角：{technical_view['explanation']}"
            f"；ARIMA 视角：{arima_view['explanation']}"
        )

        fused_view.update(
            {
                "direction": direction,
                "confidence": confidence,
                "expected_return_pct_mean": mean_comb,
                "expected_return_pct_range": [range_low, range_high],
                "explanation": explanation,
            }
        )

    short_view = fused_view
    ultra_short_view = _build_ultra_short_term_view(short_view)

    rsi_series = df.get("RSI14")
    macd_series = df.get("MACD")
    macd_signal_series = df.get("MACD_SIGNAL")

    diagnostics = {
        "last_close": float(df["Close"].astype(float).iloc[-1]),
        "rsi14": _safe_float(rsi_series.iloc[-1]) if rsi_series is not None else None,
        "macd": _safe_float(macd_series.iloc[-1]) if macd_series is not None else None,
        "macd_signal": _safe_float(macd_signal_series.iloc[-1]) if macd_signal_series is not None else None,
    }

    return {
        "symbol": symbol,
        "base_timeframe": "1d",
        "short_term": short_view,
        "ultra_short_term": ultra_short_view,
        "diagnostics": diagnostics,
        "generated_at": datetime.utcnow().isoformat(),
    }
