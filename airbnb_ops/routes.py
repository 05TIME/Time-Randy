"""HTTP interface for the Airbnb Ops Agent."""

from datetime import date
from decimal import Decimal, InvalidOperation
import os

from flask import Blueprint, jsonify, render_template_string, request

from .airbnb_ical import AirbnbICalAdapter
from .pricing import recommend_rate
from .service import AirbnbOpsService, Booking, Expense, PropertyConfig, money
from .store import SQLiteStore
from .sync import sync_channel

bp = Blueprint("airbnb_ops", __name__, url_prefix="/airbnb")


def _config() -> PropertyConfig:
    return PropertyConfig(
        property_name=os.getenv("TIMEOE_PROPERTY_NAME", "Lekki Phase 1 — 2BR"),
        nightly_rate=Decimal(os.getenv("TIMEOE_NIGHTLY_RATE", "150000")),
        outstanding_obligation=Decimal(os.getenv("TIMEOE_OUTSTANDING_OBLIGATION", "0")),
        target_monthly_fixed_costs=Decimal(os.getenv("TIMEOE_MONTHLY_FIXED_COSTS", "0")),
    )


def _store() -> SQLiteStore:
    return SQLiteStore(os.getenv("TIMEOE_AIRBNB_DB", "data/airbnb_ops.sqlite3"))


def _service() -> AirbnbOpsService:
    service = AirbnbOpsService(_config())
    store = _store()
    for booking in store.bookings():
        service.add_booking(booking)
    for expense in store.expenses():
        service.add_expense(expense)
    return service


@bp.get("/")
def dashboard():
    start = _date_arg("start") or date.today().replace(day=1)
    end = _date_arg("end") or _next_month(start)
    ops = _service()
    summary = ops.summary(start, end)
    alerts = ops.operational_alerts(start, end)
    store = _store()
    tasks = store.open_tasks()
    low_inventory = store.low_inventory()
    maintenance = store.open_maintenance()
    return render_template_string("""<!doctype html><html><head><meta charset="utf-8"><title>TIMEŒ Airbnb Ops</title><style>body{font-family:system-ui;max-width:1000px;margin:40px auto;padding:0 20px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.card{padding:18px;border:1px solid #ddd;border-radius:12px}.alert{padding:10px;background:#fff3cd;margin:8px 0;border-radius:8px}.bad{background:#f8d7da}</style></head><body><h1>TIMEŒ — Airbnb Ops</h1><p>{{ summary.property }}</p><div class="grid"><div class="card"><b>Occupancy</b><h2>{{ '%.1f'|format(summary.occupancy_rate * 100) }}%</h2></div><div class="card"><b>Gross revenue</b><h2>{{ money(summary.gross_revenue) }}</h2></div><div class="card"><b>Net operating result</b><h2>{{ money(summary.net_operating_result) }}</h2></div><div class="card"><b>Booked nights</b><h2>{{ summary.booked_nights }}</h2></div><div class="card"><b>ADR</b><h2>{{ money(summary.adr) }}</h2></div><div class="card"><b>Debt-clearing nights</b><h2>{{ summary.debt_clearing_nights }}</h2></div></div><h2>Operational alerts</h2>{% for alert in alerts %}<div class="alert">{{ alert }}</div>{% else %}<p>No alerts.</p>{% endfor %}<h2>Open work</h2><p>{{ tasks|length }} task(s), {{ low_inventory|length }} low-inventory item(s), {{ maintenance|length }} maintenance issue(s).</p></body></html>""", summary=summary, alerts=alerts, tasks=tasks, low_inventory=low_inventory, maintenance=maintenance, money=money)


@bp.get("/summary")
def summary_api():
    start = _date_arg("start") or date.today().replace(day=1)
    end = _date_arg("end") or _next_month(start)
    return jsonify(_json_safe(_service().summary(start, end)))


