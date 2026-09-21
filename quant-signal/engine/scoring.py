"""점수 -> 액션 매핑.

레짐이 RISK_OFF 면 아무리 점수가 높아도 신규 진입(ACCUMULATE)을
내지 않는다. 설계 문서의 "위험회피 구간에서는 신규 진입 신호를
발생시키지 않음" 규칙이 구현되는 지점이다.
"""
from __future__ import annotations

from typing import Tuple

import numpy as np

from .config import ScoreConfig
from .regime import Regime

ACCUMULATE = "ACCUMULATE"
HOLD = "HOLD"
REDUCE = "REDUCE"
EXIT = "EXIT"

ACTION_KO = {
    ACCUMULATE: "분할 매수",
    HOLD: "보유 유지",
    REDUCE: "비중 축소",
    EXIT: "청산",
}


def decide(score: float, regime: Regime, cfg: ScoreConfig) -> Tuple[str, str]:
    """(액션, 사유) 반환."""
    if score is None or not np.isfinite(score):
        return EXIT, "점수 산출 불가 — 데이터 부족"

    if score < cfg.reduce_below:
        return REDUCE, f"점수 {score:.0f} < {cfg.reduce_below:.0f} — 하위권"

    if score >= cfg.accumulate_at:
        if not regime.allows_new_entry:
            return HOLD, f"점수 {score:.0f} 로 상위권이나 시장 레짐이 위험회피 — 신규 진입 보류"
        return ACCUMULATE, f"점수 {score:.0f} ≥ {cfg.accumulate_at:.0f}, 레짐 {regime.state}"

    if score >= cfg.hold_at:
        return HOLD, f"점수 {score:.0f} — 중위권, 신규 진입 기준 미달"

    return HOLD, f"점수 {score:.0f} — 관망"
