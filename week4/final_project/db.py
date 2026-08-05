"""SQLite persistence for the Satellite Design Assistant."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


JSON_FIELDS = {
    "payload_options",
    "required_subsystems",
    "design_drivers",
    "advantages",
    "limitations",
    "selection_rules",
}


def _connect(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_database(database_path: Path, knowledge_file: Path) -> None:
    """Create the schema and seed all missing knowledge-base records."""

    database_path.parent.mkdir(parents=True, exist_ok=True)

    with _connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                mission_type TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_id INTEGER NOT NULL,
                recommended_orbit TEXT NOT NULL,
                altitude_km REAL NOT NULL,
                payload TEXT NOT NULL,
                power_watts REAL NOT NULL,
                mass_class TEXT NOT NULL,
                lifetime_years REAL NOT NULL,
                adcs_type TEXT NOT NULL,
                justification TEXT NOT NULL,
                FOREIGN KEY (mission_id)
                    REFERENCES missions(id)
                    ON DELETE CASCADE
            );

            CREATE UNIQUE INDEX IF NOT EXISTS
                idx_recommendations_mission_id
                ON recommendations(mission_id);

            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_type TEXT NOT NULL UNIQUE,
                default_orbit TEXT NOT NULL,
                minimum_altitude_km REAL,
                maximum_altitude_km REAL,
                typical_mass_class TEXT,
                typical_lifetime_years REAL,
                payload_options TEXT NOT NULL,
                required_subsystems TEXT NOT NULL,
                design_drivers TEXT NOT NULL,
                advantages TEXT NOT NULL,
                limitations TEXT NOT NULL,
                selection_rules TEXT NOT NULL
            );
            """
        )

    seed_knowledge_base(database_path, knowledge_file)


def seed_knowledge_base(database_path: Path, knowledge_file: Path) -> int:
    """Insert knowledge records that are not already in SQLite."""

    if not knowledge_file.exists():
        raise FileNotFoundError(f"Knowledge base not found: {knowledge_file}")

    with knowledge_file.open(encoding="utf-8") as source:
        knowledge_contents = json.load(source)

    inserted_count = 0

    with _connect(database_path) as connection:
        for mission_type, mission_data in knowledge_contents.items():
            cursor = connection.execute(
                """
                INSERT INTO knowledge_base (
                    mission_type,
                    default_orbit,
                    minimum_altitude_km,
                    maximum_altitude_km,
                    typical_mass_class,
                    typical_lifetime_years,
                    payload_options,
                    required_subsystems,
                    design_drivers,
                    advantages,
                    limitations,
                    selection_rules
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(mission_type) DO NOTHING
                """,
                (
                    mission_type,
                    mission_data["default_orbit"],
                    mission_data["minimum_altitude_km"],
                    mission_data["maximum_altitude_km"],
                    mission_data["typical_mass_class"],
                    mission_data["typical_lifetime_years"],
                    json.dumps(mission_data["payload_options"], ensure_ascii=False),
                    json.dumps(mission_data["required_subsystems"], ensure_ascii=False),
                    json.dumps(mission_data["design_drivers"], ensure_ascii=False),
                    json.dumps(mission_data["advantages"], ensure_ascii=False),
                    json.dumps(mission_data["limitations"], ensure_ascii=False),
                    json.dumps(mission_data["selection_rules"], ensure_ascii=False),
                ),
            )
            inserted_count += max(cursor.rowcount, 0)

    return inserted_count


def get_knowledge(database_path: Path, mission_type: str) -> dict[str, Any] | None:
    """Return engineering knowledge for one canonical mission type."""

    with _connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM knowledge_base WHERE mission_type = ?",
            (mission_type,),
        ).fetchone()

    if row is None:
        return None

    knowledge = dict(row)
    knowledge.pop("id", None)

    for field in JSON_FIELDS:
        knowledge[field] = json.loads(knowledge[field])

    return knowledge


def save_processed_mission(
    database_path: Path,
    description: str,
    recommendation: dict[str, Any],
) -> int:
    """Save a mission and its recommendation in one transaction."""

    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with _connect(database_path) as connection:
        mission_cursor = connection.execute(
            """
            INSERT INTO missions (description, mission_type, created_at)
            VALUES (?, ?, ?)
            """,
            (description, recommendation["mission_type"], created_at),
        )
        mission_id = int(mission_cursor.lastrowid)

        connection.execute(
            """
            INSERT INTO recommendations (
                mission_id,
                recommended_orbit,
                altitude_km,
                payload,
                power_watts,
                mass_class,
                lifetime_years,
                adcs_type,
                justification
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                mission_id,
                recommendation["recommended_orbit"],
                recommendation["altitude_km"],
                recommendation["payload"],
                recommendation["power_watts"],
                recommendation["mass_class"],
                recommendation["lifetime_years"],
                recommendation["adcs_type"],
                recommendation["justification"],
            ),
        )

    return mission_id


def list_missions(database_path: Path) -> list[dict[str, Any]]:
    """Return concise mission-history records, newest first."""

    with _connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT
                m.id,
                m.description,
                m.mission_type,
                m.created_at,
                r.recommended_orbit,
                r.payload
            FROM missions AS m
            JOIN recommendations AS r ON r.mission_id = m.id
            ORDER BY m.id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_mission(database_path: Path, mission_id: int) -> dict[str, Any] | None:
    """Return one mission, recommendation, and matching knowledge record."""

    with _connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT
                m.id AS mission_id,
                m.description AS mission_description,
                m.mission_type,
                m.created_at,
                r.id AS recommendation_id,
                r.recommended_orbit,
                r.altitude_km,
                r.payload,
                r.power_watts,
                r.mass_class,
                r.lifetime_years,
                r.adcs_type,
                r.justification
            FROM missions AS m
            JOIN recommendations AS r ON r.mission_id = m.id
            WHERE m.id = ?
            """,
            (mission_id,),
        ).fetchone()

    if row is None:
        return None

    record = dict(row)
    recommendation = {
        "mission_type": record["mission_type"],
        "recommended_orbit": record["recommended_orbit"],
        "altitude_km": record["altitude_km"],
        "payload": record["payload"],
        "power_watts": record["power_watts"],
        "mass_class": record["mass_class"],
        "lifetime_years": record["lifetime_years"],
        "adcs_type": record["adcs_type"],
        "justification": record["justification"],
    }

    return {
        "mission_id": record["mission_id"],
        "recommendation_id": record["recommendation_id"],
        "mission_description": record["mission_description"],
        "mission_type": record["mission_type"],
        "created_at": record["created_at"],
        "ai_recommendation": recommendation,
        "engineering_knowledge": get_knowledge(database_path, record["mission_type"]),
    }


def delete_mission(database_path: Path, mission_id: int) -> bool:
    """Delete a mission and cascade-delete its recommendation."""

    with _connect(database_path) as connection:
        cursor = connection.execute(
            "DELETE FROM missions WHERE id = ?",
            (mission_id,),
        )

    return cursor.rowcount > 0

