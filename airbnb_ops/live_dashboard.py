"""Build dashboard state from the persistent SQLite ledger."""

from datetime import date
from decimal import Decimal

from .dashboard import BusinessCommandCenter, build_command_center
from .sqlite_store import SQLiteStore


def live_command_center(store: SQLiteStore, period_start: date, period_end: date) -> BusinessCommandCenter:
    service = store.load_service()
    summary = service.summary(period_start, period_end)
    finance_like = type("Finance", (), {
        "gross_revenue": summary["gross_revenue"],
        "platform_fees": summary["platform_fees"],
        "operating_expenses": summary["operating_expenses"],
        "net_operating_result": summary["net_operating_result"],
        "outstanding_obligation": summary["outstanding_obligation"],
        "cash_available_for_debt": max(Decimal("0"), summary["net_operating_result"]),
        "debt_clearing_nights": summary["debt_clearing_nights"],
        "break_even_nights": 0,
    })()
    return build_command_center(
        occupancy_percent=summary["occupancy_rate"],
        finance=finance_like,
        turnovers=[],
    )
