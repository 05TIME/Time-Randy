"""Deterministic, auditable decision scoring for TIMEŒ."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from .temporal_engine import TemporalFeatures


@dataclass(frozen=True)
class Decision:
    action: str
    priority: str
    risk_score: Decimal
    confidence: Decimal
    rationale: str

    def as_dict(self) -> dict:
        return {
            "action": self.action,
            "priority": self.priority,
            "risk_score": str(self.risk_score),
            "confidence": str(self.confidence),
            "rationale": self.rationale,
        }


def evaluate(task_type: str, temporal: TemporalFeatures, priority: str) -> Decision:
    base_risk = {
        "low": Decimal("0.20"),
        "medium": Decimal("0.45"),
        "high": Decimal("0.70"),
        "critical": Decimal("0.90"),
    }.get(priority, Decimal("0.50"))
    risk = min(Decimal("1.00"), base_risk + temporal.urgency * Decimal("0.30"))
    confidence = max(Decimal("0.00"), Decimal("1.00") - risk / Decimal("2"))
    risk = risk.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    confidence = confidence.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    action = "review_now" if temporal.days_to_due <= 2 or priority in {"high", "critical"} else "monitor"
    return Decision(
        action=action,
        priority=priority,
        risk_score=risk,
        confidence=confidence,
        rationale=f"{task_type} is {temporal.horizon}-horizon with {temporal.days_to_due} days to due date.",
    )
