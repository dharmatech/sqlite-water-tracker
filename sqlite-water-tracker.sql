-- database: sqlite-water-tracker.db

-- ----------------------------------------------------------------------
INSERT INTO water_log (timestamp, ounces) VALUES ('2025-07-01 06:00:00', 8.0);
INSERT INTO water_log (timestamp, ounces) VALUES ('2025-07-01 08:00:00', 8.0);
INSERT INTO water_log (timestamp, ounces) VALUES ('2025-07-01 10:00:00', 8.0);

INSERT INTO water_log (timestamp, ounces) VALUES ('2025-10-12 01:00:00', 8.0);
INSERT INTO water_log (timestamp, ounces) VALUES ('2025-10-12 05:31:00', 8.0);
INSERT INTO water_log (timestamp, ounces) VALUES ('2025-10-12 08:15:00', 8.0);
INSERT INTO water_log (timestamp, ounces) VALUES ('2025-10-12 10:06:00', 8.0);
INSERT INTO water_log (timestamp, ounces) VALUES ('2025-10-12 11:35:00', 8.0);
INSERT INTO water_log (timestamp, ounces) VALUES ('2025-10-12 19:34:00', 8.0);

INSERT INTO water_log (timestamp, ounces) VALUES ('2025-10-13 12:59:00', 8.0);
INSERT INTO water_log (timestamp, ounces) VALUES ('2025-10-13 04:09:00', 8.0);
INSERT INTO water_log (timestamp, ounces) VALUES ('2025-10-13 05:36:00', 8.0);


UPDATE water_log SET timestamp = '2025-10-12 10:06:00' WHERE id = 4;

INSERT INTO water_log (timestamp, ounces) VALUES (datetime('now', 'localtime'), 8.0);

SELECT * FROM water_log ORDER BY timestamp;

SELECT * FROM water_log_daily;
SELECT * FROM water_log_full;

SELECT datetime('now', 'localtime');

DELETE FROM water_log WHERE id = 14;
-- ----------------------------------------------------------------------
SELECT
    SUBSTR(timestamp, 1, 10) AS consumption_date,
    SUM(ounces) AS total_daily_ounces
FROM
    water_log
GROUP BY
    consumption_date
ORDER BY
    consumption_date DESC;

-- consider : create a view for daily totals

DROP VIEW IF EXISTS daily_water_totals;

CREATE VIEW daily_water_totals AS
SELECT
    SUBSTR(timestamp, 1, 10) AS consumption_date,
    SUM(ounces) AS total_daily_ounces
FROM
    water_log
GROUP BY
    consumption_date
ORDER BY
    consumption_date;

SELECT * FROM daily_water_totals;
-- ----------------------------------------------------------------------
INSERT INTO user_weight (timestamp, weight_lbs) VALUES ('2025-06-01 00:00:00', 154.0);
INSERT INTO user_weight (timestamp, weight_lbs) VALUES ('2025-10-11 00:00:00', 173.0);
INSERT INTO user_weight (timestamp, weight_lbs) VALUES ('2025-10-12 10:15:00', 173.8);
INSERT INTO user_weight (timestamp, weight_lbs) VALUES ('2025-10-13 07:38:00', 171.0);

SELECT * FROM user_weight ORDER BY timestamp;
-- ----------------------------------------------------------------------
SELECT
    weight_lbs AS latest_weight,
    (weight_lbs / 2) AS ounces_target
FROM
    user_weight
ORDER BY
    timestamp DESC
LIMIT 1;
-- ----------------------------------------------------------------------
-- issue with this version: it only works if there's a weight entry for each day

SELECT
    SUBSTR(timestamp, 1, 10) AS consumption_date,
    SUM(ounces) AS total_daily_ounces
FROM
    water_log
JOIN user_weight
ON SUBSTR(water_log.timestamp, 1, 10) = SUBSTR(user_weight.timestamp, 1, 10)
WHERE user_weight.timestamp = (SELECT MAX(timestamp) FROM user_weight WHERE SUBSTR(timestamp, 1, 10) <= SUBSTR(water_log.timestamp, 1, 10))
GROUP BY
    consumption_date
ORDER BY
    consumption_date DESC;


SELECT *
FROM water_log
JOIN user_weight;



