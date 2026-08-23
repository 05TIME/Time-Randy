from flask import Flask

from airbnb_ops.dashboard_routes import bp


def test_command_center_uses_live_ledger_source():
    app = Flask(__name__)
    app.register_blueprint(bp)
    response = app.test_client().get("/airbnb/command-center")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["data_source"] == "sqlite-ledger"
    assert "period_start" in payload
    assert "period_end" in payload
