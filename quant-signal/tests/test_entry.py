import numpy as np
import pytest

from engine.config import RiskConfig
from engine.entry import build


CFG = RiskConfig()


def test_position_size_implies_configured_risk(bars):
    """비중 x 주당위험 / 진입가 == 감내손실률 (상한에 걸리지 않는 경우)."""
    df = bars(np.full(60, 100.0), spread=5.0)  # ATR = 10
    plan, risk = build(df, CFG)
    implied = risk.position_size_pct * risk.risk_per_share / plan.avg_entry
    assert implied == pytest.approx(CFG.account_risk_pct, rel=1e-2)


def test_position_size_respects_cap(bars):
    df = bars(np.full(60, 100.0), spread=0.2)  # ATR 작음 -> 비중 커짐
    _, risk = build(df, CFG)
    assert risk.position_size_pct == pytest.approx(CFG.max_position_pct)


def test_higher_volatility_shrinks_position(bars):
    _, low = build(bars(np.full(60, 100.0), spread=2.0), CFG)
    _, high = build(bars(np.full(60, 100.0), spread=8.0), CFG)
    assert high.position_size_pct < low.position_size_pct


def test_all_tranches_below_last_close(bars):
    """지정가 분할매수는 현재가보다 높을 수 없다 (20일선 지지 케이스 포함)."""
    for close in (np.full(60, 100.0), np.linspace(80, 100, 60), np.linspace(120, 100, 60)):
        df = bars(close)
        plan, _ = build(df, CFG)
        last = float(df.close.iloc[-1])
        assert all(t.price < last for t in plan.tranches), plan.tranches


def test_tranches_are_ordered_and_weighted(bars):
    plan, _ = build(bars(np.full(60, 100.0)), CFG)
    prices = [t.price for t in plan.tranches]
    assert prices == sorted(prices, reverse=True)
    assert sum(t.weight for t in plan.tranches) == pytest.approx(1.0)


def test_stop_is_below_average_entry(bars):
    plan, risk = build(bars(np.full(60, 100.0)), CFG)
    assert risk.stop_loss < plan.avg_entry
    assert risk.risk_per_share == pytest.approx(plan.avg_entry - risk.stop_loss, abs=0.02)


def test_returns_none_without_enough_history(bars):
    assert build(bars(np.full(5, 100.0)), CFG) is None
