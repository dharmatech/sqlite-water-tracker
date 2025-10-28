
-- Get-Content .\import-rows-preview.sql | sqlite3 .\sqlite-water-tracker.db

ATTACH DATABASE 'WaterTracker-2025-10-27.db' AS android_db;

.mode table

SELECT * FROM water_log ORDER BY timestamp DESC LIMIT 10;

SELECT COUNT(*) FROM water_log;

SELECT timestamp, ounces
FROM android_db.water_log
WHERE NOT EXISTS (
    SELECT 1
    FROM water_log
    WHERE
        water_log.timestamp = android_db.water_log.timestamp AND 
        water_log.ounces    = android_db.water_log.ounces
)
ORDER BY timestamp;

-- perform the import

-- INSERT INTO water_log (timestamp, ounces)
-- SELECT timestamp, ounces
-- FROM android_db.water_log
-- WHERE NOT EXISTS (
--     SELECT 1
--     FROM water_log
--     WHERE
--         water_log.timestamp = android_db.water_log.timestamp AND
--         water_log.ounces    = android_db.water_log.ounces
-- );

-- ------------------------------------------------------