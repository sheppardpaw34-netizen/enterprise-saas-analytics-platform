with source as (
    select * from {{ source('stripe', 'disputes') }}
),

cleaned as (
    select
        "id" as dispute_id,
        "charge" as charge_id,
        "status" as status,
        "reason" as reason,
        {{ cents_to_dollars('"amount"') }} as amount,
        {{ epoch_to_timestamp('"created"') }} as created_at,
        row_number() over (
            partition by "id" 
            order by "created" desc
        ) as row_num

    from source
    where "id" is not null
),

deduped as (
    select 
        dispute_id,
        charge_id,
        status,
        reason,
        amount,
        created_at
    from cleaned
    where row_num = 1 
)

select * from deduped