import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
import random

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"❌ Supabase Connection Failed: {e}")
    supabase = None

def seed_data():
    if not supabase:
        print("⚠️ Skipping seeding: Supabase client not initialized.")
        return

    profiles = [
        {"name": "Anas", "score": 78, "amount": 600, "risk": "Low", "prof": "Software Engineer", "cat": "freelance"},
        {"name": "Samer", "score": 86, "amount": 1000, "risk": "Low", "prof": "Senior Developer", "cat": "freelance"},
        {"name": "Rana", "score": 52, "amount": 300, "risk": "Medium", "prof": "Instagram Store", "cat": "gig"},
        {"name": "Khaled", "score": 17, "amount": 0, "risk": "High", "prof": "Daily Laborer", "cat": "gig"},
        {"name": "Laila", "score": 65, "amount": 600, "risk": "Low", "prof": "Graphic Designer", "cat": "freelance"},
        {"name": "Omar", "score": 42, "amount": 150, "risk": "Medium", "prof": "Uber Driver", "cat": "gig"},
        {"name": "Zaid", "score": 91, "amount": 1000, "risk": "Low", "prof": "Consultant", "cat": "freelance"},
        {"name": "Sara", "score": 28, "amount": 0, "risk": "High", "prof": "Delivery Rider", "cat": "gig"},
        {"name": "Muna", "score": 70, "amount": 600, "risk": "Low", "prof": "Tutor", "cat": "freelance"},
        {"name": "Hassan", "score": 58, "amount": 300, "risk": "Medium", "prof": "Carpenter", "cat": "gig"},
    ]

    # Add some historical entries for Anas
    for i in range(1, 4):
        profiles.append({
            "name": "Anas",
            "score": 78 - (i * 5),
            "amount": 600 - (i * 100),
            "risk": "Low" if (78 - (i * 5)) > 60 else "Medium",
            "prof": "Software Engineer",
            "cat": "freelance"
        })

    records = []
    for i, p in enumerate(profiles):
        # Stagger dates over the last 6 months
        date = datetime.now() - timedelta(days=random.randint(0, 180))
        records.append({
            "name": p["name"],
            "profession": p["prof"],
            "profession_category": p["cat"],
            "avg_monthly_income_jod": float(random.randint(250, 1200)),
            "credit_score": p["score"],
            "risk_level": p["risk"],
            "decision": "Approved" if p["score"] >= 60 else "Conditional Approval" if p["score"] >= 30 else "Rejected",
            "approved_amount_jod": p["amount"],
            "generated_at": date.isoformat()
        })

    try:
        # Clear existing data first to avoid duplicates in the prototype
        # Note: In a real app, we might not want to truncate, but for seeding fresh mockup data it's easier.
        # supabase.table("tamweel_results").delete().neq("id", 0).execute() 
        
        supabase.table("tamweel_results").insert(records).execute()
        print(f"✅ Successfully seeded {len(records)} realistic assessments into tamweel_results!")
    except Exception as e:
        print(f"❌ Error seeding data: {e}")

if __name__ == "__main__":
    seed_data()
