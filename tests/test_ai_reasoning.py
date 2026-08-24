from decimal import Decimal

from airbnb_ops.ai_reasoning import explain_decision
from airbnb_ops.decision_engine import Decision


def test_reasoning_explains_existing_decision_without_changing_it():
    decision = Decision("review_now", "high", Decimal("0.62"), Decimal("0.66"), "urgent operational issue")
    report = explain_decision(decision)
    assert report.recommendation == decision.action
    assert report.risk_score == decision.risk_score
    assert report.confidence == decision.confidence
    assert report.factors
    assert report.uncertainty
    assert "urgent operational issue" in report.rationale


def test_reasoning_reports_low_confidence_uncertainty():
    decision = Decision("monitor", "low", Decimal("0.20"), Decimal("0.40"), "limited evidence")
    report = explain_decision(decision)
    assert any("confidence" in item for item in report.uncertainty)
