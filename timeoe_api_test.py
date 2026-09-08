import timeoe_api
from app import app


class FakeQuery:
    def __init__(self, data):
        self.data = data

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def order(self, *_args, **_kwargs):
        return self

    def single(self):
        return self

    def in_(self, *_args, **_kwargs):
        return self

    def insert(self, *_args, **_kwargs):
        return self

    def execute(self):
        return self


class FakeSupabase:
    def __init__(self, data=None):
        self.data = data or []

    def table(self, name):
        if name == "businesses":
            return FakeQuery(self.data)
        return FakeQuery([])


def test_timeoe_requires_authentication():
    client = app.test_client()
    response = client.post("/timeoe/commands", json={})
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"].startswith("Bearer")


def test_timeoe_requires_command_fields(monkeypatch):
    monkeypatch.setattr(timeoe_api, "authenticate_request", lambda: "user-1")
    client = app.test_client()
    response = client.post(
        "/timeoe/commands",
        json={},
        headers={"Authorization": "Bearer test"},
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "objective and business_id are required"


def test_timeoe_routes_registered():
    routes = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/timeoe/commands" in routes
    assert "/timeoe/events" in routes


def test_events_requires_business_scope(monkeypatch):
    monkeypatch.setattr(timeoe_api, "authenticate_request", lambda: "user-1")
    client = app.test_client()
    response = client.get(
        "/timeoe/events",
        headers={"Authorization": "Bearer test"},
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "business_id is required"
