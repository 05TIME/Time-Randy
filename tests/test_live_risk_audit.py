import sqlite3
from datetime import date

from airbnb_ops.approval_queue import ApprovalItem
from airbnb_ops.audit_ledger import list_events
from airbnb_ops.command_center_decisions import build_decision_panel
from airbnb_ops.task_engine import OpsTask


def test_command_center_persists_risk_gate_evaluation():
    conn = sqlite3.connect(":memory:")
    item = ApprovalItem(OpsTask("maintenance", "Inspect", date(2026, 9, 30), "BK-1", "low"))
    panel = build_decision_panel([item], date(2026, 8, 23), conn)
    events = list_events(conn, item.approval_id)
    assert len(events) == 1
    assert events[0].event_type == "risk_gate"
    assert panel[0]["risk_allowed"] is True
    assert panel[0]["risk_gate_reason"]
