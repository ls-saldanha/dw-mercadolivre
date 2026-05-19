-- Singular test: fails if any row has negative revenue.
-- Negative revenue means a join or calculation error in mart_sales.
select *
from {{ ref('mart_sales') }}
where revenue_brl < 0
