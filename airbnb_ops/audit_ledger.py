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


def make_event(event_id: str, event_type: str, approval_id: str, risk_score: Decimal, confidence: Decimal, allowed: bool, reason: str, prediction: str | None = None, actual: str | None = None, correct: bool | None = None, error: Decimal | None = None) -> AuditEvent:
    return AuditEvent(event_id, event_type, approval_id, risk_score, confidence, allowed, reason, datetime.now(timezone.utc).isoformat(), prediction, actual, correct, error)


def append_event(conn: sqlite3.Connection, event: AuditEvent) -> None:
    conn.execute(
        "INSERT INTO decision_audit (event_id,event_type,approval_id,risk_score,confidence,allowed,reason,created_at,prediction,actual,correct,error) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (event.event_id, event.event_type, event.approval_id, str(event.risk_score), str(event.confidence), int(event.allowed), event.reason, event.created_at, event.prediction, event.actual, event.correct, str(event.error) if event.error is not None else None),
    )


def list_events(conn: sqlite3.Connection, approval_id: str | None = None) -> list[AuditEvent]:
    columns = [row[1] for row in conn.execute("PRAGMA table_info(decision_audit)")]
    optional = {name: None for name in ("prediction", "actual", "correct", "error") if name not in columns}
    query = "SELECT * FROM decision_audit"
    params: tuple = ()
    if approval_id:
        query += " WHERE approval_id = ?"
        params = (approval_id,)
    query += " ORDER BY created_at, event_id"
    rows = conn.execute(query, params).fetchall()
    index = {name: i for i, name in enumerate(columns)}
    return [AuditEvent(row[index["event_id"]], row[index["event_type"]], row[index["approval_id"]], Decimal(row[index["risk_score"]]), Decimal(row[index["confidence"]]), bool(row[index["allowed"]]), row[index["reason"]], row[index["created_at"]], optional.get("prediction", row[index["prediction"]] if "prediction" in index else None), optional.get("actual", row[index["actual"]] if "actual" in index else None), optional.get("correct", row[index["correct"]] if "correct" in index else None), optional.get("error", None if "error" not in index or row[index["error"]] is None else Decimal(row[index["error"]]))) for row in rows]


def append_validation_event(conn: sqlite3.Connection, event_id: str, approval_id: str, risk_score: Decimal, confidence: Decimal, prediction: str, actual: str, correct: bool, error: Decimal, reason: str) -> AuditEvent:
    conn.executescript(SCHEMA)
    event = make_event(event_id, "validation", approval_id, risk_score, confidence, True, reason, prediction, actual, correct, error)
    append_event(conn, event)
    conn.commit()
    return event
