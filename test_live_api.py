import os
import sys
import json
import logging

sys.path.insert(0, os.path.abspath('backend'))
from fastapi.testclient import TestClient
from app.main import app

# Set up logging so we can see the output of the logger in rag_engine.py
logging.getLogger("ml_pipeline.rag_engine").setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
logging.getLogger("ml_pipeline.rag_engine").addHandler(stream_handler)

from app.ml.hybrid_engine import TamweelHybridEngine
import asyncio

engine = TamweelHybridEngine()

def test_profile(name, data):
    print(f"\n{'='*50}\n--- {name} ---\n{'='*50}")
    try:
        # run_pipeline is synchronous
        resp_data = engine.run_pipeline(data)
        
        print("\n--- FULL RESPONSE DATA ---")
        print(json.dumps(resp_data, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print("Error:", str(e))

# Profile 1: Normal Gig Worker
gig_worker = {
    "profession_category": "gig",
    "avg_monthly_income_jod": 400.0,
    "income_stability_score": 0.8,
    "late_bills_count": 0,
    "bill_reliability_pct": 95.0,
    "current_balance_jod": 150.0,
    "balance_to_income_ratio": 0.375,
    "wallet_total_volume_jod": 450.0
}
test_profile("NORMAL PROFILE (Gig Worker)", gig_worker)

# Profile 2: Edge Case Unlikely Profile
astronaut = {
    "profession_category": "astronaut",
    "avg_monthly_income_jod": 15000.0,
    "income_stability_score": 0.9,
    "late_bills_count": 0,
    "bill_reliability_pct": 100.0,
    "current_balance_jod": 5000.0,
    "balance_to_income_ratio": 0.3,
    "wallet_total_volume_jod": 6000.0
}
test_profile("EDGE CASE PROFILE (Astronaut)", astronaut)
