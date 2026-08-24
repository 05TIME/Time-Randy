from decimal import Decimal

from forex.regime import classify_regime
from forex.signals import MarketBar


def bars(values):
    return [MarketBar(str(i), Decimal(v), Decimal(v), Decimal(v), Decimal(v)) for i, v in enumerate(values)]


def test_regime_detects_trend():
    result = classify_regime(bars([100, 101, 102, 103, 104, 105]))
    assert result.name == "trend"
    assert Decimal("0") <= result.confidence <= Decimal("1")


def test_regime_detects_range():
    result = classify_regime(bars([100, 100.01, 99.99, 100.01, 100, 99.99]))
    assert result.name == "range"


def test_regime_detects_insufficient_history():
    result = classify_regime(bars([100, 101]))
    assert result.name == "insufficient"
