# B2B SaaS ELT Pipeline & Orchestration Architecture

This repository contains an enterprise-grade, multi-source B2B SaaS analytics pipeline orchestrated via **Prefect**, loaded into **Snowflake** via custom Python automation, and transformed downstream using **dbt-core**.

## Architecture & Tech Stack
* **Orchestration:** Prefect (Python workflow automation, retry logic, dynamic dependency tracking)
* **Data Warehouse:** Snowflake (`MY_FLAKE` database, `PUBLIC` schema)[cite: 15]
* **Transformation Layer:** dbt-core (SQL models, staging views, incremental models, and data tests)
* **Extraction/Generation:** Custom Python mock data generators for 5 core business domains

## Pipeline Execution Flow
Run the master orchestration script from the project root to execute the full end-to-end ELT lifecycle:
```bash
python orchestration/elt_pipeline.py