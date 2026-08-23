"""Notification-ready operational workflow primitives.

No external provider is called here. The service produces actionable messages
that can later be delivered through Gmail, SMS, WhatsApp, or another adapter.
"""

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


class TurnoverStatus(StrEnum):
    SCHEDULED = "scheduled"
    CLEANING_REQUIRED = "cleaning_required"
    CLEANING_CONFIRMED = "cleaning_confirmed"
    INSPECTION_REQUIRED = "inspection_required"
    READY = "ready"
    ESCALATED = "escalated"


@dataclass(frozen=True)
class TurnoverTask:
    booking_id: str
    check_out: date
    next_check_in: date | None
    cleaner_name: str | None = None
    manager_name: str | None = None
    status: TurnoverStatus = TurnoverStatus.SCHEDULED

    @property
    def turnaround_hours(self) -> int | None:
        if self.next_check_in is None:
            return None
        return int((datetime.combine(self.next_check_in, datetime.min.time()) - datetime.combine(self.check_out, datetime.min.time())).total_seconds() / 3600)

    def message(self) -> str:
        next_guest = self.next_check_in.isoformat() if self.next_check_in else "no immediate next check-in"
        return (
            f"TURNOVER: booking {self.booking_id} checked out {self.check_out.isoformat()}. "
            f"Next check-in: {next_guest}. Status: {self.status.value}."
        )


def create_turnover_task(booking_id: str, check_out: date, next_check_in: date | None) -> TurnoverTask:
    if next_check_in is not None and next_check_in < check_out:
        raise ValueError("next_check_in cannot be before check_out")
    return TurnoverTask(
        booking_id=booking_id,
        check_out=check_out,
        next_check_in=next_check_in,
        status=TurnoverStatus.CLEANING_REQUIRED,
    )
