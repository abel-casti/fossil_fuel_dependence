{% set stg_generation = ref('stg_generation_log')%}

-- Since generation and load tables have data for the same period, we get first and last date from one of those
WITH bounds AS (
    SELECT 
        MIN(timestamp)::date AS start_date,
        MAX(timestamp)::date AS end_date
    FROM 
        {{ stg_generation }}
),
date_spine AS (
    SELECT 
        generate_series(
            (SELECT start_date FROM bounds),
            (SELECT end_date FROM bounds),
            interval '1 day'
        )::date AS date_day
)
SELECT 
    date_day
FROM 
    date_spine