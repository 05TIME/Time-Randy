"""Flask routes for the Airbnb Business Command Center."""

from flask import Blueprint, jsonify
from decimal import Decimal

from .dashboard import build_command_center
from .finance import build_snapshot

bp = Blueprint("airbnb_dashboard", __name__, url_prefix="/airbnb")


@bp.get("/command-center")
def command_center():
    # Safe demo state until real booking/expense records are wired into the
    # view model. This endpoint deliberately does not invent live Airbnb data.
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
    return jsonify(state.as_dict())
