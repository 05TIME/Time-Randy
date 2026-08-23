"""Chief-of-Staff brief endpoint backed by SQLite."""

from datetime import date, timedelta
from flask import Blueprint, jsonify

from .chief_of_staff import build_brief
from .sqlite_store import SQLiteStore

bp = Blueprint("airbnb_brief", __name__, url_prefix="/airbnb")


@bp.get("/brief")
def daily_brief():
    today = date.today()
    end = today + timedelta(days=30)
    service = SQLiteStore().load_service()
    summary = service.summary(today, end)
    brief = build_brief(summary)
    return jsonify({
        "priority": brief.priority,
        "headline": brief.headline,
        "actions": list(brief.actions),
        "escalations": list(brief.escalations),
    })
