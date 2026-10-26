{% set reference = ref('fact_load') %}

-- Get first and last hour from the reference table
WITH bounds AS (
    SELECT 
        date_trunc('hour', MIN(ts_utc)) AS start_ts,
        date_trunc('hour', MAX(ts_utc)) AS end_ts
    FROM 
        {{ reference }}
),
hour_spine AS (
    SELECT 
        generate_series(
            (SELECT start_ts FROM bounds),
            (SELECT end_ts FROM bounds),
            interval '1 hour'
        ) AS ts_utc
)
SELECT 
    ts_utc,
    ts_utc::date                            AS date_day,
    to_char(ts_utc, 'HH24:00')              AS hour_label,
    extract(year from ts_utc)::int          AS year,
    extract(month from ts_utc)::int         AS month_number,
    to_char(ts_utc, 'Mon')                  AS month_name,
    to_char(ts_utc, 'YYYY-MM')              AS year_month,
    to_char(ts_utc, 'YYYY-Mon')             AS year_month_name,
    extract(isodow from ts_utc)::int        AS day_of_week_number,
    to_char(ts_utc, 'FMDy')                 AS day_of_week_name
FROM 
    hour_spine