from datetime import date
from decimal import Decimal

from airbnb_ops import dashboard_routes
from airbnb_ops.service import Booking, Expense, PropertyConfig
from airbnb_ops.sqlite_store import SQLiteStore
from app import app


def test_command_center_route_exposes_live_ledger_metrics(tmp_path, monkeypatch):
    db_path = tmp_path / "airbnb.sqlite3"
    store = SQLiteStore(db_path)
    store.save_property_config(
        PropertyConfig(
            nightly_rate=Decimal("150000"),
            outstanding_obligation=Decimal("900000"),
        )
    )
    store.save_booking(Booking("B-ROUTE", date(2026, 8, 24), date(2026, 8, 26), Decimal("150000")))
    store.save_expense(Expense("E-ROUTE", "repair", Decimal("50000"), date(2026, 8, 25), "fix"))
    monkeypatch.setattr(dashboard_routes, "_ledger", store)

    response = app.test_client().get("/airbnb/command-center")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["data_source"] == "sqlite-ledger"
    assert payload["gross_revenue"] == "300000"
    assert payload["net_operating_result"] == "250000"
    assert payload["outstanding_obligation"] == "900000"
    assert payload["occupancy_percent"].startswith("0.285714")
