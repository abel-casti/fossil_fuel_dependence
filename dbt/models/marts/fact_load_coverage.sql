{% set energy_sources = ref('dim_energy_sources') %}
{% set load_data = ref('int_load') %}
{% set generation_data = ref('int_generation') %}

SELECT
    g.country_code,
    g.date,
    g.ts_utc,
    SUM(CASE WHEN s.category = 'renewable' THEN g.generation_MW ELSE 0 END) AS renewable_generation_MW,
    SUM(CASE WHEN s.category = 'fossil' THEN g.generation_MW ELSE 0 END) AS fossil_generation_MW,
    SUM(CASE WHEN s.category = 'nuclear' THEN g.generation_MW ELSE 0 END) AS nuclear_generation_MW,
    SUM(CASE WHEN s.category = 'ambiguous' THEN g.generation_MW ELSE 0 END) AS ambiguous_generation_MW,
    l.load_MW
FROM
    {{ generation_data }} g
INNER JOIN
    {{ load_data }} l
    ON g.country_code = l.country_code
    AND g.ts_utc = l.ts_utc
INNER JOIN
    {{ energy_sources }} s
    ON l.source = s.source