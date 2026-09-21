"""진입 계획: 얼마에, 언제까지, 얼마나.

이 모듈이 제품의 차별점이다. "종목만 찍어 주는" 서비스와
"리스크 관리 도구" 를 가르는 지점이라 계산 근거를 전부 출력에 남긴다.

핵심 공식
---------
  손절선   = 가중평균 진입가 - stop_atr_mult x ATR
  주식수   = (계좌자산 x 감내위험%) / (진입가 - 손절선)
  비중(%)  = 주식수 x 진입가 / 계좌자산
           = 감내위험% x 진입가 / (진입가 - 손절선)

계좌 규모와 무관하게 비중이 결정되므로, 사용자 계좌 잔고를
서버가 알 필요가 없다. 이건 규제 측면에서도 중요하다 —
개인 자산에 맞춘 조언이 아니라 모든 구독자에게 동일한 비중을
제시하는 구조여야 유사투자자문업 범위 안에 머문다.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Optional

import numpy as np
import pandas as pd

from .config import RiskConfig
from . import indicators as I


@dataclass
class Tranche:
    price: float
    weight: float
    note: str


@dataclass
class EntryPlan:
    method: str
    tranches: List[Tranche]
    avg_entry: float
    valid_until: str
    invalidate_if: str

    def to_dict(self) -> dict:
        return {
            "method": self.method,
            "tranches": [asdict(t) for t in self.tranches],
            "avg_entry": self.avg_entry,
            "valid_until": self.valid_until,
            "invalidate_if": self.invalidate_if,
        }


@dataclass
class RiskPlan:
    stop_loss: float
    atr: float
    atr_pct: float
    position_size_pct: float
    max_loss_pct: float
    risk_per_share: float

    def to_dict(self) -> dict:
        return {k: round(v, 4) for k, v in asdict(self).items()}


def _round_price(x: float) -> float:
    """호가 단위에 맞춘 반올림. 소수점 6자리 가격이 나오면 못 쓴다."""
    return round(x, 2) if x >= 1.0 else round(x, 4)


def build(
    df: pd.DataFrame,
    cfg: RiskConfig,
    as_of: Optional[pd.Timestamp] = None,
) -> Optional[tuple[EntryPlan, RiskPlan]]:
    """일봉 데이터로 진입·리스크 계획을 만든다. 계산 불가면 None."""
    close = df["close"]
    atr_series = I.atr(df["high"], df["low"], close, cfg.atr_period).dropna()
    if atr_series.empty or len(close) < cfg.atr_period + 1:
        return None

    last = float(close.iloc[-1])
    a = float(atr_series.iloc[-1])
    if not np.isfinite(a) or a <= 0 or last <= 0:
        return None

    sma20 = I.sma(close, 20).dropna()
    support = float(sma20.iloc[-1]) if len(sma20) else np.nan

    tranches: List[Tranche] = []
    for idx, (mult, weight) in enumerate(cfg.tranches):
        price = last - mult * a
        note = f"종가 -{mult:g} ATR"
        # 마지막 분할은 20일선이 (a) 그 가격보다 위이고 (b) 현재가보다 아래일 때만
        # 지지선을 쓴다. 지지선 위에서 체결되는 편이 확률이 낫고 손절폭도 줄지만,
        # 현재가보다 높은 지정가는 분할매수로서 의미가 없으므로 배제한다.
        if (
            idx == len(cfg.tranches) - 1
            and np.isfinite(support)
            and price < support < last
        ):
            price, note = support, "20일선 지지"
        if price <= 0:
            return None
        tranches.append(Tranche(_round_price(price), round(weight, 4), note))

    total_w = sum(t.weight for t in tranches)
    if total_w <= 0:
        return None
    avg_entry = sum(t.price * t.weight for t in tranches) / total_w

    stop = avg_entry - cfg.stop_atr_mult * a
    if stop <= 0:
        return None
    risk_per_share = avg_entry - stop

    # 비중 = 감내위험% x 진입가 / 주당위험 (계좌 규모 불변)
    size_pct = min(cfg.account_risk_pct * avg_entry / risk_per_share, cfg.max_position_pct)

    base = as_of if as_of is not None else pd.Timestamp(df.index[-1])
    valid_until = (base + pd.tseries.offsets.BDay(cfg.valid_days)).strftime("%Y-%m-%d")

    plan = EntryPlan(
        method=f"{len(tranches)}분할 지정가",
        tranches=tranches,
        avg_entry=_round_price(avg_entry),
        valid_until=valid_until,
        invalidate_if=f"종가 {_round_price(stop)} 하회 시 신호 무효",
    )
    risk = RiskPlan(
        stop_loss=_round_price(stop),
        atr=round(a, 4),
        atr_pct=round(a / last * 100.0, 3),
        position_size_pct=round(size_pct, 2),
        max_loss_pct=round(cfg.account_risk_pct, 2),
        risk_per_share=round(risk_per_share, 4),
    )
    return plan, risk
