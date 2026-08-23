from datetime import date
from decimal import Decimal

from airbnb_ops.pricing import recommend_rate
from airbnb_ops.service import Booking, Expense
from airbnb_ops.store import SQLiteStore


def test_sqlite_store_round_trips_booking_and_expense(tmp_path):
    store = SQLiteStore(str(tmp_path / "airbnb.sqlite3"))
    booking = Booking("b1", date(2026, 8, 10), date(2026, 8, 12), Decimal("150000"), Decimal("4500"))
    expense = Expense("e1", "cleaning", Decimal("10000"), date(2026, 8, 12), "turnover")

    store.add_booking(booking)
    store.add_expense(expense)

    assert store.bookings() == [booking]
    assert store.expenses() == [expense]


def test_low_inventory_and_maintenance_are_exposed(tmp_path):
    store = SQLiteStore(str(tmp_path / "airbnb.sqlite3"))
    store.set_inventory("toilet paper", 2, 4)
    issue_id = store.add_maintenance("Generator inspection", "high")

    assert store.low_inventory()[0]["item"] == "toilet paper"
    assert store.open_maintenance()[0]["issue_id"] == issue_id


def test_pricing_recommendation_is_transparent():
    rec = recommend_rate(Decimal("150000"), Decimal("0.20"), 10)
    assert rec.recommended_rate == Decimal("127500")
    assert "15%" in rec.reason
