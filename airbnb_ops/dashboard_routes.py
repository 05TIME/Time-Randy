"""Flask routes for the Airbnb Business Command Center."""

from decimal import Decimal

from flask import Blueprint, jsonify

from .approval_queue import ApprovalItem
from .approval_runtime import ApprovalRuntime
from .approval_service import transition
from .dashboard import build_command_center
from .finance import build_snapshot

bp = Blueprint("airbnb_dashboard", __name__, url_prefix="/airbnb")
_runtime = ApprovalRuntime()


def _approval_payload(item: ApprovalItem) -> dict:
    return {
        "approval_id": item.approval_id,
        "status": item.status.value,
        "task": item.task.as_dict(),
        "decided_at": item.decided_at,
    }


@bp.get("/command-center")
def command_center():
    finance = build_snapshot(
        gross_revenue=Decimal("0"),
        platform_fees=Decimal("0"),
        operating_expenses=Decimal("0"),
        outstanding_obligation=Decimal("0"),
        nightly_contribution=Decimal("150000"),
    )
    state = build_command_center(
        occupancy_percent=Decimal("0"),
        finance=finance,
        turnovers=[],
    )
    payload = state.as_dict()
    with _runtime.store() as store:
        payload["approvals"] = [_approval_payload(item) for item in store.list_all()]
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
