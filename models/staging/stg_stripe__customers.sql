with source as (
    select * from {{ source('stripe', 'customers') }}
),

cleaned as (
    select
        "id" as customer_id,
        "object" as object,
        {{ epoch_to_timestamp('"created"') }} as created_at,
        "email" as customer_email,
        "name" as name,
        "currency" as currency,
        "discount_coupon" as discount_coupon,
        "delinquent" as is_delinquent,
        row_number() over(
            partition by "id" 
            order by "created" desc 
        ) as row_num

    from source
    where "id" is not null
),

deduped as (
    select 
        customer_id,
        object,
        created_at,
        customer_email,
        name,
        currency,
        discount_coupon,
        is_delinquent
    from cleaned
    where row_num = 1
)

select * from deduped