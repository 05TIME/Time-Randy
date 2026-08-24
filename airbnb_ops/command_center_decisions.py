"""Command Center view model for ranked TIMEŒ approval decisions."""

from datetime import date
import sqlite3
from uuid import uuid4

from .approval_queue import ApprovalItem
from .decision_queue import rank_approvals
from .audit_ledger import append_event, make_event, SCHEMA as AUDIT_SCHEMA
from .risk_controls import evaluate_risk_gate


def build_decision_panel(items: list[ApprovalItem], as_of: date, audit_conn: sqlite3.Connection | None = None) -> list[dict]:
    """Return ranked recommendations and optionally persist risk-gate evaluations."""
    if audit_conn is not None:
        audit_conn.executescript(AUDIT_SCHEMA)

    panel = []
    for item in rank_approvals(items, as_of):
        gate = evaluate_risk_gate(item.decision)
        payload = item.as_dict()
        payload["risk_allowed"] = gate.allowed
        payload["risk_gate_reason"] = gate.reason
        if audit_conn is not None:
            event = make_event(
                str(uuid4()),
                "risk_gate",
                item.approval_id,
                item.decision.risk_score,
                item.decision.confidence,
                gate.allowed,
                gate.reason,
            )
            append_event(audit_conn, event)
        panel.append(payload)
    if audit_conn is not None:
        audit_conn.commit()
    return panel
