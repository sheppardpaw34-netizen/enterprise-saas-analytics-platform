import json
import os
import random
from datetime import datetime, timedelta

# Ensure reproducibility
random.seed(42)

# Set base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEDS_DIR = os.path.join(BASE_DIR, "seeds")
os.makedirs(SEEDS_DIR, exist_ok=True)

# Define Reference Data
INDUSTRIES = [
    "Fintech",
    "Healthcare",
    "DevTools",
    "E-Commerce",
    "Cybersecurity",
    "MarTech",
]
EMPLOYEE_TIERS = ["1-10", "11-50", "51-200", "201-1000", "1000+"]
SOURCES = [
    "Organic Search",
    "Paid Search",
    "Paid Social",
    "Direct",
    "Referral",
    "Offline",
]
DEAL_STAGES = [
    "Discovery",
    "Value Proposition",
    "Contract Sent",
    "Closed Won",
    "Closed Lost",
]

# 1. Generate Owners (Sales Reps & CSMs)
owners = [
    {"owner_id": "hub_own_001", "owner_name": "Sarah Connor", "team": "Inbound SDR"},
    {"owner_id": "hub_own_002", "owner_name": "Marcus Wright", "team": "Outbound AE"},
    {"owner_id": "hub_own_003", "owner_name": "Kyle Reese", "team": "Enterprise AE"},
    {"owner_id": "hub_own_004", "owner_name": "Ellen Ripley", "team": "CSM"},
]

companies = []
contacts = []
deals = []

# Aligned perfectly with Stripe mock generation timeline
start_date = datetime(2023, 1, 1)
end_date = datetime(2026, 10, 31)
total_days = (end_date - start_date).days

# 2. Generate 500 Core B2B SaaS Companies & Linked Entities
for i in range(1, 501):
    company_id = f"hub_comp_{i:05d}"
    
    # Injecting dirty domain data (whitespace, uppercase casing) for dbt staging test practice
    raw_domain = f"acmecorp{i}.com"
    if i % 10 == 0:
        formatted_domain = f"  {raw_domain.upper()}  "
    elif i % 15 == 0:
        formatted_domain = f"{raw_domain.upper()}"
    else:
        formatted_domain = f" {raw_domain}" # leading space edge case

    comp_created_dt = start_date + timedelta(days=random.randint(0, total_days - 60))
    
    companies.append({
        "company_id": company_id,
        "company_name": f"Enterprise Corp {i} LLC",
        "domain": formatted_domain,
        "industry": random.choice(INDUSTRIES),
        "employee_count_tier": random.choice(EMPLOYEE_TIERS),
        "created_at": comp_created_dt.strftime("%Y-%m-%d %H:%M:%S")
    })

    # Generate 1 to 3 Contacts per Company (Many-to-One Cardinality & Dirty Data)
    num_contacts = random.randint(1, 3)
    for c_idx in range(num_contacts):
        cnt_id = f"hub_cnt_{i:05d}_{c_idx+1}"
        
        # Simulating billing vs decision maker email divergence
        prefix = "billing" if c_idx == 0 else f"user{c_idx}"
        
        # ~5% chance of orphan/unmatched domain to test pipeline join fallback edge cases
        if random.random() < 0.05:
            contact_email = f"{prefix}@unmatched-domain-{i}.com"
        else:
            contact_email = f"{prefix}@{raw_domain.strip()}"
        
        # ~15% chance of missing/direct original source
        source = None if random.random() < 0.15 else random.choice(SOURCES)
        
        contacts.append({
            "contact_id": cnt_id,
            "company_id": company_id,
            "email": contact_email,
            "first_name": f"Contact_{i}",
            "last_name": f"User_{c_idx+1}",
            "lifecycle_stage": random.choice(["lead", "mql", "sql", "opportunity", "customer"]),
            "original_source": source,
            "created_at": (comp_created_dt + timedelta(days=random.randint(0, 10))).strftime("%Y-%m-%d %H:%M:%S")
        })

    # Generate Deal Progression & Edge Cases
    deal_stage = random.choice(DEAL_STAGES)
    deal_created_dt = comp_created_dt + timedelta(days=random.randint(2, 20))
    
    closed_at = None
    amount = random.choice([1200, 3600, 12000, 24000, 60000])
    
    if deal_stage in ["Closed Won", "Closed Lost"]:
        closed_date_obj = deal_created_dt + timedelta(days=random.randint(5, 45))
        if closed_date_obj <= end_date:
            closed_at = closed_date_obj.strftime("%Y-%m-%d %H:%M:%S")
        
        if deal_stage == "Closed Lost":
            amount = 0  # Lost deals yield 0 ARR

    # Injecting a "Ghost Deal" edge case: Closed Won but missing closed_at timestamp
    if i == 42:
        deal_stage = "Closed Won"
        closed_at = None 

    deals.append({
        "deal_id": f"hub_deal_{i:05d}",
        "company_id": company_id,
        "owner_id": random.choice(owners)["owner_id"],
        "deal_name": f"Enterprise Corp {i} - Expansion Deal",
        "deal_stage": deal_stage,
        "amount": amount,
        "created_at": deal_created_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "closed_at": closed_at
    })

# Write JSON output files to seeds directory
files_to_write = {
    "raw_hubspot_companies.json": companies,
    "raw_hubspot_contacts.json": contacts,
    "raw_hubspot_deals.json": deals,
    "raw_hubspot_owners.json": owners,
}

for filename, data in files_to_write.items():
    filepath = os.path.join(SEEDS_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

print(f"Successfully generated HubSpot seed files (Timeline: 2023-01-01 to 2026-10-31) in {SEEDS_DIR}:")
for filename in files_to_write.keys():
    print(f" - {filename}")