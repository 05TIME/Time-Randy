"""Live business metrics for the Airbnb Ops Command Center."""

from datetime import date

from .dashboard import BusinessCommandCenter, build_command_center
from .finance import build_snapshot
from .sqlite_store import SQLiteStore


def build_live_command_center(
    store: SQLiteStore,
    period_start: date,
    period_end: date,
) -> BusinessCommandCenter:
    """Build dashboard metrics directly from the persisted business ledger."""
    service = store.load_service()
    summary = service.summary(period_start, period_end)
    finance = build_snapshot(
        gross_revenue=summary["gross_revenue"],
        platform_fees=summary["platform_fees"],
        operating_expenses=summary["operating_expenses"],
        outstanding_obligation=summary["outstanding_obligation"],
        nightly_contribution=service.config.nightly_rate,
        fixed_costs=service.config.target_monthly_fixed_costs,
    )
    return build_command_center(
        occupancy_percent=summary["occupancy_rate"],
        finance=finance,
        turnovers=[],
    )
