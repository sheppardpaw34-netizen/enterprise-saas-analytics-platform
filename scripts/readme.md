# Ingestion Scripts

Python automation scripts for generating and loading synthetic Stripe B2B subscription data into Snowflake.

## Overview
* **`generate_stripe_mock_data.py`**: Generates 500+ enterprise accounts, 17k+ historical subscriptions, invoices, charges, and webhook events with realistic B2B edge cases (prorations, discounts, dispute chargebacks, and webhook retries).
* **`load_stripe_to_snowflake.py`**: Establishes a Snowflake connection and bulk-loads pandas DataFrames into the raw schema using `write_pandas(overwrite=True)`.

## Data Specifications
* **Timestamps:** Unix epoch integers (seconds).
* **Monetary Values:** Integer cents to prevent floating-point precision loss.

## Usage
```bash
python scripts/generate_stripe_mock_data.py
python scripts/load_stripe_to_snowflake.py