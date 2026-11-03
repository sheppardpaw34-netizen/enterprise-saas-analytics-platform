with source as (
    select * from {{ source('stripe', 'invoices') }}
),

cleaned as (
    select
        "id" as invoice_id,
        "object" as object ,
        "customer" as customer_id,
        "subscription" as subscription_id,
        "status" as status,
        {{ cents_to_dollars('"subtotal"') }} as subtotal_amount,
        {{ cents_to_dollars('"discount"') }} as discount_amount,
        {{ cents_to_dollars('"total"') }} as total_amount,
        {{ cents_to_dollars('"amount_paid"') }} as amount_paid,
        "currency",
        {{ epoch_to_timestamp('"created"') }} as created_at,
        {{ epoch_to_timestamp('"period_start"') }} as period_start_at,
        {{ epoch_to_timestamp('"period_end"') }} as period_end_at,
        row_number() over(
            partition by "id"
            order by "created"
        ) as row_num

    from source
    where "id" is not null
),

deduped as (
    select 
        invoice_id,
        object,
        customer_id,
        subscription_id,
        subtotal_amount,
        discount_amount,
        total_amount,
        amount_paid,
        created_at,
        period_start_at,
        period_end_at
    from cleaned
    where row_num = 1 

)

select * from deduped