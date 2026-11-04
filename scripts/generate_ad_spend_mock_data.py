import json
import os
import random
from datetime import datetime, timedelta

# Ensure reproducibility
random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEDS_DIR = os.path.join(BASE_DIR, "seeds")
os.makedirs(SEEDS_DIR, exist_ok=True)

CHANNELS = ["Google Search", "Google Display", "LinkedIn Sponsored", "Meta Ads", "YouTube B2B"]
CAMPAIGNS = [
    "brand_search_core", 
    "saas_analytics_competitor", 
    "data_engineers_retargeting", 
    "mrr_waterfall_lead_gen", 
    "enterprise_account_abm"
]

ad_spend_records = []

# Aligned with Stripe and HubSpot timeline (2023-01-01 to 2026-10-31)
start_date = datetime(2023, 1, 1)
end_date = datetime(2026, 10, 31)
current_date = start_date

record_id = 1
while current_date <= end_date:
    # Generate 3 to 6 daily ad spend entries across different channels/campaigns
    daily_entries = random.randint(3, 6)
    for _ in range(daily_entries):
        channel = random.choice(CHANNELS)
        campaign = random.choice(CAMPAIGNS)
        
        # Simulating realistic daily spend and performance numbers
        spend = round(random.uniform(50.0, 850.0), 2)
        impressions = int(spend * random.uniform(15, 40))
        clicks = int(impressions * random.uniform(0.02, 0.08))
        conversions = int(clicks * random.uniform(0.01, 0.05))
        
        ad_spend_records.append({
            "spend_id": f"spend_{record_id:06d}",
            "date": current_date.strftime("%Y-%m-%d"),
            "channel": channel,
            "campaign_name": campaign,
            "spend_amount": spend,
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions
        })
        record_id += 1
        
    current_date += timedelta(days=1)

# Write to seeds
filepath = os.path.join(SEEDS_DIR, "raw_ad_spend.json")
with open(filepath, "w") as f:
    json.dump(ad_spend_records, f, indent=2)

print(f"Successfully generated Ad Spend seed file ({len(ad_spend_records)} daily records) in {SEEDS_DIR}: raw_ad_spend.json")