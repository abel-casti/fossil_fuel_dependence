{% set generation_data = ref('int_generation') %}

-- Get generation by source and country
SELECT
    country_code,
    date,
    ts_utc,
    REPLACE(REPLACE(source, 'fossil_', ''), '_', ' ') AS source,
    generation_MW
FROM
    {{ generation_data }}