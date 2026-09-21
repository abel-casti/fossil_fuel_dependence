{% set load_data = source('staging_tables', 'load_log') %}

SELECT
    country_code,
    timestamp,
    actual_load AS load
FROM {{ load_data }}