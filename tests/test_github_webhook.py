import hashlib
import hmac
import json
import sqlite3

from flask import Flask

from airbnb_ops.github_webhook import bp


def _client(monkeypatch, tmp_path):
    db = tmp_path / "airbnb_ops.sqlite3"
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "test-secret")
    monkeypatch.setenv("AIRBNB_DB_PATH", str(db))
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app.test_client(), db


def _headers(body: bytes, delivery="delivery-1", event="push"):
    digest = hmac.new(b"test-secret", body, hashlib.sha256).hexdigest()
    return {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": f"sha256={digest}",
        "X-GitHub-Delivery": delivery,
        "X-GitHub-Event": event,
    }


def test_webhook_accepts_valid_signed_delivery(monkeypatch, tmp_path):
    client, db = _client(monkeypatch, tmp_path)
    body = json.dumps({"ref": "refs/heads/main"}).encode()
    response = client.post("/webhooks/github", data=body, headers=_headers(body))
    assert response.status_code == 202

    with sqlite3.connect(db) as connection:
        row = connection.execute(
            "SELECT event_name, payload FROM github_webhook_events WHERE delivery_id = ?",
            ("delivery-1",),
        ).fetchone()
    assert row[0] == "push"
    assert json.loads(row[1])["ref"] == "refs/heads/main"


def test_webhook_rejects_bad_signature(monkeypatch, tmp_path):
    client, _ = _client(monkeypatch, tmp_path)
    body = b"{}"
    headers = _headers(body)
    headers["X-Hub-Signature-256"] = "sha256=bad"
    assert client.post("/webhooks/github", data=body, headers=headers).status_code == 401


def test_webhook_deduplicates_delivery(monkeypatch, tmp_path):
    client, db = _client(monkeypatch, tmp_path)
    body = b"{}"
    headers = _headers(body, delivery="same-delivery")
    assert client.post("/webhooks/github", data=body, headers=headers).status_code == 202
    assert client.post("/webhooks/github", data=body, headers=headers).status_code == 202

    with sqlite3.connect(db) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM github_webhook_events WHERE delivery_id = ?",
            ("same-delivery",),
        ).fetchone()[0]
    assert count == 1
