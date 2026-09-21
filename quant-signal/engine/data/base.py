"""가격 데이터의 공통 스키마.

패널은 {티커: DataFrame} 이고, 각 DataFrame 은
[open, high, low, close, volume] 컬럼에 DatetimeIndex 를 가진다.
인덱스는 tz-naive 거래일 기준으로 통일한다 (시장별 타임존 혼선 방지).
"""
from __future__ import annotations

from typing import Dict, Protocol, Sequence

import pandas as pd

OHLCV = ["open", "high", "low", "close", "volume"]
PricePanel = Dict[str, pd.DataFrame]


class PriceSource(Protocol):
    """일봉 가격 공급자."""

    def fetch(self, symbols: Sequence[str], lookback_days: int) -> PricePanel:
        ...


def empty_panel() -> PricePanel:
    return {}


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """컬럼명을 소문자로 맞추고 필요한 컬럼만 남긴다."""
    df = df.rename(columns={c: str(c).lower() for c in df.columns})
    missing = [c for c in OHLCV if c not in df.columns]
    if missing:
        raise ValueError(f"필수 컬럼 누락: {missing}")
    out = df[OHLCV].astype("float64").copy()
    idx = pd.to_datetime(out.index)
    if getattr(idx, "tz", None) is not None:
        idx = idx.tz_localize(None)
    out.index = idx.normalize()
    out = out[~out.index.duplicated(keep="last")].sort_index()
    # 가격이 0 이하인 행은 데이터 오류다. 지표를 오염시키므로 버린다.
    return out[(out[["open", "high", "low", "close"]] > 0).all(axis=1)]


def validate(panel: PricePanel, min_rows: int) -> PricePanel:
    """이력이 부족하거나 최근 데이터가 비어 있는 종목을 제외한다."""
    return {
        sym: df
        for sym, df in panel.items()
        if len(df) >= min_rows and df["close"].iloc[-20:].notna().all()
    }
