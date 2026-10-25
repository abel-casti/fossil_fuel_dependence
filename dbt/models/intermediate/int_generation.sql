{% set stg_generation_log = ref("stg_generation_log") %}
{% set columns = adapter.get_columns_in_relation(stg_generation_log) %}
{% set source_columns = columns | rejectattr("name", "in", ["country_code", "timestamp"]) | list %}

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
            {% for col in source_columns %}
                (g.{{ col.name }}, '{{ col.name }}')
                {% if not loop.last %},{% endif %}
            {% endfor %}
    ) AS s(generation_value, source)
)

-- Add date column for relation with dim_calendar
SELECT
    country_code,
    timestamp::date AS date,
    DATE_TRUNC('hour', timestamp) AS ts_utc,
    source,
    AVG(generation_value) AS generation_MW
FROM
    cte
GROUP BY
    country_code,
    timestamp::date,
    source,
    DATE_TRUNC('hour', timestamp)