"""Execution-free portfolio exposure and concentration metrics."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Position:
    symbol: str
    quantity: Decimal
    average_cost: Decimal
    market_price: Decimal

    @property
    def market_value(self) -> Decimal:
        return self.quantity * self.market_price

    @property
    def cost_basis(self) -> Decimal:
        return self.quantity * self.average_cost


def portfolio_snapshot(positions: list[Position]) -> dict:
    total_value = sum((p.market_value for p in positions), Decimal("0"))
    total_cost = sum((p.cost_basis for p in positions), Decimal("0"))
    return {
        "total_value": total_value,
        "total_cost": total_cost,
        "unrealized_pnl": total_value - total_cost,
        "positions": [
            {
                "symbol": p.symbol,
                "market_value": p.market_value,
                "weight": Decimal("0") if total_value == 0 else p.market_value / total_value,
            }
            for p in positions
        ],
    }
