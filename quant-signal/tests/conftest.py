import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.data.base import normalize  # noqa: E402


def make_bars(close, spread=1.0, volume=1e6, end="2026-09-18"):
    """종가 배열로 OHLCV 프레임을 만든다. spread 고정 시 TR = 2*spread."""
    close = np.asarray(close, dtype=float)
    idx = pd.bdate_range(end=end, periods=len(close))
    c = pd.Series(close, index=idx)
    return normalize(
        pd.DataFrame(
            {"open": c, "high": c + spread, "low": c - spread, "close": c, "volume": volume},
            index=idx,
        )
    )


@pytest.fixture
def bars():
    return make_bars
