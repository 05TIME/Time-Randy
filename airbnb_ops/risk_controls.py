"""Deterministic safety gates for TIMEŒ recommendations."""

from dataclasses import dataclass
from decimal import Decimal

from .decision_engine import Decision


@dataclass(frozen=True)
class RiskGateResult:
    allowed: bool
    reason: str


def evaluate_risk_gate(
    decision: Decision,
    *,
    max_risk: Decimal = Decimal("0.75"),
    min_confidence: Decimal = Decimal("0.50"),
) -> RiskGateResult:
    if decision.risk_score > max_risk:
        return RiskGateResult(False, "risk score exceeds configured threshold")
    if decision.confidence < min_confidence:
        return RiskGateResult(False, "confidence is below configured threshold")
    return RiskGateResult(True, "decision satisfies configured risk controls")
