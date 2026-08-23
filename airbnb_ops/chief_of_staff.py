"""Chief-of-Staff decision layer for the Airbnb business unit."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ChiefOfStaffBrief:
    priority: str
    headline: str
    actions: tuple[str, ...]
    escalations: tuple[str, ...]


def build_brief(summary: dict, *, target_occupancy: Decimal = Decimal("0.70")) -> ChiefOfStaffBrief:
    actions: list[str] = []
    escalations: list[str] = []
    occupancy = Decimal(str(summary["occupancy_rate"]))
    gap = int(summary["available_nights"]) - int(summary["booked_nights"])
    obligation = Decimal(str(summary["outstanding_obligation"]))

    if occupancy < target_occupancy and gap > 0:
        actions.append(f"Review targeted pricing/promotion for {gap} unbooked night(s).")
    if obligation > 0:
        escalations.append(
            f"Outstanding obligation is ₦{obligation:,.0f}; protect cash flow and reconcile payments."
        )

    if escalations:
        priority = "escalate"
    elif actions:
        priority = "growth"
    else:
        priority = "maintain"

    headline = (
        f"Occupancy is {occupancy * 100:.0f}% with {gap} unbooked night(s)."
        if gap >= 0 else f"Occupancy data requires review: {gap} night overlap."
    )
    if not actions:
        actions.append("Continue monitoring bookings and operational readiness.")

    return ChiefOfStaffBrief(priority, headline, tuple(actions), tuple(escalations))
