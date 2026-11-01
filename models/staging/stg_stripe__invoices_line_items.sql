with source as (
    select * from {{ source('stripe', 'invoice_line_items') }}
),

renamed as (
    select
        "id" as line_item_id,
        "invoice" as invoice_id,
        {{ cents_to_dollars('"amount"') }} as amount,
        "description",
        "type"

    from source
    where "id" is not null
)

select * from renamed