SELECT
    SUBSTR(water_log.timestamp, 1, 10) AS consumption_date,
    SUM(ounces) AS total_daily_ounces,
    user_weight.weight_lbs,
    (user_weight.weight_lbs / 2) AS ounces_target,
    ROUND((SUM(ounces) / (user_weight.weight_lbs / 2)) * 100, 2) AS percent_of_target
FROM water_log
JOIN user_weight
ON SUBSTR(water_log.timestamp, 1, 10) = SUBSTR(user_weight.timestamp, 1, 10)
GROUP BY
    consumption_date
ORDER BY
    consumption_date DESC;




SELECT
    SUBSTR(water_log.timestamp, 1, 10) AS consumption_date,
    SUM(ounces) AS total_daily_ounces,
    user_weight.weight_lbs,
    (user_weight.weight_lbs / 2) AS ounces_target,
    ROUND((SUM(ounces) / (user_weight.weight_lbs / 2)) * 100, 2) AS percent_of_target
FROM water_log
JOIN user_weight
ON SUBSTR(water_log.timestamp, 1, 10) = SUBSTR(user_weight.timestamp, 1, 10)
WHERE
    user_weight.timestamp = (
        SELECT MAX(timestamp) 
        FROM user_weight 
        WHERE SUBSTR(timestamp, 1, 10) <= SUBSTR(water_log.timestamp, 1, 10)
    )
GROUP BY
    consumption_date
ORDER BY
    consumption_date DESC;

-- WHERE user_weight.timestamp = (SELECT MAX(timestamp) FROM user_weight WHERE SUBSTR(timestamp, 1, 10) <= SUBSTR(water_log.timestamp, 1, 10))

-- ----------------------------------------------------------------------

-- version that uses corellated subquery

SELECT * FROM user_weight WHERE SUBSTR(user_weight.timestamp, 1, 10) <= '2025-10-12' ORDER BY user_weight.timestamp DESC LIMIT 1;

SELECT * FROM user_weight WHERE SUBSTR(user_weight.timestamp, 1, 10) <= '2025-11-12' ORDER BY user_weight.timestamp DESC LIMIT 1;

SELECT
    SUBSTR(water_log.timestamp, 1, 10) AS date,
    SUM(ounces) AS total,
    (
        SELECT weight_lbs
        FROM user_weight 
        WHERE SUBSTR(user_weight.timestamp, 1, 10) <= SUBSTR(water_log.timestamp, 1, 10)
        ORDER BY user_weight.timestamp DESC
        LIMIT 1
    ) AS weight,
    (
        SELECT weight_lbs / 2 
        FROM user_weight 
        WHERE SUBSTR(user_weight.timestamp, 1, 10) <= SUBSTR(water_log.timestamp, 1, 10)
        ORDER BY user_weight.timestamp DESC
        LIMIT 1
    ) AS target,
    (
        SELECT ROUND(SUM(ounces) / (weight_lbs / 2) * 100, 2)
        FROM user_weight 
        WHERE SUBSTR(user_weight.timestamp, 1, 10) <= SUBSTR(water_log.timestamp, 1, 10)
        ORDER BY user_weight.timestamp DESC
        LIMIT 1
    ) AS percent_of_target
FROM water_log
GROUP BY date;

-- Downside to this approach:
-- We'll need a relatively large corellated subquery for each of `target`, `weight`, and `percent_of_target`.
-- -----------------------------------------------------------------------
-- version from gemini:

SELECT
    T1.consumption_date,
    T1.total_daily_ounces,

    (
        SELECT weight_lbs
        FROM user_weight
        WHERE SUBSTR(timestamp, 1, 10) <= T1.consumption_date 
        ORDER BY timestamp DESC
        LIMIT 1
    ) AS weight_lbs_as_of_day,

    (
        SELECT weight_lbs / 2
        FROM user_weight
        WHERE SUBSTR(timestamp, 1, 10) <= T1.consumption_date
        ORDER BY timestamp DESC
        LIMIT 1
    ) AS ounces_target_as_of_day

FROM
    (
        -- T1: Your original query results (Daily Consumption Totals)
        SELECT
            SUBSTR(timestamp, 1, 10) AS consumption_date,
            SUM(ounces_consumed) AS total_daily_ounces
        FROM
            water_log
        GROUP BY
            consumption_date
    ) AS T1
ORDER BY
    T1.consumption_date DESC;







