
SELECT * FROM water_log;
SELECT * FROM water_log ORDER BY timestamp DESC LIMIT 10;

SELECT * FROM user_weight;

SELECT * FROM water_log_daily;
SELECT * FROM water_log_daily ORDER BY date DESC LIMIT 10;

SELECT * FROM water_log_daily_with_weight;
SELECT * FROM water_log_daily_with_weight ORDER BY date DESC LIMIT 10;

SELECT * FROM water_log_daily_with_weight_and_target;
SELECT * FROM water_log_daily_with_weight_and_target ORDER BY date DESC LIMIT 10;

SELECT * FROM water_log_daily_with_weight_target_percent;
SELECT * FROM water_log_daily_with_weight_target_percent ORDER BY date DESC LIMIT 10;

SELECT * FROM water_log_full;
SELECT * FROM water_log_full ORDER BY date DESC LIMIT 10;

SELECT * FROM last_24_hours_summary;

SELECT * FROM rolling_24_hour_summary;
SELECT * FROM rolling_24_hour_summary ORDER BY timestamp DESC LIMIT 10;
SELECT * FROM rolling_24_hour_summary ORDER BY timestamp DESC LIMIT 20;