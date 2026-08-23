"""Core business logic for the TIMEŒ Airbnb Ops Agent.

The first implementation is deliberately provider-agnostic: it manages a
property ledger and operational state without pretending to have direct
Airbnb access. Channel integrations can be added behind adapters later.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True)
class Booking:
    booking_id: str
    check_in: date
    check_out: date
    nightly_rate: Decimal
    platform_fee: Decimal = Decimal("0")

    @property
    def nights(self) -> int:
        return (self.check_out - self.check_in).days

    @property
    def gross_revenue(self) -> Decimal:
        return self.nightly_rate * self.nights

    @property
    def net_revenue(self) -> Decimal:
        return self.gross_revenue - self.platform_fee


@dataclass(frozen=True)
class Expense:
    expense_id: str
    category: str
    amount: Decimal
    expense_date: date
    note: str = ""


@dataclass(frozen=True)
class PropertyConfig:
    property_name: str = "Lekki Phase 1 — 2BR"
    nightly_rate: Decimal = Decimal("150000")
    outstanding_obligation: Decimal = Decimal("0")
    target_monthly_fixed_costs: Decimal = Decimal("0")


class AirbnbOpsService:
    """Calculations and operational rules for one Airbnb property."""

    def __init__(self, config: PropertyConfig | None = None) -> None:
        self.config = config or PropertyConfig()
        self.bookings: list[Booking] = []
        self.expenses: list[Expense] = []

    def add_booking(self, booking: Booking) -> None:
        if booking.nights <= 0:
            raise ValueError("check_out must be after check_in")
        if booking.nightly_rate < 0 or booking.platform_fee < 0:
            raise ValueError("booking amounts cannot be negative")
        self.bookings.append(booking)

    def add_expense(self, expense: Expense) -> None:
        if expense.amount < 0:
            raise ValueError("expense amount cannot be negative")
        self.expenses.append(expense)

    def summary(self, period_start: date, period_end: date) -> dict:
        if period_end <= period_start:
            raise ValueError("period_end must be after period_start")

        period_nights = (period_end - period_start).days
        booked_nights = 0
        gross = Decimal("0")
        platform_fees = Decimal("0")

        for booking in self.bookings:
            overlap_start = max(period_start, booking.check_in)
            overlap_end = min(period_end, booking.check_out)
            nights = max(0, (overlap_end - overlap_start).days)
            if nights:
                booked_nights += nights
                gross += booking.nightly_rate * nights
                # Allocate platform fees proportionally for partial periods.
                platform_fees += booking.platform_fee * Decimal(nights) / Decimal(booking.nights)

        expenses = sum(
            (e.amount for e in self.expenses if period_start <= e.expense_date < period_end),
            Decimal("0"),
        )
        net = gross - platform_fees - expenses
        occupancy = Decimal(booked_nights) / Decimal(period_nights) if period_nights else Decimal("0")
        adr = gross / Decimal(booked_nights) if booked_nights else Decimal("0")

        return {
            "property": self.config.property_name,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "available_nights": period_nights,
            "booked_nights": booked_nights,
            "occupancy_rate": occupancy,
            "gross_revenue": gross,
            "platform_fees": platform_fees,
            "operating_expenses": expenses,
            "net_operating_result": net,
            "adr": adr,
            "outstanding_obligation": self.config.outstanding_obligation,
            "debt_clearing_nights": self.nights_to_clear(self.config.outstanding_obligation),
        }

    def nights_to_clear(self, amount: Decimal) -> int:
        """Conservative night count using the configured nightly rate."""
        if amount <= 0:
            return 0
        rate = self.config.nightly_rate
        if rate <= 0:
            return 0
        return int((amount / rate).to_integral_value(rounding="ROUND_CEILING"))

    def revenue_forecast(self, nights: int, nightly_rate: Decimal | None = None) -> Decimal:
        if nights < 0:
            raise ValueError("nights cannot be negative")
        rate = nightly_rate if nightly_rate is not None else self.config.nightly_rate
        if rate < 0:
            raise ValueError("nightly_rate cannot be negative")
        return rate * nights

    def occupancy_gap(self, period_start: date, period_end: date) -> int:
        """Return unbooked nights in the requested period."""
        result = self.summary(period_start, period_end)
        return result["available_nights"] - result["booked_nights"]

    def operational_alerts(self, period_start: date, period_end: date) -> list[str]:
        alerts: list[str] = []
        gap = self.occupancy_gap(period_start, period_end)
        if gap > 0:
            alerts.append(f"{gap} unbooked night(s) in the period")
        if self.config.outstanding_obligation > 0:
            alerts.append(
                f"Outstanding obligation: ₦{self.config.outstanding_obligation:,.0f} "
                f"(~{self.nights_to_clear(self.config.outstanding_obligation)} full-rate nights)"
            )
        return alerts


def money(value: Decimal) -> str:
    """Render a naira amount for UI output."""
    return f"₦{value:,.0f}"
