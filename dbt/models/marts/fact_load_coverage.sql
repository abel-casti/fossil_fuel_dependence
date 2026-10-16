{% set energy_sources = ref('dim_energy_sources') %}
{% set country_codes = ref('dim_country_codes') %}
{% set load_data = ref('int_load') %}
{% set generation_data = ref('int_generation') %}

-- Get total generation by category and total load. This will be used to calculate the load coverage ratio
WITH generation_aggregated AS (
    SELECT
        g.country_code,
        g.date,
        g.ts_utc,
        SUM(CASE WHEN s.category = 'renewable' THEN g.generation_MW ELSE 0 END) AS renewable_generation_MW,
        SUM(CASE WHEN s.category = 'fossil' THEN g.generation_MW ELSE 0 END) AS fossil_generation_MW,
        SUM(CASE WHEN s.category = 'nuclear' THEN g.generation_MW ELSE 0 END) AS nuclear_generation_MW,
        SUM(CASE WHEN s.category = 'ambiguous' THEN g.generation_MW ELSE 0 END) AS ambiguous_generation_MW
    FROM
        {{ generation_data }} g
    INNER JOIN
        {{ energy_sources }} s
        ON g.source = s.source
    GROUP BY
        g.country_code,
        g.date,
        g.ts_utc
)
SELECT
    cc.country_name,
    g.date,
    g.ts_utc,
    g.renewable_generation_MW,
    g.fossil_generation_MW,
    g.nuclear_generation_MW,
    g.ambiguous_generation_MW,
    l.load_MW
FROM
    generation_aggregated g
INNER JOIN
    {{ country_codes }} cc
    ON g.country_code = cc.country_code
INNER JOIN
    {{ load_data }} l
    ON g.country_code = l.country_code 
    AND g.ts_utc = l.ts_utc