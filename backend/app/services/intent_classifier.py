from enum import Enum
from dataclasses import dataclass, field
from typing import Dict
import rapidfuzz

class IntentType(Enum):
    GENERIC = "GENERIC"
    PROFILE_LIGHT = "PROFILE_LIGHT"
    TRANSACTIONS = "TRANSACTIONS"
    DTI_ANALYSIS = "DTI_ANALYSIS"
    FINANCIAL_ADVICE = "FINANCIAL_ADVICE"
    FULL_REVIEW = "FULL_REVIEW"
    HYBRID = "HYBRID"

@dataclass
class IntentResult:
    intent: IntentType
    filters: Dict[str, str] = field(default_factory=dict)

# --- Keywords & Constants ---
POLICY_KEYWORDS = {
    "someone with", "for a score of", "what happens if", "maximum loan amount", 
    "loan requirements", "approval criteria", "average score", "what determines",
    "larger loan", "get a larger loan"
}
PERSONAL_KEYWORDS = {
    "my credit score", "my score", "my account", "my loan", "my credit limit", 
    "my transactions", "my spending", "my income", "my profile",
    "درجتي", "حسابي", "راتبي", "دخلي", "مصروفاتي", "معاملاتي"
}

DTI_KEYWORDS = {
    "afford", "loan", "borrow", "debt", "mortgage", "car loan", 
    "monthly payment", "installment", "dti", "debt to income", "can i get", "car", "vehicle"
}
DTI_KEYWORDS_AR = {
    "أتحمل", "قرض", "اقتراض", "دين", "رهن", "قسط",
    "دفعة شهرية", "تمويل", "هل أستطيع", "هل يمكنني",
    "سيارة", "تمويل سيارة", "نسبة الدين"
}

FULL_REVIEW_KEYWORDS = {
    "full review", "financial health", "overview", "summary", 
    "everything", "overall", "approved", "rejected", "decision", "risk level",
    "why was my application"
}
FULL_REVIEW_KEYWORDS_AR = {
    "مراجعة شاملة", "الصحة المالية", "نظرة عامة",
    "ملخص", "كل شيء", "بشكل عام", "وضعي المالي", "موافقة", "مرفوض", "قرار", "مستوى الخطر"
}

TRANSACTION_KEYWORDS = {
    "spend", "spent", "spending", "transactions", "bought", 
    "purchases", "how much did i", "last month", "this month", 
    "category", "food", "restaurant", "groceries", "uber", 
    "transfer", "withdrawal"
}
TRANSACTION_KEYWORDS_AR = {
    "أنفقت", "إنفاق", "معاملات", "مشتريات", "اشتريت",
    "كم أنفقت", "الشهر الماضي", "هذا الشهر", "فئة",
    "طعام", "مطعم", "بقالة", "تحويل", "سحب"
}

PROFILE_LIGHT_KEYWORDS = {
    "credit score", "my score", "my income", "my salary", 
    "my balance", "my profile", "my rating", "maximum account limit",
    "approved amount", "profession", "monthly income", "account limit",
    "maximum limit", "limit for my account", "my limit", "limit on my account",
    "approved limit", "job", "work", "career", "occupation", "employment", 
    "field", "sector"
}
PROFILE_LIGHT_KEYWORDS_AR = {
    "درجة الائتمان", "درجتي", "دخلي", "راتبي",
    "رصيدي", "ملفي", "تقييمي", "الحد الأقصى", "المبلغ المعتمد", "مهنتي", "الدخل الشهري",
    "الحد لحسابي", "حدي الأقصى", "حد حسابي", "وظيفتي", "عملي"
}

ADVICE_KEYWORDS = {
    "save", "saving", "savings", "advice", "recommend", "improve", "plan",
    "budget", "cut", "reduce", "spend less", "help me", "what should i",
    "how can i", "tips", "suggestion", "raise my score", "score up",
    "financial plan", "money management", "where am i wasting", "better",
    "lower my spending", "increase my savings", "afford", "goal"
}
ADVICE_KEYWORDS_AR = {
    "ادخر", "توفير", "ادخار", "نصيحة", "أنصحني", "خطة", "ميزانية",
    "كيف أحسن", "كيف أوفر", "ماذا أفعل", "ساعدني", "وين أخسر",
    "كيف أرفع", "تحسين", "نصائح", "اقتراح", "تقليل", "أوفر فلوس",
    "خطة مالية", "إدارة المال", "وفر", "رفع النقاط"
}

POSSESSIVE_WORDS = {'my', 'mine', 'i have', 'my account', 'لدي', 'حسابي', 'عندي'}

# Transaction Category Keywords
CAT_FOOD = ["food", "restaurant", "groceries", "طعام", "مطعم", "بقالة"]
CAT_TRANSPORT = ["uber", "taxi", "transport", "gas", "تاكسي", "مواصلات", "وقود"]
CAT_ENTERTAINMENT = ["netflix", "cinema", "entertainment", "سينما", "ترفيه"]


