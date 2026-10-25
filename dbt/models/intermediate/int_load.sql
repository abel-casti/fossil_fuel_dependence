-- Add date column for relation with dim_calendar
SELECT
    country_code,
    timestamp::date AS date,
    DATE_TRUNC('hour', timestamp) AS ts_utc,
    AVG(load) AS load_MW
FROM
    {{ref("stg_load_log")}}
GROUP BY
    country_code,
    timestamp::date,
    DATE_TRUNC('hour', timestamp)   