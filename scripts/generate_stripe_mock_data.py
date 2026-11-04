import os
import random
from datetime import datetime, timedelta
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

PLANS = {
    "price_starter_monthly": {"name": "Starter Plan", "amount": 4900, "interval": "month"},
    "price_growth_monthly": {"name": "Growth Plan", "amount": 19900, "interval": "month"},
    "price_scale_annual": {"name": "Scale Annual", "amount": 199900, "interval": "year"},
}

COUPONS = {
    "20_OFF": {"percent_off": 20},
    "50_OFF": {"percent_off": 50},
}

def generate_production_stripe_mock_data(start_date=datetime(2023, 1, 1), end_date=datetime(2026, 10, 31)):
    print(f"🚀 Initializing Optimized Enterprise Stripe Mock Data Generator (with Proration & Events)...")
    
    customers = []
    subscriptions = []
    invoices = []
    invoice_line_items = []
    charges = []
    disputes = []
    events = []

    # 1. Generate 500 Core B2B SaaS Customers
    for i in range(1, 501):
        cust_id = f"cus_{i:05d}"
        created_dt = start_date + timedelta(days=random.randint(0, 800))
        if created_dt > end_date:
            created_dt = end_date - timedelta(days=30)
            
        has_coupon = random.random() < 0.20
        coupon_key = random.choice(list(COUPONS.keys())) if has_coupon else None

        customers.append({
            "id": cust_id,
            "object": "customer",
            "created": int(created_dt.timestamp()),
            "email": f"billing+{i}@{random.choice(['acme', 'enterprise', 'startup', 'saas', 'cloud', 'global'])}-corp.com",
            "name": f"Enterprise Corp {i} LLC",
            "currency": "usd",
            "discount_coupon": coupon_key,
            "delinquent": random.choice([True, False, False, False, False]),
        })

        events.append({
            "id": f"evt_{random.randint(100000, 999999)}",
            "object": "event",
            "type": "customer.created",
            "created": int(created_dt.timestamp()),
            "customer": cust_id
        })

    customer_active_subs = {c["id"]: [] for c in customers}
    current_time = start_date

    # 2. Optimized Daily Loop
    while current_time <= end_date:
        for cust in customers:
            cust_id = cust["id"]
            if current_time < datetime.fromtimestamp(cust["created"]):
                continue
            
            active_subs = customer_active_subs[cust_id]
            
            # Scenario A: Subscribe
            if len(active_subs) < 2 and random.random() < 0.08:
                sub_id = f"sub_{random.randint(100000, 999999)}"
                plan_key = random.choice(list(PLANS.keys()))
                plan = PLANS[plan_key]
                
                sub_start = current_time
                sub_end = sub_start + (timedelta(days=365) if plan["interval"] == "year" else timedelta(days=30))
                
                sub_obj = {
                    "id": sub_id,
                    "object": "subscription",
                    "customer": cust_id,
                    "status": "active",
                    "price_id": plan_key,
                    "plan_nickname": plan["name"],
                    "unit_amount": plan["amount"],
                    "current_period_start": int(sub_start.timestamp()),
                    "current_period_end": int(sub_end.timestamp()),
                    "cancel_at_period_end": False,
                    "created": int(sub_start.timestamp())
                }
                subscriptions.append(sub_obj)
                active_subs.append(sub_obj)

                events.append({
                    "id": f"evt_{random.randint(100000, 999999)}",
                    "object": "event",
                    "type": "customer.subscription.created",
                    "created": int(sub_start.timestamp()),
                    "customer": cust_id
                })
                
                # Invoice & Charge
                discount_amount = 0
                if cust["discount_coupon"]:
                    pct = COUPONS[cust["discount_coupon"]]["percent_off"]
                    discount_amount = int(plan["amount"] * (pct / 100))
                
                final_total = plan["amount"] - discount_amount
                inv_id = f"in_{random.randint(100000, 999999)}"
                chg_id = f"ch_{random.randint(100000, 999999)}"
                
                invoices.append({
                    "id": inv_id,
                    "object": "invoice",
                    "customer": cust_id,
                    "subscription": sub_id,
                    "status": "paid",
                    "subtotal": plan["amount"],
                    "discount": discount_amount,
                    "total": final_total,
                    "amount_paid": final_total,
                    "currency": "usd",
                    "created": int(sub_start.timestamp()),
                    "period_start": int(sub_start.timestamp()),
                    "period_end": int(sub_end.timestamp())
                })

                invoice_line_items.append({
                    "id": f"ili_{random.randint(100000, 999999)}",
                    "invoice": inv_id,
                    "amount": plan["amount"],
                    "description": f"Subscription for {plan['name']}",
                    "type": "subscription"
                })

                if discount_amount > 0:
                    invoice_line_items.append({
                        "id": f"ili_{random.randint(100000, 999999)}",
                        "invoice": inv_id,
                        "amount": -discount_amount,
                        "description": f"Discount ({cust['discount_coupon']})",
                        "type": "discount"
                    })

                is_disputed = random.random() < 0.02
                charges.append({
                    "id": chg_id,
                    "object": "charge",
                    "customer": cust_id,
                    "invoice": inv_id,
                    "amount": final_total,
                    "currency": "usd",
                    "status": "succeeded",
                    "disputed": is_disputed,
                    "created": int(sub_start.timestamp())
                })

                events.append({
                    "id": f"evt_{random.randint(100000, 999999)}",
                    "object": "event",
                    "type": "invoice.payment_succeeded",
                    "created": int(sub_start.timestamp()),
                    "customer": cust_id
                })

                if is_disputed:
                    disputes.append({
                        "id": f"dp_{random.randint(10000, 99999)}",
                        "charge": chg_id,
                        "amount": final_total,
                        "status": random.choice(["won", "lost", "needs_response"]),
                        "reason": random.choice(["fraudulent", "general", "subscription_canceled"]),
                        "created": int(sub_start.timestamp()) + 259200
                    })

            # Scenario B: Plan Upgrade/Downgrade ( generando Proration )
            elif active_subs and random.random() < 0.03:
                sub = active_subs[0]
                old_amount = sub["unit_amount"]
                new_plan_key = random.choice([k for k in PLANS.keys() if PLANS[k]["amount"] != old_amount])
                new_plan = PLANS[new_plan_key]
                
                sub["price_id"] = new_plan_key
                sub["plan_nickname"] = new_plan["name"]
                sub["unit_amount"] = new_plan["amount"]

                # Proration calculation item
                proration_amount = new_plan["amount"] - old_amount
                inv_id = f"in_{random.randint(100000, 999999)}"
                
                invoices.append({
                    "id": inv_id,
                    "object": "invoice",
                    "customer": cust_id,
                    "subscription": sub["id"],
                    "status": "paid",
                    "subtotal": proration_amount,
                    "discount": 0,
                    "total": proration_amount,
                    "amount_paid": proration_amount,
                    "currency": "usd",
                    "created": int(current_time.timestamp()),
                    "period_start": int(current_time.timestamp()),
                    "period_end": sub["current_period_end"]
                })

                invoice_line_items.append({
                    "id": f"ili_{random.randint(100000, 999999)}",
                    "invoice": inv_id,
                    "amount": proration_amount,
                    "description": f"Proration (upgrade/downgrade) to {new_plan['name']}",
                    "type": "invoiceitem"
                })

                events.append({
                    "id": f"evt_{random.randint(100000, 999999)}",
                    "object": "event",
                    "type": "customer.subscription.updated",
                    "created": int(current_time.timestamp()),
                    "customer": cust_id
                })

            # Scenario C: Churn active subscription
            elif active_subs and random.random() < 0.04:
                sub_to_churn = active_subs.pop(0)
                sub_to_churn["status"] = "canceled"

                events.append({
                    "id": f"evt_{random.randint(100000, 999999)}",
                    "object": "event",
                    "type": "customer.subscription.deleted",
                    "created": int(current_time.timestamp()),
                    "customer": cust_id
                })

        current_time += timedelta(days=1)

    print(f"✅ Generated Dataset Successfully!")
    print(f"   - Customers: {len(customers)}")
    print(f"   - Subscriptions: {len(subscriptions)}")
    print(f"   - Invoices: {len(invoices)}")
    print(f"   - Line Items (incl. Proration & Discounts): {len(invoice_line_items)}")
    print(f"   - Charges: {len(charges)}")
    print(f"   - Disputes: {len(disputes)}")
    print(f"   - Events: {len(events)}")

    return customers, subscriptions, invoices, invoice_line_items, charges, disputes, events

