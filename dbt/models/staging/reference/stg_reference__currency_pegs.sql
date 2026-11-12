-- Placeholder staging model, built by the sandbox smoke test (scripts/smoke_test.py).
with source as (
    select * from {{ ref('currency_pegs') }}
)

select
    currency_code,
    anchor_currency_code,
    units_per_anchor
from source
