"""Decision layer for the Airbnb Ops Agent.

This agent recommends actions; it does not silently execute financial or
channel changes. External actions must pass through an authorized adapter.
"""

from dataclasses import dataclass
from decimal import Decimal

from .escalation import Escalation, assess
from .forecast import OccupancyForecast, forecast


@dataclass(frozen=True)
class OpsRecommendation:
    priority: str
    action: str
    reason: str
    escalation: Escalation


def recommend(
    *,
    available_nights: int,
    booked_nights: int,
    expected_fill_rate: Decimal,
    nightly_rate: Decimal,
    financial_discrepancy: bool = False,
    urgent_maintenance: bool = False,
) -> tuple[OccupancyForecast, OpsRecommendation]:
    projection = forecast(available_nights, booked_nights, expected_fill_rate, nightly_rate)
    escalation = assess(
        financial_discrepancy=financial_discrepancy,
        urgent_maintenance=urgent_maintenance,
    )

    if escalation.level.value in {"urgent", "escalate"}:
        return projection, OpsRecommendation(
            priority=escalation.level.value,
            action="Escalate before changing pricing or committing funds.",
            reason=escalation.reason,
            escalation=escalation,
        )

    if projection.expected_additional_nights > 0:
        return projection, OpsRecommendation(
            priority="growth",
            action="Review pricing/promotion for the unbooked nights.",
            reason=f"Forecast leaves {projection.expected_additional_nights} additional night(s) to fill.",
            escalation=escalation,
        )

    return projection, OpsRecommendation(
        priority="maintain",
        action="Maintain current pricing and monitor occupancy.",
        reason="Forecast target is already met.",
        escalation=escalation,
    )
