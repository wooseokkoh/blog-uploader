"""횡단면 팩터 계산.

팩터는 레지스트리로 관리한다. P1 에서 밸류/퀄리티(재무 기반)를
추가할 때 `FACTORS` 에 함수를 등록하고 config 의 weights 에
가중치만 넣으면 엔진 본체는 수정할 필요가 없다.

P0 는 가격·거래량만 쓴다. 무료로 신뢰성 있게 얻을 수 있는 게
그것뿐이고, 재무데이터를 무료 소스로 500종목 긁으면 결측과
지연 때문에 오히려 신호가 나빠진다.
"""
from __future__ import annotations

from typing import Callable, Dict

import numpy as np
import pandas as pd

from .config import FactorConfig
from .data.base import PricePanel
from . import indicators as I

FactorFn = Callable[[pd.DataFrame, FactorConfig], float]


def _momentum(df: pd.DataFrame, cfg: FactorConfig) -> float:
    return _tail(I.momentum(df["close"], cfg.momentum_lookback, cfg.momentum_skip))


def _trend(df: pd.DataFrame, cfg: FactorConfig) -> float:
    return _tail(I.trend_strength(df["close"], cfg.trend_sma))


def _low_vol(df: pd.DataFrame, cfg: FactorConfig) -> float:
    # 변동성은 낮을수록 좋으므로 부호를 뒤집어 "높을수록 좋음"으로 통일한다.
    v = _tail(I.realized_vol(df["close"], cfg.vol_lookback))
    return -v if np.isfinite(v) else np.nan


def _volume_confirm(df: pd.DataFrame, cfg: FactorConfig) -> float:
    return _tail(I.volume_ratio(df["volume"]))


def _tail(s: pd.Series) -> float:
    s = s.dropna()
    return float(s.iloc[-1]) if len(s) else np.nan


FACTORS: Dict[str, FactorFn] = {
    "momentum": _momentum,
    "trend": _trend,
    "low_vol": _low_vol,
    "volume_confirm": _volume_confirm,
}


def raw_factors(panel: PricePanel, cfg: FactorConfig) -> pd.DataFrame:
    """종목 x 팩터 원시값 테이블."""
    rows = {
        sym: {name: fn(df, cfg) for name, fn in FACTORS.items()}
        for sym, df in panel.items()
    }
    return pd.DataFrame.from_dict(rows, orient="index").sort_index()


def composite(raw: pd.DataFrame, cfg: FactorConfig) -> pd.DataFrame:
    """z-score 표준화 후 가중합 -> 0~100 점수.

    가중치가 지정된 팩터 중 결측이 아닌 것들로만 합산하고,
    사용된 가중치 합으로 나눠 준다. 한 팩터가 결측이라고 해서
    그 종목 점수가 통째로 낮아지면 안 되기 때문이다.
    """
    if raw.empty:
        return pd.DataFrame(columns=["score", "composite_z"])

    weights = {k: v for k, v in cfg.weights.items() if k in raw.columns}
    if not weights:
        raise ValueError("적용 가능한 팩터 가중치가 없습니다")

    z = pd.DataFrame(
        {name: I.zscore(raw[name], cfg.winsorize_z) for name in weights},
        index=raw.index,
    )
    w = pd.Series(weights, dtype="float64")
    weighted = z.mul(w, axis=1)
    used_w = z.notna().mul(w, axis=1).sum(axis=1)
    comp = weighted.sum(axis=1, min_count=1) / used_w.replace(0.0, np.nan)

    out = z.add_suffix("_z")
    out["composite_z"] = comp
    out["score"] = I.percentile_rank(comp)
    # 사용자에게 보여줄 팩터별 0~100 점수
    for name in weights:
        out[f"{name}_pct"] = I.percentile_rank(raw[name])
    return out.join(raw.add_suffix("_raw"))
