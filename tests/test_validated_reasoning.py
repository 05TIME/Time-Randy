from decimal import Decimal

from airbnb_ops.decision_engine import Decision
from airbnb_ops.validation import validate_prediction
from airbnb_ops.validated_reasoning import explain_with_validation


def test_validated_reasoning_exposes_historical_accuracy():
    decision = Decision("monitor", "low", Decimal("0.20"), Decimal("0.80"), "stable")
    outcomes = [validate_prediction("monitor", "monitor"), validate_prediction("monitor", "review_now")]
    result = explain_with_validation(decision, outcomes)
    assert result.historical_sample_size == 2
    assert result.validation_summary["accuracy"] == Decimal("0.5")


def test_validated_reasoning_flags_missing_history():
    decision = Decision("monitor", "low", Decimal("0.20"), Decimal("0.80"), "stable")
    result = explain_with_validation(decision, [])
    assert result.historical_sample_size == 0
    assert any("no historical" in item for item in result.report.uncertainty)


def test_validated_reasoning_flags_poor_history():
    decision = Decision("monitor", "low", Decimal("0.20"), Decimal("0.80"), "stable")
    outcomes = [validate_prediction("monitor", "review_now"), validate_prediction("monitor", "review_now")]
    result = explain_with_validation(decision, outcomes)
    assert any("accuracy" in item for item in result.report.uncertainty)
