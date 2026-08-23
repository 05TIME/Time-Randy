"""Provider-neutral booking channel adapter contracts.

Adapters normalize external booking providers into TIMEŒ records. No real
provider credentials or network calls belong in this module.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class ExternalBooking:
    external_id: str
    source: str
    check_in: date
    check_out: date
    nightly_rate: Decimal
    platform_fee: Decimal = Decimal("0")
    guest_name: str | None = None


class BookingChannelAdapter(Protocol):
    name: str

    def fetch_bookings(self, start: date, end: date) -> list[ExternalBooking]:
        """Return normalized bookings overlapping [start, end)."""
        ...


class ManualChannelAdapter:
    """Safe local adapter for development and reconciliation tests."""

    name = "manual"

    def __init__(self, bookings: list[ExternalBooking] | None = None) -> None:
        self._bookings = bookings or []

    def fetch_bookings(self, start: date, end: date) -> list[ExternalBooking]:
        return [
            booking
            for booking in self._bookings
            if booking.check_in < end and booking.check_out > start
        ]
