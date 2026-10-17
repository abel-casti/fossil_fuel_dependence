{% set load_data = ref('int_load') %}

SELECT
    country_code,
    date,
    ts_utc,
    load_MW
FROM
    {{ load_data }}