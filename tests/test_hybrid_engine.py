import sys
import os
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

os.environ["JWT_SECRET_KEY"] = "mock"

from app.ml.hybrid_engine import TamweelHybridEngine

@patch("app.ml.hybrid_engine.generate_explanation")
@patch("app.ml.hybrid_engine.TamweelHybridEngine.predict_ml")
def test_deterministic_score_calculation(mock_predict, mock_explanation):
    """Assert deterministic score calculation remains unchanged."""
    engine = TamweelHybridEngine()
    
    mock_explanation.return_value = {}
    
    # Test Tier 1 Hard Rule
    mock_predict.return_value = 85.0 
    res1 = engine.run_pipeline({"requested_amount_jod": 2000})
    assert res1["decision"] == "Approved"
    assert res1["approved_amount_jod"] <= 1000 # TIER_1_LIMIT is 1000
    
    # Test Tier 3 Hard Rule
    mock_predict.return_value = 50.0 
    res2 = engine.run_pipeline({"requested_amount_jod": 2000})
    assert res2["decision"] == "Conditional Approval"
    assert res2["approved_amount_jod"] <= 300 # TIER_3_LIMIT is 300

    # Test Late Bills Override Rule
    mock_predict.return_value = 85.0
    res3 = engine.run_pipeline({"late_bills_count": 5, "requested_amount_jod": 2000})
    assert res3["final_score"] == 50 # LATE_BILLS_SCORE_CAP
    assert res3["decision"] == "Conditional Approval"
