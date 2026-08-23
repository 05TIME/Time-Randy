"""SQLite persistence for human approval decisions."""

import sqlite3
from datetime import date

from .approval_queue import ApprovalItem, ApprovalStatus
from .task_engine import OpsTask


class ApprovalStore:
    """Persist approval state so decisions survive process restarts."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS approval_items (
                approval_id TEXT PRIMARY KEY,
                task_type TEXT NOT NULL,
                title TEXT NOT NULL,
                due_date TEXT NOT NULL,
                booking_id TEXT,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                decided_at TEXT
            )"""
        )
        self.connection.commit()

    def save(self, item: ApprovalItem) -> None:
        task = item.task
        self.connection.execute(
            """INSERT INTO approval_items
            (approval_id, task_type, title, due_date, booking_id, priority, status, decided_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(approval_id) DO UPDATE SET
                status=excluded.status,
                decided_at=excluded.decided_at""",
            (
                item.approval_id,
                task.task_type,
                task.title,
                task.due_date.isoformat(),
                task.booking_id,
                task.priority,
                item.status.value,
                item.decided_at,
            ),
        )
        self.connection.commit()

    def get(self, approval_id: str) -> ApprovalItem | None:
        row = self.connection.execute(
            "SELECT task_type, title, due_date, booking_id, priority, status, decided_at "
            "FROM approval_items WHERE approval_id = ?",
            (approval_id,),
        ).fetchone()
        if row is None:
            return None
        task = OpsTask(
            row[0], row[1], date.fromisoformat(row[2]), row[3], row[4]
        )
        return ApprovalItem(task, ApprovalStatus(row[5]), row[6])

    def list_all(self) -> list[ApprovalItem]:
        rows = self.connection.execute(
            "SELECT approval_id FROM approval_items ORDER BY due_date, approval_id"
        ).fetchall()
        return [item for (approval_id,) in rows if (item := self.get(approval_id))]
