import sqlite3
from datetime import date

from flask import Flask

from airbnb_ops.approval_queue import ApprovalItem
from airbnb_ops.approval_store import ApprovalStore
from airbnb_ops.dashboard_routes import bp
from airbnb_ops.task_engine import OpsTask


def test_command_center_reads_persisted_approval():
    # The route uses its application-scoped store; seed the same SQLite file.
    from airbnb_ops import dashboard_routes
    dashboard_routes._store.save(
        ApprovalItem(OpsTask("turnover", "Clean property", date(2026, 8, 24), "BK-PERSIST", "high"))
    )
    app = Flask(__name__)
    app.register_blueprint(bp)
    payload = app.test_client().get("/airbnb/command-center").get_json()
    assert any(x["approval_id"].startswith("turnover:BK-PERSIST") for x in payload["approvals"])
