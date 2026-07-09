import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.intent_classifier import classify_intent, IntentType

@pytest.mark.parametrize(
    "message, expected_intent, expected_filters",
    [
        # English Cases (8 cases)
        ("What is my credit score?", IntentType.PROFILE_LIGHT, {}),
        ("How much did I spend on food this month?", IntentType.TRANSACTIONS, {"category": "food"}),
        ("How much did I spend on uber last week?", IntentType.TRANSACTIONS, {"category": "transport"}),
        ("Can I afford a car loan?", IntentType.DTI_ANALYSIS, {}),
        ("Give me a full financial health review.", IntentType.FULL_REVIEW, {}),
        ("Show me my recent transactions.", IntentType.TRANSACTIONS, {}),
        ("Tell me about my income.", IntentType.PROFILE_LIGHT, {}),
        ("What is compound interest?", IntentType.GENERIC, {}),
        
        # Arabic Cases (5 cases)
        ("هل أستطيع الحصول على قرض سيارة؟", IntentType.DTI_ANALYSIS, {}),
        ("كم أنفقت على الطعام هذا الشهر؟", IntentType.TRANSACTIONS, {"category": "food"}),
        ("ما هي درجة الائتمان الخاصة بي؟", IntentType.PROFILE_LIGHT, {}),
        ("أعطني مراجعة شاملة لوضعي المالي.", IntentType.FULL_REVIEW, {}),
        ("ما هو الفرق بين الفائدة البسيطة والمركبة؟", IntentType.GENERIC, {}),
        
        # Additional boundary cases just in case
        ("I spent money on netflix", IntentType.TRANSACTIONS, {"category": "entertainment"}),
        ("كم أنفقت على سينما؟", IntentType.TRANSACTIONS, {"category": "entertainment"}),
    ]
)
def test_classify_intent(message, expected_intent, expected_filters):
    result = classify_intent(message)
    assert result.intent == expected_intent, f"Failed on message: {message}"
    assert result.filters == expected_filters, f"Failed filters on message: {message}"
