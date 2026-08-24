from decimal import Decimal

from portfolio.risk import Position, portfolio_snapshot


def test_portfolio_snapshot_tracks_value_cost_and_weight():
    result = portfolio_snapshot([
        Position("VOO", Decimal("0.02"), Decimal("450"), Decimal("450")),
    ])
    assert result["total_value"] == Decimal("9.00")
    assert result["total_cost"] == Decimal("9.00")
    assert result["unrealized_pnl"] == Decimal("0.00")
    assert result["positions"][0]["weight"] == Decimal("1")
