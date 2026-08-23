from datetime import date, timedelta

from airbnb_ops.notification_queue import build_notification_queue
from airbnb_ops.task_engine import OpsTask


def test_queue_includes_due_and_overdue_tasks_and_skips_future():
    today = date(2026, 8, 23)
    tasks = [
        OpsTask("check_in", "Prepare check-in", today, "B1", "high"),
        OpsTask("turnover", "Clean property", today - timedelta(days=1), "B2", "high"),
        OpsTask("finance", "Review obligation", today, None, "critical"),
        OpsTask("check_in", "Future check-in", today + timedelta(days=1), "B3", "high"),
    ]

    queue = build_notification_queue(tasks, today)

    assert [n.task_type for n in queue] == ["finance", "check_in", "turnover"]
    assert queue[1].channels == ("owner_dashboard", "manager")
    assert queue[0].notification_id == "finance:general:2026-08-23"
