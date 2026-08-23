"""Turn operational tasks into a safe, provider-neutral notification queue.

This module deliberately does not send messages. It creates deterministic
notification records that can later be consumed by Gmail/SMS/WhatsApp adapters.
"""

from dataclasses import dataclass
from datetime import date

from .task_engine import OpsTask


@dataclass(frozen=True)
class Notification:
    notification_id: str
    task_type: str
    title: str
    due_date: date
    priority: str
    channels: tuple[str, ...] = ("owner_dashboard",)

    def as_dict(self) -> dict:
        return {
            "notification_id": self.notification_id,
            "task_type": self.task_type,
            "title": self.title,
            "due_date": self.due_date.isoformat(),
            "priority": self.priority,
            "channels": list(self.channels),
        }


def build_notification_queue(tasks: list[OpsTask], today: date) -> list[Notification]:
    """Create notifications for tasks due today or overdue, without sending them."""
    queue: list[Notification] = []
    for task in tasks:
        if task.due_date > today:
            continue
        booking_key = task.booking_id or "general"
        notification_id = f"{task.task_type}:{booking_key}:{task.due_date.isoformat()}"
        channels = ("owner_dashboard", "manager") if task.task_type in {"turnover", "check_in"} else ("owner_dashboard",)
        queue.append(Notification(notification_id, task.task_type, task.title, task.due_date, task.priority, channels))
    return sorted(queue, key=lambda n: (n.priority != "critical", n.due_date, n.notification_id))
