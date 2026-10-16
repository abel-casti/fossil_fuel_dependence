{% set stg_generation_log = ref("stg_generation_log") %}



-- Unpivot table
WITH cte AS (
    SELECT
        g.country_code, 
        g."timestamp",
        s.generation_value,
        s.source
    FROM 
        {{ stg_generation_log }} g
    CROSS JOIN LATERAL (
        VALUES
            (g.biomass, 'biomass'),
            (g.fossil_brown_coal_or_lignite, 'fossil_brown_coal_or_lignite'),
            (g.fossil_coal_derived_gas, 'fossil_coal_derived_gas'),
            (g.fossil_gas, 'fossil_gas'),
            (g.fossil_hard_coal, 'fossil_hard_coal'),
            (g.fossil_oil, 'fossil_oil'),
            (g.fossil_oil_shale, 'fossil_oil_shale'),
            (g.fossil_peat, 'fossil_peat'),
            (g.geothermal, 'geothermal'),
            (g.hydro_pumped_storage, 'hydro_pumped_storage'),
            (g.hydro_run_of_river_and_pondage, 'hydro_run_of_river_and_pondage'),
            (g.hydro_water_reservoir, 'hydro_water_reservoir'),
            (g.marine, 'marine'),
            (g.nuclear, 'nuclear'),
            (g.other_renewable, 'other_renewable'),
            (g.solar, 'solar'),
            (g.waste, 'waste'),
            (g.wind_offshore, 'wind_offshore'),
            (g.wind_onshore, 'wind_onshore'),
            (g.other, 'other'),
            (g.energy_storage, 'energy_storage')
    ) AS s(generation_value, source)
)

-- Add date column for relation with dim_calendar
SELECT
    country_code,
    timestamp::date AS date,
    timestamp,
    source,
    generation_value
FROM
    cte