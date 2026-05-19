with sales as (
    select * from {{ ref('stg_internal_sales') }}
),

products as (
    select * from {{ ref('stg_internal_products') }}
),

ptax as (
    select * from {{ ref('stg_bacen_ptax') }}
),

-- Join sales to products to bring in category
joined as (
    select
        s.order_id,
        s.ordered_at::date     as sale_date,
        p.category             as product_category,
        s.quantity,
        s.total_amount
    from sales s
    left join products p on p.product_id = s.product_id
),

-- Aggregate to one row per (sale_date, product_category)
aggregated as (
    select
        sale_date,
        product_category,
        sum(total_amount)                                           as revenue_brl,
        count(distinct order_id)                                   as order_count,
        sum(quantity)                                              as units_sold,
        sum(total_amount) / nullif(count(distinct order_id), 0)   as avg_order_value_brl
    from joined
    group by sale_date, product_category
),

-- Look up the most recent PTAX rate available on or before each sale date.
-- This handles weekends: a Saturday sale gets Friday's rate.
with_fx as (
    select
        a.*,
        (
            select bid_rate
            from ptax
            where cotacao_date <= a.sale_date
            order by cotacao_date desc
            limit 1
        ) as bid_rate
    from aggregated a
),

final as (
    select
        sale_date,
        product_category,
        revenue_brl,
        round(revenue_brl / nullif(bid_rate, 0), 2)            as revenue_usd,
        order_count,
        units_sold,
        round(avg_order_value_brl, 2)                          as avg_order_value_brl,
        round(
            sum(revenue_brl) over (
                partition by product_category
                order by sale_date
                rows between 6 preceding and current row
            ),
            2
        )                                                      as revenue_7d_rolling_brl
    from with_fx
)

select * from final
order by sale_date, product_category
