from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


# ============================================================
# Environment and project paths
# ============================================================

load_dotenv()

SCRIPT_DIR = Path(__file__).resolve().parent

# Supports:
# week3/day5/day5.py
# or:
# week3/day5.py
if SCRIPT_DIR.name.lower() == "day5":
    WEEK3_DIR = SCRIPT_DIR.parent
else:
    WEEK3_DIR = SCRIPT_DIR

DATABASE_PATH = WEEK3_DIR / "satellites.db"
KNOWLEDGE_FILE = WEEK3_DIR / "day4" / "knowledge_base.json"
DEFAULT_EXPORT_FILE = (
    WEEK3_DIR
    / "day4"
    / "knowledge_base_export.json"
)

MODEL_NAME = os.getenv(
    "OPENAI_MODEL",
    "gpt-4.1-mini"
)


# ============================================================
# Application constants
# ============================================================

MISSION_TYPES = {
    "Earth Observation",
    "Communication",
    "Navigation",
    "Weather Monitoring",
    "Remote Sensing",
    "Scientific Research",
    "Technology Demonstration",
    "Disaster Management",
}

ALLOWED_ORBITS = {
    "LEO",
    "MEO",
    "GEO",
    "SSO",
    "HEO",
}

AI_FIELDS = {
    "mission_type",
    "recommended_orbit",
    "altitude_km",
    "payload",
    "power_watts",
    "mass_class",
    "lifetime_years",
    "adcs_type",
    "justification",
}

JSON_FIELDS = {
    "payload_options",
    "required_subsystems",
    "design_drivers",
    "advantages",
    "limitations",
    "selection_rules",
}

UPDATABLE_KNOWLEDGE_FIELDS = {
    "default_orbit",
    "minimum_altitude_km",
    "maximum_altitude_km",
    "typical_mass_class",
    "typical_lifetime_years",
    *JSON_FIELDS,
}


# ============================================================
# OpenAI client
# ============================================================

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY was not found. "
        "Add it to your .env file."
    )

client = OpenAI(api_key=api_key)


# ============================================================
# AI output validation
# ============================================================

def normalize_mission_type(
    mission_type: str
) -> str | None:
    """
    Convert different capitalization styles into the
    exact mission-type name used by the knowledge base.
    """

    normalized_value = mission_type.strip().casefold()

    for valid_type in MISSION_TYPES:
        if valid_type.casefold() == normalized_value:
            return valid_type

    return None


def validate_ai_design(design: Any) -> dict[str, Any] | None:
    """
    Validate the structure and values returned by the AI.
    """

    if not isinstance(design, dict):
        print(
            "AI validation failed: "
            "the response is not a JSON object."
        )
        return None

    received_fields = set(design.keys())

    if received_fields != AI_FIELDS:
        missing_fields = AI_FIELDS - received_fields
        extra_fields = received_fields - AI_FIELDS

        if missing_fields:
            print(
                "AI validation failed. Missing fields:",
                sorted(missing_fields)
            )

        if extra_fields:
            print(
                "AI validation failed. Unexpected fields:",
                sorted(extra_fields)
            )

        return None

    canonical_mission_type = normalize_mission_type(
        str(design["mission_type"])
    )

    if canonical_mission_type is None:
        print(
            "AI validation failed: unsupported mission type:",
            design["mission_type"]
        )
        return None

    recommended_orbit = str(
        design["recommended_orbit"]
    ).strip().upper()

    if recommended_orbit not in ALLOWED_ORBITS:
        print(
            "AI validation failed: unsupported orbit:",
            design["recommended_orbit"]
        )
        return None

    numeric_fields = (
        "altitude_km",
        "power_watts",
        "lifetime_years",
    )

    for field in numeric_fields:
        value = design[field]

        # Boolean values are technically integers in Python,
        # so they must be rejected separately.
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
        ):
            print(
                f"AI validation failed: "
                f"{field} must be numeric."
            )
            return None

        if value < 0:
            print(
                f"AI validation failed: "
                f"{field} cannot be negative."
            )
            return None

    text_fields = (
        "payload",
        "mass_class",
        "adcs_type",
        "justification",
    )

    for field in text_fields:
        value = design[field]

        if (
            not isinstance(value, str)
            or not value.strip()
        ):
            print(
                f"AI validation failed: "
                f"{field} must contain text."
            )
            return None

    validated_design = dict(design)

    validated_design["mission_type"] = canonical_mission_type
        
    validated_design["recommended_orbit"] = recommended_orbit

    return validated_design


# ============================================================
# AI mission analysis
# ============================================================

