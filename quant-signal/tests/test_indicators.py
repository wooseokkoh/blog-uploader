import numpy as np
import pandas as pd
import pytest

from engine import indicators as I


def test_atr_constant_true_range(bars):
    """TR 이 항상 2 인 시리즈의 ATR 은 2 로 수렴한다."""
    df = bars(np.full(60, 100.0), spread=1.0)
    assert I.atr(df.high, df.low, df.close, 14).iloc[-1] == pytest.approx(2.0)


def test_rsi_bounds_and_extremes():
    up = pd.Series(np.arange(1, 61, dtype=float))
    assert I.rsi(up, 14).iloc[-1] == pytest.approx(100.0)
    down = pd.Series(np.arange(60, 0, -1, dtype=float))
    assert I.rsi(down, 14).iloc[-1] == pytest.approx(0.0)
    noisy = pd.Series(np.cumsum(np.random.default_rng(0).normal(0, 1, 300)) + 100)
    r = I.rsi(noisy, 14).dropna()
    assert r.between(0, 100).all()


def test_sma_known_value():
    s = pd.Series(np.arange(1, 61, dtype=float))
    assert I.sma(s, 20).iloc[-1] == pytest.approx(50.5)


def test_momentum_skips_recent_month():
    """12-1 모멘텀은 최근 21거래일을 제외한다."""
    s = pd.Series(np.concatenate([np.full(253, 100.0), np.full(21, 999.0)]))
    # 최근 급등 구간이 제외되므로 모멘텀은 0 이어야 한다.
    assert I.momentum(s, 252, 21).iloc[-1] == pytest.approx(0.0)


def test_realized_vol_is_annualized():
    rng = np.random.default_rng(42)
    daily = 0.01
    s = pd.Series(100 * np.exp(np.cumsum(rng.normal(0, daily, 2000))))
    got = I.realized_vol(s, 250).iloc[-1]
    assert got == pytest.approx(daily * np.sqrt(252), rel=0.25)


def test_zscore_handles_constant_and_empty():
    assert list(I.zscore(pd.Series([5.0, 5.0, 5.0]))) == [0.0, 0.0, 0.0]
    assert I.zscore(pd.Series([np.nan, np.nan])).isna().all()


def test_zscore_winsorizes():
    s = pd.Series([1.0] * 50 + [1e6])
    assert I.zscore(s, clip=3.0).max() == pytest.approx(3.0)
