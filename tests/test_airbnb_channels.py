from datetime import date
from decimal import Decimal

from airbnb_ops.channels import ExternalBooking, ManualChannelAdapter
from airbnb_ops.service import AirbnbOpsService, PropertyConfig
from airbnb_ops.sync import sync_channel


def test_manual_channel_filters_by_date():
    booking = ExternalBooking(
        external_id="A1",
        source="manual",
        check_in=date(2026, 9, 1),
        check_out=date(2026, 9, 4),
        nightly_rate=Decimal("150000"),
    )
    adapter = ManualChannelAdapter([booking])
    assert len(adapter.fetch_bookings(date(2026, 9, 2), date(2026, 9, 3))) == 1
    assert adapter.fetch_bookings(date(2026, 9, 4), date(2026, 9, 5)) == []


def test_sync_is_idempotent():
    booking = ExternalBooking(
        external_id="A1",
        source="manual",
        check_in=date(2026, 9, 1),
        check_out=date(2026, 9, 4),
        nightly_rate=Decimal("150000"),
    )
    service = AirbnbOpsService(PropertyConfig())
    adapter = ManualChannelAdapter([booking])
    assert sync_channel(service, adapter, date(2026, 9, 1), date(2026, 9, 5)) == 1
    assert sync_channel(service, adapter, date(2026, 9, 1), date(2026, 9, 5)) == 0
    assert len(service.bookings) == 1
