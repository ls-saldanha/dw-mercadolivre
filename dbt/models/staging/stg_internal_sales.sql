with source as (
    select * from {{ source('bronze', 'internal_sales') }}
),

typed as (
    select
        order_id::text                              as order_id,
        customer_id::text                           as customer_id,
        product_id::text                            as product_id,
        quantity::integer                           as quantity,
        unit_price_brl::numeric(10, 2)              as unit_price_brl,
        total_price_brl::numeric(10, 2)             as total_amount,
        ordered_at::timestamptz                     as ordered_at,
        ingestion_date::date                        as ingestion_date
    from source
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by order_id
            order by ingestion_date desc
        ) as rn
    from typed
)

select
    order_id,
    customer_id,
    product_id,
    quantity,
    unit_price_brl,
    total_amount,
    ordered_at,
    ingestion_date
from deduplicated
where rn = 1
