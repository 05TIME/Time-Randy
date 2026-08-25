from datetime import date
from decimal import Decimal

from airbnb_ops.airbnb_ical import parse_ical_bookings


ICS = """BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nUID:reservation-123\nDTSTART;VALUE=DATE:20260828\nDTEND;VALUE=DATE:20260901\nSUMMARY:Reserved\nEND:VEVENT\nBEGIN:VEVENT\nUID:blocked-456\nDTSTART;VALUE=DATE:20260910\nDTEND;VALUE=DATE:20260912\nEND:VEVENT\nEND:VCALENDAR\n"""


def test_parse_ical_bookings_filters_by_period():
    bookings = parse_ical_bookings(ICS, date(2026, 8, 1), date(2026, 9, 1))
    assert len(bookings) == 1
    booking = bookings[0]
    assert booking.external_id == "reservation-123"
    assert booking.source == "airbnb"
    assert booking.check_in == date(2026, 8, 28)
    assert booking.check_out == date(2026, 9, 1)
    assert booking.nightly_rate == Decimal("0")
