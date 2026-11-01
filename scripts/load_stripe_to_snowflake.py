import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from generate_stripe_mock_data import generate_production_stripe_mock_data
import pandas as pd

def load_stripe_data_to_snowflake():
    print("🚀 Generating Stripe Mock Dataset...")
    customers, subscriptions, invoices, invoice_line_items, charges, disputes, events = generate_production_stripe_mock_data()

    print("🔌 Connecting to Snowflake...")
    conn = snowflake.connector.connect(
        user='ZIHAD034',
        password='Tiyapakhi234zbm',
        account='GMYFHUL-ZS40079',  # Keep your account locator here
        warehouse='COMPUTE_WH',
        database='my_flake',
        schema='PUBLIC'
    )

    cursor = conn.cursor()
    cursor.execute("USE WAREHOUSE COMPUTE_WH")
    cursor.execute("USE DATABASE my_flake")
    cursor.execute("USE SCHEMA PUBLIC")
    cursor.close()

    datasets = {
        "CUSTOMERS": customers,
        "SUBSCRIPTIONS": subscriptions,
        "INVOICES": invoices,
        "INVOICE_LINE_ITEMS": invoice_line_items,
        "CHARGES": charges,
        "DISPUTES": disputes,
        "EVENTS": events
    }

    try:
        for table_name, data in datasets.items():
            if not data:
                continue
            
            df = pd.DataFrame(data)
            print(f"📥 Loading {len(df)} rows into Snowflake table: {table_name}...")
            
            try:
                success, nchunks, nrows, _ = write_pandas(
                    conn=conn,
                    df=df,
                    table_name=table_name,
                    auto_create_table=True,
                    overwrite=True
                )
                print(f"   ✅ Successfully loaded {nrows} rows into {table_name}")
            except Exception as e:
                print(f"   ❌ Failed on table {table_name}. Error: {e}")
                raise e

    finally:
        conn.close()
        print("🔒 Snowflake connection closed successfully.")

if __name__ == "__main__":
    load_stripe_data_to_snowflake()