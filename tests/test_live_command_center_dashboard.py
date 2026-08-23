from datetime import date
from decimal import Decimal

from airbnb_ops.service import Booking, PropertyConfig
from airbnb_ops.sqlite_store import SQLiteStore
from app import app


def test_command_center_reads_airbnb_sqlite(tmp_path, monkeypatch):
    db_path = tmp_path / "airbnb.sqlite3"
    store = SQLiteStore(db_path)
    store.save_property_config(
        PropertyConfig(
            nightly_rate=Decimal("150000"),
            outstanding_obligation=Decimal("900000"),
        )
    )
    year = date.today().year
    month = date.today().month
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    start = date(year, month, 1)
    check_out = start.replace(day=min(5, (next_month - start).days))
    store.save_booking(Booking("B-LIVE", start, check_out, Decimal("150000")))

    monkeypatch.setenv("AIRBNB_DB_PATH", str(db_path))
    client = app.test_client()
    response = client.get("/chief-of-staff")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Live Airbnb ledger" in body
    assert "₦900,000" in body
    assert "Debt nights" in body
