"""시그널 파이프라인: 데이터 -> 레짐 -> 팩터 -> 진입계획 -> signals.json"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Sequence

import pandas as pd

from . import __version__
from .config import Settings, DEFAULT
from .data.base import PriceSource, PricePanel, validate
from .entry import build as build_entry
from .factors import raw_factors, composite
from .indicators import dollar_volume
from .regime import detect, REGIME_KO, Regime
from .scoring import decide, ACTION_KO, ACCUMULATE

# 레짐 판정에만 쓰고 종목 후보로는 쓰지 않는 심볼
MACRO_SYMBOLS = ["SPY", "^VIX", "^VIX3M", "HYG", "IEF"]


def _liquid(panel: PricePanel, min_dv: float) -> PricePanel:
    out = {}
    for sym, df in panel.items():
        dv = dollar_volume(df["close"], df["volume"]).dropna()
        if len(dv) and float(dv.iloc[-1]) >= min_dv:
            out[sym] = df
    return out


def run(
    source: PriceSource,
    symbols: Sequence[str],
    settings: Settings = DEFAULT,
    market: str = "US_EQUITY",
    as_of: Optional[pd.Timestamp] = None,
) -> dict:
    """전체 파이프라인 실행 후 signals.json 에 들어갈 dict 반환."""
    wanted = list(dict.fromkeys(list(symbols) + MACRO_SYMBOLS))
    lookback = settings.min_history_days + settings.factors.momentum_lookback
    panel = source.fetch(wanted, lookback)

    regime = detect(panel, settings.regime)

    # 종목 후보 = 매크로 심볼 제외 + 이력 충분 + 유동성 통과
    candidates = {s: d for s, d in panel.items() if s not in MACRO_SYMBOLS}
    candidates = validate(candidates, settings.min_history_days)
    before_liq = len(candidates)
    candidates = _liquid(candidates, settings.min_dollar_volume)

    raw = raw_factors(candidates, settings.factors)
    scores = composite(raw, settings.factors) if not raw.empty else pd.DataFrame()

    signals: List[dict] = []
    if not scores.empty:
        ranked = scores.sort_values("score", ascending=False)
        for sym, row in ranked.head(settings.top_n).iterrows():
            sig = _make_signal(sym, row, candidates[sym], regime, settings, market, as_of)
            if sig:
                signals.append(sig)

    generated = (as_of or pd.Timestamp.now(tz=timezone.utc)).isoformat()
    return {
        "schema_version": 1,
        "engine_version": __version__,
        "generated_at": generated,
        "market": market,
        "regime": regime.to_dict(),
        "regime_label": REGIME_KO.get(regime.state, regime.state),
        "universe": {
            "requested": len(symbols),
            "with_data": before_liq,
            "after_liquidity": len(candidates),
            "emitted": len(signals),
        },
        "params": settings.to_dict(),
        "signals": signals,
        "disclaimer": (
            "본 정보는 투자 참고자료이며 투자 권유가 아닙니다. "
            "모든 투자의 최종 판단과 책임은 투자자 본인에게 있으며 원금 손실이 발생할 수 있습니다."
        ),
    }


def _make_signal(
    sym: str,
    row: pd.Series,
    df: pd.DataFrame,
    regime: Regime,
    settings: Settings,
    market: str,
    as_of: Optional[pd.Timestamp],
) -> Optional[dict]:
    score = float(row["score"])
    action, reason = decide(score, regime, settings.score)

    built = build_entry(df, settings.risk, as_of)
    # 신규 진입 신호인데 진입가를 못 만들면 내보내지 않는다.
    # "사라"고만 하고 얼마에 살지 못 주는 신호는 이 제품의 정의상 불완전하다.
    if built is None and action == ACCUMULATE:
        return None

    last_bar = df.iloc[-1]
    out = {
        "symbol": sym,
        "market": market,
        "as_of": str(df.index[-1].date()),
        "last_close": round(float(last_bar["close"]), 4),
        "score": round(score, 1),
        "action": action,
        "action_label": ACTION_KO.get(action, action),
        "reason": reason,
        "regime": regime.state,
        "factors": {
            k.replace("_pct", ""): round(float(row[k]), 1)
            for k in row.index
            if k.endswith("_pct") and pd.notna(row[k])
        },
    }
    if built is not None:
        plan, risk = built
        out["entry_plan"] = plan.to_dict()
        out["risk"] = risk.to_dict()
    return out


def write(payload: dict, out_dir: Path) -> Path:
    """최신 스냅샷과 날짜별 불변 기록을 함께 남긴다.

    이력 보관은 성과 대시보드의 근거가 된다. 신호를 사후에 고치지
    않는다는 것을 보여줄 수 있어야 유료화 명분이 선다.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    latest = out_dir / "signals.json"
    latest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    hist_dir = out_dir / "history"
    hist_dir.mkdir(exist_ok=True)
    stamp = payload["generated_at"][:10]
    (hist_dir / f"{stamp}-{payload['market'].lower()}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return latest
