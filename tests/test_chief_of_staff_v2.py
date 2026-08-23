from chief_of_staff.orchestrator import BusinessUnitSignal, DecisionType, rank_signals


def test_cross_unit_signals_are_ranked():
    signals = [
        BusinessUnitSignal("growth", "Occupancy below target", 60, DecisionType.ACTION, "Review weekday pricing"),
        BusinessUnitSignal("airbnb", "Payment discrepancy", 100, DecisionType.ESCALATE, escalation="Owner reconciliation required"),
        BusinessUnitSignal("engineering", "CI healthy", 20, DecisionType.MONITOR),
    ]
    decisions = rank_signals(signals)
    assert decisions[0].unit == "airbnb"
    assert decisions[0].priority == "escalate"
    assert decisions[1].unit == "growth"
    assert decisions[2].unit == "engineering"


def test_rank_limit_is_respected():
    signals = [BusinessUnitSignal(str(i), "signal", i, DecisionType.MONITOR) for i in range(10)]
    assert len(rank_signals(signals, limit=3)) == 3
