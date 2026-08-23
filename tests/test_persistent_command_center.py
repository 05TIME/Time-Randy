from datetime import date

from flask import Flask

from airbnb_ops.approval_queue import ApprovalItem
from airbnb_ops.approval_runtime import ApprovalRuntime
from airbnb_ops.dashboard_routes import bp
from airbnb_ops.task_engine import OpsTask


def test_command_center_reads_persisted_approval(monkeypatch, tmp_path):
    from airbnb_ops import dashboard_routes

    runtime = ApprovalRuntime(tmp_path / "approvals.sqlite3")
    monkeypatch.setattr(dashboard_routes, "_runtime", runtime)
    item = ApprovalItem(OpsTask("turnover", "Clean property", date(2026, 8, 24), "BK-PERSIST", "high"))
    with runtime.store() as store:
        store.save(item)

    app = Flask(__name__)
    app.register_blueprint(bp)
    payload = app.test_client().get("/airbnb/command-center").get_json()
    assert any(x["approval_id"].startswith("turnover:BK-PERSIST") for x in payload["approvals"])
