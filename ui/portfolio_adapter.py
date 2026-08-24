"""Presentation adapter for TIMEŒ portfolio-risk metrics."""

from decimal import Decimal

from portfolio.risk import Position, portfolio_snapshot


def build_portfolio_view(positions: list[Position]) -> dict:
    """Return JSON-safe portfolio metrics for the Command Center."""
    snapshot = portfolio_snapshot(positions)
    return {
        "total_value": str(snapshot["total_value"]),
        "total_cost": str(snapshot["total_cost"]),
        "unrealized_pnl": str(snapshot["unrealized_pnl"]),
        "positions": [
            {"symbol": item["symbol"], "market_value": str(item["market_value"]), "weight": str(item["weight"])}
            for item in snapshot["positions"]
        ],
    }
