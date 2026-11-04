import os
import sys
import subprocess
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from prefect import flow, task

# Dynamically locate the repository root folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@task(name="Extract & Generate Raw Mock Data", description="Generates raw source data across all business domains", retries=1)
def extract_data():
    python_exe = sys.executable
    
    # List all 5 generator scripts in exact order
    scripts = [
        "scripts/generate_stripe_mock_data.py",
        "scripts/generate_hubspot_mock_data.py",
        "scripts/generate_ad_spend_mock_data.py",
        "scripts/generate_mixpanel_mock_data.py",
        "scripts/generate_support_ticket_mock_data.py"
    ]
    
    for script_rel_path in scripts:
        script_full_path = os.path.join(BASE_DIR, script_rel_path)
        print(f"Executing: {script_rel_path}")
        subprocess.run([python_exe, script_full_path], check=True, cwd=BASE_DIR)
        
    print("✅ All 5 domain datasets generated successfully.")

@task(name="Load to Snowflake", description="Loads all raw JSON seed files into Snowflake RAW tables", retries=1)
def load_to_snowflake():
    print("🚀 Connecting to Snowflake to load all domain datasets...")
    
    # Connect using environment credentials or config
    conn = snowflake.connector.connect(
        user="ZIHAD034",
        password=os.getenv("DBT_SNOWFLAKE_PASSWORD"), # Reads from your environment variable
        account="GMYFHUL-ZS40079",
        warehouse="COMPUTE_WH",
        database="my_flake",
        schema="PUBLIC"
    )

    # Map JSON seed filenames to their target Snowflake table names
    datasets_to_load = {
        "raw_hubspot_companies.json": "HUBSPOT_COMPANIES",
        "raw_hubspot_contacts.json": "HUBSPOT_CONTACTS",
        "raw_hubspot_deals.json": "HUBSPOT_DEALS",
        "raw_hubspot_owners.json": "HUBSPOT_OWNERS",
        "raw_ad_spend.json": "AD_SPEND",
        "raw_mixpanel_events.json": "MIXPANEL_EVENTS",
        "raw_support_tickets.json": "SUPPORT_TICKETS"
    }

    for filename, table_name in datasets_to_load.items():
        file_path = os.path.join(BASE_DIR, "seeds", filename)
        if not os.path.exists(file_path):
            print(f"⚠️ Warning: {filename} not found in seeds folder. Skipping.")
            continue
            
        print(f"📥 Loading {filename} into Snowflake table: {table_name}...")
        
        # Read JSON file into pandas DataFrame
        df = pd.read_json(file_path)
        
        # Normalize columns to uppercase for clean Snowflake standard
        df.columns = [c.upper() for c in df.columns]
        
        # Write pandas DataFrame to Snowflake
        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name=table_name,
            auto_create_table=True,
            overwrite=True
        )
        
        if success:
            print(f"✅ Successfully loaded {nrows} rows into {table_name}")
        else:
            print(f"❌ Failed to load {table_name}")

    conn.close()
    print("🔒 Snowflake connection closed successfully.")

@task(name="Run dbt Transformations", description="Executes dbt models, tests, and snapshots in Snowflake", retries=1)
def run_dbt():
    print("⚙️ Executing dbt build on Snowflake...")
    # Trigger dbt build via CLI subprocess
    subprocess.run(["dbt", "build"], check=True, cwd=BASE_DIR)
    print("✅ dbt build completed successfully.")

@flow(name="b2b_saas_elt_pipeline", log_prints=True)
def main_elt_pipeline():
    extract = extract_data()
    load = load_to_snowflake(wait_for=[extract])
    run_dbt(wait_for=[load])

if __name__ == "__main__":
    main_elt_pipeline()