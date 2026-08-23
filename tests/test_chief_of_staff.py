from decimal import Decimal

from airbnb_ops.chief_of_staff import build_brief


def test_growth_brief_for_low_occupancy():
    brief = build_brief({
        "occupancy_rate": Decimal("0.43"),
        "available_nights": 14,
        "booked_nights": 6,
        "outstanding_obligation": Decimal("0"),
    })
    assert brief.priority == "growth"
    assert "8 unbooked" in brief.headline
    assert brief.actions


def test_finance_issue_escalates():
    brief = build_brief({
        "occupancy_rate": Decimal("0.80"),
        "available_nights": 10,
        "booked_nights": 8,
        "outstanding_obligation": Decimal("900000"),
    })
    assert brief.priority == "escalate"
    assert brief.escalations
