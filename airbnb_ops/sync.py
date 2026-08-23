"""Booking reconciliation between channel adapters and the local ledger."""

from datetime import date

from .channels import BookingChannelAdapter
from .service import AirbnbOpsService, Booking


def sync_channel(
    service: AirbnbOpsService,
    adapter: BookingChannelAdapter,
    start: date,
    end: date,
) -> int:
    """Import normalized external bookings that are not already in the ledger.

    Returns the number of newly imported bookings. Existing booking IDs are
    left untouched so a sync cannot silently overwrite financial records.
    """
    existing = {booking.booking_id for booking in service.bookings}
    imported = 0
    for external in adapter.fetch_bookings(start, end):
        booking_id = f"{external.source}:{external.external_id}"
        if booking_id in existing:
            continue
        service.add_booking(
            Booking(
                booking_id=booking_id,
                check_in=external.check_in,
                check_out=external.check_out,
                nightly_rate=external.nightly_rate,
                platform_fee=external.platform_fee,
            )
        )
        existing.add(booking_id)
        imported += 1
    return imported
