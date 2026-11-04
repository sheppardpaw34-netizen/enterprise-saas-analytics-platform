import json
import os
import random
from datetime import datetime, timedelta

# Ensure exact reproducibility
random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEDS_DIR = os.path.join(BASE_DIR, "seeds")
os.makedirs(SEEDS_DIR, exist_ok=True)

EVENTS = [
    "user_logged_in",
    "dashboard_viewed",
    "report_exported",
    "integration_connected",
    "query_executed",
    "team_member_invited"
]

DEVICE_TYPES = ["Desktop", "Mobile", "Web"]

mixpanel_events = []

start_date = datetime(2023, 1, 1)
end_date = datetime(2026, 10, 31)
total_days = (end_date - start_date).days

print(f"🚀 Generating Enterprise Mixpanel Event Stream with Pre-Churn & Edge Cases...")

event_id_counter = 1

for company_idx in range(1, 501):
    domain = f"acmecorp{company_idx}.com"
    num_users = random.randint(1, 4)
    
    # Define Account Health Persona for Edge Cases
    health_type = random.choices(
        population=["healthy", "churn_decay", "ghost_account"],
        weights=[0.70, 0.22, 0.08]
    )[0]

    for u_idx in range(num_users):
        user_email = f"user{u_idx+1}@{domain}"

        if health_type == "ghost_account":
            # Ghost account: Logs in 1-3 times near creation, then goes completely dark
            num_events = random.randint(1, 3)
            account_start = start_date + timedelta(days=random.randint(0, total_days - 300))
            
            for _ in range(num_events):
                event_time = account_start + timedelta(hours=random.randint(1, 48))
                mixpanel_events.append({
                    "event_id": f"evt_{event_id_counter:08d}",
                    "user_id": user_email,
                    "company_domain": domain,
                    "event_name": "user_logged_in" if _ == 0 else random.choice(EVENTS),
                    "event_timestamp": event_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "device_type": random.choice(DEVICE_TYPES)
                })
                event_id_counter += 1

        elif health_type == "churn_decay":
            # Pre-Churn Decay: Active early on, but activity drops to near ZERO in final 90 days
            decay_point_day = total_days - random.randint(90, 180)
            
            # Phase 1: High activity before decay point
            for _ in range(random.randint(20, 40)):
                day_offset = random.randint(0, decay_point_day)
                event_date = start_date + timedelta(days=day_offset)
                event_time = event_date.replace(hour=random.randint(9, 18), minute=random.randint(0, 59))
                
                mixpanel_events.append({
                    "event_id": f"evt_{event_id_counter:08d}",
                    "user_id": user_email,
                    "company_domain": domain,
                    "event_name": random.choice(EVENTS),
                    "event_timestamp": event_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "device_type": random.choice(DEVICE_TYPES)
                })
                event_id_counter += 1

            # Phase 2: Massive decay (1-2 events max after decay point)
            for _ in range(random.randint(0, 2)):
                day_offset = random.randint(decay_point_day, total_days)
                event_date = start_date + timedelta(days=day_offset)
                event_time = event_date.replace(hour=random.randint(9, 18), minute=random.randint(0, 59))
                
                mixpanel_events.append({
                    "event_id": f"evt_{event_id_counter:08d}",
                    "user_id": user_email,
                    "company_domain": domain,
                    "event_name": "user_logged_in",
                    "event_timestamp": event_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "device_type": random.choice(DEVICE_TYPES)
                })
                event_id_counter += 1

        else:  # "healthy" power accounts
            # Consistent usage throughout the timeline with high engagement
            for _ in range(random.randint(40, 80)):
                day_offset = random.randint(0, total_days)
                event_date = start_date + timedelta(days=day_offset)
                event_time = event_date.replace(hour=random.randint(8, 20), minute=random.randint(0, 59))

                evt_id = f"evt_{event_id_counter:08d}"
                mixpanel_events.append({
                    "event_id": evt_id,
                    "user_id": user_email,
                    "company_domain": domain,
                    "event_name": random.choice(EVENTS),
                    "event_timestamp": event_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "device_type": random.choice(DEVICE_TYPES)
                })
                event_id_counter += 1

                # ~2% chance of duplicate event log spike (network retry edge case)
                if random.random() < 0.02:
                    mixpanel_events.append({
                        "event_id": evt_id,  # Duplicate event ID
                        "user_id": user_email,
                        "company_domain": domain,
                        "event_name": random.choice(EVENTS),
                        "event_timestamp": event_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "device_type": random.choice(DEVICE_TYPES)
                    })

# Sort event log chronologically
mixpanel_events.sort(key=lambda x: x["event_timestamp"])

# Output file
filepath = os.path.join(SEEDS_DIR, "raw_mixpanel_events.json")
with open(filepath, "w") as f:
    json.dump(mixpanel_events, f, indent=2)

print(f"Successfully generated Enterprise Mixpanel Events ({len(mixpanel_events):,} total events) in {SEEDS_DIR}: raw_mixpanel_events.json")