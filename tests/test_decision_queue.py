from datetime import date

from airbnb_ops.approval_queue import ApprovalItem
from airbnb_ops.decision_queue import rank_approvals, score_approval
from airbnb_ops.task_engine import OpsTask


def make_item(task_type, due_date, priority, booking_id):
    return ApprovalItem(OpsTask(task_type, task_type, due_date, booking_id, priority))


def test_score_approval_preserves_approval_identity():
    item = make_item("turnover", date(2026, 8, 24), "high", "BK-1")
    scored = score_approval(item, date(2026, 8, 23))
    assert scored.approval_id == item.approval_id
    assert scored.decision.action == "review_now"


def test_rank_approvals_puts_high_risk_first():
    items = [
        make_item("maintenance", date(2026, 9, 30), "low", "BK-LOW"),
        make_item("turnover", date(2026, 8, 24), "high", "BK-HIGH"),
    ]
    ranked = rank_approvals(items, date(2026, 8, 23))
    assert ranked[0].approval_id == items[1].approval_id
    assert ranked[1].approval_id == items[0].approval_id
