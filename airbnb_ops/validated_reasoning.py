"""Add historical validation context to transparent decision explanations."""

from dataclasses import dataclass
from decimal import Decimal

from .ai_reasoning import ReasoningReport, explain_decision
from .decision_engine import Decision
from .validation import ValidationOutcome, summarize_outcomes


@dataclass(frozen=True)
class ValidatedReasoning:
    report: ReasoningReport
    validation_summary: dict
    historical_sample_size: int

    def as_dict(self) -> dict:
        payload = self.report.as_dict()
        payload["validation_summary"] = {
            key: str(value) if isinstance(value, Decimal) else value
            for key, value in self.validation_summary.items()
        }
        payload["historical_sample_size"] = self.historical_sample_size
        return payload


def explain_with_validation(decision: Decision, outcomes: list[ValidationOutcome]) -> ValidatedReasoning:
    """Explain an existing decision while exposing historical validation evidence."""
    report = explain_decision(decision)
    summary = summarize_outcomes(outcomes)
    uncertainty = list(report.uncertainty)
    if not outcomes:
        uncertainty.append("no historical validation outcomes are available")
    elif summary["accuracy"] < Decimal("0.50"):
        uncertainty.append("historical decision accuracy is below 0.50")
    return ValidatedReasoning(
        ReasoningReport(report.recommendation, report.risk_score, report.confidence, report.factors, tuple(uncertainty), report.rationale),
        summary,
        len(outcomes),
    )