SELECT date, total,

    (
        SELECT weight_lbs
        FROM user_weight
        WHERE SUBSTR(timestamp, 1, 10) <= date 
        ORDER BY timestamp DESC
        LIMIT 1
    ) AS weight,

    (
        SELECT weight_lbs / 2
        FROM user_weight
        WHERE SUBSTR(timestamp, 1, 10) <= date
        ORDER BY timestamp DESC
        LIMIT 1
    ) AS target

FROM
    (
        SELECT
            SUBSTR(timestamp, 1, 10) AS date,
            SUM(ounces) AS total
        FROM water_log
        GROUP BY date
    )
ORDER BY date DESC;



WITH tbl_1 AS (
    SELECT
        SUBSTR(timestamp, 1, 10) AS date,
        SUM(ounces) AS total
    FROM water_log
    GROUP BY date    
)
SELECT * FROM tbl_1;


WITH tbl_1 AS (
    SELECT
        SUBSTR(timestamp, 1, 10) AS date,
        SUM(ounces) AS total
    FROM water_log
    GROUP BY date    
)
SELECT
    *,
    (
        SELECT weight_lbs
        FROM user_weight
        WHERE SUBSTR(timestamp, 1, 10) <= tbl_1.date 
        ORDER BY timestamp DESC
        LIMIT 1    
    )
FROM tbl_1;



WITH tbl_1 AS (
    SELECT
        SUBSTR(timestamp, 1, 10) AS date,
        SUM(ounces) AS total
    FROM water_log
    GROUP BY date    
),

tbl_2 AS (
        SELECT weight_lbs
        FROM user_weight
        WHERE SUBSTR(timestamp, 1, 10) <= tbl_1.date 
        ORDER BY timestamp DESC
        LIMIT 1    
)
SELECT * FROM tbl_2;





-- -----------------------------------------------------------------------

SELECT * FROM water_log;

SELECT
    SUBSTR(timestamp, 1, 10) AS date,
    SUM(ounces) AS ounces
FROM water_log
GROUP BY date;



WITH daily_consumption AS (
    SELECT
        SUBSTR(timestamp, 1, 10) AS date,
        SUM(ounces) AS ounces
    FROM water_log
    GROUP BY date
),

daily_weight AS (
    SELECT daily_consumption.date
)


WITH daily_consumption AS (
    SELECT
        SUBSTR(timestamp, 1, 10) AS consumption_date,
        SUM(ounces_consumed) AS total_daily_ounces
    FROM
        water_log
    GROUP BY
        consumption_date
),

daily_weight AS (
    -- CTE 2: Factors out the complex weight-finding logic
    SELECT
        dc.consumption_date,
        (
            -- Correlated Subquery (Lateral Join Pattern)
            SELECT uw.weight_lbs
            FROM user_weight AS uw
            -- Find the most recent weight recorded on or before the consumption day
            WHERE uw.timestamp <= (dc.consumption_date || ' 23:59:59') 
            ORDER BY uw.timestamp DESC
            LIMIT 1
        ) AS weight_lbs
    FROM
        daily_consumption AS dc
)

-- Final SELECT: Uses the factored-out 'weight_lbs' column directly
SELECT
    dc.consumption_date,
    dc.total_daily_ounces,
    dw.weight_lbs AS weight_lbs_as_of_day,
    
    -- Now, the target calculation is simple: (weight / 2)
    (dw.weight_lbs / 2) AS ounces_target_as_of_day,
    
    -- And the percent calculation is also simple:
    ROUND(
        dc.total_daily_ounces * 100.0 / (dw.weight_lbs / 2)
    , 2) AS percent_of_target

FROM
    daily_consumption AS dc
JOIN
    daily_weight AS dw 
    ON dc.consumption_date = dw.consumption_date -- Join on the date key
ORDER BY
    dc.consumption_date DESC;



-- -----------------------------------------------------------------------
-- version from grok
--
-- https://x.com/i/grok?conversation=1977451552915980319

SELECT
    date,
    total,
    weight,
    weight / 2 AS target
FROM (
    SELECT
        date,
        total,
        (
            SELECT weight_lbs
            FROM user_weight
            WHERE SUBSTR(timestamp, 1, 10) <= date
            ORDER BY timestamp DESC
            LIMIT 1
        ) AS weight
    FROM (
        SELECT
            SUBSTR(timestamp, 1, 10) AS date,
            SUM(ounces) AS total
        FROM water_log
        GROUP BY date
    )
)
ORDER BY date DESC;


