from hybrid_engine import TamweelHybridEngine, print_report

def run_tests():
    engine = TamweelHybridEngine()
    
    # 1. Excellent Profile (High Score expected)
    excellent_user = {
        "name": "سامر العجلوني",
        "profession": "Senior Developer",
        "profession_category": "freelance",
        "avg_monthly_income_jod": 450.0,
        "income_stability_score": 0.95,
        "income_source_count": 3,
        "late_bills_count": 0,
        "bill_reliability_pct": 100.0,
        "total_bills_checked": 15,
        "current_balance_jod": 300.0,
        "wallet_tx_count": 40,
        "wallet_total_volume_jod": 800.0,
        "balance_to_income_ratio": 0.66,
        "existing_loans": 0
    }

    # 2. Fair Profile (Medium Score expected)
    fair_user = {
        "name": "رنا العبادي",
        "profession": "Instagram Store",
        "profession_category": "business",
        "avg_monthly_income_jod": 180.0,
        "income_stability_score": 0.65,
        "income_source_count": 1,
        "late_bills_count": 2,
        "bill_reliability_pct": 75.0,
        "total_bills_checked": 8,
        "current_balance_jod": 40.0,
        "wallet_tx_count": 10,
        "wallet_total_volume_jod": 150.0,
        "balance_to_income_ratio": 0.22,
        "existing_loans": 1
    }

    # 3. Risky Profile (Low Score + Overrides expected)
    risky_user = {
        "name": "خالد الزعبي",
        "profession": "Daily Laborer",
        "profession_category": "daily",
        "avg_monthly_income_jod": 90.0,
        "income_stability_score": 0.25,
        "income_source_count": 1,
        "late_bills_count": 5, # High late bills triggers rule
        "bill_reliability_pct": 20.0,
        "total_bills_checked": 5,
        "current_balance_jod": 5.0,
        "wallet_tx_count": 2,
        "wallet_total_volume_jod": 30.0,
        "balance_to_income_ratio": 0.05,
        "existing_loans": 2
    }

    test_cases = [
        ("EXCELLENT CASE", excellent_user),
        ("FAIR CASE", fair_user),
        ("HIGH RISK CASE", risky_user)
    ]

    for title, data in test_cases:
        print(f"\n🚀 TESTING: {title}")
        result = engine.run_pipeline(data)
        print_report(result)

if __name__ == "__main__":
    run_tests()
