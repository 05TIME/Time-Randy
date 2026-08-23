from flask import Flask

from airbnb_ops.dashboard_routes import bp


def test_command_center_exposes_decisions_collection():
    app = Flask(__name__)
    app.register_blueprint(bp)
    response = app.test_client().get("/airbnb/command-center")
    assert response.status_code == 200
    payload = response.get_json()
    assert isinstance(payload["approvals"], list)
    assert isinstance(payload["decisions"], list)