-- factor out the inner query as a view

SELECT
    SUBSTR(timestamp, 1, 10) AS date,
    SUM(ounces) AS total
FROM water_log
GROUP BY date;



-- query that uses the water_log_daily view

SELECT
    date,
    total,
    weight,
    weight / 2 AS target
FROM (
    SELECT
        date,
        total,
        (
            SELECT weight_lbs
            FROM user_weight
            WHERE SUBSTR(timestamp, 1, 10) <= date
            ORDER BY timestamp DESC
            LIMIT 1
        ) AS weight
    FROM water_log_daily
)
ORDER BY date DESC;



SELECT * FROM water_log_daily_with_weight;


SELECT * FROM water_log_daily_with_weight_and_target;
-- -------------------------------------------------------
-- version with percent_of_target

-- SELECT *, ROUND(total * 100.0 / target, 2) AS percent_of_target
-- FROM water_log_daily_with_weight_and_target;


SELECT * FROM water_log_full;
-- -------------------------------------------------------

SELECT * FROM water_log ORDER BY timestamp;

-- Get rows from `water_log` within the past 24 hours
SELECT * FROM water_log WHERE timestamp >= datetime('now', '-1 day', 'localtime');

SELECT SUM(ounces) FROM water_log WHERE timestamp >= datetime('now', '-1 day', 'localtime');

-- get most recent weight entry

SELECT weight_lbs FROM user_weight ORDER BY timestamp DESC LIMIT 1;

-- target

SELECT weight_lbs / 2 AS target FROM user_weight ORDER BY timestamp DESC LIMIT 1;



SELECT 
    (SELECT SUM(ounces) FROM water_log WHERE timestamp >= datetime('now', '-1 day', 'localtime')) AS total_ounces_last_24_hours,
    (SELECT weight_lbs FROM user_weight ORDER BY timestamp DESC LIMIT 1)                          AS weight,
    (SELECT weight_lbs / 2 FROM user_weight ORDER BY timestamp DESC LIMIT 1)                      AS target_ounces;


SELECT 
    (SELECT SUM(ounces) FROM water_log WHERE timestamp >= datetime('now', '-1 day', 'localtime')) AS total_ounces_last_24_hours,
    (SELECT weight_lbs FROM user_weight ORDER BY timestamp DESC LIMIT 1)                          AS weight;


SELECT
    total_ounces_last_24_hours,
    weight,
    weight / 2 AS target_ounces
FROM
(
    SELECT 
        (SELECT SUM(ounces) FROM water_log WHERE timestamp >= datetime('now', '-1 day', 'localtime')) AS total_ounces_last_24_hours,
        (SELECT weight_lbs FROM user_weight ORDER BY timestamp DESC LIMIT 1)                          AS weight
);



SELECT
    *,
    ROUND(total_ounces_last_24_hours * 100.0 / target_ounces, 2) AS percent_of_target
FROM
(
    SELECT
        *,
        weight / 2 AS target_ounces
    FROM
    (
        SELECT 
            (SELECT SUM(ounces) FROM water_log WHERE timestamp >= datetime('now', '-1 day', 'localtime')) AS total_ounces_last_24_hours,
            (SELECT weight_lbs FROM user_weight ORDER BY timestamp DESC LIMIT 1)                          AS weight
    )    
);



-- ----------------------------------------------------------------------


SELECT * FROM last_24_hours_summary;



-- ----------------------------------------------------------------------

ATTACH DATABASE 'WaterTracker-2025-10-27.db' AS other_db;

SELECT * FROM water_log ORDER BY timestamp;

SELECT COUNT(*) FROM water_log;

SELECT COUNT(*) FROM other_db.water_log;



INSERT INTO water_log (timestamp, ounces)
SELECT timestamp, ounces
FROM android_db.water_log AS source_log
WHERE NOT EXISTS (
    SELECT 1
    FROM water_log AS dest_log
    WHERE dest_log.timestamp = source_log.timestamp AND dest_log.ounces = source_log.ounces
);



-- rows to import

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

INSERT INTO water_log (timestamp, ounces)
SELECT timestamp, ounces
FROM android_db.water_log
WHERE NOT EXISTS (
    SELECT 1
    FROM water_log
    WHERE
        water_log.timestamp = android_db.water_log.timestamp AND
        water_log.ounces    = android_db.water_log.ounces
);

-- ------------------------------------------------------