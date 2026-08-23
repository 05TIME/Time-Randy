from decimal import Decimal
from datetime import datetime

from airbnb_ops.dashboard import build_command_center
from airbnb_ops.finance import build_snapshot
from airbnb_ops.turnover import Turnover, TurnoverState


def test_command_center_aggregates_business_state():
    finance = build_snapshot(
        gross_revenue=Decimal("1500000"),
        platform_fees=Decimal("75000"),
        operating_expenses=Decimal("300000"),
        outstanding_obligation=Decimal("900000"),
        nightly_contribution=Decimal("125000"),
    )
    ready = Turnover("B1", datetime(2026, 8, 23, 11), datetime(2026, 8, 23, 15), TurnoverState.READY)
    escalated = Turnover("B2", datetime(2026, 8, 24, 11), datetime(2026, 8, 24, 15), TurnoverState.ESCALATED)
    result = build_command_center(
        occupancy_percent=Decimal("0.75"),
        finance=finance,
        turnovers=[ready, escalated],
        low_inventory_items=2,
        open_maintenance_issues=1,
    )
    assert result.occupancy_percent == Decimal("0.75")
    assert result.upcoming_turnovers == 2
    assert result.turnovers_ready == 1
    assert result.turnovers_escalated == 1
    assert result.low_inventory_items == 2
    assert result.open_maintenance_issues == 1
