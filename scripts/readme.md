## Extraction & Utilities Scripts (`scripts/`)

The `scripts/` directory houses the modular data generation and standalone utility scripts that feed the pipeline.

### Mock Data Generators (`generate_*.py`)
These scripts simulate upstream production data sources and output structured JSON files into the `seeds/` folder:

1. **`generate_stripe_mock_data.py`**
   * **Domain:** Billing & Revenue
   * **Outputs:** `charges.json`, `customers.json`, `disputes.json`, `events.json`, `invoices.json`, `invoice_line_items.json`, `subscriptions.json`
   * **Purpose:** Generates realistic SaaS subscription lifecycles, MRR events, invoices, and payment disputes.

2. **`generate_hubspot_mock_data.py`**
   * **Domain:** CRM & Sales Pipeline
   * **Outputs:** `raw_hubspot_companies.json`, `raw_hubspot_contacts.json`, `raw_hubspot_deals.json`, `raw_hubspot_owners.json`
   * **Purpose:** Simulates B2B account hierarchies, deal stages, and sales representative ownership.

3. **`generate_ad_spend_mock_data.py`**
   * **Domain:** Marketing Acquisition
   * **Outputs:** `raw_ad_spend.json`
   * **Purpose:** Tracks channel-level marketing spend across platforms (Google Ads, LinkedIn, Meta) for CAC and unit economics modeling.

4. **`generate_mixpanel_mock_data.py`**
   * **Domain:** Product Analytics & User Engagement
   * **Outputs:** `raw_mixpanel_events.json`
   * **Purpose:** Generates user event telemetry for feature adoption and product-led growth (PLG) tracking.

5. **`generate_support_ticket_mock_data.py`**
   * **Domain:** Customer Success & Support
   * **Outputs:** `raw_support_tickets.json`
   * **Purpose:** Simulates customer support inquiries, resolution times, and ticket priorities for churn risk correlation.

### Utilities
* **`load_stripe_to_snowflake.py`**
  * **Purpose:** Legacy standalone loader script for Stripe data. *Note: Maintained for historical reference; primary multi-source loading is now handled uniformly inside `orchestration/elt_pipeline.py`.*