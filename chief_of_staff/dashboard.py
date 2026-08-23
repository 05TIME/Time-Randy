"""Web dashboard for the TIMEŒ Chief of Staff command center."""

from flask import Blueprint, render_template_string

from .command_center import build_command_center

bp = Blueprint("chief_of_staff_dashboard", __name__)

_TEMPLATE = """
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TIMEŒ Command Center</title>
<style>body{font-family:system-ui;background:#0b1020;color:#eef;padding:24px;max-width:1100px;margin:auto}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.card{background:#151d32;border:1px solid #293554;border-radius:14px;padding:16px}.escalate{border-left:5px solid #ff5d6c}.action{border-left:5px solid #ffb84d}.monitor{border-left:5px solid #62d7a3}small{color:#9ba8c7}@media(max-width:700px){.grid{grid-template-columns:1fr}}</style>
</head><body><h1>TIMEŒ Command Center</h1><p><small>Owner decision layer</small></p>
<div class="grid"><section class="card escalate"><h2>🔴 Escalate</h2>{% for d in center.escalations %}<p><b>{{d.unit}}</b> — {{d.headline}}<br><small>{{d.escalation or ''}}</small></p>{% else %}<p>Nothing urgent.</p>{% endfor %}</section>
<section class="card action"><h2>🟠 Action</h2>{% for d in center.actions %}<p><b>{{d.unit}}</b> — {{d.headline}}<br><small>{{d.action or ''}}</small></p>{% else %}<p>No immediate actions.</p>{% endfor %}</section>
<section class="card monitor"><h2>🟢 Monitor</h2>{% for d in center.monitors %}<p><b>{{d.unit}}</b> — {{d.headline}}</p>{% else %}<p>Nothing to monitor.</p>{% endfor %}</section></div>
</body></html>
"""


@bp.get("/chief-of-staff")
def dashboard():
    return render_template_string(_TEMPLATE, center=build_command_center([]))
