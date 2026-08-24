import sqlite3
from decimal import Decimal

from airbnb_ops.audit_ledger import AuditEvent, append_event, list_events, make_event


def test_audit_events_are_appendable_and_queryable():
    conn = sqlite3.connect(":memory:")
    conn.execute("""CREATE TABLE decision_audit (
        event_id TEXT PRIMARY KEY,
        event_type TEXT NOT NULL,
        approval_id TEXT NOT NULL,
        risk_score TEXT NOT NULL,
        confidence TEXT NOT NULL,
        allowed INTEGER NOT NULL,
        reason TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")
    event = make_event("evt-1", "risk_gate", "approval-1", Decimal("0.72"), Decimal("0.81"), True, "safe")
    append_event(conn, event)
    conn.commit()
    events = list_events(conn, "approval-1")
    assert events == [event]


def test_audit_event_round_trip_preserves_decimal_precision():
    conn = sqlite3.connect(":memory:")
    conn.execute("""CREATE TABLE decision_audit (
        event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, approval_id TEXT NOT NULL,
        risk_score TEXT NOT NULL, confidence TEXT NOT NULL, allowed INTEGER NOT NULL,
        reason TEXT NOT NULL, created_at TEXT NOT NULL
    )""")
    event = AuditEvent("evt-2", "risk_gate", "approval-2", Decimal("0.123456"), Decimal("0.987654"), False, "blocked", "2026-08-24T00:00:00+00:00")
    append_event(conn, event)
    conn.commit()
    loaded = list_events(conn)[0]
    assert loaded.risk_score == Decimal("0.123456")
    assert loaded.confidence == Decimal("0.987654")
    assert loaded.allowed is False
