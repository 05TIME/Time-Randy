"""Deterministic explanation layer for TIMEŒ decisions.

This module explains an existing decision; it does not create or execute one.
"""

from dataclasses import dataclass
from decimal import Decimal

from .decision_engine import Decision


@dataclass(frozen=True)
class ReasoningReport:
    recommendation: str
    risk_score: Decimal
    confidence: Decimal
    factors: tuple[str, ...]
    uncertainty: tuple[str, ...]
    rationale: str

    def as_dict(self) -> dict:
        return {
            "recommendation": self.recommendation,
            "risk_score": str(self.risk_score),
            "confidence": str(self.confidence),
            "factors": list(self.factors),
            "uncertainty": list(self.uncertainty),
            "rationale": self.rationale,
        }


def explain_decision(decision: Decision) -> ReasoningReport:
    """Produce a transparent explanation from the already-computed decision."""
    factors = [f"priority={decision.priority}", f"risk_score={decision.risk_score}", f"confidence={decision.confidence}"]
    uncertainty: list[str] = []
    if decision.confidence < Decimal("0.70"):
        uncertainty.append("confidence is below the explanation confidence target")
    if decision.risk_score > Decimal("0.50"):
        uncertainty.append("risk is material and should remain subject to the risk gate")
    if not uncertainty:
        uncertainty.append("no additional uncertainty flags from deterministic decision fields")
    rationale = decision.rationale
    if uncertainty:
        rationale = f"{rationale}; uncertainty: {', '.join(uncertainty)}"
    return ReasoningReport(decision.action, decision.risk_score, decision.confidence, tuple(factors), tuple(uncertainty), rationale)
