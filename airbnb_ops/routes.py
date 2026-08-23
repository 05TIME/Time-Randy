"""HTTP interface for the Airbnb Ops Agent."""

from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, render_template_string, request

from .service import AirbnbOpsService, Booking, Expense, PropertyConfig, money


bp = Blueprint("airbnb_ops", __name__, url_prefix="/airbnb")

# Temporary in-memory store for the first vertical slice.
# Persistence/database integration comes next.
ops = AirbnbOpsService(
    PropertyConfig(
        property_name="Lekki Phase 1 — 2BR",
        nightly_rate=Decimal("150000"),
    )
)


@bp.get("/")
def dashboard():
    start = _date_arg("start") or date.today().replace(day=1)
    end = _date_arg("end") or _next_month(start)
    summary = ops.summary(start, end)
    alerts = ops.operational_alerts(start, end)

    return render_template_string(
        """
        <!doctype html>
        <html><head><meta charset="utf-8"><title>TIMEŒ Airbnb Ops</title>
        <style>body{font-family:system-ui;max-width:900px;margin:40px auto;padding:0 20px}
        .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.card{padding:18px;border:1px solid #ddd;border-radius:12px}
        .alert{padding:10px;background:#fff3cd;margin:8px 0;border-radius:8px}</style></head>
        <body><h1>TIMEŒ — Airbnb Ops</h1><p>{{ summary.property }}</p>
        <div class="grid">
          <div class="card"><b>Occupancy</b><h2>{{ '%.1f'|format(summary.occupancy_rate * 100) }}%</h2></div>
          <div class="card"><b>Gross revenue</b><h2>{{ money(summary.gross_revenue) }}</h2></div>
          <div class="card"><b>Net operating result</b><h2>{{ money(summary.net_operating_result) }}</h2></div>
          <div class="card"><b>Booked nights</b><h2>{{ summary.booked_nights }}</h2></div>
          <div class="card"><b>ADR</b><h2>{{ money(summary.adr) }}</h2></div>
          <div class="card"><b>Debt-clearing nights</b><h2>{{ summary.debt_clearing_nights }}</h2></div>
        </div>
        <h2>Alerts</h2>{% for alert in alerts %}<div class="alert">{{ alert }}</div>{% else %}<p>No alerts.</p>{% endfor %}
        </body></html>
        """,
        summary=summary,
        alerts=alerts,
        money=money,
    )


@bp.get("/summary")
def summary_api():
    start = _date_arg("start") or date.today().replace(day=1)
    end = _date_arg("end") or _next_month(start)
    result = ops.summary(start, end)
    return jsonify(_json_safe(result))


@bp.post("/bookings")
def create_booking():
    data = request.get_json(silent=True) or {}
    try:
        booking = Booking(
            booking_id=str(data["booking_id"]),
            check_in=date.fromisoformat(data["check_in"]),
            check_out=date.fromisoformat(data["check_out"]),
            nightly_rate=Decimal(str(data.get("nightly_rate", ops.config.nightly_rate))),
            platform_fee=Decimal(str(data.get("platform_fee", "0"))),
        )
        ops.add_booking(booking)
    except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"status": "created", "booking_id": booking.booking_id, "nights": booking.nights}), 201


@bp.post("/expenses")
def create_expense():
    data = request.get_json(silent=True) or {}
    try:
        expense = Expense(
            expense_id=str(data["expense_id"]),
            category=str(data["category"]),
            amount=Decimal(str(data["amount"])),
            expense_date=date.fromisoformat(data.get("expense_date", date.today().isoformat())),
            note=str(data.get("note", "")),
        )
        ops.add_expense(expense)
    except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"status": "created", "expense_id": expense.expense_id}), 201


def _date_arg(name: str):
    value = request.args.get(name)
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _next_month(day: date) -> date:
    if day.month == 12:
        return date(day.year + 1, 1, 1)
    return date(day.year, day.month + 1, 1)


def _json_safe(data: dict) -> dict:
    return {
        key: float(value) if isinstance(value, Decimal) else value
        for key, value in data.items()
    }
