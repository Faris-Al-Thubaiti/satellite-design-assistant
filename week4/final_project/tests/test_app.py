from __future__ import annotations

import sqlite3

import pytest

from ai_api import AIServiceError


def test_home_and_health_routes(client):
    home = client.get("/")
    assert home.status_code == 200
    assert b"Satellite Design Assistant" in home.data

    health = client.get("/health")
    assert health.status_code == 200
    assert health.get_json()["status"] == "ok"


def test_complete_analyze_and_history_flow(client, mission_description):
    response = client.post("/analyze", json={"description": mission_description})
    assert response.status_code == 201

    mission = response.get_json()
    assert mission["mission_id"] > 0
    assert mission["mission_description"] == mission_description
    assert mission["ai_recommendation"]["recommended_orbit"] == "SSO"
    assert mission["engineering_knowledge"]["mission_type"] == "Earth Observation"

    history = client.get("/missions")
    assert history.status_code == 200
    assert history.get_json()["missions"][0]["id"] == mission["mission_id"]

    detail = client.get(f"/mission/{mission['mission_id']}")
    assert detail.status_code == 200
    assert detail.get_json() == mission


@pytest.mark.parametrize(
    ("request_kwargs", "expected_message"),
    [
        ({}, "Send a JSON body"),
        ({"json": {}}, "Description must be text"),
        ({"json": {"description": "short"}}, "at least 10 characters"),
        ({"json": {"description": "x" * 2001}}, "2,000 characters or fewer"),
    ],
)
def test_invalid_analyze_requests(client, request_kwargs, expected_message):
    response = client.post("/analyze", **request_kwargs)
    assert response.status_code == 400
    assert expected_message in response.get_json()["error"]


def test_ai_failure_returns_clear_gateway_error(app, client, mission_description):
    def unavailable(_description):
        raise AIServiceError("The upstream service timed out.")

    app.config["ANALYZER"] = unavailable
    response = client.post("/analyze", json={"description": mission_description})
    assert response.status_code == 502
    assert response.get_json()["error"] == "The upstream service timed out."


def test_delete_cascades_and_missing_ids_return_404(app, client, saved_mission):
    mission_id = saved_mission["mission_id"]
    response = client.delete(f"/mission/{mission_id}")
    assert response.status_code == 200

    assert client.get(f"/mission/{mission_id}").status_code == 404
    assert client.delete(f"/mission/{mission_id}").status_code == 404

    with sqlite3.connect(app.config["TEST_DATABASE_PATH"]) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM recommendations WHERE mission_id = ?",
            (mission_id,),
        ).fetchone()[0]
    assert count == 0


def test_pdf_download_contains_a_real_pdf(client, saved_mission):
    mission_id = saved_mission["mission_id"]
    response = client.get(f"/download/{mission_id}")
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF-")
    assert len(response.data) > 2_000
    assert f"satellite-design-{mission_id}.pdf" in response.headers["Content-Disposition"]


def test_unknown_routes_return_json(client):
    response = client.get("/not-a-route")
    assert response.status_code == 404
    assert response.is_json
    assert response.get_json()["error"] == "Route not found."