def analyze_mission(
    mission_description: str
) -> dict[str, Any] | None:
    """
    Analyze a mission description and return a validated
    conceptual satellite design.
    """

    instructions = """
You are a satellite systems engineer.

Analyze the provided mission description and create a
conceptual satellite design.

Return ONLY one valid JSON object.

Do not include:
- Markdown
- Comments
- Explanations outside the JSON object
- Additional fields

The JSON object must contain exactly these fields:

{
    "mission_type": "",
    "recommended_orbit": "",
    "altitude_km": 0,
    "payload": "",
    "power_watts": 0,
    "mass_class": "",
    "lifetime_years": 0,
    "adcs_type": "",
    "justification": ""
}

Rules:

- mission_type must be exactly one of:
  Earth Observation,
  Communication,
  Navigation,
  Weather Monitoring,
  Remote Sensing,
  Scientific Research,
  Technology Demonstration,
  Disaster Management.

- recommended_orbit must be exactly one of:
  LEO, MEO, GEO, SSO, HEO.

- altitude_km must be a number.
- power_watts must be a number.
- lifetime_years must be a number.
- Put all engineering reasoning inside justification only.
"""

    try:
        response = client.responses.create(
            model=MODEL_NAME,
            instructions=instructions,
            input=mission_description
        )
        response_text = response.output_text
        if not response_text.strip():
            print(
                "AI analysis failed: "
                "the response was empty."
            )
            return None

        raw_design = json.loads(response_text)

        return validate_ai_design(raw_design)

    except json.JSONDecodeError:
        print(
            "AI analysis failed: "
            "the response was not valid JSON."
        )
        return None

    except OpenAIError as error:
        print(
            f"AI request failed: {error}"
        )
        return None

    except Exception as error:
        print(
            f"Unexpected AI error: {error}"
        )
        return None


# ============================================================
# Database initialization
# ============================================================

def init_database() -> None:
    """
    Create the missions, recommendations, and knowledge-base
    tables if they do not already exist.
    """

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                mission_type TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
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
            )
            """
        )

        connection.execute(
            """
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
            )
            """
        )

    print(
        "Database tables initialized successfully."
    )


# ============================================================
# Knowledge-base seeding
# ============================================================

def seed_knowledge_base() -> int:
    """
    Insert missing mission types from the original JSON seed.

    Existing database records are not overwritten.
    """

    if not KNOWLEDGE_FILE.exists():
        raise FileNotFoundError(
            "Knowledge file was not found:\n"
            f"{KNOWLEDGE_FILE}"
        )

    with KNOWLEDGE_FILE.open("r",encoding="utf-8") as file:
        
        knowledge_contents = json.load(file)

    inserted_count = 0

    with sqlite3.connect(DATABASE_PATH) as connection:
        for (
            mission_type,
            mission_data
        ) in knowledge_contents.items():

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
                    mission_data[
                        "minimum_altitude_km"
                    ],
                    mission_data[
                        "maximum_altitude_km"
                    ],
                    mission_data[
                        "typical_mass_class"
                    ],
                    mission_data[
                        "typical_lifetime_years"
                    ],
                    json.dumps(
                        mission_data[
                            "payload_options"
                        ],
                        ensure_ascii=False
                    ),
                    json.dumps(
                        mission_data[
                            "required_subsystems"
                        ],
                        ensure_ascii=False
                    ),
                    json.dumps(
                        mission_data[
                            "design_drivers"
                        ],
                        ensure_ascii=False
                    ),
                    json.dumps(
                        mission_data["advantages"],
                        ensure_ascii=False
                    ),
                    json.dumps(
                        mission_data["limitations"],
                        ensure_ascii=False
                    ),
                    json.dumps(
                        mission_data[
                            "selection_rules"
                        ],
                        ensure_ascii=False
                    ),
                )
            )

            if cursor.rowcount > 0:
                inserted_count += 1

    print(
        "Knowledge-base seed check completed: "
        f"{inserted_count} new mission type(s) added."
    )

    return inserted_count


# ============================================================
# Knowledge-base retrieval
# ============================================================

def get_knowledge(
    mission_type: str
) -> dict[str, Any] | None:
    """
    Retrieve one knowledge-base record and convert its JSON
    fields back into Python lists and dictionaries.
    """

    canonical_mission_type = normalize_mission_type(
        mission_type
    )

    if canonical_mission_type is None:
        return None

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row

        row = connection.execute(
            """
            SELECT *
            FROM knowledge_base
            WHERE mission_type = ?
            """,
            (canonical_mission_type,)
        ).fetchone()

    if row is None:
        return None

    knowledge = dict(row)

    for field in JSON_FIELDS:
        knowledge[field] = json.loads(
            knowledge[field]
        )

    return knowledge


# ============================================================
# Knowledge-base update
# ============================================================

def update_knowledge(
    mission_type: str,
    field: str,
    new_value: Any
) -> bool:
    """
    Safely update one approved knowledge-base field.
    """

    if field not in UPDATABLE_KNOWLEDGE_FIELDS:
        print(
            f"Update rejected: "
            f"field '{field}' is not allowed."
        )
        return False

    canonical_mission_type = normalize_mission_type(
        mission_type
    )

    if canonical_mission_type is None:
        print(
            f"Update failed: unknown mission type "
            f"'{mission_type}'."
        )
        return False

    database_value = new_value

    if field in JSON_FIELDS:
        database_value = json.dumps(
            new_value,
            ensure_ascii=False
        )

    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.execute(
            f"""
            UPDATE knowledge_base
            SET {field} = ?
            WHERE mission_type = ?
            """,
            (
                database_value,
                canonical_mission_type
            )
        )

    return cursor.rowcount > 0


# ============================================================
# Knowledge-base export
# ============================================================

def export_knowledge_base(
    output_file: Path = DEFAULT_EXPORT_FILE
) -> Path:
    """
    Export the current live SQLite knowledge into JSON.

    This is a maintenance operation and is not called during
    normal mission processing.
    """

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT *
            FROM knowledge_base
            ORDER BY id
            """
        ).fetchall()

    exported_knowledge = {}

    for row in rows:
        knowledge = dict(row)

        mission_type = knowledge.pop(
            "mission_type"
        )

        # The SQLite ID is not needed in the JSON export.
        knowledge.pop("id", None)

        for field in JSON_FIELDS:
            knowledge[field] = json.loads(
                knowledge[field]
            )

        exported_knowledge[mission_type] = knowledge

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_file.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            exported_knowledge,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        "Knowledge base exported successfully to:\n"
        f"{output_file}"
    )

    return output_file


