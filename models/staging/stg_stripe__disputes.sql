with source as (
    select * from {{ source('stripe', 'disputes') }}
),

renamed as (
    select
        "id" as dispute_id,
        "charge" as charge_id,
        "status",
        "reason",
        {{ cents_to_dollars('"amount"') }} as amount,
        {{ epoch_to_timestamp('"created"') }} as created_at

    from source
    where "id" is not null
)

select * from renamed