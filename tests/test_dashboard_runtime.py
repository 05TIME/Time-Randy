from datetime import date
from decimal import Decimal

from airbnb_ops.dashboard_runtime import build_live_command_center
from airbnb_ops.service import Booking, Expense, PropertyConfig
from airbnb_ops.sqlite_store import SQLiteStore


def test_live_command_center_uses_persisted_booking_and_expense_data(tmp_path):
    store = SQLiteStore(tmp_path / "airbnb.sqlite3")
    store.save_property_config(
        PropertyConfig(
            nightly_rate=Decimal("150000"),
            outstanding_obligation=Decimal("900000"),
            target_monthly_fixed_costs=Decimal("100000"),
        )
    )
    store.save_booking(
        Booking("B-LIVE", date(2026, 8, 24), date(2026, 8, 27), Decimal("150000"), Decimal("30000"))
    )
    store.save_expense(
        Expense("E-LIVE", "cleaning", Decimal("20000"), date(2026, 8, 25), "turnover")
    )

    state = build_live_command_center(store, date(2026, 8, 23), date(2026, 8, 30))

    assert state.occupancy_percent == Decimal("3") / Decimal("7")
    assert state.gross_revenue == Decimal("450000")
    assert state.net_operating_result == Decimal("400000")
    assert state.outstanding_obligation == Decimal("900000")
    assert state.debt_clearing_nights == 6
