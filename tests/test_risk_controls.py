from decimal import Decimal

from airbnb_ops.decision_engine import Decision
from airbnb_ops.risk_controls import evaluate_risk_gate


def decision(risk, confidence):
    return Decision("review_now", "high", Decimal(risk), Decimal(confidence), "test")


def test_risk_gate_allows_safe_decision():
    result = evaluate_risk_gate(decision("0.60", "0.80"))
    assert result.allowed is True


def test_risk_gate_blocks_excessive_risk():
    result = evaluate_risk_gate(decision("0.76", "0.90"))
    assert result.allowed is False
    assert "risk score" in result.reason


def test_risk_gate_blocks_low_confidence():
    result = evaluate_risk_gate(decision("0.60", "0.49"))
    assert result.allowed is False
    assert "confidence" in result.reason
