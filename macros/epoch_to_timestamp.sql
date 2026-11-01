{% macro epoch_to_timestamp(column_name) %}
    to_timestamp_ntz({{ column_name }})
{% endmacro %}