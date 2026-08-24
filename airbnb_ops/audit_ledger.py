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
        return {"event_id": self.event_id, "event_type": self.event_type, "approval_id": self.approval_id, "risk_score": str(self.risk_score), "confidence": str(self.confidence), "allowed": self.allowed, "reason": self.reason, "created_at": self.created_at, "prediction": self.prediction, "actual": self.actual, "correct": self.correct, "error": str(self.error) if self.error is not None else None}


SCHEMA = """
CREATE TABLE IF NOT EXISTS decision_audit (
    event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, approval_id TEXT NOT NULL,
    risk_score TEXT NOT NULL, confidence TEXT NOT NULL, allowed INTEGER NOT NULL,
    reason TEXT NOT NULL, created_at TEXT NOT NULL, prediction TEXT, actual TEXT,
    correct INTEGER, error TEXT
);
"""


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    columns = {row[1] for row in conn.execute("PRAGMA table_info(decision_audit)")}
    for name, definition in (("prediction", "TEXT"), ("actual", "TEXT"), ("correct", "INTEGER"), ("error", "TEXT")):
        if name not in columns:
            conn.execute(f"ALTER TABLE decision_audit ADD COLUMN {name} {definition}")


def make_event(event_id: str, event_type: str, approval_id: str, risk_score: Decimal, confidence: Decimal, allowed: bool, reason: str, prediction: str | None = None, actual: str | None = None, correct: bool | None = None, error: Decimal | None = None) -> AuditEvent:
    return AuditEvent(event_id, event_type, approval_id, risk_score, confidence, allowed, reason, datetime.now(timezone.utc).isoformat(), prediction, actual, correct, error)


def append_event(conn: sqlite3.Connection, event: AuditEvent) -> None:
    columns = {row[1] for row in conn.execute("PRAGMA table_info(decision_audit)")}
    base_columns = ["event_id", "event_type", "approval_id", "risk_score", "confidence", "allowed", "reason", "created_at"]
    values = [event.event_id, event.event_type, event.approval_id, str(event.risk_score), str(event.confidence), int(event.allowed), event.reason, event.created_at]
    optional = [("prediction", event.prediction), ("actual", event.actual), ("correct", event.correct), ("error", str(event.error) if event.error is not None else None)]
    for name, value in optional:
        if name in columns:
            base_columns.append(name)
            values.append(value)
    placeholders = ",".join("?" for _ in values)
    conn.execute(f"INSERT INTO decision_audit ({','.join(base_columns)}) VALUES ({placeholders})", values)


def list_events(conn: sqlite3.Connection, approval_id: str | None = None) -> list[AuditEvent]:
    columns = [row[1] for row in conn.execute("PRAGMA table_info(decision_audit)")]
    query = "SELECT * FROM decision_audit"
    params: tuple = ()
    if approval_id:
        query += " WHERE approval_id = ?"
        params = (approval_id,)
    query += " ORDER BY created_at, event_id"
    rows = conn.execute(query, params).fetchall()
    index = {name: i for i, name in enumerate(columns)}
    def value(row, name):
        return row[index[name]] if name in index else None
    return [AuditEvent(value(row,"event_id"), value(row,"event_type"), value(row,"approval_id"), Decimal(value(row,"risk_score")), Decimal(value(row,"confidence")), bool(value(row,"allowed")), value(row,"reason"), value(row,"created_at"), value(row,"prediction"), value(row,"actual"), None if value(row,"correct") is None else bool(value(row,"correct")), None if value(row,"error") is None else Decimal(value(row,"error"))) for row in rows]


def append_validation_event(conn: sqlite3.Connection, event_id: str, approval_id: str, risk_score: Decimal, confidence: Decimal, prediction: str, actual: str, correct: bool, error: Decimal, reason: str) -> AuditEvent:
    ensure_schema(conn)
    event = make_event(event_id, "validation", approval_id, risk_score, confidence, True, reason, prediction, actual, correct, error)
    append_event(conn, event)
    conn.commit()
    return event
