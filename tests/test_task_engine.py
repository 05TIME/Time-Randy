from datetime import date
from decimal import Decimal

from airbnb_ops.service import AirbnbOpsService, Booking, PropertyConfig
from airbnb_ops.task_engine import upcoming_tasks


def test_upcoming_tasks_generates_turnover_checkin_and_finance():
    service = AirbnbOpsService(PropertyConfig(outstanding_obligation=Decimal("300000")))
    service.add_booking(Booking("B1", date(2026, 8, 25), date(2026, 8, 27), Decimal("150000")))

    tasks = upcoming_tasks(service, date(2026, 8, 24), horizon_days=4)

    assert [task.task_type for task in tasks] == ["finance", "check_in", "turnover"]
    assert tasks[1].booking_id == "B1"
    assert tasks[2].due_date == date(2026, 8, 27)
    assert tasks[0].priority == "critical"
