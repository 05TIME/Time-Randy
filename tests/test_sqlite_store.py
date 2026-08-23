from datetime import date
from decimal import Decimal

from airbnb_ops.service import Booking, Expense, PropertyConfig
from airbnb_ops.sqlite_store import SQLiteStore


def test_sqlite_round_trip(tmp_path):
    store = SQLiteStore(tmp_path / "airbnb.sqlite3")
    store.save_property_config(PropertyConfig(outstanding_obligation=Decimal("900000")))
    store.save_booking(Booking("B1", date(2026, 9, 1), date(2026, 9, 3), Decimal("150000"), Decimal("7500")))
    store.save_expense(Expense("E1", "cleaning", Decimal("20000"), date(2026, 9, 2), "Turnover"))

    service = store.load_service()
    assert service.config.outstanding_obligation == Decimal("900000")
    assert len(service.bookings) == 1
    assert len(service.expenses) == 1
    summary = service.summary(date(2026, 9, 1), date(2026, 9, 4))
    assert summary["booked_nights"] == 2
    assert summary["gross_revenue"] == Decimal("300000")
