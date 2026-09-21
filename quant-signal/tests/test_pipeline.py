import json

import pytest

from engine.config import DEFAULT, Settings, RegimeConfig, FactorConfig, RiskConfig, ScoreConfig
from engine.data.synthetic import SyntheticSource
from engine.pipeline import run, write, MACRO_SYMBOLS
from engine.scoring import ACCUMULATE


@pytest.fixture(scope="module")
def payload():
    syms = [f"S{i:02d}" for i in range(30)]
    return run(SyntheticSource(seed=7), syms, DEFAULT, market="TEST")


def test_payload_shape(payload):
    for key in ("schema_version", "generated_at", "regime", "signals", "params", "disclaimer"):
        assert key in payload
    assert payload["market"] == "TEST"


def test_macro_symbols_are_not_emitted_as_signals(payload):
    emitted = {s["symbol"] for s in payload["signals"]}
    assert not emitted & set(MACRO_SYMBOLS)


def test_every_buy_signal_has_price_and_stop(payload):
    """'사라'고 하면서 얼마에 살지 못 주는 신호는 내보내지 않는다."""
    for s in payload["signals"]:
        if s["action"] != ACCUMULATE:
            continue
        assert s["entry_plan"]["tranches"], s["symbol"]
        assert s["risk"]["stop_loss"] < s["entry_plan"]["avg_entry"]
        assert 0 < s["risk"]["position_size_pct"] <= DEFAULT.risk.max_position_pct


def test_signals_sorted_by_score(payload):
    scores = [s["score"] for s in payload["signals"]]
    assert scores == sorted(scores, reverse=True)


def test_top_n_is_respected():
    settings = Settings(RegimeConfig(), FactorConfig(), RiskConfig(), ScoreConfig(), top_n=5)
    out = run(SyntheticSource(seed=7), [f"S{i:02d}" for i in range(30)], settings)
    assert len(out["signals"]) <= 5


def test_liquidity_filter_excludes_thin_names():
    settings = Settings(RegimeConfig(), FactorConfig(), RiskConfig(), ScoreConfig(),
                        min_dollar_volume=1e15)
    out = run(SyntheticSource(seed=7), [f"S{i:02d}" for i in range(30)], settings)
    assert out["universe"]["after_liquidity"] == 0
    assert out["signals"] == []


def test_write_creates_latest_and_history(payload, tmp_path):
    path = write(payload, tmp_path)
    assert path.exists()
    hist = list((tmp_path / "history").glob("*.json"))
    assert len(hist) == 1
    assert json.loads(path.read_text(encoding="utf-8"))["market"] == "TEST"


def test_output_is_json_serializable(payload):
    json.dumps(payload, ensure_ascii=False)
