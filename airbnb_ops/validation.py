"""Outcome tracking and deterministic validation metrics for TIMEŒ decisions."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ValidationOutcome:
    prediction: str
    actual: str
    correct: bool
    error: Decimal
    note: str


def validate_prediction(prediction: str, actual: str, expected_risk: Decimal | None = None, observed_loss: Decimal | None = None) -> ValidationOutcome:
    correct = prediction == actual
    error = Decimal("0") if correct else Decimal("1")
    if expected_risk is not None and observed_loss is not None:
        calibration_error = abs(expected_risk - observed_loss)
        error = max(error, calibration_error)
    note = "prediction matched observed outcome" if correct else "prediction diverged from observed outcome"
    return ValidationOutcome(prediction, actual, correct, error, note)


def summarize_outcomes(outcomes: list[ValidationOutcome]) -> dict:
    total = len(outcomes)
    correct = sum(outcome.correct for outcome in outcomes)
    return {
        "total": total,
        "correct": correct,
        "accuracy": (Decimal(correct) / Decimal(total)) if total else Decimal("0"),
        "mean_error": (sum((item.error for item in outcomes), Decimal("0")) / Decimal(total)) if total else Decimal("0"),
    }
