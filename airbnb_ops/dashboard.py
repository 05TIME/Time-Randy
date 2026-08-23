"""Business command-center view model for the Airbnb Ops dashboard."""

from dataclasses import asdict, dataclass
from decimal import Decimal

from .finance import FinanceSnapshot
from .turnover import Turnover, TurnoverState


@dataclass(frozen=True)
class BusinessCommandCenter:
    occupancy_percent: Decimal
    gross_revenue: Decimal
    net_operating_result: Decimal
    outstanding_obligation: Decimal
    debt_clearing_nights: int
    upcoming_turnovers: int
    turnovers_ready: int
    turnovers_escalated: int
    low_inventory_items: int
    open_maintenance_issues: int

    def as_dict(self) -> dict:
        return asdict(self)


def build_command_center(
    *,
    occupancy_percent: Decimal,
    finance: FinanceSnapshot,
    turnovers: list[Turnover],
    low_inventory_items: int = 0,
    open_maintenance_issues: int = 0,
) -> BusinessCommandCenter:
    if not Decimal("0") <= occupancy_percent <= Decimal("1"):
        raise ValueError("occupancy_percent must be between 0 and 1")
    if low_inventory_items < 0 or open_maintenance_issues < 0:
        raise ValueError("operational counts cannot be negative")

    return BusinessCommandCenter(
        occupancy_percent=occupancy_percent,
        gross_revenue=finance.gross_revenue,
        net_operating_result=finance.net_operating_result,
        outstanding_obligation=finance.outstanding_obligation,
        debt_clearing_nights=finance.debt_clearing_nights,
        upcoming_turnovers=len(turnovers),
        turnovers_ready=sum(t.state == TurnoverState.READY for t in turnovers),
        turnovers_escalated=sum(t.state == TurnoverState.ESCALATED for t in turnovers),
        low_inventory_items=low_inventory_items,
        open_maintenance_issues=open_maintenance_issues,
    )
