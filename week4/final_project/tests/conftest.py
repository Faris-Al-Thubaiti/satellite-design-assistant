from __future__ import annotations

import sys
from pathlib import Path

import pytest


PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from app import create_app


@pytest.fixture
def recommendation():
    return {
        "mission_type": "Earth Observation",
        "recommended_orbit": "SSO",
        "altitude_km": 600,
        "payload": "Multispectral camera",
        "power_watts": 750,
        "mass_class": "Small Satellite",
        "lifetime_years": 5,
        "adcs_type": "Three-axis stabilized with reaction wheels",
        "justification": "SSO provides repeatable lighting for comparable imagery.",
    }


@pytest.fixture
def app(tmp_path, recommendation):
    database_path = tmp_path / "test-satellite.db"

    def analyzer(_description):
        return dict(recommendation)

    application = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": database_path,
            "KNOWLEDGE_BASE_PATH": PROJECT_DIR / "knowledge_base.json",
            "ANALYZER": analyzer,
        }
    )
    application.config["TEST_DATABASE_PATH"] = database_path
    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mission_description():
    return "Monitor agricultural vegetation health across Taif every five days."


@pytest.fixture
def saved_mission(client, mission_description):
    response = client.post("/analyze", json={"description": mission_description})
    assert response.status_code == 201
    return response.get_json()

