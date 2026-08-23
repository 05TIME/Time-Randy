"""Runtime helpers for building a live Command Center from the ledger."""

from datetime import date
from decimal import Decimal

from .dashboard import build_command_center
from .finance import build_snapshot
from .sqlite_store import SQLiteStore


def build_live_command_center(store: SQLiteStore, period_start: date, period_end: date):
    service = store.load_service()
    summary = service.summary(period_start, period_end)
    period_nights = summary["available_nights"]
    occupancy = (
        Decimal(summary["booked_nights"]) / Decimal(period_nights)
        if period_nights else Decimal("0")
    )
    finance = build_snapshot(
        gross_revenue=summary["gross_revenue"],
        platform_fees=summary["platform_fees"],
        operating_expenses=summary["operating_expenses"],
        outstanding_obligation=summary["outstanding_obligation"],
        nightly_contribution=service.config.nightly_rate,
        fixed_costs=service.config.target_monthly_fixed_costs,
    )
    return build_command_center(
        occupancy_percent=occupancy,
        finance=finance,
        turnovers=[],
    )
