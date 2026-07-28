CREATE TABLE missions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    mission_type TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE recommendations (
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

INSERT INTO missions (description, mission_type, created_at)
VALUES
(
    'Monitor agricultural crops in Saudi Arabia',
    'Earth Observation',
    '2026-07-28'
),
(
    'Provide communication coverage for remote desert regions',
    'Communication',
    '2026-07-28'
),
(
    'Monitor storms and cloud movement over the Arabian Peninsula',
    'Weather Monitoring',
    '2026-07-28'
);

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
VALUES
(
    1,
    'SSO',
    600,
    'Multispectral Camera',
    1200,
    'Small Satellite',
    5,
    'Three-axis stabilized',
    'SSO provides consistent lighting conditions for agricultural monitoring.'
),
(
    2,
    'GEO',
    35786,
    'Communication Transponder',
    5000,
    'Large Satellite',
    15,
    'Three-axis stabilized',
    'GEO provides continuous coverage over the same region.'
),
(
    3,
    'GEO',
    35786,
    'Multispectral Weather Imager',
    4500,
    'Large Satellite',
    12,
    'Three-axis stabilized',
    'GEO enables continuous observation of weather systems over a wide area.'
);
SELECT
    m.id,
    m.description,
    m.mission_type,
    r.recommended_orbit,
    r.altitude_km,
    r.payload
FROM missions AS m
JOIN recommendations AS r
    ON m.id = r.mission_id;