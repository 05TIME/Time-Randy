import os

import pytest

from app import app


def test_timeoe_requires_command_fields():
    client = app.test_client()
    response = client.post("/timeoe/commands", json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "objective and business_id are required"


def test_timeoe_routes_registered():
    routes = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/timeoe/commands" in routes
    assert "/timeoe/events" in routes
