"""Simple occupancy and revenue forecasting helpers."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class OccupancyForecast:
    available_nights: int
    booked_nights: int
    expected_additional_nights: int
    expected_occupancy: Decimal
    expected_revenue: Decimal


def forecast(
    available_nights: int,
    booked_nights: int,
    expected_fill_rate: Decimal,
    nightly_rate: Decimal,
) -> OccupancyForecast:
    if available_nights < 0 or booked_nights < 0:
        raise ValueError("night counts cannot be negative")
    if booked_nights > available_nights:
        raise ValueError("booked_nights cannot exceed available_nights")
    if not Decimal("0") <= expected_fill_rate <= Decimal("1"):
        raise ValueError("expected_fill_rate must be between 0 and 1")
    if nightly_rate < 0:
        raise ValueError("nightly_rate cannot be negative")

    expected_total = max(booked_nights, int((Decimal(available_nights) * expected_fill_rate).to_integral_value(rounding="ROUND_CEILING")))
    expected_total = min(expected_total, available_nights)
    additional = expected_total - booked_nights
    occupancy = Decimal(expected_total) / Decimal(available_nights) if available_nights else Decimal("0")
    revenue = Decimal(expected_total) * nightly_rate
    return OccupancyForecast(available_nights, booked_nights, additional, occupancy, revenue)
