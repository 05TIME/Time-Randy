from datetime import date
from decimal import Decimal

from airbnb_ops.service import Booking, Expense, PropertyConfig
from airbnb_ops.sqlite_store import SQLiteStore
from airbnb_ops import dashboard_routes
from app import app


def test_command_center_uses_persisted_ledger(tmp_path, monkeypatch):
    db_path = tmp_path / "airbnb.sqlite3"
    store = SQLiteStore(db_path)
    store.save_property_config(
        PropertyConfig(
            nightly_rate=Decimal("150000"),
            outstanding_obligation=Decimal("900000"),
            target_monthly_fixed_costs=Decimal("100000"),
        )
    )
    store.save_booking(Booking("B1", date(2026, 8, 10), date(2026, 8, 13), Decimal("150000")))
    store.save_expense(Expense("E1", "repair", Decimal("50000"), date(2026, 8, 11)))
    monkeypatch.setenv("AIRBNB_DB_PATH", str(db_path))
    response = app.test_client().get("/airbnb/command-center")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["data_source"] == "sqlite-ledger"
    assert payload["gross_revenue"] == "450000"
    assert payload["net_operating_result"] == "400000"
    assert payload["outstanding_obligation"] == "900000"
    # Debt-clearing nights use the realized net operating contribution per booked night.
    assert payload["debt_clearing_nights"] == 7
    assert payload["occupancy_percent"] == "0.09677419354838709677419354839"


def test_live_state_falls_back_to_configured_rate_for_zero_or_negative_contribution(tmp_path):
    db_path = tmp_path / "airbnb.sqlite3"
    store = SQLiteStore(db_path)
    store.save_property_config(PropertyConfig(nightly_rate=Decimal("150000")))
    monkeypatch = __import__("pytest").MonkeyPatch()
    monkeypatch.setenv("AIRBNB_DB_PATH", str(db_path))
    try:
        summary, finance = dashboard_routes._live_business_state(date(2026, 8, 23))
        assert summary["booked_nights"] == 0
        assert finance.debt_clearing_nights == 0
    finally:
        monkeypatch.undo()
