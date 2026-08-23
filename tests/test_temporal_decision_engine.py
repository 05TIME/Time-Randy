from datetime import date
from decimal import Decimal

from airbnb_ops.decision_engine import evaluate
from airbnb_ops.temporal_engine import extract_temporal_features


def test_temporal_features_are_deterministic():
    features = extract_temporal_features(date(2026, 8, 23), date(2026, 8, 25))
    assert features.days_to_due == 2
    assert features.urgency == Decimal("0.85")
    assert features.horizon == "near"


def test_overdue_tasks_are_due_and_max_urgent():
    features = extract_temporal_features(date(2026, 8, 23), date(2026, 8, 20))
    assert features.days_to_due == -3
    assert features.urgency == Decimal("1.00")
    assert features.horizon == "due"


def test_high_priority_near_term_task_requires_review():
    temporal = extract_temporal_features(date(2026, 8, 23), date(2026, 8, 25))
    decision = evaluate("turnover", temporal, "high")
    assert decision.action == "review_now"
    assert decision.priority == "high"
    assert decision.risk_score == Decimal("0.96")
    assert decision.confidence == Decimal("0.52")
    assert "2 days" in decision.rationale


def test_low_priority_long_horizon_task_is_monitored():
    temporal = extract_temporal_features(date(2026, 8, 23), date(2026, 10, 1))
    decision = evaluate("maintenance", temporal, "low")
    assert decision.action == "monitor"
    assert decision.risk_score == Decimal("0.23")
