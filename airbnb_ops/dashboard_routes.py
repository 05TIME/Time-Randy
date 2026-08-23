"""Flask routes for the Airbnb Business Command Center."""

from datetime import date, timedelta

from flask import Blueprint, jsonify

from .approval_queue import ApprovalItem
from .approval_runtime import ApprovalRuntime
from .approval_service import transition
from .command_center_decisions import build_decision_panel
from .dashboard_runtime import build_live_command_center
from .sqlite_store import SQLiteStore

bp = Blueprint("airbnb_dashboard", __name__, url_prefix="/airbnb")
_runtime = ApprovalRuntime()
_ledger = SQLiteStore()


def _approval_payload(item: ApprovalItem) -> dict:
    return {
        "approval_id": item.approval_id,
        "status": item.status.value,
        "task": item.task.as_dict(),
        "decided_at": item.decided_at,
    }


@bp.get("/command-center")
def command_center():
    period_start = date.today()
    period_end = period_start + timedelta(days=30)
    state = build_live_command_center(_ledger, period_start, period_end)
    payload = state.as_dict()
    with _runtime.store() as store:
        approvals = store.list_all()
        payload["approvals"] = [_approval_payload(item) for item in approvals]
        payload["decisions"] = build_decision_panel(approvals, period_start)
    payload["data_source"] = "sqlite-ledger"
    payload["period_start"] = period_start.isoformat()
    payload["period_end"] = period_end.isoformat()
    return jsonify(payload)


@bp.post("/approvals/<approval_id>/<action>")
def approval_action(approval_id: str, action: str):
    with _runtime.store() as store:
        item = store.get(approval_id)
        if item is None:
            return jsonify({"error": "approval not found"}), 404
        try:
            updated = transition(item, action)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        store.save(updated)
        return jsonify(_approval_payload(updated))
