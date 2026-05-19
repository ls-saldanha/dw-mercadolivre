with source as (
    select * from {{ source('bronze', 'bacen_ptax') }}
),

typed as (
    select
        cotacao_date::date          as cotacao_date,
        bid_rate::numeric(10, 4)    as bid_rate,
        ask_rate::numeric(10, 4)    as ask_rate,
        source_timestamp::text      as source_timestamp,
        ingestion_date::date        as ingestion_date
    from source
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by cotacao_date
            order by ingestion_date desc
        ) as rn
    from typed
)

select
    cotacao_date,
    bid_rate,
    ask_rate,
    source_timestamp,
    ingestion_date
from deduplicated
where rn = 1
