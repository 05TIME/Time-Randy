"""Notification adapter contracts for cleaner/manager operations."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class NotificationChannel(StrEnum):
    CONSOLE = "console"
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"


@dataclass(frozen=True)
class Notification:
    recipient: str
    message: str
    channel: NotificationChannel = NotificationChannel.CONSOLE
    priority: str = "normal"


class NotificationAdapter(Protocol):
    def send(self, notification: Notification) -> None:
        """Deliver a notification through the configured provider."""
        ...


class InMemoryNotificationAdapter:
    """Safe test/development adapter; sends nothing externally."""

    def __init__(self) -> None:
        self.sent: list[Notification] = []

    def send(self, notification: Notification) -> None:
        self.sent.append(notification)


def turnover_notification(recipient: str, booking_id: str, next_check_in: str, urgent: bool = False) -> Notification:
    priority = "urgent" if urgent else "normal"
    message = (
        f"TIMEŒ TURNOVER: Booking {booking_id} has checked out. "
        f"Cleaning/inspection required before next check-in at {next_check_in}."
    )
    return Notification(recipient, message, NotificationChannel.CONSOLE, priority)
