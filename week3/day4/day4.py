import json
import sqlite3

DATABASE_PATH = "satellites.db"
KNOWLEDGE_FILE = "day4/knowledge_base.json"

def init_knowledge_table():
    with sqlite3.connect(DATABASE_PATH) as connection:
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

    print("Knowledge base table initialized successfully")

def seed_knowledge_base():
    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        knowledge_contents = json.load(file)

    with sqlite3.connect(DATABASE_PATH) as connection:
        for mission_type, mission_data in knowledge_contents.items():
            connection.execute(
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
                    json.dumps(mission_data["selection_rules"], ensure_ascii=False)
                )
            )

    print("Knowledge base seed check completed")

def get_knowledge(mission_type):
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row

        cursor = connection.execute(
            """
            SELECT *
            FROM knowledge_base
            WHERE mission_type = ?
            """,
            (mission_type,)
        )

        row = cursor.fetchone()

    if row is None:
        return None

    knowledge = dict(row)

    # Convert JSON text back into Python objects
    knowledge["payload_options"] = json.loads(
        knowledge["payload_options"]
    )

    knowledge["required_subsystems"] = json.loads(
        knowledge["required_subsystems"]
    )

    knowledge["design_drivers"] = json.loads(
        knowledge["design_drivers"]
    )

    knowledge["advantages"] = json.loads(
        knowledge["advantages"]
    )

    knowledge["limitations"] = json.loads(
        knowledge["limitations"]
    )

    knowledge["selection_rules"] = json.loads(
        knowledge["selection_rules"]
    )

    return knowledge

def update_knowledge(mission_type, field, new_value):
    allowed_fields = {
        "default_orbit",
        "minimum_altitude_km",
        "maximum_altitude_km",
        "typical_mass_class",
        "typical_lifetime_years",
        "payload_options",
        "required_subsystems",
        "design_drivers",
        "advantages",
        "limitations",
        "selection_rules"
    }

    if field not in allowed_fields:
        return False

    with sqlite3.connect(DATABASE_PATH) as connection:

        cursor = connection.execute(
            f"""
            UPDATE knowledge_base
            SET {field} = ?
            WHERE mission_type = ?
            """,
            (
                new_value,
                mission_type
            )
        )

    return cursor.rowcount > 0

def export_knowledge_base(
    output_file="day4/knowledge_base_export.json"
):
    json_fields = {
        "payload_options",
        "required_subsystems",
        "design_drivers",
        "advantages",
        "limitations",
        "selection_rules"
    }

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
        mission_type = knowledge.pop("mission_type")

        # Database-specific ID is not needed in the JSON knowledge file.
        knowledge.pop("id", None)

        for field in json_fields:
            knowledge[field] = json.loads(knowledge[field])

        exported_knowledge[mission_type] = knowledge

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            exported_knowledge,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"Knowledge base exported successfully to {output_file}"
    )

def main():

    init_knowledge_table()
    seed_knowledge_base()
    export_knowledge_base()
    



if __name__ == "__main__":
    main()