"""Durable, append-only audit events for TIMEŒ decisions and outcomes."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
import sqlite3


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    event_type: str
    approval_id: str
    risk_score: Decimal
    confidence: Decimal
    allowed: bool
    reason: str
    created_at: str
    prediction: str | None = None
    actual: str | None = None
    correct: bool | None = None
    error: Decimal | None = None

    def as_dict(self) -> dict:
        return {
            "event_id": self.event_id, "event_type": self.event_type,
            "approval_id": self.approval_id, "risk_score": str(self.risk_score),
            "confidence": str(self.confidence), "allowed": self.allowed,
            "reason": self.reason, "created_at": self.created_at,
            "prediction": self.prediction, "actual": self.actual,
            "correct": self.correct, "error": str(self.error) if self.error is not None else None,
        }


SCHEMA = """
CREATE TABLE IF NOT EXISTS decision_audit (
    event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, approval_id TEXT NOT NULL,
    risk_score TEXT NOT NULL, confidence TEXT NOT NULL, allowed INTEGER NOT NULL,
    reason TEXT NOT NULL, created_at TEXT NOT NULL, prediction TEXT, actual TEXT,
    correct INTEGER, error TEXT
);
"""


def make_event(event_id: str, event_type: str, approval_id: str, risk_score: Decimal, confidence: Decimal, allowed: bool, reason: str, prediction: str | None = None, actual: str | None = None, correct: bool | None = None, error: Decimal | None = None) -> AuditEvent:
    return AuditEvent(event_id, event_type, approval_id, risk_score, confidence, allowed, reason, datetime.now(timezone.utc).isoformat(), prediction, actual, correct, error)


def append_event(conn: sqlite3.Connection, event: AuditEvent) -> None:
    conn.execute(
        "INSERT INTO decision_audit VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (event.event_id, event.event_type, event.approval_id, str(event.risk_score), str(event.confidence), int(event.allowed), event.reason, event.created_at, event.prediction, event.actual, event.correct, str(event.error) if event.error is not None else None),
    )


def list_events(conn: sqlite3.Connection, approval_id: str | None = None) -> list[AuditEvent]:
    query = "SELECT * FROM decision_audit"
    params: tuple = ()
    if approval_id:
        query += " WHERE approval_id = ?"
        params = (approval_id,)
    query += " ORDER BY created_at, event_id"
    rows = conn.execute(query, params).fetchall()
    return [AuditEvent(row[0], row[1], row[2], Decimal(row[3]), Decimal(row[4]), bool(row[5]), row[6], row[7], row[8], row[9], None if row[10] is None else bool(row[10]), None if row[11] is None else Decimal(row[11])) for row in rows]


def append_validation_event(conn: sqlite3.Connection, event_id: str, approval_id: str, risk_score: Decimal, confidence: Decimal, prediction: str, actual: str, correct: bool, error: Decimal, reason: str) -> AuditEvent:
    event = make_event(event_id, "validation", approval_id, risk_score, confidence, True, reason, prediction, actual, correct, error)
    append_event(conn, event)
    conn.commit()
    return event
