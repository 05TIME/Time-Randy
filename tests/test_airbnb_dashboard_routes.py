from app import app


def test_command_center_route_returns_json():
    client = app.test_client()
    response = client.get("/airbnb/command-center")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["occupancy_percent"] == "0"
    assert payload["debt_clearing_nights"] == 0
