from airbnb_ops.dashboard_routes import command_center


def test_command_center_route_returns_json():
    response = command_center()
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["occupancy_percent"] == "0"
    assert payload["debt_clearing_nights"] == 0
