"""시장 레짐 판정.

추세 / 변동성 / 신용 세 축을 각각 0·1 로 채점해 합산한다.
단일 지표로 판단하면 한 축이 고장났을 때(데이터 결측, 일시적 왜곡)
전체가 흔들리므로 축을 분리하고, 결측 축은 점수에서 제외한다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pandas as pd

from .config import RegimeConfig
from .data.base import PricePanel
from .indicators import sma

RISK_ON = "RISK_ON"
NEUTRAL = "NEUTRAL"
RISK_OFF = "RISK_OFF"


@dataclass
class Regime:
    state: str
    score: float  # 0.0 ~ 1.0 (판정 가능한 축들의 평균)
    components: Dict[str, Optional[bool]] = field(default_factory=dict)
    detail: Dict[str, float] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    @property
    def allows_new_entry(self) -> bool:
        return self.state != RISK_OFF

    def to_dict(self) -> dict:
        return {
            "state": self.state,
            "score": round(self.score, 3),
            "components": self.components,
            "detail": {k: round(v, 4) for k, v in self.detail.items()},
            "notes": self.notes,
        }


def _last(s: pd.Series) -> Optional[float]:
    s = s.dropna()
    return float(s.iloc[-1]) if len(s) else None


def _close(panel: PricePanel, sym: str) -> Optional[pd.Series]:
    df = panel.get(sym)
    if df is None or df.empty:
        return None
    return df["close"]


def detect(panel: PricePanel, cfg: RegimeConfig = RegimeConfig()) -> Regime:
    comps: Dict[str, Optional[bool]] = {}
    detail: Dict[str, float] = {}
    notes: List[str] = []

    # --- 1축: 지수 추세 (SPY 200일선 위인가) ---
    spx = _close(panel, cfg.trend_symbol)
    if spx is not None and len(spx) >= cfg.trend_sma:
        px, ma = _last(spx), _last(sma(spx, cfg.trend_sma))
        if px and ma:
            comps["trend"] = px > ma
            detail["spy_vs_sma200_pct"] = (px / ma - 1.0) * 100.0
    if "trend" not in comps:
        comps["trend"] = None
        notes.append(f"{cfg.trend_symbol} 추세 판정 불가 (데이터 부족)")

    # --- 2축: 변동성 기간구조 (VIX/VIX3M < 1 이면 평온) ---
    vix, vix3m = _close(panel, cfg.vix_symbol), _close(panel, cfg.vix_far_symbol)
    if vix is not None and vix3m is not None:
        near, far = _last(vix), _last(vix3m)
        if near and far and far > 0:
            ratio = near / far
            comps["volatility"] = ratio < cfg.vix_contango_max
            detail["vix_term_ratio"] = ratio
    if "volatility" not in comps:
        comps["volatility"] = None
        notes.append("VIX 기간구조 판정 불가")

    # --- 3축: 신용 (하이일드가 국채 대비 강한가) ---
    hyg, ief = _close(panel, cfg.credit_risk_symbol), _close(panel, cfg.credit_safe_symbol)
    if hyg is not None and ief is not None:
        ratio = (hyg / ief).dropna()
        if len(ratio) >= cfg.credit_sma:
            cur, ma = _last(ratio), _last(sma(ratio, cfg.credit_sma))
            if cur and ma:
                comps["credit"] = cur > ma
                detail["credit_ratio_vs_sma_pct"] = (cur / ma - 1.0) * 100.0
    if "credit" not in comps:
        comps["credit"] = None
        notes.append("신용 스프레드 판정 불가")

    decided = [v for v in comps.values() if v is not None]
    if not decided:
        # 아무 축도 판정 못 하면 보수적으로 막는다. "모르면 사지 않는다".
        return Regime(RISK_OFF, 0.0, comps, detail, notes + ["판정 가능한 축 없음 → 보수적 RISK_OFF"])

    score = sum(decided) / len(decided)
    if score >= 0.99:
        state = RISK_ON
    elif score >= 0.5:
        state = NEUTRAL
    else:
        state = RISK_OFF
    return Regime(state, score, comps, detail, notes)


REGIME_KO = {
    RISK_ON: "위험선호",
    NEUTRAL: "중립",
    RISK_OFF: "위험회피",
}
