from fastapi.testclient import TestClient

from app.main import create_app


client = TestClient(create_app())


def _create_project_payload():
    return {
        "title": "G+2 residential in Hyderabad",
        "location": "Hyderabad",
        "usage": "residential",
        "floors": 3,
        "footprint_m2": 120.0,
        "preferred_codes": ["IS 456", "IS 875"],
        "structure_types": ["RCC"],
        "soil_type": "stiff clay",
        "regional_rate": "telangana-2024",
    }


def test_full_pipeline_generates_artifacts():
    project_resp = client.post("/api/projects", json=_create_project_payload())
    assert project_resp.status_code == 201
    project = project_resp.json()
    project_id = project["id"]

    layout_resp = client.post(f"/api/projects/{project_id}/layout")
    assert layout_resp.status_code == 201
    layout = layout_resp.json()
    assert layout["rooms"]
    assert layout["efficiency"] > 0

    structure_resp = client.post(f"/api/projects/{project_id}/structure")
    assert structure_resp.status_code == 201
    structure = structure_resp.json()
    assert structure["columns"] >= 4

    estimate_resp = client.post(f"/api/projects/{project_id}/estimate")
    assert estimate_resp.status_code == 201
    estimate_project = estimate_resp.json()
    assert estimate_project["estimate"]["total"] > 0
    assert estimate_project["execution_plan"]


def test_missing_project_returns_404():
    resp = client.get("/api/projects/non-existent")
    assert resp.status_code == 404
