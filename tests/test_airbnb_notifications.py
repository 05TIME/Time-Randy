from airbnb_ops.notifications_adapter import (
    InMemoryNotificationAdapter,
    NotificationChannel,
    turnover_notification,
)


def test_turnover_notification():
    notification = turnover_notification("Cleaner", "B1", "2026-08-23T15:00", urgent=True)
    adapter = InMemoryNotificationAdapter()
    adapter.send(notification)
    assert len(adapter.sent) == 1
    assert adapter.sent[0].channel == NotificationChannel.CONSOLE
    assert adapter.sent[0].priority == "urgent"
    assert "B1" in adapter.sent[0].message
