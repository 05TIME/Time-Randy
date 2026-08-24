from decimal import Decimal

from forex.signals import MarketBar, momentum_signal


def bar(close):
    value = Decimal(close)
    return MarketBar("2026-08-24T00:00:00Z", value, value, value, value)


def test_momentum_signal_is_bounded_and_directional():
    signal = momentum_signal([bar("100"), bar("101"), bar("102"), bar("103")], 3)
    assert signal.direction == "long"
    assert signal.score == Decimal("1")


def test_momentum_signal_requires_history():
    signal = momentum_signal([bar("100"), bar("101")], 3)
    assert signal.direction == "neutral"
    assert signal.score == Decimal("0")
