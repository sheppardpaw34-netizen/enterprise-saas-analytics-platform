import random
from datetime import datetime, timedelta

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
    print(f"🚀 Initializing Optimized Enterprise Stripe Mock Data Generator...")
    
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

    # Index active subscriptions by customer ID for O(1) fast lookup
    customer_active_subs = {c["id"]: [] for c in customers}
    current_time = start_date
    event_counter = 100000

    # 2. Optimized Daily Loop
    while current_time <= end_date:
        for cust in customers:
            cust_id = cust["id"]
            if current_time < datetime.fromtimestamp(cust["created"]):
                continue
            
            active_subs = customer_active_subs[cust_id]
            
            # Scenario A: Subscribe or add multi-sub
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

                if is_disputed:
                    disputes.append({
                        "id": f"dp_{random.randint(10000, 99999)}",
                        "charge": chg_id,
                        "amount": final_total,
                        "status": random.choice(["won", "lost", "needs_response"]),
                        "reason": random.choice(["fraudulent", "general", "subscription_canceled"]),
                        "created": int(sub_start.timestamp()) + 259200
                    })

            # Scenario B: Churn active subscription
            elif active_subs and random.random() < 0.04:
                sub_to_churn = active_subs.pop(0)
                sub_to_churn["status"] = "canceled"

        current_time += timedelta(days=1)

    print(f"✅ Generated Dataset Successfully in a fraction of a second!")
    print(f"   - Customers: {len(customers)}")
    print(f"   - Total Subscriptions: {len(subscriptions)}")
    print(f"   - Active Subscriptions: {len([s for s in subscriptions if s['status'] == 'active'])}")
    print(f"   - Canceled Subscriptions: {len([s for s in subscriptions if s['status'] == 'canceled'])}")
    print(f"   - Invoices: {len(invoices)}")
    print(f"   - Charges: {len(charges)}")
    
    return customers, subscriptions, invoices, invoice_line_items, charges, disputes, events

if __name__ == "__main__":
    generate_production_stripe_mock_data()