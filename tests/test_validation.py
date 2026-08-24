from decimal import Decimal

from airbnb_ops.validation import summarize_outcomes, validate_prediction


def test_validation_marks_matching_outcome_correct():
    outcome = validate_prediction("review_now", "review_now")
    assert outcome.correct is True
    assert outcome.error == Decimal("0")


def test_validation_captures_calibration_error():
    outcome = validate_prediction("monitor", "review_now", Decimal("0.30"), Decimal("0.80"))
    assert outcome.correct is False
    assert outcome.error == Decimal("1")


def test_validation_summary_reports_accuracy_and_error():
    outcomes = [validate_prediction("a", "a"), validate_prediction("a", "b")]
    summary = summarize_outcomes(outcomes)
    assert summary["total"] == 2
    assert summary["correct"] == 1
    assert summary["accuracy"] == Decimal("0.5")
