from datetime import date
from decimal import Decimal

from airbnb_ops.live_dashboard import live_command_center
from airbnb_ops.service import Booking, PropertyConfig
from airbnb_ops.sqlite_store import SQLiteStore


def test_live_dashboard_reads_sqlite(tmp_path):
    store = SQLiteStore(tmp_path / "airbnb.sqlite3")
    store.save_property_config(PropertyConfig(outstanding_obligation=Decimal("300000")))
    store.save_booking(Booking("B1", date(2026, 9, 1), date(2026, 9, 3), Decimal("150000")))
    state = live_command_center(store, date(2026, 9, 1), date(2026, 9, 4))
    assert state.occupancy_percent == Decimal("0.6666666666666666666666666667")
    assert state.gross_revenue == Decimal("300000")
    assert state.debt_clearing_nights == 2
