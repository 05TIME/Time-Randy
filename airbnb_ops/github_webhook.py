"""GitHub webhook receiver for the TIMEŒ event queue.

The receiver verifies GitHub's HMAC signature and stores each delivery in
SQLite. It deliberately does not call external providers from the webhook
request; downstream workers can process the durable event queue.
"""

import hashlib
import hmac
import json
import os
import sqlite3
from pathlib import Path

from flask import Blueprint, Response, request

bp = Blueprint("github_webhook", __name__, url_prefix="/webhooks/github")


def _database_path() -> Path:
    return Path(os.getenv("AIRBNB_DB_PATH", "data/airbnb_ops.sqlite3"))


def _verify_signature(body: bytes, signature: str | None, secret: str) -> bool:
    if not signature or not signature.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)


def _ensure_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """CREATE TABLE IF NOT EXISTS github_webhook_events (
            delivery_id TEXT PRIMARY KEY,
            event_name TEXT NOT NULL,
            payload TEXT NOT NULL,
            received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            processed INTEGER NOT NULL DEFAULT 0
        )"""
    )
    connection.commit()


@bp.post("")
def receive_github_webhook() -> Response:
    secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    if not secret:
        return Response("webhook secret not configured", status=503)

    body = request.get_data(cache=False)
    if not _verify_signature(body, request.headers.get("X-Hub-Signature-256"), secret):
        return Response("invalid signature", status=401)

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return Response("invalid JSON", status=400)

    delivery_id = request.headers.get("X-GitHub-Delivery")
    event_name = request.headers.get("X-GitHub-Event")
    if not delivery_id or not event_name:
        return Response("missing GitHub event headers", status=400)

    database_path = _database_path()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        _ensure_table(connection)
        connection.execute(
            "INSERT OR IGNORE INTO github_webhook_events "
            "(delivery_id, event_name, payload) VALUES (?, ?, ?)",
            (delivery_id, event_name, json.dumps(payload, separators=(",", ":"))),
        )

    return Response("accepted", status=202)
