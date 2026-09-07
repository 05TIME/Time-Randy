from timeoe_engine import State, Task, TimeoeEngine


def test_command_creates_graph():
    e = TimeoeEngine()
    snap = e.command("launch recurring revenue", [
        {"name": "Validate demand", "agent": "research"},
        {"name": "Create offer", "agent": "product"},
        {"name": "Launch campaign", "agent": "marketing"},
    ])
    assert len(snap["tasks"]) == 4
    assert any(x["type"] == "COMMAND_RECEIVED" for x in snap["events"])


def test_dependency_execution():
    e = TimeoeEngine()
    e.register_worker("research", lambda t: {"demand": True})
    e.register_worker("product", lambda t: {"offer": "subscription"})
    e.command("build", [
        {"name": "research", "agent": "research"},
        {"name": "product", "agent": "product"},
    ])
    snap = e.run_ready()
    states = [x["state"] for x in snap["tasks"]]
    assert State.COMPLETED.value in states
    assert all(x["state"] != State.FAILED.value for x in snap["tasks"])
