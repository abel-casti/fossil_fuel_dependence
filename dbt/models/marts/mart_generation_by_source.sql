{% set stg_generation_log = ref("stg_generation_log") %}
{% set columns = adapter.get_columns_in_relation(stg_generation_log) %}
{% set metric_columns = columns | rejectattr("name", "in", ["country_code", "timestamp"]) | list %}


-- Sum generation prouced by each energy source
SELECT
    country_code,
    timestamp::date AS date,
    {% for col in metric_columns %}
        ROUND(SUM({{ col.name }}), 2) AS {{ col.name }}
    {% if not loop.last %},{% endif %}
    {% endfor %}
FROM
    {{ stg_generation_log }}
GROUP BY
    country_code,
    timestamp::date