import json
import os
import random
from datetime import datetime, timedelta

# Ensure exact reproducibility
random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEDS_DIR = os.path.join(BASE_DIR, "seeds")
os.makedirs(SEEDS_DIR, exist_ok=True)

PRIORITIES = ["Low", "Normal", "High", "Urgent"]
STATUSES = ["Solved", "Closed", "Pending", "Open"]
CATEGORIES = ["Billing", "Technical Bug", "Feature Request", "Account Access", "Integration Setup"]

support_tickets = []

start_date = datetime(2023, 1, 1)
end_date = datetime(2026, 10, 31)
total_days = (end_date - start_date).days

print(f"🚀 Initializing Customer Support Ticket Generator (2023-01-01 to 2026-10-31)...")

ticket_id_counter = 1

# Generate support tickets across our 500 enterprise companies
for company_idx in range(1, 501):
    domain = f"acmecorp{company_idx}.com"
    
    # Random number of support tickets per company over the multi-year span
    num_tickets = random.randint(2, 8)
    
    for _ in range(num_tickets):
        ticket_created = start_date + timedelta(days=random.randint(0, total_days))
        priority = random.choices(PRIORITIES, weights=[0.3, 0.4, 0.2, 0.1])[0]
        category = random.choice(CATEGORIES)
        
        # Edge Case 1: ~10% of tickets remain Open/Pending (SLA breach / unresolved edge case)
        if random.random() < 0.10:
            status = random.choice(["Open", "Pending"])
            resolved_at = None
        else:
            status = random.choice(["Solved", "Closed"])
            # Resolution time scales with priority (Urgent is fast, Low can take weeks)
            if priority == "Urgent":
                resolution_delta = timedelta(hours=random.randint(1, 24))
            elif priority == "High":
                resolution_delta = timedelta(days=random.randint(1, 3))
            else:
                resolution_delta = timedelta(days=random.randint(2, 14))
                
            resolved_dt = ticket_created + resolution_delta
            if resolved_dt <= end_date:
                resolved_at = resolved_dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                resolved_at = None
                status = "Open"

        support_tickets.append({
            "ticket_id": f"tkt_{ticket_id_counter:06d}",
            "company_domain": domain,
            "user_id": f"support_user@{domain}",
            "priority": priority,
            "status": status,
            "category": category,
            "created_at": ticket_created.strftime("%Y-%m-%d %H:%M:%S"),
            "resolved_at": resolved_at
        })
        ticket_id_counter += 1

# Sort chronologically
support_tickets.sort(key=lambda x: x["created_at"])

# Write to seeds directory
filepath = os.path.join(SEEDS_DIR, "raw_support_tickets.json")
with open(filepath, "w") as f:
    json.dump(support_tickets, f, indent=2)

print(f"Successfully generated Support Tickets seed file ({len(support_tickets):,} total records) in {SEEDS_DIR}: raw_support_tickets.json")