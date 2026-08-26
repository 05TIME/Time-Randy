"""SQLite persistence for the TIMEŒ Airbnb Ops ledger."""

import os
import sqlite3
from datetime import date
from decimal import Decimal
from pathlib import Path

from .service import AirbnbOpsService, Booking, Expense, PropertyConfig


SCHEMA = """
CREATE TABLE IF NOT EXISTS property_config (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    property_name TEXT NOT NULL,
    nightly_rate TEXT NOT NULL,
    outstanding_obligation TEXT NOT NULL,
    target_monthly_fixed_costs TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS bookings (
    booking_id TEXT PRIMARY KEY,
    check_in TEXT NOT NULL,
    check_out TEXT NOT NULL,
    nightly_rate TEXT NOT NULL,
    platform_fee TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS expenses (
    expense_id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    amount TEXT NOT NULL,
    expense_date TEXT NOT NULL,
    note TEXT NOT NULL
);
"""


def _default_database_path() -> str:
    """Use Vercel's writable temp filesystem unless explicitly configured."""
    if os.getenv("AIRBNB_DB_PATH"):
        return os.environ["AIRBNB_DB_PATH"]
    if os.getenv("VERCEL"):
        return "/tmp/airbnb_ops.sqlite3"
    return "data/airbnb_ops.sqlite3"


class SQLiteStore:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path or _default_database_path())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def save_property_config(self, config: PropertyConfig) -> None:
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO property_config VALUES (1, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET property_name=excluded.property_name,
                nightly_rate=excluded.nightly_rate,
                outstanding_obligation=excluded.outstanding_obligation,
                target_monthly_fixed_costs=excluded.target_monthly_fixed_costs""",
                (config.property_name, str(config.nightly_rate), str(config.outstanding_obligation), str(config.target_monthly_fixed_costs)),
            )

    def save_booking(self, booking: Booking) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO bookings VALUES (?, ?, ?, ?, ?)",
                (booking.booking_id, booking.check_in.isoformat(), booking.check_out.isoformat(), str(booking.nightly_rate), str(booking.platform_fee)),
            )

    def save_expense(self, expense: Expense) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO expenses VALUES (?, ?, ?, ?, ?)",
                (expense.expense_id, expense.category, str(expense.amount), expense.expense_date.isoformat(), expense.note),
            )

    def load_service(self) -> AirbnbOpsService:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM property_config WHERE id = 1").fetchone()
            config = PropertyConfig(
                property_name=row["property_name"] if row else "Lekki Phase 1 — 2BR",
                nightly_rate=Decimal(row["nightly_rate"]) if row else Decimal("150000"),
                outstanding_obligation=Decimal(row["outstanding_obligation"]) if row else Decimal("0"),
                target_monthly_fixed_costs=Decimal(row["target_monthly_fixed_costs"]) if row else Decimal("0"),
            )
            service = AirbnbOpsService(config)
            for row in conn.execute("SELECT * FROM bookings ORDER BY check_in"):
                service.add_booking(Booking(row["booking_id"], date.fromisoformat(row["check_in"]), date.fromisoformat(row["check_out"]), Decimal(row["nightly_rate"]), Decimal(row["platform_fee"])))
            for row in conn.execute("SELECT * FROM expenses ORDER BY expense_date"):
                service.add_expense(Expense(row["expense_id"], row["category"], Decimal(row["amount"]), date.fromisoformat(row["expense_date"]), row["note"]))
            return service
