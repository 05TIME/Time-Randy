"""Finance dashboard API for the Airbnb Ops Agent."""

from decimal import Decimal, InvalidOperation
from flask import Blueprint, jsonify, request

from .finance import build_snapshot

bp = Blueprint("airbnb_finance", __name__, url_prefix="/airbnb/finance")


def _decimal(data, key):
    try:
        return Decimal(str(data[key]))
    except (KeyError, TypeError, InvalidOperation) as exc:
        raise ValueError(f"invalid finance value: {key}") from exc


@bp.post("/snapshot")
def snapshot():
    data = request.get_json(silent=True) or {}
    try:
        result = build_snapshot(
            gross_revenue=_decimal(data, "gross_revenue"),
            platform_fees=_decimal(data, "platform_fees"),
            operating_expenses=_decimal(data, "operating_expenses"),
            outstanding_obligation=_decimal(data, "outstanding_obligation"),
            nightly_contribution=_decimal(data, "nightly_contribution"),
            fixed_costs=Decimal(str(data.get("fixed_costs", "0"))),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({key: str(value) for key, value in result.__dict__.items()}), 200
