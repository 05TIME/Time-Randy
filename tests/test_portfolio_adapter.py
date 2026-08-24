from decimal import Decimal

from portfolio.risk import Position
from ui.portfolio_adapter import build_portfolio_view


def test_portfolio_adapter_returns_engine_values():
    view = build_portfolio_view([Position("VOO", Decimal("0.02"), Decimal("450"), Decimal("450"))])
    assert view["total_value"] == "9.00"
    assert view["total_cost"] == "9.00"
    assert view["unrealized_pnl"] == "0.00"
    assert view["positions"][0]["weight"] == "1"
