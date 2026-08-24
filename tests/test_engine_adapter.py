from decimal import Decimal

from forex.signals import MarketBar
from ui.engine_adapter import build_market_view


def test_engine_adapter_exposes_real_quantitative_outputs():
    bars = [MarketBar(str(i), Decimal(v), Decimal(v), Decimal(v), Decimal(v)) for i, v in enumerate([100, 101, 102, 103, 104, 105])]
    view = build_market_view(bars)
    assert view["last_price"] == "105"
    assert view["regime"]["name"] == "trend"
    assert view["signal"]["direction"] == "long"
    assert len(view["factors"]) == 2
