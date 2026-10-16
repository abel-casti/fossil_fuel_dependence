{% set reference = ref('fact_load_coverage')%}

-- Get first and last date from the reference table
WITH bounds AS (
    SELECT 
        MIN(timestamp)::date AS start_date,
        MAX(timestamp)::date AS end_date
    FROM 
        {{ reference }}
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
    date_day,
    extract(year from date_day)::int            as year,
    extract(month from date_day)::int           as month_number,
    to_char(date_day, 'Mon')                    as month_name,
    to_char(date_day, 'YYYY-MM')                as year_month
FROM 
    date_spine