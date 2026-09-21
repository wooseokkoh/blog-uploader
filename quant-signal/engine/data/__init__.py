"""데이터 어댑터.

모든 어댑터는 `PriceSource` 프로토콜을 만족한다. 시장을 추가할 때
(국내주식/선물/코인) 엔진 본체를 건드리지 않고 어댑터만 추가하면 된다.
"""
from .base import PriceSource, PricePanel, empty_panel

__all__ = ["PriceSource", "PricePanel", "empty_panel"]
