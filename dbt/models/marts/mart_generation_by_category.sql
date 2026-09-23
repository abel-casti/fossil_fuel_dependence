{% set renewable_sources = [
    'biomass', 'geothermal', 'hydro_run_of_river_and_pondage',
    'hydro_water_reservoir', 'marine', 'other_renewable',
    'solar', 'wind_offshore', 'wind_onshore'
] %}
{% set fossil_sources = [
    'fossil_brown_coal_or_lignite', 'fossil_coal_derived_gas',
    'fossil_gas', 'fossil_hard_coal', 'fossil_oil',
    'fossil_oil_shale', 'fossil_peat'
] %}
{% set ambiguous_sources = [
    'waste', 'other', 'energy_storage', 
    'hydro_pumped_storage'
] %}

-- Divide columns by energy source category
{% set stg_generation_log = ref("stg_generation_log") %}
{% set all_columns = adapter.get_columns_in_relation(stg_generation_log) %}
{% set renewable_columns = all_columns | selectattr("name", "in", renewable_sources) | list %}
{% set fossil_columns = all_columns | selectattr("name", "in", fossil_sources) | list %}
{% set ambiguous_columns = all_columns | selectattr("name", "in", ambiguous_sources | list) %}


-- Sum generation by each energy source category
WITH cte AS (
    SELECT
        country_code,
        timestamp::date AS date,
        nuclear,
        ({% for col in renewable_columns %}
            {{ col.name }}
            {% if not loop.last %}+{% endif %}
        {% endfor %}) AS renewable_sources,
        ({% for col in fossil_columns %}
            {{ col.name }}
            {% if not loop.last %}+{% endif %}
        {% endfor %}) AS fossil_sources,
        ({% for col in ambiguous_columns %}
            {{ col.name }}
            {% if not loop.last %}+{% endif %}
        {% endfor %}) AS ambiguous_sources
    FROM
        {{ stg_generation_log }}
)

SELECT
    country_code,
    date,
    ROUND(SUM(nuclear), 2) AS nuclear_sources,
    ROUND(SUM(renewable_sources), 2) AS renewable_sources,
    ROUND(SUM(fossil_sources), 2) AS fossil_sources,
    ROUND(SUM(ambiguous_sources), 2) AS ambiguous_sources
FROM
    cte
GROUP BY
    country_code,
    date