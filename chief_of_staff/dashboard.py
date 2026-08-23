"""Web dashboard for the TIMEŒ Chief of Staff command center."""

import os
from datetime import date

from flask import Blueprint, render_template_string

from airbnb_ops.sqlite_store import SQLiteStore
from airbnb_ops.task_engine import upcoming_tasks
from .airbnb_adapter import signal_from_airbnb_summary
from .command_center import build_command_center

bp = Blueprint("chief_of_staff_dashboard", __name__)

_TEMPLATE = """
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TIMEŒ Command Center</title>
<style>body{font-family:system-ui;background:#0b1020;color:#eef;padding:24px;max-width:1100px;margin:auto}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:18px}.metric,.card{background:#151d32;border:1px solid #293554;border-radius:14px;padding:16px}.metric b{display:block;font-size:1.35rem;margin-top:6px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.tasks{margin-top:14px}.escalate{border-left:5px solid #ff5d6c}.action{border-left:5px solid #ffb84d}.monitor{border-left:5px solid #62d7a3}.task{padding:10px 0;border-bottom:1px solid #293554}.task:last-child{border-bottom:0}small{color:#9ba8c7}@media(max-width:800px){.metrics,.grid{grid-template-columns:1fr 1fr}}@media(max-width:520px){.metrics,.grid{grid-template-columns:1fr}}</style>
</head><body><h1>TIMEŒ Command Center</h1><p><small>Live Airbnb ledger → owner decision layer</small></p>
{% if live %}<div class="metrics">
<div class="metric">Occupancy<b>{{occupancy}}</b></div>
<div class="metric">Booked nights<b>{{booked_nights}} / {{available_nights}}</b></div>
<div class="metric">Gross revenue<b>{{gross_revenue}}</b></div>
<div class="metric">Debt nights<b>{{debt_nights}}</b></div>
</div>{% else %}<div class="card"><b>Airbnb ledger not connected.</b><p>Set <code>AIRBNB_DB_PATH</code> to the local SQLite file.</p></div>{% endif %}
<div class="grid"><section class="card escalate"><h2>🔴 Escalate</h2>{% for d in center.escalations %}<p><b>{{d.unit}}</b> — {{d.headline}}<br><small>{{d.escalation or ''}}</small></p>{% else %}<p>Nothing urgent.</p>{% endfor %}</section>
<section class="card action"><h2>🟠 Action</h2>{% for d in center.actions %}<p><b>{{d.unit}}</b> — {{d.headline}}<br><small>{{d.action or ''}}</small></p>{% else %}<p>No immediate actions.</p>{% endfor %}</section>
<section class="card monitor"><h2>🟢 Monitor</h2>{% for d in center.monitors %}<p><b>{{d.unit}}</b> — {{d.headline}}</p>{% else %}<p>Nothing to monitor.</p>{% endfor %}</section></div>
<section class="card tasks"><h2>🧹 Upcoming operations</h2>{% for task in tasks %}<div class="task"><b>{{task.due_date}}</b> — {{task.title}} <small>({{task.priority}})</small></div>{% else %}<p>No upcoming operational tasks.</p>{% endfor %}</section>
</body></html>
"""


def _money(value):
    return f"₦{value:,.0f}"


@bp.get("/chief-of-staff")
def dashboard():
    db_path = os.getenv("AIRBNB_DB_PATH", "data/airbnb_ops.sqlite3")
    signals = []
    tasks = []
    live = os.path.exists(db_path)
    metrics = {"occupancy": "—", "booked_nights": 0, "available_nights": 0, "gross_revenue": "₦0", "debt_nights": 0}

    if live:
        service = SQLiteStore(db_path).load_service()
        period_start = date.today().replace(day=1)
        if period_start.month == 12:
            next_month = period_start.replace(year=period_start.year + 1, month=1)
        else:
            next_month = period_start.replace(month=period_start.month + 1)
        summary = service.summary(period_start, next_month)
        signals.append(signal_from_airbnb_summary(summary))
        tasks = [task.as_dict() for task in upcoming_tasks(service, date.today())]
        metrics.update(
            occupancy=f"{summary['occupancy_rate'] * 100:.0f}%",
            booked_nights=summary["booked_nights"],
            available_nights=summary["available_nights"],
            gross_revenue=_money(summary["gross_revenue"]),
            debt_nights=summary["debt_clearing_nights"],
        )

    center = build_command_center(signals)
    return render_template_string(_TEMPLATE, center=center, live=live, tasks=tasks, **metrics)
