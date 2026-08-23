import sqlite3
from datetime import date

from flask import Flask

from airbnb_ops.approval_queue import ApprovalItem
from airbnb_ops.approval_store import ApprovalStore
from airbnb_ops.dashboard_routes import bp
from airbnb_ops.task_engine import OpsTask


def make_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app


def test_command_center_exposes_approval_state(monkeypatch):
    from airbnb_ops import dashboard_routes

    connection = sqlite3.connect(":memory:")
    store = ApprovalStore(connection)
    monkeypatch.setattr(dashboard_routes, "_store", store)

    item = ApprovalItem(OpsTask("turnover", "Clean property", date(2026, 8, 24), "BK-1", "high"))
    store.save(item)

    response = make_app().test_client().get("/airbnb/command-center")
    assert response.status_code == 200
    assert response.get_json()["approvals"][0]["status"] == "pending"


def test_approval_actions_update_state(monkeypatch):
    from airbnb_ops import dashboard_routes

    connection = sqlite3.connect(":memory:")
    store = ApprovalStore(connection)
    monkeypatch.setattr(dashboard_routes, "_store", store)

    item = ApprovalItem(OpsTask("turnover", "Clean property", date(2026, 8, 24), "BK-2", "high"))
    store.save(item)

    client = make_app().test_client()
    approved = client.post(f"/airbnb/approvals/{item.approval_id}/approve")
    assert approved.status_code == 200
    assert approved.get_json()["status"] == "approved"

    completed = client.post(f"/airbnb/approvals/{item.approval_id}/complete")
    assert completed.status_code == 200
    assert completed.get_json()["status"] == "completed"
    assert store.get(item.approval_id).status.value == "completed"


def test_missing_approval_is_404(monkeypatch):
    from airbnb_ops import dashboard_routes

    connection = sqlite3.connect(":memory:")
    store = ApprovalStore(connection)
    monkeypatch.setattr(dashboard_routes, "_store", store)

    response = make_app().test_client().post("/airbnb/approvals/missing/approve")
    assert response.status_code == 404
