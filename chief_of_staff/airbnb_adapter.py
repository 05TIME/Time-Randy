"""Convert Airbnb Ops summaries into Chief of Staff signals."""

from decimal import Decimal

from .orchestrator import BusinessUnitSignal, DecisionType


def signal_from_airbnb_summary(summary: dict, *, target_occupancy: Decimal = Decimal("0.70")) -> BusinessUnitSignal:
    occupancy = Decimal(str(summary["occupancy_rate"]))
    available = int(summary["available_nights"])
    booked = int(summary["booked_nights"])
    unbooked = max(0, available - booked)
    obligation = Decimal(str(summary["outstanding_obligation"]))

    if obligation > 0:
        return BusinessUnitSignal(
            unit="airbnb",
            headline=f"Outstanding Airbnb obligation: ₦{obligation:,.0f}",
            priority=100,
            decision=DecisionType.ESCALATE,
            escalation="Owner reconciliation and cash-flow review required.",
        )

    if occupancy < target_occupancy and unbooked:
        return BusinessUnitSignal(
            unit="airbnb",
            headline=f"Airbnb occupancy is {occupancy * 100:.0f}% with {unbooked} unbooked night(s)",
            priority=70,
            decision=DecisionType.ACTION,
            action=f"Review targeted pricing/promotion for {unbooked} unbooked night(s).",
        )

    return BusinessUnitSignal(
        unit="airbnb",
        headline=f"Airbnb occupancy is {occupancy * 100:.0f}% and operating normally",
        priority=20,
        decision=DecisionType.MONITOR,
        action="Continue monitoring bookings, turnovers, and cash flow.",
    )
