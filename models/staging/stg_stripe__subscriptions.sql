with source as (
    select * from {{ source('stripe', 'subscriptions') }}
),

renamed as (
    select
        "id" as subscription_id,
        "customer" as customer_id,
        "status",
        "price_id",
        "plan_nickname",
        
        {{ cents_to_dollars('"unit_amount"') }} as unit_amount,
        {{ epoch_to_timestamp('"created"') }} as created_at,
        {{ epoch_to_timestamp('"current_period_start"') }} as current_period_start_at,
        {{ epoch_to_timestamp('"current_period_end"') }} as current_period_end_at,
        
        "cancel_at_period_end"

    from source
    where "id" is not null
)

select * from renamed