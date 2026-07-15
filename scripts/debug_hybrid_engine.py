import sys
import os

# Add backend to path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.ml.hybrid_engine import TamweelHybridEngine
from app.utils.report_formatter import print_report

if __name__ == "__main__":
    engine = TamweelHybridEngine()
    
    test_user = {
        "name": "أحمد الخالدي",
        "profession": "Uber Driver",
        "profession_category": "gig",
        "avg_monthly_income_jod": 320.50,
        "income_stability_score": 0.85,
        "income_source_count": 1,
        "late_bills_count": 1,
        "bill_reliability_pct": 92.0,
        "total_bills_checked": 12,
        "current_balance_jod": 150.0,
        "wallet_tx_count": 25,
        "wallet_total_volume_jod": 450.0,
        "balance_to_income_ratio": 0.46,
        "existing_loans": 0
    }
    
    result = engine.run_pipeline(test_user)
    print_report(result)
