from datetime import datetime

import pytest

from airbnb_ops.turnover import Turnover, TurnoverState


def test_turnover_happy_path():
    turnover = Turnover(
        booking_id="B1",
        check_out=datetime(2026, 8, 23, 11),
        next_check_in=datetime(2026, 8, 23, 15),
    )
    assert turnover.turnaround_minutes == 240
    turnover.assign_cleaner("Cleaner")
    turnover.start_cleaning()
    turnover.complete_cleaning()
    turnover.require_inspection("Manager")
    turnover.mark_ready()
    assert turnover.state == TurnoverState.READY


def test_turnover_blocks_invalid_transition():
    turnover = Turnover("B1", datetime(2026, 8, 23, 11), datetime(2026, 8, 23, 15))
    with pytest.raises(ValueError):
        turnover.complete_cleaning()


def test_turnover_can_escalate():
    turnover = Turnover("B1", datetime(2026, 8, 23, 11), datetime(2026, 8, 23, 15))
    turnover.escalate("Cleaner unavailable")
    assert turnover.state == TurnoverState.ESCALATED
    assert turnover.note == "Cleaner unavailable"
