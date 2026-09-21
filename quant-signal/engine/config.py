"""엔진 전역 설정.

모든 파라미터를 여기 모아 둔다. 백테스트에서 파라미터를 바꿔 가며 돌릴 때
함수 시그니처를 건드리지 않기 위해서다.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict


@dataclass(frozen=True)
class RegimeConfig:
    """시장 레짐 판정 파라미터."""

    trend_symbol: str = "SPY"
    trend_sma: int = 200
    vix_symbol: str = "^VIX"
    vix_far_symbol: str = "^VIX3M"
    # VIX/VIX3M 가 이 값보다 낮으면 콘탱고(평온) 로 본다.
    vix_contango_max: float = 1.0
    credit_risk_symbol: str = "HYG"
    credit_safe_symbol: str = "IEF"
    credit_sma: int = 50


@dataclass(frozen=True)
class FactorConfig:
    """횡단면 팩터 파라미터."""

    # 12-1 모멘텀: 최근 1개월을 제외한 12개월 수익률 (단기 반전 효과 제거)
    momentum_lookback: int = 252
    momentum_skip: int = 21
    trend_sma: int = 200
    vol_lookback: int = 60
    # z-score 를 자르는 범위. 이상치 한 종목이 순위를 뒤집는 것을 막는다.
    winsorize_z: float = 3.0
    weights: Dict[str, float] = field(
        default_factory=lambda: {
            "momentum": 0.40,
            "trend": 0.30,
            "low_vol": 0.20,
            "volume_confirm": 0.10,
        }
    )


@dataclass(frozen=True)
class RiskConfig:
    """진입가·손절가·비중 계산 파라미터."""

    atr_period: int = 14
    # 손절 = 평균진입가 - stop_atr_mult * ATR
    stop_atr_mult: float = 2.0
    # 계좌 자산 대비 1회 매매에서 감내할 손실 비율
    account_risk_pct: float = 1.0
    # 한 종목이 가질 수 있는 최대 비중
    max_position_pct: float = 10.0
    # 진입 분할: (ATR 배수 아래, 비중)
    tranches: tuple = ((0.5, 0.4), (1.0, 0.3), (1.5, 0.3))
    # 신호 유효기간 (거래일)
    valid_days: int = 5


@dataclass(frozen=True)
class ScoreConfig:
    """점수 -> 액션 매핑 임계값."""

    accumulate_at: float = 70.0
    hold_at: float = 55.0
    reduce_below: float = 35.0


@dataclass(frozen=True)
class Settings:
    regime: RegimeConfig = field(default_factory=RegimeConfig)
    factors: FactorConfig = field(default_factory=FactorConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    score: ScoreConfig = field(default_factory=ScoreConfig)

    # 유동성 하한. 이 아래는 슬리피지로 신호가 무의미해진다.
    min_dollar_volume: float = 5_000_000.0
    # 지표 계산에 필요한 최소 거래일 수
    min_history_days: int = 260
    # 출력할 상위 종목 수
    top_n: int = 25

    def to_dict(self) -> dict:
        return asdict(self)


DEFAULT = Settings()
