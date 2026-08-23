from datetime import date
from decimal import Decimal

import pytest

from airbnb_ops.escalation import EscalationLevel, assess
from airbnb_ops.forecast import forecast
from airbnb_ops.notifications import TurnoverStatus, create_turnover_task


def test_turnover_requires_cleaning():
    task = create_turnover_task("b1", date(2026, 8, 23), date(2026, 8, 23))
    assert task.status == TurnoverStatus.CLEANING_REQUIRED
    assert task.turnaround_hours == 0


def test_turnover_rejects_invalid_dates():
    with pytest.raises(ValueError):
        create_turnover_task("b1", date(2026, 8, 24), date(2026, 8, 23))


def test_forecast():
    result = forecast(10, 4, Decimal("0.8"), Decimal("150000"))
    assert result.expected_additional_nights == 4
    assert result.expected_revenue == Decimal("1200000")


def test_escalation_for_financial_discrepancy():
    result = assess(financial_discrepancy=True)
    assert result.level == EscalationLevel.ESCALATE
