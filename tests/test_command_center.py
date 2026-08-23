from chief_of_staff.command_center import build_command_center
from chief_of_staff.orchestrator import BusinessUnitSignal, DecisionType


def test_command_center_groups_decisions():
    center = build_command_center([
        BusinessUnitSignal("airbnb", "Debt discrepancy", 100, DecisionType.ESCALATE, escalation="Reconcile"),
        BusinessUnitSignal("growth", "Low occupancy", 70, DecisionType.ACTION, action="Promote gaps"),
        BusinessUnitSignal("engineering", "Healthy CI", 20, DecisionType.MONITOR),
    ])
    assert len(center.escalations) == 1
    assert center.escalations[0].unit == "airbnb"
    assert len(center.actions) == 1
    assert len(center.monitors) == 1
    assert center.as_dict()["total"] == 3
