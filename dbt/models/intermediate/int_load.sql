-- Add date column for relation with dim_calendar
SELECT
    country_code,
    timestamp::date AS date,
    timestamp,
    load
FROM
    {{ref("stg_load_log")}}