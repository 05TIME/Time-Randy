from datetime import date

from airbnb_ops.approval_queue import ApprovalItem
from airbnb_ops.dashboard_routes import _approvals, bp
from airbnb_ops.task_engine import OpsTask


def test_command_center_exposes_approval_state():
    app = __import__("flask").Flask(__name__)
    app.register_blueprint(bp)
    _approvals.clear()
    task = OpsTask("turnover", "Clean property", date(2026, 8, 24), "BK-1", "high")
    item = ApprovalItem(task)
    _approvals[item.approval_id] = item
    client = app.test_client()
    response = client.get("/airbnb/command-center")
    assert response.status_code == 200
    assert response.get_json()["approvals"][0]["status"] == "pending"


def test_approval_actions_update_state():
    app = __import__("flask").Flask(__name__)
    app.register_blueprint(bp)
    _approvals.clear()
    item = ApprovalItem(OpsTask("turnover", "Clean property", date(2026, 8, 24), "BK-2", "high"))
    _approvals[item.approval_id] = item
    client = app.test_client()
    approved = client.post(f"/airbnb/approvals/{item.approval_id}/approve")
    assert approved.status_code == 200
    assert approved.get_json()["status"] == "approved"
    completed = client.post(f"/airbnb/approvals/{item.approval_id}/complete")
    assert completed.status_code == 200
    assert completed.get_json()["status"] == "completed"


def test_missing_approval_is_404():
    app = __import__("flask").Flask(__name__)
    app.register_blueprint(bp)
    _approvals.clear()
    response = app.test_client().post("/airbnb/approvals/missing/approve")
    assert response.status_code == 404
