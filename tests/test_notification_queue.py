from datetime import date

from airbnb_ops.notification_queue import build_notification_queue
from airbnb_ops.task_engine import OpsTask


def test_build_notification_queue_filters_future_and_routes_operational_tasks():
    today = date(2026, 8, 23)
    tasks = [
        OpsTask("turnover", "Clean property", today, "B1", "high"),
        OpsTask("check_in", "Prepare guest", today, "B2", "high"),
        OpsTask("finance", "Review obligation", today, None, "critical"),
        OpsTask("check_in", "Future guest", date(2026, 8, 24), "B3", "high"),
    ]

    queue = build_notification_queue(tasks, today)

    assert len(queue) == 3
    assert queue[0].priority == "critical"
    assert queue[1].channels == ("owner_dashboard", "manager")
    assert queue[2].notification_id == "check_in:B2:2026-08-23"
