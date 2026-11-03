with source as (
    select * from {{ source('stripe', 'events')}}
),

cleaned as (
    select 
        "id" as event_id,
        "customer" as customer_id,
        "type" as event_type,
        {{ epoch_to_timestamp ('"created"')}} as created_at,
        row_number() over(
            partition by "id"
            order by "created" desc
        ) as row_num
    from source
    where "id" is not null
),

deduped as (
    select 
        event_id,
        customer_id,
        event_type,
        created_at
    from cleaned 
    where row_num = 1 
)

select * from deduped