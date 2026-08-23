"""Conservative rule-based pricing recommendations for Airbnb Ops.

This is advisory only. It never changes a channel listing automatically.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PricingRecommendation:
    recommended_rate: Decimal
    reason: str
    confidence: str


def recommend_rate(base_rate: Decimal, occupancy_rate: Decimal, gap_nights: int,
                    days_to_checkin: int | None = None) -> PricingRecommendation:
    """Recommend a rate using transparent occupancy/gap rules."""
    if base_rate <= 0:
        raise ValueError("base_rate must be positive")
    if not 0 <= occupancy_rate <= 1:
        raise ValueError("occupancy_rate must be between 0 and 1")

    rate = base_rate
    reason = "Base rate maintained."
    confidence = "medium"

    if gap_nights <= 0:
        return PricingRecommendation(rate, "No vacant nights detected in the target period.", "high")

    if occupancy_rate < Decimal("0.35"):
        rate = (base_rate * Decimal("0.85")).quantize(Decimal("1"))
        reason = "Low occupancy and meaningful vacancy gap; consider a 15% tactical reduction."
        confidence = "high"
    elif occupancy_rate < Decimal("0.55"):
        rate = (base_rate * Decimal("0.92")).quantize(Decimal("1"))
        reason = "Moderate occupancy with vacant nights; consider an 8% tactical reduction."
        confidence = "medium"
    elif days_to_checkin is not None and days_to_checkin <= 3:
        rate = (base_rate * Decimal("0.95")).quantize(Decimal("1"))
        reason = "Near-term vacancy; consider a 5% last-minute adjustment."
        confidence = "medium"

    return PricingRecommendation(rate, reason, confidence)
