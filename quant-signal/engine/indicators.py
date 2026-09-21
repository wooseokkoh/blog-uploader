"""기술 지표.

모두 pandas Series/DataFrame 위에서 동작하는 순수 함수다.
실시간(P0.5) 단계에서 증분 계산으로 바꿀 때 기준이 되는 정의이므로,
여기 정의와 실시간 엔진의 결과가 어긋나지 않도록 테스트로 묶어 둔다.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def sma(s: pd.Series, period: int) -> pd.Series:
    return s.rolling(period, min_periods=period).mean()


def ema(s: pd.Series, period: int) -> pd.Series:
    return s.ewm(span=period, adjust=False, min_periods=period).mean()


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)
    return pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Wilder 방식 ATR. 실시간 증분 갱신과 같은 정의다."""
    tr = true_range(high, low, close)
    return tr.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = gain.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    out = 100.0 - 100.0 / (1.0 + rs)
    # 하락이 전혀 없었던 구간은 RSI 100 으로 둔다.
    return out.where(avg_loss != 0.0, 100.0).where(avg_gain.notna())


def realized_vol(close: pd.Series, period: int = 60) -> pd.Series:
    """연율화 실현 변동성."""
    r = np.log(close / close.shift(1))
    return r.rolling(period, min_periods=period).std() * np.sqrt(TRADING_DAYS)


def momentum(close: pd.Series, lookback: int = 252, skip: int = 21) -> pd.Series:
    """12-1 모멘텀. 최근 `skip` 거래일을 제외한 누적 수익률."""
    past = close.shift(lookback)
    recent = close.shift(skip)
    return recent / past - 1.0


def trend_strength(close: pd.Series, period: int = 200) -> pd.Series:
    """장기 이동평균 대비 이격도. 추세의 방향과 강도를 함께 담는다."""
    base = sma(close, period)
    return close / base - 1.0


def volume_ratio(volume: pd.Series, short: int = 5, long: int = 60) -> pd.Series:
    """단기 거래량이 장기 평균 대비 몇 배인지. 돌파의 진위 판단에 쓴다."""
    return volume.rolling(short, min_periods=short).mean() / volume.rolling(
        long, min_periods=long
    ).mean()


def dollar_volume(close: pd.Series, volume: pd.Series, period: int = 20) -> pd.Series:
    return (close * volume).rolling(period, min_periods=period).mean()


def zscore(s: pd.Series, clip: float | None = 3.0) -> pd.Series:
    """횡단면 z-score. 표준편차가 0이면 전부 0으로 둔다."""
    valid = s.dropna()
    if valid.empty:
        return pd.Series(np.nan, index=s.index, dtype="float64")
    std = valid.std(ddof=0)
    if not np.isfinite(std) or std == 0:
        return pd.Series(0.0, index=s.index).where(s.notna())
    z = (s - valid.mean()) / std
    return z.clip(-clip, clip) if clip is not None else z


def percentile_rank(s: pd.Series) -> pd.Series:
    """0~100 백분위. 사용자에게 보여줄 점수는 z 가 아니라 이 값이다."""
    return s.rank(pct=True) * 100.0
