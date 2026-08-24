"""Flask routes for the Airbnb Business Command Center."""

import os
from datetime import date
from decimal import Decimal

from flask import Blueprint, jsonify

from .approval_queue import ApprovalItem
from .approval_runtime import ApprovalRuntime
from .approval_service import transition
from .command_center_decisions import build_decision_panel
from .dashboard import build_command_center
from .finance import build_snapshot
from .sqlite_store import SQLiteStore

bp = Blueprint("airbnb_dashboard", __name__, url_prefix="/airbnb")
_runtime = ApprovalRuntime()


def _approval_payload(item: ApprovalItem) -> dict:
    return {
        "approval_id": item.approval_id,
        "status": item.status.value,
        "task": item.task.as_dict(),
        "decided_at": item.decided_at,
    }


def _period(today: date) -> tuple[date, date]:
    start = today.replace(day=1)
    if start.month == 12:
        end = date(start.year + 1, 1, 1)
    else:
        end = date(start.year, start.month + 1, 1)
    return start, end


def _live_business_state(today: date) -> tuple[dict, object]:
    store = SQLiteStore(os.getenv("AIRBNB_DB_PATH", "data/airbnb_ops.sqlite3"))
    service = store.load_service()
    start, end = _period(today)
    summary = service.summary(start, end)
    booked_nights = summary["booked_nights"]
    nightly_contribution = (
        summary["net_operating_result"] / Decimal(booked_nights)
        if booked_nights > 0 and summary["net_operating_result"] > 0
        else service.config.nightly_rate
    )
    finance = build_snapshot(
        gross_revenue=summary["gross_revenue"],
        platform_fees=summary["platform_fees"],
        operating_expenses=summary["operating_expenses"],
        outstanding_obligation=summary["outstanding_obligation"],
        nightly_contribution=nightly_contribution,
        fixed_costs=service.config.target_monthly_fixed_costs,
    )
    return summary, finance


@bp.get("/command-center")
def command_center():
    today = date.today()
    summary, finance = _live_business_state(today)
    state = build_command_center(
        occupancy_percent=summary["occupancy_rate"],
        finance=finance,
        turnovers=[],
    )
    payload = state.as_dict()
    payload["data_source"] = "sqlite-ledger"
    payload["period_start"] = summary["period_start"]
    payload["period_end"] = summary["period_end"]
    with _runtime.store() as store:
        approvals = store.list_all()
        payload["approvals"] = [_approval_payload(item) for item in approvals]
        payload["decisions"] = build_decision_panel(approvals, today)
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
