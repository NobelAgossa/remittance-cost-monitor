{#-
    Decides the BigQuery dataset of every model and seed.
    The `prod` target uses the dataset as is (staging, marts). Every other target adds
    its name as a suffix (staging_dev), so experiments never touch dashboard data.
-#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set dataset = target.schema -%}
    {%- if custom_schema_name is not none -%}
        {%- set dataset = custom_schema_name | trim -%}
    {%- endif -%}
    {%- if target.name == "prod" -%}
        {{ dataset }}
    {%- else -%}
        {{ dataset }}_{{ target.name }}
    {%- endif -%}
{%- endmacro %}
