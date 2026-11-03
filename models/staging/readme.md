# Staging Layer (`stg_stripe`)

The staging layer serves as the specialized boundary between raw Stripe ingestion tables and downstream business models.

## Design Patterns & Standards

* **Pure Mirror:** Raw source tables are never altered directly; staging views handle data quality and transformation natively.
* **Deterministic Deduplication:** Webhook retry duplicates are resolved via window functions:
  ```sql
  ROW_NUMBER() OVER (PARTITION BY "id" ORDER BY "created" DESC) AS row_num


Filtered out via `WHERE row_num = 1` to guarantee primary key uniqueness.

* **Snowflake Casing:** Raw column identifiers are explicitly double-quoted (`"id"`, `"status"`, `"created"`) to resolve casing mismatches between Snowflake and dbt.

## Model Catalog

| Model                                 | Primary Key       | Description                                               |
| ---                                   | ---               | ---                                                       |
| `stg_stripe__customers.sql`           | `customer_id`     | Cleaned customer profiles and metadata                    |
| `stg_stripe__subscriptions.sql`       | `subscription_id` | Deduplicated subscription contracts and terms             |
| `stg_stripe__invoices.sql`            | `invoice_id`      | Deduplicated billing invoices and payment totals          |
| `stg_stripe__invoices_line_items.sql` | `line_item_id`    | Itemized invoice charge breakdown                         |
| `stg_stripe__charges.sql`             | `charge_id`       | Transaction records and payment outcomes                  |
| `stg_stripe__disputes.sql`            | `dispute_id`      | Chargebacks and dispute events                            |
| `stg_stripe__events.sql`              | `event_id`        | Webhook log history                                       |
  ---                      
## Testing

All models are validated against `schema.yml` with 17 automated tests (`unique`, `not_null`, `accepted_values`):

```bash
dbt test --select staging
```