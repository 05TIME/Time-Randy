"""Small SQLite persistence layer for TIMEŒ Airbnb Ops.

SQLite keeps the first deployment simple and durable. The service can later
swap this repository for PostgreSQL without changing the business API.
"""

from datetime import date
from decimal import Decimal
import sqlite3
from pathlib import Path
from typing import Iterable

from .service import Booking, Expense


class SQLiteStore:
    def __init__(self, path: str = "data/airbnb_ops.sqlite3") -> None:
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS bookings (
                    booking_id TEXT PRIMARY KEY,
                    check_in TEXT NOT NULL,
                    check_out TEXT NOT NULL,
                    nightly_rate TEXT NOT NULL,
                    platform_fee TEXT NOT NULL DEFAULT '0'
                );
                CREATE TABLE IF NOT EXISTS expenses (
                    expense_id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    amount TEXT NOT NULL,
                    expense_date TEXT NOT NULL,
                    note TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    title TEXT NOT NULL,
                    due_at TEXT,
                    status TEXT NOT NULL DEFAULT 'open',
                    assignee TEXT,
                    note TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS inventory (
                    item TEXT PRIMARY KEY,
                    quantity INTEGER NOT NULL,
                    reorder_level INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS maintenance (
                    issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    severity TEXT NOT NULL DEFAULT 'normal',
                    status TEXT NOT NULL DEFAULT 'open',
                    reported_at TEXT NOT NULL,
                    note TEXT NOT NULL DEFAULT ''
                );
                """
            )

    def add_booking(self, booking: Booking) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO bookings VALUES (?, ?, ?, ?, ?)",
                (booking.booking_id, booking.check_in.isoformat(), booking.check_out.isoformat(),
                 str(booking.nightly_rate), str(booking.platform_fee)),
            )

    def add_expense(self, expense: Expense) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO expenses VALUES (?, ?, ?, ?, ?)",
                (expense.expense_id, expense.category, str(expense.amount),
                 expense.expense_date.isoformat(), expense.note),
            )

    def bookings(self) -> list[Booking]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM bookings ORDER BY check_in").fetchall()
        return [
            Booking(r["booking_id"], date.fromisoformat(r["check_in"]), date.fromisoformat(r["check_out"]),
                    Decimal(r["nightly_rate"]), Decimal(r["platform_fee"]))
            for r in rows
        ]

    def expenses(self) -> list[Expense]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM expenses ORDER BY expense_date").fetchall()
        return [
            Expense(r["expense_id"], r["category"], Decimal(r["amount"]),
                    date.fromisoformat(r["expense_date"]), r["note"])
            for r in rows
        ]

    def add_task(self, kind: str, title: str, due_at: str | None = None,
                 assignee: str | None = None, note: str = "") -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO tasks(kind,title,due_at,assignee,note) VALUES(?,?,?,?,?)",
                (kind, title, due_at, assignee, note),
            )
            return int(cur.lastrowid)

    def open_tasks(self) -> list[dict]:
        with self._connect() as conn:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM tasks WHERE status='open' ORDER BY due_at IS NULL, due_at"
            ).fetchall()]

    def set_inventory(self, item: str, quantity: int, reorder_level: int) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO inventory(item,quantity,reorder_level,updated_at) VALUES(?,?,?,?)",
                (item, quantity, reorder_level, date.today().isoformat()),
            )

    def low_inventory(self) -> list[dict]:
        with self._connect() as conn:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM inventory WHERE quantity <= reorder_level ORDER BY item"
            ).fetchall()]

    def add_maintenance(self, title: str, severity: str = "normal", note: str = "") -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO maintenance(title,severity,reported_at,note) VALUES(?,?,?,?)",
                (title, severity, date.today().isoformat(), note),
            )
            return int(cur.lastrowid)

    def open_maintenance(self) -> list[dict]:
        with self._connect() as conn:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM maintenance WHERE status='open' ORDER BY CASE severity WHEN 'critical' THEN 0 WHEN 'high' THEN 1 ELSE 2 END, reported_at"
            ).fetchall()]
