import numpy as np

from engine.regime import detect, RISK_ON, NEUTRAL, RISK_OFF


def _macro(bars, trend_up, vix, vix3m, credit_up):
    n = 260
    line = np.linspace(100, 200, n) if trend_up else np.linspace(200, 100, n)
    credit = np.linspace(100, 200, n) if credit_up else np.linspace(200, 100, n)
    return {
        "SPY": bars(line),
        "^VIX": bars(np.full(n, float(vix))),
        "^VIX3M": bars(np.full(n, float(vix3m))),
        "HYG": bars(credit),
        "IEF": bars(np.full(n, 100.0)),
    }


def test_all_favorable_is_risk_on(bars):
    r = detect(_macro(bars, True, 15, 20, True))
    assert r.state == RISK_ON and r.allows_new_entry


def test_all_unfavorable_is_risk_off(bars):
    r = detect(_macro(bars, False, 30, 20, False))
    assert r.state == RISK_OFF and not r.allows_new_entry


def test_two_of_three_is_neutral(bars):
    r = detect(_macro(bars, True, 15, 20, False))
    assert r.state == NEUTRAL and r.allows_new_entry


def test_missing_data_fails_closed():
    """판정 근거가 없으면 보수적으로 막는다."""
    r = detect({})
    assert r.state == RISK_OFF and not r.allows_new_entry
    assert r.notes


def test_partial_data_uses_available_axes(bars):
    """VIX 만 없어도 나머지 두 축으로 판정한다."""
    m = _macro(bars, True, 15, 20, True)
    del m["^VIX3M"]
    r = detect(m)
    assert r.components["volatility"] is None
    assert r.state == RISK_ON
