import sqlite3
from datetime import datetime
DATABASE_PATH = "satellites.db"

def init_db():
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        connection.execute("""
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                mission_type TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        connection.execute("""
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
        """)
    print("Database initialized successfully")

def add_mission(description, mission_type):
    created_at = datetime.now().isoformat()

    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.execute(
            """
            INSERT INTO missions (
                description,
                mission_type,
                created_at
            )
            VALUES (?, ?, ?)
            """,
            (description, mission_type, created_at)
        )

        mission_id = cursor.lastrowid

    return mission_id

def add_recommendation(mission_id, rec_dict):
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

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
                rec_dict["recommended_orbit"],
                rec_dict["altitude_km"],
                rec_dict["payload"],
                rec_dict["power_watts"],
                rec_dict["mass_class"],
                rec_dict["lifetime_years"],
                rec_dict["adcs_type"],
                rec_dict["justification"]
            )
        )

        recommendation_id = cursor.lastrowid

    return recommendation_id

def get_all_missions():
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row

        cursor = connection.execute(
            """
            SELECT *
            FROM missions
            ORDER BY id
            """
        )

        rows = cursor.fetchall()

    return [dict(row) for row in rows]

def get_mission_with_recommendation(mission_id):
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row

        cursor = connection.execute(
            """
            SELECT
                m.id,
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
                ON m.id = r.mission_id
            WHERE m.id = ?
            """,
            (mission_id,)
        )

        row = cursor.fetchone()

    if row is None:
        return None

    return dict(row)

def delete_mission(mission_id):
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        cursor = connection.execute(
            """
            DELETE FROM missions
            WHERE id = ?
            """,
            (mission_id,)
        )

        deleted = cursor.rowcount > 0

    return deleted

def main():
    # init_db()
    # recommendation = {
    #     "mission_type": "Earth Observation",
    #     "recommended_orbit": "SSO",
    #     "altitude_km": 600,
    #     "payload": "Multispectral Camera",
    #     "power_watts": 1200,
    #     "mass_class": "Small Satellite",
    #     "lifetime_years": 5,
    #     "adcs_type": "Three-axis stabilized",
    #     "justification": "SSO provides consistent lighting for crop monitoring."
    # }

    # mission_id = add_mission(
    #         "Monitor agricultural crops in Saudi Arabia",
    #         recommendation["mission_type"]
    #         )

    # recommendation_id = add_recommendation(
    #     mission_id,
    #     recommendation
    #     )
    # missions = get_all_missions()

    # print("All missions:")

    # for mission in missions:
    #     print(mission)
    # print(f"Mission added with ID: {mission_id}")
    # print(f"Recommendation added with ID: {recommendation_id}")
    # mission = get_mission_with_recommendation(1)

    # if mission is None:
    #     print("Mission not found")
    # else:
    #     print("Mission with recommendation:")
    #     print(mission)
    recommendation = {
    "mission_type": "Technology Demonstration",
    "recommended_orbit": "LEO",
    "altitude_km": 500,
    "payload": "Experimental Communication Payload",
    "power_watts": 700,
    "mass_class": "Small Satellite",
    "lifetime_years": 2,
    "adcs_type": "Three-axis stabilized",
    "justification": "LEO reduces launch cost and supports technology validation."
    }

    mission_id = add_mission(
    "Test a new communication payload",
    recommendation["mission_type"]
    )

    add_recommendation(mission_id, recommendation)
    if delete_mission(mission_id):
        print("Mission deleted successfully")
    else:
        print("Mission not found")
        
    print(get_all_missions())
    
    print(get_mission_with_recommendation(1))
    

if __name__ == "__main__":
    main()