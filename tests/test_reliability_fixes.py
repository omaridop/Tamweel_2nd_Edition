import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.services.intent_classifier import classify_intent, IntentType
import json

def test_intent_classification_personal():
    result = classify_intent("What is my credit score?")
    assert result.intent == IntentType.PROFILE_LIGHT

def test_intent_classification_general_rag():
    result = classify_intent("What is the maximum loan amount for someone with a score of 65?")
    assert result.intent == IntentType.GENERIC

def test_intent_classification_hybrid():
    result = classify_intent("Based on my score, how can I get a larger loan?")
    assert result.intent == IntentType.HYBRID

def test_intent_classification_dti():
    result = classify_intent("Can I afford a car loan?")
    assert result.intent == IntentType.DTI_ANALYSIS

def test_intent_classification_advice():
    result = classify_intent("How can I improve my finances and save more?")
    assert result.intent == IntentType.FINANCIAL_ADVICE

def test_intent_classification_full_review():
    result = classify_intent("Give me a full financial health review.")
    assert result.intent == IntentType.FULL_REVIEW

def test_intent_classification_transactions():
    result = classify_intent("How much did I spend on uber last week?")
    assert result.intent == IntentType.TRANSACTIONS
    assert result.filters.get("category") == "transport"

def test_intent_classification_arabic_dti():
    # Arabic example: Can I get a car loan? (هل أستطيع الحصول على قرض سيارة؟)
    result = classify_intent("هل أستطيع الحصول على قرض سيارة؟")
    assert result.intent == IntentType.DTI_ANALYSIS

def test_intent_classification_arabic_transactions():
    # Arabic example: How much did I spend on food this month?
    result = classify_intent("كم أنفقت على الطعام هذا الشهر؟")
    assert result.intent == IntentType.TRANSACTIONS
    assert result.filters.get("category") == "food"

def test_robust_json_extraction():
    # Simulate the robust extraction from chat.py
    def extract_json(response_text):
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
            json_str = response_text[start_idx:end_idx+1]
            return json.loads(json_str)
        raise ValueError("No valid JSON")

    # 1. Valid JSON
    valid_json = '{"answer": "Test", "support_score": 5}'
    assert extract_json(valid_json)["support_score"] == 5

    # 2. JSON wrapped in markdown
    md_json = '```json\n{"answer": "Test", "support_score": 5}\n```'
    assert extract_json(md_json)["support_score"] == 5

    # 3. JSON with extra text before/after
    dirty_json = 'Here is the evaluation:\n{"answer": "Test", "support_score": 5}\nHave a nice day!'
    assert extract_json(dirty_json)["support_score"] == 5

    # 4. Invalid JSON fallback
    invalid_json = 'There is no JSON here'
    with pytest.raises(ValueError):
        extract_json(invalid_json)

from unittest.mock import patch, MagicMock
import httpx
import openai
from fastapi.responses import JSONResponse
from app.routes.chat import _call_llm_with_fallback

def test_llm_fallback_network_error():
    with patch('app.routes.chat.openai_client.chat.completions.create') as mock_create:
        mock_create.side_effect = httpx.ConnectError("Network error")
        response = _call_llm_with_fallback([{"role": "user", "content": "test"}])
        assert isinstance(response, dict)
        assert "عذراً، واجهنا مشكلة في الاتصال بالخادم" in response["response"]
        assert response["support_score"] == 1

def test_llm_fallback_dual_failure():
    with patch('app.routes.chat.openai_client.chat.completions.create') as mock_create:
        # Fails for both DeepSeek (first call) and OpenRouter (second call)
        mock_create.side_effect = openai.APIConnectionError(request=MagicMock())
        response = _call_llm_with_fallback([{"role": "user", "content": "test"}])
        assert isinstance(response, JSONResponse)
        assert response.status_code == 503
        body = json.loads(response.body.decode('utf-8'))
        assert body["success"] is False
        assert "temporarily unavailable" in body["message"]

def test_llm_fallback_success():
    with patch('app.routes.chat.openai_client.chat.completions.create') as mock_create:
        mock_response = MagicMock()
        mock_create.return_value = mock_response
        response = _call_llm_with_fallback([{"role": "user", "content": "test"}])
        assert response == mock_response
