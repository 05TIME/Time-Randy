"""Airbnb iCal calendar adapter.

Airbnb hosts can export a listing calendar as an .ics URL. This adapter reads
that calendar and normalizes reservation events into TIMEŒ's provider-neutral
ExternalBooking contract. It intentionally does not scrape Airbnb or use
private APIs.
"""

from datetime import date
from decimal import Decimal
from urllib.request import Request, urlopen

from .channels import ExternalBooking


class AirbnbICalAdapter:
    """Fetch an Airbnb-exported iCal calendar and return normalized bookings."""

    name = "airbnb_ical"

    def __init__(self, calendar_url: str, timeout: int = 15) -> None:
        if not calendar_url or not calendar_url.lower().startswith(("https://", "http://")):
            raise ValueError("calendar_url must be an http(s) URL")
        self.calendar_url = calendar_url
        self.timeout = timeout

    def fetch_bookings(self, start: date, end: date) -> list[ExternalBooking]:
        request = Request(self.calendar_url, headers={"User-Agent": "TIMEOE-Airbnb-Ops/1.0"})
        with urlopen(request, timeout=self.timeout) as response:
            payload = response.read().decode("utf-8-sig", errors="replace")
        return parse_ical_bookings(payload, start, end)


def parse_ical_bookings(payload: str, start: date, end: date) -> list[ExternalBooking]:
    """Parse simple VEVENT blocks emitted by Airbnb's exported calendar."""
    events: list[ExternalBooking] = []
    for block in payload.replace("\r\n", "\n").replace("\r", "\n").split("BEGIN:VEVENT")[1:]:
        block = block.split("END:VEVENT", 1)[0]
        fields: dict[str, str] = {}
        for raw_line in block.split("\n"):
            if ":" not in raw_line:
                continue
            key, value = raw_line.split(":", 1)
            fields[key.split(";", 1)[0].upper()] = value.strip()

        uid = fields.get("UID")
        start_value = fields.get("DTSTART")
        end_value = fields.get("DTEND")
        if not uid or not start_value or not end_value:
            continue

        check_in = _ical_date(start_value)
        check_out = _ical_date(end_value)
        if check_in >= check_out or check_in >= end or check_out <= start:
            continue

        events.append(
            ExternalBooking(
                external_id=uid,
                source="airbnb",
                check_in=check_in,
                check_out=check_out,
                nightly_rate=Decimal("0"),
            )
        )
    return events


def _ical_date(value: str) -> date:
    value = value[:8]
    return date(int(value[0:4]), int(value[4:6]), int(value[6:8]))
