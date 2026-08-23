from datetime import date

from airbnb_ops.approval_queue import ApprovalItem
from airbnb_ops.command_center_decisions import build_decision_panel
from airbnb_ops.task_engine import OpsTask


def test_decision_panel_is_ranked_and_ui_safe():
    items = [
        ApprovalItem(OpsTask("maintenance", "Inspect", date(2026, 9, 30), "M-1", "low")),
        ApprovalItem(OpsTask("turnover", "Reset", date(2026, 8, 24), "T-1", "high")),
    ]
    panel = build_decision_panel(items, date(2026, 8, 23))
    assert panel[0]["approval_id"] == items[1].approval_id
    assert panel[0]["action"] == "review_now"
    assert "risk_score" in panel[0]
    assert "confidence" in panel[0]
    assert "rationale" in panel[0]
