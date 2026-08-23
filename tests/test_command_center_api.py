from app import app


def test_command_center_api_returns_airbnb_escalation():
    client = app.test_client()
    response = client.post(
        "/chief-of-staff/command-center",
        json={
            "airbnb": {
                "occupancy_rate": "0.80",
                "available_nights": 10,
                "booked_nights": 8,
                "outstanding_obligation": "900000",
            }
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["total"] == 1
    assert body["escalations"][0]["unit"] == "airbnb"
