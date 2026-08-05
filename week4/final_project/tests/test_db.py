from __future__ import annotations

import sqlite3

from ai_api import MISSION_TYPES
from db import get_knowledge


def test_database_is_seeded_with_all_mission_types(app):
    database_path = app.config["TEST_DATABASE_PATH"]
    with sqlite3.connect(database_path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM knowledge_base").fetchone()[0]
    assert count == len(MISSION_TYPES) == 8


def test_knowledge_json_fields_are_decoded(app):
    knowledge = get_knowledge(
        app.config["TEST_DATABASE_PATH"],
        "Disaster Management",
    )
    assert knowledge is not None
    assert isinstance(knowledge["payload_options"], list)
    assert isinstance(knowledge["required_subsystems"], list)
    assert knowledge["mission_type"] == "Disaster Management"

