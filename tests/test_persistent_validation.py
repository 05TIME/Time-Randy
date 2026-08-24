import sqlite3
from decimal import Decimal

from airbnb_ops.audit_ledger import append_validation_event, list_events


def test_validation_outcome_is_persisted():
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
    CREATE TABLE decision_audit (
        event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, approval_id TEXT NOT NULL,
        risk_score TEXT NOT NULL, confidence TEXT NOT NULL, allowed INTEGER NOT NULL,
        reason TEXT NOT NULL, created_at TEXT NOT NULL, prediction TEXT, actual TEXT,
        correct INTEGER, error TEXT
    );
    """)
    event = append_validation_event(conn, "evt-v1", "approval-1", Decimal("0.42"), Decimal("0.81"), "monitor", "monitor", True, Decimal("0"), "matched")
    loaded = list_events(conn, "approval-1")
    assert loaded[0] == event
    assert loaded[0].event_type == "validation"
    assert loaded[0].correct is True
    assert loaded[0].error == Decimal("0")
