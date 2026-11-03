with source as (
    select * from {{ source('stripe', 'invoice_line_items') }}
),

cleaned as (
    select
        "id" as line_item_id,
        "invoice" as invoice_id,
        {{ cents_to_dollars('"amount"') }} as amount,
        "description" as description,
        "type" as type,
        row_number() over (
            partition by "id" 
            order by "invoice"
        ) as row_num

    from source
    where "id" is not null
),

deduped as (
    select 
        line_item_id,
        invoice_id,
        amount,
        description,
        type
    from cleaned
    where row_num = 1 
)

select * from deduped