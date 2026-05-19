with source as (
    select * from {{ source('bronze', 'internal_customers') }}
),

typed as (
    select
        customer_id::text       as customer_id,
        name::text              as name,
        email::text             as email,
        city::text              as city,
        state::text             as state,
        created_at::timestamptz as created_at,
        ingestion_date::date    as ingestion_date
    from source
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by customer_id
            order by ingestion_date desc
        ) as rn
    from typed
)

select
    customer_id,
    name,
    email,
    city,
    state,
    created_at,
    ingestion_date
from deduplicated
where rn = 1
