"""Small Flask API surface for the Chief of Staff command center."""

from flask import Blueprint, jsonify, request

from .airbnb_adapter import signal_from_airbnb_summary
from .command_center import build_command_center

bp = Blueprint("chief_of_staff_command_center", __name__)


@bp.get("/chief-of-staff/command-center")
def command_center():
    """Return the current command-center view from supplied unit summaries."""
    payload = request.get_json(silent=True) or {}
    signals = []
    airbnb = payload.get("airbnb")
    if airbnb:
        signals.append(signal_from_airbnb_summary(airbnb))
    return jsonify(build_command_center(signals).as_dict())
