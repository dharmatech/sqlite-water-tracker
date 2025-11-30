
.mode table

SELECT * FROM water_log;

SELECT * FROM water_log_full;

SELECT * FROM water_log_daily_with_weight;




WITH RECURSIVE slots(t) AS (
    SELECT :start_ts
    UNION ALL
    SELECT datetime(t, '+30 minutes')
    FROM slots
    WHERE datetime(t, '+30 minutes') <= :end_ts
)
SELECT t
FROM slots;




WITH RECURSIVE
  limits AS (
    SELECT
      datetime(min(timestamp)) AS start_ts,
      datetime(max(timestamp)) AS end_ts
    FROM water_log
  ),
  slots(t) AS (
    SELECT start_ts FROM limits
    UNION ALL
    SELECT datetime(t, '+30 minutes')
    FROM slots, limits
    WHERE datetime(t, '+30 minutes') <= end_ts
)
SELECT t
FROM slots;







WITH RECURSIVE
  limits AS (
    SELECT
      datetime(min(timestamp)) AS start_ts,
      datetime(max(timestamp)) AS end_ts
    FROM water_log
  ),
  slots(t) AS (
    SELECT start_ts FROM limits
    UNION ALL
    SELECT datetime(t, '+30 minutes')
    FROM slots, limits
    WHERE datetime(t, '+30 minutes') <= end_ts
)
SELECT
    t AS slot_time,
    (
        SELECT COALESCE(SUM(w.ounces), 0)
        FROM water_log AS w
        WHERE w.timestamp > datetime(t, '-24 hours')
          AND w.timestamp <= t
    ) AS ounces_last_24h
FROM slots
ORDER BY slot_time;



-- ----------------------------------------------------------------------

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
FROM water_log;



SELECT 
    id, 
    timestamp, 
    ounces,
    (
        SELECT weight_lbs
        FROM user_weight
        WHERE SUBSTR(timestamp, 1, 10) <= water_log.timestamp
        ORDER BY timestamp DESC
        LIMIT 1
    ) AS weight    
FROM water_log;




-- ----------------------------------------------------------------------

SELECT * FROM water_log;

-- ----------------------------------------------------------------------

DROP VIEW IF EXISTS rolling_24_hour_summary;
CREATE VIEW rolling_24_hour_summary AS
SELECT
    w1.id,
    w1.timestamp,
    w1.ounces,
    (
        SELECT SUM(w2.ounces)
        FROM water_log AS w2
        WHERE
            w2.timestamp > datetime(w1.timestamp, '-24 hours')
            AND w2.timestamp <= w1.timestamp
    ) AS rolling_24h_ounces
FROM water_log AS w1
ORDER BY w1.timestamp;

SELECT * FROM rolling_24_hour_summary;

SELECT * FROM rolling_24_hour_summary ORDER BY timestamp DESC LIMIT 10;

SELECT * FROM rolling_24_hour_summary ORDER BY timestamp LIMIT 10;