from fastapi.testclient import TestClient

from app.main import create_app


client = TestClient(create_app())


def test_health_returns_ok():
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["modules"]


def test_brief_echo():
    payload = {
        "title": "G+2 residential in Hyderabad",
        "location": "Hyderabad",
        "preferred_codes": ["IS 456", "IS 875"],
        "structure_types": ["RCC"],
        "description": "Test brief",
    }
    response = client.post("/api/briefs", json=payload)
    assert response.status_code == 201
    body = response.json()
    for key, value in payload.items():
        assert body[key] == value
