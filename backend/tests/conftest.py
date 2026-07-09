import pytest
import sys
import os

# Ensure backend can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the engine and mock out supabase BEFORE instantiation
from app.ml import hybrid_engine
hybrid_engine.supabase = None

@pytest.fixture(scope="session")
def engine():
    """Returns a shared, session-scoped TamweelHybridEngine instance."""
    from app.ml.hybrid_engine import TamweelHybridEngine
    return TamweelHybridEngine()

@pytest.fixture
def base_user_data():
    """Provides a baseline set of valid user data."""
    return {
        "name": "Test User",
        "profession": "Engineer",
        "profession_category": "salaried",
        "avg_monthly_income_jod": 1500.0,
        "income_stability_score": 0.9,
        "income_source_count": 1,
        "late_bills_count": 0,
        "bill_reliability_pct": 100.0,
        "total_bills_checked": 24,
        "current_balance_jod": 2000.0,
        "wallet_tx_count": 100,
        "wallet_total_volume_jod": 3000.0,
        "balance_to_income_ratio": 1.33,
        "existing_loans": 0,
        "requested_amount_jod": 1000,
        "loan_duration_months": 12,
        "interest_rate": 0.12
    }
