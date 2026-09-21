"""유니버스 구성.

위키피디아에서 S&P 500 구성종목을 받아오고, 실패하면 동봉된
폴백 목록(대형주 중심)을 쓴다. 네트워크가 막힌 환경에서도
파이프라인이 멈추지 않게 하기 위한 구조다.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

_FALLBACK = Path(__file__).with_name("universe_fallback.json")
_WIKI = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


def load_fallback() -> List[str]:
    return json.loads(_FALLBACK.read_text(encoding="utf-8"))["symbols"]


def sp500(use_remote: bool = True) -> List[str]:
    if use_remote:
        try:
            import pandas as pd

            tables = pd.read_html(_WIKI)
            syms = tables[0]["Symbol"].astype(str).str.replace(".", "-", regex=False)
            out = sorted(set(syms.tolist()))
            if len(out) > 400:
                return out
            print(f"[warn] S&P500 목록이 {len(out)}개뿐 — 폴백 사용")
        except Exception as exc:
            print(f"[warn] S&P500 목록 조회 실패 ({exc}) — 폴백 사용")
    return load_fallback()
