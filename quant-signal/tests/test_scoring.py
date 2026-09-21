import pytest

from engine.config import ScoreConfig
from engine.regime import Regime, RISK_ON, RISK_OFF, NEUTRAL
from engine.scoring import decide, ACCUMULATE, HOLD, REDUCE, EXIT

CFG = ScoreConfig()
ON = Regime(RISK_ON, 1.0)
OFF = Regime(RISK_OFF, 0.0)
MID = Regime(NEUTRAL, 0.66)


def test_high_score_in_risk_on_accumulates():
    assert decide(85.0, ON, CFG)[0] == ACCUMULATE


def test_high_score_in_risk_off_is_blocked():
    """설계의 핵심 규칙: 위험회피 구간에서는 신규 진입을 내지 않는다."""
    action, reason = decide(99.0, OFF, CFG)
    assert action == HOLD
    assert "위험회피" in reason


def test_neutral_regime_allows_entry():
    assert decide(85.0, MID, CFG)[0] == ACCUMULATE


def test_low_score_reduces_regardless_of_regime():
    assert decide(10.0, ON, CFG)[0] == REDUCE
    assert decide(10.0, OFF, CFG)[0] == REDUCE


def test_mid_score_holds():
    assert decide(60.0, ON, CFG)[0] == HOLD


@pytest.mark.parametrize("bad", [None, float("nan")])
def test_unscoreable_exits(bad):
    assert decide(bad, ON, CFG)[0] == EXIT
