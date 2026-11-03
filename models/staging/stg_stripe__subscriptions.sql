with source as (
    select * from {{ source('stripe', 'subscriptions') }}
),

cleaned as (
    select
        "id" as subscription_id,
        "customer" as customer_id,
        "status" as status,
        "price_id" as price_id,
        "plan_nickname" as plan_nickname,
        {{ cents_to_dollars('"unit_amount"') }} as unit_amount,
        {{ epoch_to_timestamp('"created"') }} as created_at,
        {{ epoch_to_timestamp('"current_period_start"') }} as current_period_start,
        {{ epoch_to_timestamp('"current_period_end"') }} as current_period_end,
        "cancel_at_period_end" as cancel_at_period_end,
        row_number() over (
            partition by "id" 
            order by "created" desc
        ) as row_num
    from source
    where "id" is not null
),

deduped as (
    select
        subscription_id,
        customer_id,
        status,
        price_id,
        plan_nickname,
        unit_amount,
        created_at,
        current_period_start,
        current_period_end,
        cancel_at_period_end
    from cleaned
    where row_num = 1
)

select * from deduped