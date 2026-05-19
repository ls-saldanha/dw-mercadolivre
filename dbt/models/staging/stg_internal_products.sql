with source as (
    select * from {{ source('bronze', 'internal_products') }}
),

typed as (
    select
        product_id::text            as product_id,
        name::text                  as name,
        category::text              as category,
        unit_price_brl::numeric(10, 2) as unit_price_brl,
        ingestion_date::date        as ingestion_date
    from source
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by product_id
            order by ingestion_date desc
        ) as rn
    from typed
),

unique_products as (
    select
        product_id,
        name,
        category,
        unit_price_brl,
        ingestion_date
    from deduplicated
    where rn = 1
),

with_price_tier as (
    select
        *,
        case ntile(3) over (order by unit_price_brl)
            when 1 then 'cheap'
            when 2 then 'mid'
            when 3 then 'premium'
        end as price_tier
    from unique_products
)

select
    product_id,
    name,
    category,
    unit_price_brl,
    price_tier,
    ingestion_date
from with_price_tier
