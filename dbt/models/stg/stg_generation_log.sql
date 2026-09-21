{% set generation_data = source('staging_tables', 'generation_log') %}
{% set columns = adapter.get_columns_in_relation(generation_data) %}

-- Filter out non-generation columns for name normalization
{% set generation_columns = [] %}
{% for col in columns %}
    {% if col.name not in ['country_code', 'timestamp'] and 'consumption' not in col.name %}
        {% do generation_columns.append(col) %}
    {% endif %}
{% endfor %}

SELECT
    country_code,
    timestamp,

    -- Normalize column names and replace NULL values with 0.0 (MW)
    {% for col in generation_columns %}
        {% set clean_name = col.name.split('_actual')[0].replace('-', '_').replace('/', '_or_') %}
        COALESCE("{{ col.name }}", 0.0) AS {{ clean_name }}
        {% if not loop.last %},{% endif %}
    {% endfor %}
FROM
    {{ generation_data }}