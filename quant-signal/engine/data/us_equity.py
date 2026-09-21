"""미국 주식 일봉 어댑터 (yfinance).

무료 데이터라 P0 검증용으로만 쓴다. 유료 전환 시 이 파일만
Polygon/EODHD 어댑터로 교체하면 엔진 본체는 그대로 간다.
"""
from __future__ import annotations

import time
from typing import Sequence

import pandas as pd

from .base import PricePanel, normalize

_BATCH = 50
_RETRIES = 3


class YahooSource:
    """yfinance 기반 공급자. 배치로 끊어서 받고 실패 시 재시도한다."""

    def __init__(self, batch_size: int = _BATCH, retries: int = _RETRIES, pause: float = 1.5):
        self.batch_size = batch_size
        self.retries = retries
        self.pause = pause

    def fetch(self, symbols: Sequence[str], lookback_days: int) -> PricePanel:
        import yfinance as yf  # 무거우므로 호출 시점에 import

        symbols = list(dict.fromkeys(symbols))  # 순서 유지 중복 제거
        period = f"{max(lookback_days, 260) + 60}d"
        panel: PricePanel = {}

        for start in range(0, len(symbols), self.batch_size):
            chunk = symbols[start : start + self.batch_size]
            raw = self._download(yf, chunk, period)
            if raw is None:
                continue
            for sym in chunk:
                df = self._extract(raw, sym, len(chunk))
                if df is None or df.empty:
                    continue
                try:
                    panel[sym] = normalize(df)
                except ValueError:
                    continue
            time.sleep(self.pause)
        return panel

    def _download(self, yf, chunk: Sequence[str], period: str):
        last_err: Exception | None = None
        for attempt in range(self.retries):
            try:
                return yf.download(
                    list(chunk),
                    period=period,
                    interval="1d",
                    auto_adjust=True,  # 배당·액면분할 반영. 모멘텀 계산에 필수.
                    group_by="ticker",
                    threads=True,
                    progress=False,
                )
            except Exception as exc:  # 네트워크 오류는 재시도로 흡수
                last_err = exc
                time.sleep(2.0 * (attempt + 1))
        print(f"[warn] 배치 다운로드 실패 ({len(chunk)}종목): {last_err}")
        return None

    @staticmethod
    def _extract(raw: pd.DataFrame, sym: str, chunk_len: int) -> pd.DataFrame | None:
        """yfinance 는 단일/복수 종목에서 컬럼 구조가 달라진다."""
        if isinstance(raw.columns, pd.MultiIndex):
            if sym not in raw.columns.get_level_values(0):
                return None
            return raw[sym].dropna(how="all")
        return raw.dropna(how="all") if chunk_len == 1 else None
