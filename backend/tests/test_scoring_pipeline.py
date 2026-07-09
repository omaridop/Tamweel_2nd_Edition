import pytest

def test_high_income_excellent_history(engine, base_user_data):
    """Test a profile with high income and excellent history."""
    user_data = base_user_data.copy()
    user_data.update({
        "avg_monthly_income_jod": 3000.0,
        "income_stability_score": 0.95,
        "late_bills_count": 0,
        "bill_reliability_pct": 100.0,
        "current_balance_jod": 5000.0,
        "requested_amount_jod": 500
    })
    
    result = engine.run_pipeline(user_data)
    
    assert 0 <= result['final_score'] <= 100
    assert result['risk_level'] in ["Low", "Medium", "High", "Critical"]
    assert result['approved_amount_jod'] >= 0
    # Expected to be Approved
    assert "Approved" in result['decision']

def test_low_income_poor_history(engine, base_user_data):
    """Test a profile with low income and poor history."""
    user_data = base_user_data.copy()
    user_data.update({
        "avg_monthly_income_jod": 300.0,
        "income_stability_score": 0.3,
        "late_bills_count": 5,
        "bill_reliability_pct": 40.0,
        "current_balance_jod": 10.0,
        "requested_amount_jod": 1000
    })
    
    result = engine.run_pipeline(user_data)
    
    assert 0 <= result['final_score'] <= 100
    assert result['risk_level'] in ["Low", "Medium", "High", "Critical"]
    assert result['approved_amount_jod'] >= 0
    
    # 1% Exploration Loop could randomly approve, but amount is at most 100. Or it is rejected.
    # The rule says if avg_monthly_income < 50, it rejects. Here it's 300, so it might be Conditional or Rejected.
    # Actually, 5 late bills with low stability will yield a low score.
    # The override cap applies if late bills >= 4.
    
    assert result['final_score'] <= 50 or result.get('approved_amount_jod') <= 150

def test_middle_income_conditional(engine, base_user_data):
    """Test a profile on the edge that might get Conditional Approval."""
    user_data = base_user_data.copy()
    user_data.update({
        "avg_monthly_income_jod": 700.0,
        "income_stability_score": 0.6,
        "late_bills_count": 2,
        "bill_reliability_pct": 75.0,
        "current_balance_jod": 300.0,
        "requested_amount_jod": 400
    })
    
    result = engine.run_pipeline(user_data)
    
    assert 0 <= result['final_score'] <= 100
    assert result['risk_level'] in ["Low", "Medium", "High", "Critical"]
    assert result['approved_amount_jod'] >= 0

def test_missing_data_resilience(engine):
    """Test that the engine handles missing columns gracefully with defaults."""
    user_data = {
        "name": "Ghost User",
        # Missing almost everything, including profession, income, etc.
        "requested_amount_jod": 100
    }
    
    # Should not raise KeyError or ValueError
    result = engine.run_pipeline(user_data)
    
    assert 0 <= result['final_score'] <= 100
    assert result['risk_level'] in ["Low", "Medium", "High", "Critical"]
    assert result['approved_amount_jod'] >= 0

def test_late_bills_override(engine, base_user_data):
    """Test the business rule override for late_bills_count >= 4."""
    user_data = base_user_data.copy()
    user_data.update({
        # High income that would normally get a high score
        "avg_monthly_income_jod": 5000.0,
        "income_stability_score": 0.99,
        "current_balance_jod": 10000.0,
        "late_bills_count": 4, # TRIGGER
        "requested_amount_jod": 1000
    })
    
    result = engine.run_pipeline(user_data)
    
    assert 0 <= result['final_score'] <= 100
    assert result['risk_level'] in ["Low", "Medium", "High", "Critical"]
    assert result['approved_amount_jod'] >= 0
    
    # The override rule caps the score at 50 if score was > 50.
    assert result['final_score'] <= 50
    # And caps approved_amount at 150
    assert result['approved_amount_jod'] <= 150
    assert result['decision'] in ["Conditional Approval", "Rejected", "Approved (Exploration Cohort)"]
