{% set country_codes = ref('country_codes') %}
{% set generation_data = ref('int_generation') %}

-- Get generation by source and country
SELECT
    cc.country_name,
    g.date,
    g.ts_utc,
    g.source,
    g.generation_MW
FROM
    {{ generation_data }} g
INNER JOIN
    {{ country_codes }} cc
    ON g.country_code = cc.country_code