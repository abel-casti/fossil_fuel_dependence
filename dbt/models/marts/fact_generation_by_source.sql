{% set generation_data = ref('int_generation') %}

-- Get generation by source and country
SELECT
    g.country_code,
    g.date,
    g.ts_utc,
    g.source,
    g.generation_MW
FROM
    {{ generation_data }} g