def _sync_airbnb():
    """Sync the listing from an Airbnb-exported iCal URL without exposing the URL."""
    calendar_url = os.getenv("TIMEOE_AIRBNB_ICAL_URL")
    if not calendar_url:
        return jsonify({"error": "TIMEOE_AIRBNB_ICAL_URL is not configured"}), 503
    start = _date_arg("start") or date.today()
    end = _date_arg("end") or date(start.year + 1, 1, 1)
    store = _store()
    try:
        imported = sync_channel(_service(), AirbnbICalAdapter(calendar_url), start, end, on_import=store.add_booking)
    except (OSError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 502
    return jsonify({"status": "synced", "source": "airbnb_ical", "imported": imported, "start": start.isoformat(), "end": end.isoformat()})


@bp.post("/sync/airbnb")
def sync_airbnb():
    return _sync_airbnb()


@bp.get("/sync/airbnb")
def sync_airbnb_browser():
    """Browser-friendly sync so the host can trigger a refresh from Safari."""
    return _sync_airbnb()


@bp.post("/bookings")
def create_booking():
    data = request.get_json(silent=True) or {}
    try:
        booking = Booking(booking_id=str(data["booking_id"]), check_in=date.fromisoformat(data["check_in"]), check_out=date.fromisoformat(data["check_out"]), nightly_rate=Decimal(str(data.get("nightly_rate", _config().nightly_rate))), platform_fee=Decimal(str(data.get("platform_fee", "0"))))
        _service().add_booking(booking)
        _store().add_booking(booking)
    except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"status": "created", "booking_id": booking.booking_id, "nights": booking.nights}), 201


@bp.post("/expenses")
def create_expense():
    data = request.get_json(silent=True) or {}
    try:
        expense = Expense(expense_id=str(data["expense_id"]), category=str(data["category"]), amount=Decimal(str(data["amount"])), expense_date=date.fromisoformat(data.get("expense_date", date.today().isoformat())), note=str(data.get("note", "")))
        _service().add_expense(expense)
        _store().add_expense(expense)
    except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"status": "created", "expense_id": expense.expense_id}), 201


@bp.post("/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    if not data.get("title") or not data.get("kind"):
        return jsonify({"error": "kind and title are required"}), 400
    task_id = _store().add_task(str(data["kind"]), str(data["title"]), data.get("due_at"), data.get("assignee"), str(data.get("note", "")))
    return jsonify({"status": "created", "task_id": task_id}), 201


@bp.get("/tasks")
def list_tasks():
    return jsonify(_store().open_tasks())


@bp.post("/inventory")
def set_inventory():
    data = request.get_json(silent=True) or {}
    try:
        item = str(data["item"]); quantity = int(data["quantity"]); reorder_level = int(data.get("reorder_level", 0))
        if quantity < 0 or reorder_level < 0: raise ValueError("inventory values cannot be negative")
        _store().set_inventory(item, quantity, reorder_level)
    except (KeyError, TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"status": "updated", "item": item}), 200


@bp.get("/inventory/low")
def low_inventory():
    return jsonify(_store().low_inventory())


@bp.post("/maintenance")
def create_maintenance():
    data = request.get_json(silent=True) or {}
    if not data.get("title"):
        return jsonify({"error": "title is required"}), 400
    issue_id = _store().add_maintenance(str(data["title"]), str(data.get("severity", "normal")), str(data.get("note", "")))
    return jsonify({"status": "created", "issue_id": issue_id}), 201


@bp.get("/maintenance")
def list_maintenance():
    return jsonify(_store().open_maintenance())


@bp.get("/pricing")
def pricing_api():
    start = _date_arg("start") or date.today().replace(day=1)
    end = _date_arg("end") or _next_month(start)
    summary = _service().summary(start, end)
    rec = recommend_rate(_config().nightly_rate, summary["occupancy_rate"], summary["available_nights"] - summary["booked_nights"], _days_until(start))
    return jsonify({"recommended_rate": float(rec.recommended_rate), "reason": rec.reason, "confidence": rec.confidence})


def _date_arg(name: str):
    value = request.args.get(name)
    if not value: return None
    try: return date.fromisoformat(value)
    except ValueError: return None


def _days_until(day: date) -> int:
    return (day - date.today()).days


def _next_month(day: date) -> date:
    if day.month == 12: return date(day.year + 1, 1, 1)
    return date(day.year, day.month + 1, 1)


def _json_safe(data: dict) -> dict:
    return {key: float(value) if isinstance(value, Decimal) else value for key, value in data.items()}
