"""합성 가격 생성기 (오프라인 검증·테스트·데모용).

외부 네트워크 없이 전체 파이프라인을 끝까지 돌려 보기 위한 것이다.
실거래 판단에는 절대 쓰지 않는다.

매크로 심볼(SPY/VIX/VIX3M/HYG/IEF)은 난수로 두면 레짐이 무작위로
나와 데모도 테스트도 불가능해진다. 그래서 `regime` 인자로 원하는
시장 국면을 지정해 결정론적으로 만든다.
"""
from __future__ import annotations

from typing import Dict, Sequence

import numpy as np
import pandas as pd

from .base import PricePanel, normalize

RISK_ON = "risk_on"
RISK_OFF = "risk_off"
RANDOM = "random"

# 레짐별 매크로 설정: (SPY 추세, VIX, VIX3M, HYG 추세)
_MACRO_PRESET: Dict[str, tuple] = {
    #        SPY드리프트  VIX  VIX3M  HYG드리프트
    RISK_ON: (0.18, 14.0, 19.0, 0.06),
    RISK_OFF: (-0.25, 32.0, 24.0, -0.10),
}
_MACRO_SYMBOLS = {"SPY", "^VIX", "^VIX3M", "HYG", "IEF"}


class SyntheticSource:
    def __init__(self, seed: int = 20260921, regime: str = RISK_ON):
        if regime not in (RISK_ON, RISK_OFF, RANDOM):
            raise ValueError(f"알 수 없는 regime: {regime}")
        self.seed = seed
        self.regime = regime

    def fetch(self, symbols: Sequence[str], lookback_days: int) -> PricePanel:
        rng = np.random.default_rng(self.seed)
        dates = pd.bdate_range(end=pd.Timestamp("today").normalize(), periods=lookback_days)
        n = len(dates)
        panel: PricePanel = {}

        for i, sym in enumerate(symbols):
            if sym in _MACRO_SYMBOLS and self.regime != RANDOM:
                close = self._macro(sym, n, rng)
                vol_hint = 0.12
            else:
                # 종목마다 다른 연 드리프트(-20%~+45%)와 변동성(15%~70%)
                drift = rng.uniform(-0.20, 0.45)
                vol_hint = rng.uniform(0.15, 0.70)
                shocks = rng.normal(drift / 252.0, vol_hint / np.sqrt(252.0), n)
                close = 50.0 * (1.0 + 0.1 * (i % 3)) * np.exp(np.cumsum(shocks))

            panel[sym] = normalize(self._to_bars(close, vol_hint, dates, rng))
        return panel

    def _macro(self, sym: str, n: int, rng: np.random.Generator) -> np.ndarray:
        spy_drift, vix, vix3m, hyg_drift = _MACRO_PRESET[self.regime]
        if sym == "^VIX":
            return np.full(n, vix) * np.exp(rng.normal(0, 0.02, n))
        if sym == "^VIX3M":
            return np.full(n, vix3m) * np.exp(rng.normal(0, 0.01, n))
        if sym == "IEF":
            return 95.0 * np.exp(np.cumsum(rng.normal(0.0, 0.04 / np.sqrt(252.0), n)))
        drift = spy_drift if sym == "SPY" else hyg_drift
        base = 450.0 if sym == "SPY" else 78.0
        # 추세가 200일선 판정을 확실히 넘기도록 변동성을 낮게 둔다.
        shocks = rng.normal(drift / 252.0, 0.10 / np.sqrt(252.0), n)
        return base * np.exp(np.cumsum(shocks))

    @staticmethod
    def _to_bars(close: np.ndarray, vol_hint: float, dates, rng) -> pd.DataFrame:
        n = len(close)
        intraday = np.abs(rng.normal(0.0, vol_hint / np.sqrt(252.0) * 0.8, n))
        return pd.DataFrame(
            {
                "open": np.concatenate([[close[0]], close[:-1]]),
                "high": close * (1.0 + intraday),
                "low": close * (1.0 - intraday),
                "close": close,
                "volume": rng.lognormal(mean=15.0, sigma=0.4, size=n),
            },
            index=dates,
        )
