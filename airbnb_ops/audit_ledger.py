"""Durable, append-only audit events for TIMEŒ decisions."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
import json
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

    def as_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "approval_id": self.approval_id,
            "risk_score": str(self.risk_score),
            "confidence": str(self.confidence),
            "allowed": self.allowed,
            "reason": self.reason,
            "created_at": self.created_at,
        }


SCHEMA = """
CREATE TABLE IF NOT EXISTS decision_audit (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    approval_id TEXT NOT NULL,
    risk_score TEXT NOT NULL,
    confidence TEXT NOT NULL,
    allowed INTEGER NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def make_event(event_id: str, event_type: str, approval_id: str, risk_score: Decimal, confidence: Decimal, allowed: bool, reason: str) -> AuditEvent:
    return AuditEvent(event_id, event_type, approval_id, risk_score, confidence, allowed, reason, datetime.now(timezone.utc).isoformat())


def append_event(conn: sqlite3.Connection, event: AuditEvent) -> None:
    conn.execute(
        "INSERT INTO decision_audit VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (event.event_id, event.event_type, event.approval_id, str(event.risk_score), str(event.confidence), int(event.allowed), event.reason, event.created_at),
    )


def list_events(conn: sqlite3.Connection, approval_id: str | None = None) -> list[AuditEvent]:
    query = "SELECT * FROM decision_audit"
    params: tuple = ()
    if approval_id:
        query += " WHERE approval_id = ?"
        params = (approval_id,)
    query += " ORDER BY created_at, event_id"
    rows = conn.execute(query, params).fetchall()
    return [AuditEvent(row[0], row[1], row[2], Decimal(row[3]), Decimal(row[4]), bool(row[5]), row[6], row[7]) for row in rows]
