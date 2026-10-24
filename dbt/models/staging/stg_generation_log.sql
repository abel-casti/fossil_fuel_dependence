{% set generation_data = source('staging_tables', 'generation_log') %}
{% set columns = adapter.get_columns_in_relation(generation_data) %}


SELECT
    country_code,
    timestamp,

    -- Normalize column names, use numeric type and replace NULL values with 0.0 (MW)
    {% for col in columns %}
        {% if col.name not in ['country_code', 'timestamp'] %}
            {% set clean_name = col.name.replace(' ', '_').replace('-', '_').replace('/', '_or_').lower() %}
            COALESCE("{{ col.name }}", 0.0) AS {{ clean_name }}
            {% if not loop.last %},{% endif %}
        {% endif %}
    {% endfor %}
FROM
    {{ generation_data }}