with source as (
    select * from {{ source('stripe', 'invoices') }}
),

renamed as (
    select
        "id" as invoice_id,
        "object",
        "customer" as customer_id,
        "subscription" as subscription_id,
        "status",
        {{ cents_to_dollars('"subtotal"') }} as subtotal_amount,
        {{ cents_to_dollars('"discount"') }} as discount_amount,
        {{ cents_to_dollars('"total"') }} as total_amount,
        {{ cents_to_dollars('"amount_paid"') }} as amount_paid,
        "currency",
        {{ epoch_to_timestamp('"created"') }} as created_at,
        {{ epoch_to_timestamp('"period_start"') }} as period_start_at,
        {{ epoch_to_timestamp('"period_end"') }} as period_end_at

    from source
    where "id" is not null
)

select * from renamed