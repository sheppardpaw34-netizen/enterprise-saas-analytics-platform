with source as (
    select * from {{ source('stripe', 'charges') }}
),

renamed as (
    select
        "id" as charge_id,
        "customer" as customer_id,
        "invoice" as invoice_id,
        "status",
        "currency",
        {{ cents_to_dollars('"amount"') }} as amount,
        "disputed" as is_disputed,
        {{ epoch_to_timestamp('"created"') }} as created_at

    from source
    where "id" is not null
)

select * from renamed