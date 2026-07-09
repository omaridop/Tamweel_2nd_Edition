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
