"""Flask routes for the Airbnb Business Command Center."""

import os
from datetime import date
from decimal import Decimal

from flask import Blueprint, jsonify, render_template_string

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
    return {"approval_id": item.approval_id, "status": item.status.value, "task": item.task.as_dict(), "decided_at": item.decided_at}


def _period(today: date) -> tuple[date, date]:
    start = today.replace(day=1)
    end = date(start.year + 1, 1, 1) if start.month == 12 else date(start.year, start.month + 1, 1)
    return start, end


def _live_business_state(today: date) -> tuple[dict, object]:
    store = SQLiteStore(os.getenv("AIRBNB_DB_PATH", "data/airbnb_ops.sqlite3"))
    service = store.load_service()
    start, end = _period(today)
    summary = service.summary(start, end)
    booked_nights = summary["booked_nights"]
    nightly_contribution = (summary["net_operating_result"] / Decimal(booked_nights) if booked_nights > 0 and summary["net_operating_result"] > 0 else service.config.nightly_rate)
    finance = build_snapshot(
        gross_revenue=summary["gross_revenue"], platform_fees=summary["platform_fees"],
        operating_expenses=summary["operating_expenses"], outstanding_obligation=summary["outstanding_obligation"],
        nightly_contribution=nightly_contribution, fixed_costs=service.config.target_monthly_fixed_costs,
    )
    return summary, finance


@bp.get("/command-center")
def command_center():
    today = date.today()
    summary, finance = _live_business_state(today)
    state = build_command_center(occupancy_percent=summary["occupancy_rate"], finance=finance, turnovers=[])
    payload = state.as_dict()
    payload["data_source"] = "sqlite-ledger"
    payload["period_start"] = summary["period_start"]
    payload["period_end"] = summary["period_end"]
    with _runtime.store() as store:
        approvals = store.list_all()
        payload["approvals"] = [_approval_payload(item) for item in approvals]
        payload["decisions"] = build_decision_panel(approvals, today)
    return jsonify(payload)


@bp.get("/dashboard")
def dashboard_ui():
    """Mobile-friendly visual dashboard using the live command-center model."""
    today = date.today()
    summary, finance = _live_business_state(today)
    state = build_command_center(occupancy_percent=summary["occupancy_rate"], finance=finance, turnovers=[]).as_dict()
    with _runtime.store() as store:
        approvals = store.list_all()
    pending = sum(1 for item in approvals if item.status.value == "pending")
    return render_template_string("""<!doctype html><html lang="en"><head>
<meta name="viewport" content="width=device-width,initial-scale=1"><title>TIMEŒ Airbnb Turnover Monitor</title>
<style>
:root{color-scheme:dark;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display",Inter,system-ui,sans-serif;background:#090b10;color:#f5f7fa}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#17202b,#090b10 55%);min-height:100vh}.wrap{max-width:920px;margin:auto;padding:22px 16px 44px}.top{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:24px}.brand{font-weight:800;letter-spacing:.04em}.brand span{color:#35f36b}.sub{color:#8d96a5;font-size:13px;margin-top:4px}.pill{border:1px solid #29313d;border-radius:999px;padding:8px 11px;font-size:12px;color:#aeb7c5}h1{font-size:30px;margin:0 0 8px}.lead{color:#aeb7c5;margin:0 0 20px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.card{background:#11151c;border:1px solid #252c36;border-radius:18px;padding:16px;box-shadow:0 10px 35px #0005}.label{color:#8993a2;font-size:12px;text-transform:uppercase;letter-spacing:.08em}.value{font-size:27px;font-weight:800;margin-top:8px}.good{color:#35f36b}.warn{color:#ffd166}.muted{color:#aeb7c5}.section{margin-top:18px}.actions{display:flex;gap:10px;flex-wrap:wrap}.button{display:inline-block;background:#35f36b;color:#071009;border-radius:12px;padding:11px 14px;font-weight:750;text-decoration:none}.button.alt{background:#171d26;color:#dce3ec;border:1px solid #2a3340}@media(min-width:720px){.grid{grid-template-columns:repeat(4,1fr)}}
</style></head><body><main class="wrap"><header class="top"><div><div class="brand">$TIMEŒ <span>AIRBNB OPS</span></div><div class="sub">Turnover Monitor • live ledger</div></div><div class="pill">{{ data_source }}</div></header><h1>Business Command Center</h1><p class="lead">{{ period_start }} → {{ period_end }}</p>
<section class="grid"><div class="card"><div class="label">Occupancy</div><div class="value">{{ occupancy }}%</div></div><div class="card"><div class="label">Gross revenue</div><div class="value">${{ gross }}</div></div><div class="card"><div class="label">Net operating</div><div class="value good">${{ net }}</div></div><div class="card"><div class="label">Pending approvals</div><div class="value warn">{{ pending }}</div></div></section>
<section class="section grid"><div class="card"><div class="label">Upcoming turnovers</div><div class="value">{{ upcoming }}</div></div><div class="card"><div class="label">Ready</div><div class="value good">{{ ready }}</div></div><div class="card"><div class="label">Escalated</div><div class="value warn">{{ escalated }}</div></div><div class="card"><div class="label">Maintenance</div><div class="value">{{ maintenance }}</div></div></section>
<section class="section card"><div class="label">Operations</div><h2>Turnover control</h2><p class="muted">Connected to the SQLite business ledger. Reservation and turnover feeds can plug into the same command-center API.</p><div class="actions"><a class="button" href="/airbnb/command-center">Live JSON</a><a class="button alt" href="/airbnb/brief">Brief</a><a class="button alt" href="/">TIMEŒ Home</a></div></section></main></body></html>""",
        data_source="sqlite-ledger", period_start=summary["period_start"], period_end=summary["period_end"],
        occupancy=round(float(state["occupancy_percent"]) * 100, 1), gross=f"{float(state['gross_revenue']):,.2f}",
        net=f"{float(state['net_operating_result']):,.2f}", pending=pending, upcoming=state["upcoming_turnovers"],
        ready=state["turnovers_ready"], escalated=state["turnovers_escalated"], maintenance=state["open_maintenance_issues"],
    )


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
""