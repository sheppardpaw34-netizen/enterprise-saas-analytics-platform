with source as (
    select * from {{ source('stripe', 'charges') }}
),

cleaned as (
    select
        "id" as charge_id,
        "customer" as customer_id,
        "invoice" as invoice_id,
        "status" as status,
        "currency" as currency,
        {{ cents_to_dollars('"amount"') }} as amount,
        "disputed" as is_disputed,
        {{ epoch_to_timestamp('"created"') }} as created_at,
        row_number() over(
            partition by "id"
            order by "created" desc
        ) as row_num

    from source
    where "id" is not null
),

deduped as (
    select 
        charge_id,
        customer_id,
        invoice_id,
        status,
        currency,
        amount,
        is_disputed,
        created_at
    from cleaned
    where row_num = 1 
)

select * from deduped