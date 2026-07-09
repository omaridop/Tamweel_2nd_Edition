import sys
import os
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

# Mock env before import
os.environ["JWT_SECRET_KEY"] = "mock"

from app.ml.hybrid_engine import TamweelHybridEngine

def test_model_loads_successfully():
    """Assert that the ML model (Hybrid Engine) loads successfully."""
    try:
        engine = TamweelHybridEngine()
        assert engine.model is not None
        assert engine.scaler is not None
        assert engine.le is not None
        assert engine.feature_names is not None
    except Exception as e:
        pytest.fail(f"Model failed to load: {e}")

@patch("app.ml.hybrid_engine.generate_explanation")
@patch("app.ml.hybrid_engine.TamweelHybridEngine.predict_ml")
def test_prediction_logic_executes(mock_predict, mock_explanation):
    """Assert prediction logic executes and returns deterministic structure."""
    mock_predict.return_value = 85.0
    mock_explanation.return_value = {"key_strengths": ["test"], "key_risks": [], "reason": "Test reason"}
    
    engine = TamweelHybridEngine()
    
    test_data = {
        "avg_monthly_income_jod": 1000,
        "email": "test@example.com",
        "_authenticated_email": "test@example.com"
    }
    
    result = engine.run_pipeline(test_data)
    
    assert "ml_score" in result
    assert result["ml_score"] == 85.0
    assert "decision" in result
    assert result["decision"] == "Approved"
    assert "risk_level" in result
