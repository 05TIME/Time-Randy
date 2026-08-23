"""Deterministic operational tasks derived from the Airbnb ledger."""

from dataclasses import dataclass
from datetime import date, timedelta

from .service import AirbnbOpsService


@dataclass(frozen=True)
class OpsTask:
    task_type: str
    title: str
    due_date: date
    booking_id: str | None = None
    priority: str = "normal"

    def as_dict(self) -> dict:
        return {"task_type": self.task_type, "title": self.title, "due_date": self.due_date.isoformat(), "booking_id": self.booking_id, "priority": self.priority}


def upcoming_tasks(service: AirbnbOpsService, start: date, horizon_days: int = 7) -> list[OpsTask]:
    """Generate planning tasks; execution remains human/provider-controlled."""
    if horizon_days < 0:
        raise ValueError("horizon_days cannot be negative")
    end = start + timedelta(days=horizon_days)
    tasks: list[OpsTask] = []
    for booking in sorted(service.bookings, key=lambda b: (b.check_out, b.booking_id)):
        if start <= booking.check_out <= end:
            tasks.append(OpsTask("turnover", f"Clean and reset property after checkout {booking.booking_id}", booking.check_out, booking.booking_id, "high"))
        if start <= booking.check_in <= end:
            tasks.append(OpsTask("check_in", f"Prepare check-in for booking {booking.booking_id}", booking.check_in, booking.booking_id, "high"))
    if service.config.outstanding_obligation > 0:
        tasks.append(OpsTask("finance", "Review outstanding Airbnb obligation and cash-flow plan", start, None, "critical"))
    return sorted(tasks, key=lambda t: (t.due_date, t.priority, t.task_type, t.booking_id or ""))
