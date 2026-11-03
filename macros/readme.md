# Macros

Custom dbt Jinja macros used for standardizing data type conversions across staging models.

## Available Macros

* **`cents_to_dollars.sql`**: Divides Stripe raw integer amounts by 100 to convert cents into standard decimal dollar values (`$USD`).
* **`epoch_to_timestamp.sql`**: Converts Unix epoch integer timestamps (seconds) into Snowflake-native `TIMESTAMP_NTZ` values.

## Usage Example
```sql
{{ cents_to_dollars('"unit_amount"') }} as unit_amount,
{{ epoch_to_timestamp('"created"') }} as created_at