{% set load_data = source('staging_tables', 'load_log') %}

-- Replace NULL load values with 0
SELECT
    country_code,
    timestamp,
    COALESCE("Actual Load", 0.0) AS load
FROM {{ load_data }}