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

{{ config(materialized='table') }}

SELECT 
    source, 
    'renewable' AS category 
FROM (
    {% for src in renewable_sources %}
        SELECT '{{ src }}' AS source{% if not loop.last %} UNION ALL {% endif %}
    {% endfor %}
) AS renewable_sources

UNION ALL

SELECT 
    source, 
    'fossil' AS category 
FROM (
    {% for src in fossil_sources %}
        SELECT '{{ src }}' AS source{% if not loop.last %} UNION ALL {% endif %}
    {% endfor %}
) AS fossil_sources

UNION ALL

SELECT 
    source, 
    'ambiguous' AS category 
FROM (
    {% for src in ambiguous_sources %}
        SELECT '{{ src }}' AS source{% if not loop.last %} UNION ALL {% endif %}
    {% endfor %}
) AS ambiguous_sources