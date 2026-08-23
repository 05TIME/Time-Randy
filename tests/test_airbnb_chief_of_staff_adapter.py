from decimal import Decimal

from chief_of_staff.airbnb_adapter import signal_from_airbnb_summary
from chief_of_staff.orchestrator import DecisionType


def test_airbnb_debt_is_escalated():
    signal = signal_from_airbnb_summary({
        "occupancy_rate": Decimal("0.80"),
        "available_nights": 10,
        "booked_nights": 8,
        "outstanding_obligation": Decimal("900000"),
    })
    assert signal.decision == DecisionType.ESCALATE
    assert signal.priority == 100


def test_low_occupancy_creates_action():
    signal = signal_from_airbnb_summary({
        "occupancy_rate": Decimal("0.43"),
        "available_nights": 14,
        "booked_nights": 6,
        "outstanding_obligation": Decimal("0"),
    })
    assert signal.decision == DecisionType.ACTION
    assert signal.priority == 70
    assert "8 unbooked" in signal.headline
