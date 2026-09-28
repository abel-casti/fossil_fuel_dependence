SELECT
    country_code,
    timestamp::date AS date,
    ROUND(SUM(load), 2) AS load
FROM
    {{ref("stg_load_log")}}
GROUP BY
    country_code,
    timestamp::date