def load_to_snowflake():
    customers, subscriptions, invoices, invoice_line_items, charges, disputes, events = generate_production_stripe_mock_data()

    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT", "GMYFHUL-ZS40079"),
        user=os.getenv("SNOWFLAKE_USER", "ZIHAD034"),
        password=os.getenv("SNOWFLAKE_PASSWORD", "Tiyapakhi234zbm"),
        role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=os.getenv("SNOWFLAKE_DATABASE", "my_flake"),
        schema=os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")
    )

    datasets = {
        "CUSTOMERS": pd.DataFrame(customers),
        "SUBSCRIPTIONS": pd.DataFrame(subscriptions),
        "INVOICES": pd.DataFrame(invoices),
        "INVOICE_LINE_ITEMS": pd.DataFrame(invoice_line_items),
        "CHARGES": pd.DataFrame(charges),
        "DISPUTES": pd.DataFrame(disputes),
        "EVENTS": pd.DataFrame(events),
    }

    print("🔌 Connecting to Snowflake and Overwriting Tables...")
    for table_name, df in datasets.items():
        print(f"loading {len(df)} rows into Snowflake table: {table_name} (Overwrite)...")
        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name=table_name,
            auto_create_table=True,
            overwrite=True  # Ensures clean replacement every time
        )
        if success:
            print(f"   Successfully loaded {nrows} rows into {table_name}")
        else:
            print(f"❌ Failed on table {table_name}.")

    conn.close()
    print("🔒 Snowflake connection closed successfully.")
