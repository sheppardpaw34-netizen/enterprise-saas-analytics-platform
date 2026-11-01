with source as (
    select * from {{ source('stripe', 'customers') }}
),

renamed as (
    select
        "id" as customer_id,
        "object",
        {{ epoch_to_timestamp('"created"') }} as created_at,
        "email",
        "name",
        "currency",
        "discount_coupon",
        "delinquent" as is_delinquent

    from source
    where "id" is not null
)

select * from renamed