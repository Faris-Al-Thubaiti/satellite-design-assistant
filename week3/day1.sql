-- Week 3, Day 1
-- SQLite fundamentals

CREATE TABLE satellites (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    orbit TEXT,
    mass_kg REAL
);

SELECT * FROM satellites;

SELECT *
FROM satellites
WHERE orbit = 'GEO';

SELECT *
FROM satellites
ORDER BY mass_kg DESC;

SELECT COUNT(*) AS lightweight_satellites
FROM satellites
WHERE mass_kg < 1000;