# ============================================================
# Mission storage
# ============================================================

def add_mission(
    connection: sqlite3.Connection,
    description: str,
    mission_type: str
) -> int:
    """
    Insert the user's mission request.

    The connection is provided by process_mission() so both
    database inserts use one transaction.
    """

    created_at = datetime.now().isoformat(
        timespec="seconds"
    )

    cursor = connection.execute(
        """
        INSERT INTO missions (
            description,
            mission_type,
            created_at
        )
        VALUES (?, ?, ?)
        """,
        (
            description,
            mission_type,
            created_at
        )
    )

    return int(cursor.lastrowid)


# ============================================================
# Recommendation storage
# ============================================================

def add_recommendation(
    connection: sqlite3.Connection,
    mission_id: int,
    recommendation: dict[str, Any]
) -> int:
    """
    Insert the validated AI recommendation.
    """

    cursor = connection.execute(
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
            recommendation[
                "recommended_orbit"
            ],
            recommendation["altitude_km"],
            recommendation["payload"],
            recommendation["power_watts"],
            recommendation["mass_class"],
            recommendation["lifetime_years"],
            recommendation["adcs_type"],
            recommendation["justification"]
        )
    )

    return int(cursor.lastrowid)


# ============================================================
# Retrieve saved mission
# ============================================================

def get_recommendation(
    mission_id: int
) -> dict[str, Any] | None:
    """
    Retrieve one saved mission with its AI recommendation.
    """

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        row = connection.execute(
            """
            SELECT
                m.id AS mission_id,
                m.description,
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

            LEFT JOIN recommendations AS r
                ON r.mission_id = m.id

            WHERE m.id = ?
            """,
            (mission_id,)
        ).fetchone()

    if row is None:
        return None

    return dict(row)


# ============================================================
# Day 5 processing unit
# ============================================================

def process_mission(
    mission_description: str
) -> dict[str, Any] | None:
    """
    Full Day 5 pipeline:

    1. Validate the user's mission description.
    2. Ask the AI for a conceptual design.
    3. Validate the AI response.
    4. Retrieve matching engineering knowledge.
    5. Save the mission.
    6. Save the recommendation.
    7. Return one complete result.
    """

    clean_description = mission_description.strip()

    if not clean_description:
        print(
            "Mission processing failed: "
            "the description cannot be empty."
        )
        return None

    recommendation = analyze_mission(
        clean_description
    )

    if recommendation is None:
        return None

    mission_type = recommendation["mission_type"]

    engineering_knowledge = get_knowledge(
        mission_type
    )

    if engineering_knowledge is None:
        print(
            "Mission processing failed: "
            "no engineering knowledge was found for "
            f"'{mission_type}'."
        )
        return None

    try:
        # Both inserts use one transaction.
        #
        # If add_recommendation() fails after add_mission(),
        # SQLite rolls the complete transaction back.
        with sqlite3.connect(
            DATABASE_PATH
        ) as connection:

            connection.execute(
                "PRAGMA foreign_keys = ON"
            )

            mission_id = add_mission(
                connection,
                clean_description,
                mission_type
            )

            recommendation_id = add_recommendation(
                connection,
                mission_id,
                recommendation
            )

    except sqlite3.Error as error:
        print(
            f"Database save failed: {error}"
        )
        return None

    return {
        "mission_id": mission_id,
        "recommendation_id": recommendation_id,
        "mission_description": clean_description,
        "ai_recommendation": recommendation,
        "engineering_knowledge": engineering_knowledge
    }


# ============================================================
# Program entry point
# ============================================================

def main() -> None:
    print(
        "Satellite Design Assistant"
    )

    print(
        f"Database: {DATABASE_PATH}"
    )

    print(
        f"AI model: {MODEL_NAME}"
    )

    init_database()
    seed_knowledge_base()

    mission_description = input(
        "\nDescribe the satellite mission:\n> "
    )

    result = process_mission(
        mission_description
    )

    if result is None:
        print(
            "\nMission was not processed."
        )
        return

    print(
        "\nMission processed and saved successfully."
    )

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )

if __name__ == "__main__":
    main()