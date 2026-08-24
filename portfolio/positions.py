"""Simple, execution-free portfolio position tracking."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Position:
    symbol: str
    invested_usd: Decimal
    shares: Decimal = Decimal("0")


def position_summary(position: Position, mark_price: Decimal | None = None) -> dict:
    """Return bookkeeping metrics; never submits or modifies an order."""
    market_value = None if mark_price is None else position.shares * mark_price
    return {
        "symbol": position.symbol,
        "invested_usd": str(position.invested_usd),
        "shares": str(position.shares),
        "mark_price": None if mark_price is None else str(mark_price),
        "market_value": None if market_value is None else str(market_value),
    }