def _extract_transaction_filters(message_lower: str, is_fuzzy: bool = False) -> Dict[str, str]:
    """Helper to detect transaction categories either via exact match or fuzzy match."""
    filters = {}
    if not is_fuzzy:
        if any(kw in message_lower for kw in CAT_FOOD):
            filters["category"] = "food"
        elif any(kw in message_lower for kw in CAT_TRANSPORT):
            filters["category"] = "transport"
        elif any(kw in message_lower for kw in CAT_ENTERTAINMENT):
            filters["category"] = "entertainment"
    else:
        if any(rapidfuzz.fuzz.partial_ratio(c, message_lower) >= 82 for c in CAT_FOOD):
            filters["category"] = "food"
        elif any(rapidfuzz.fuzz.partial_ratio(c, message_lower) >= 82 for c in CAT_TRANSPORT):
            filters["category"] = "transport"
        elif any(rapidfuzz.fuzz.partial_ratio(c, message_lower) >= 82 for c in CAT_ENTERTAINMENT):
            filters["category"] = "entertainment"
    return filters


def classify_intent(message: str) -> IntentResult:
    message_lower = message.lower()
    
    # 1. Explicit routing checks (Bug #1 Fix)
    is_policy = any(kw in message_lower for kw in POLICY_KEYWORDS)
    is_personal = any(kw in message_lower for kw in PERSONAL_KEYWORDS)
    
    if is_policy and is_personal:
        return IntentResult(intent=IntentType.HYBRID)
    if is_policy and not is_personal:
        return IntentResult(intent=IntentType.GENERIC)

    # 2. Priority matching: DTI_ANALYSIS > FINANCIAL_ADVICE > FULL_REVIEW > TRANSACTIONS > PROFILE_LIGHT > GENERIC
    if any(kw in message_lower for kw in DTI_KEYWORDS) or any(kw in message_lower for kw in DTI_KEYWORDS_AR):
        return IntentResult(intent=IntentType.DTI_ANALYSIS)
        
    if any(kw in message_lower for kw in ADVICE_KEYWORDS) or any(kw in message_lower for kw in ADVICE_KEYWORDS_AR):
        return IntentResult(intent=IntentType.FINANCIAL_ADVICE)
        
    if any(kw in message_lower for kw in FULL_REVIEW_KEYWORDS) or any(kw in message_lower for kw in FULL_REVIEW_KEYWORDS_AR):
        return IntentResult(intent=IntentType.FULL_REVIEW)
        
    if any(kw in message_lower for kw in TRANSACTION_KEYWORDS) or any(kw in message_lower for kw in TRANSACTION_KEYWORDS_AR):
        filters = _extract_transaction_filters(message_lower, is_fuzzy=False)
        return IntentResult(intent=IntentType.TRANSACTIONS, filters=filters)
        
    if any(kw in message_lower for kw in PROFILE_LIGHT_KEYWORDS) or any(kw in message_lower for kw in PROFILE_LIGHT_KEYWORDS_AR):
        return IntentResult(intent=IntentType.PROFILE_LIGHT)
        
    # 3. Fuzzy matching fallback
    if len(message_lower) < 200:
        keyword_groups = [
            (IntentType.DTI_ANALYSIS, DTI_KEYWORDS.union(DTI_KEYWORDS_AR)),
            (IntentType.FINANCIAL_ADVICE, ADVICE_KEYWORDS.union(ADVICE_KEYWORDS_AR)),
            (IntentType.FULL_REVIEW, FULL_REVIEW_KEYWORDS.union(FULL_REVIEW_KEYWORDS_AR)),
            (IntentType.TRANSACTIONS, TRANSACTION_KEYWORDS.union(TRANSACTION_KEYWORDS_AR)),
            (IntentType.PROFILE_LIGHT, PROFILE_LIGHT_KEYWORDS.union(PROFILE_LIGHT_KEYWORDS_AR))
        ]
        
        for intent_type, kw_set in keyword_groups:
            for kw in kw_set:
                if rapidfuzz.fuzz.partial_ratio(kw, message_lower) >= 82:
                    if intent_type == IntentType.TRANSACTIONS:
                        filters = _extract_transaction_filters(message_lower, is_fuzzy=True)
                        return IntentResult(intent=IntentType.TRANSACTIONS, filters=filters)
                    return IntentResult(intent=intent_type)
                    
    # 4. Possessive fallback rule
    if any(kw in message_lower for kw in POSSESSIVE_WORDS):
        return IntentResult(intent=IntentType.PROFILE_LIGHT)

    return IntentResult(intent=IntentType.GENERIC)

if __name__ == "__main__":
    # Unit tests
    test_cases = [
        "What is compound interest?",
        "What is my credit score?",
        "what is my credi score?",
        "How much did I spend on food this month?",
        "Can I afford a car loan?",
        "Give me a full financial health review.",
        "How much did I spend on uber last week?",
        "Show me my recent transactions.",
        "Tell me about my income.",
        "what is my job?",
        "هل أستطيع الحصول على قرض سيارة؟",
        "كم أنفقت على الطعام هذا الشهر؟",
        "ما هي درجة الائتمان الخاصة بي؟",
        "أعطني مراجعة شاملة لوضعي المالي.",
        "ما هو الفرق بين الفائدة البسيطة والمركبة؟"
    ]
    
    print("Testing Intent Classifier:")
    print("-" * 50)
    for msg in test_cases:
        result = classify_intent(msg)
        filters_str = f" | Filters: {result.filters}" if result.filters else ""
        print(f"Message: '{msg}'")
        print(f"-> Intent: {result.intent.value}{filters_str}\n")
