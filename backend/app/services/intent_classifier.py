from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
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

POSSESSIVE_WORDS = {'my', 'mine', 'i have', 'my account', 'لدي', 'حسابي', 'عندي'}

# Transaction category keyword lists (used by _extract_transaction_filters)
CAT_FOOD = ["food", "restaurant", "groceries", "طعام", "مطعم", "بقالة"]
CAT_TRANSPORT = ["uber", "taxi", "transport", "gas", "تاكسي", "مواصلات", "وقود"]
CAT_ENTERTAINMENT = ["netflix", "cinema", "entertainment", "سينما", "ترفيه"]

# Ordered priority list: (IntentType, combined_keyword_set)
# Both exact and fuzzy matching iterate this same structure to avoid duplication.
_KEYWORD_GROUPS: List[Tuple[IntentType, set]] = [
    (IntentType.DTI_ANALYSIS, {
        "afford", "loan", "borrow", "debt", "mortgage", "car loan",
        "monthly payment", "installment", "dti", "debt to income", "can i get", "car", "vehicle",
        "أتحمل", "قرض", "اقتراض", "دين", "رهن", "قسط",
        "دفعة شهرية", "تمويل", "هل أستطيع", "هل يمكنني",
        "سيارة", "تمويل سيارة", "نسبة الدين"
    }),
    (IntentType.FINANCIAL_ADVICE, {
        "save", "saving", "savings", "advice", "recommend", "improve", "plan",
        "budget", "cut", "reduce", "spend less", "help me", "what should i",
        "how can i", "tips", "suggestion", "raise my score", "score up",
        "financial plan", "money management", "where am i wasting", "better",
        "lower my spending", "increase my savings", "afford", "goal",
        "ادخر", "توفير", "ادخار", "نصيحة", "أنصحني", "خطة", "ميزانية",
        "كيف أحسن", "كيف أوفر", "ماذا أفعل", "ساعدني", "وين أخسر",
        "كيف أرفع", "تحسين", "نصائح", "اقتراح", "تقليل", "أوفر فلوس",
        "خطة مالية", "إدارة المال", "وفر", "رفع النقاط"
    }),
    (IntentType.FULL_REVIEW, {
        "full review", "financial health", "overview", "summary",
        "everything", "overall", "approved", "rejected", "decision", "risk level",
        "why was my application",
        "مراجعة شاملة", "الصحة المالية", "نظرة عامة",
        "ملخص", "كل شيء", "بشكل عام", "وضعي المالي", "موافقة", "مرفوض", "قرار", "مستوى الخطر"
    }),
    (IntentType.TRANSACTIONS, {
        "spend", "spent", "spending", "transactions", "bought",
        "purchases", "how much did i", "last month", "this month",
        "category", "food", "restaurant", "groceries", "uber",
        "transfer", "withdrawal",
        "أنفقت", "إنفاق", "معاملات", "مشتريات", "اشتريت",
        "كم أنفقت", "الشهر الماضي", "هذا الشهر", "فئة",
        "طعام", "مطعم", "بقالة", "تحويل", "سحب"
    }),
    (IntentType.PROFILE_LIGHT, {
        "credit score", "my score", "my income", "my salary",
        "my balance", "my profile", "my rating", "maximum account limit",
        "approved amount", "profession", "monthly income", "account limit",
        "maximum limit", "limit for my account", "my limit", "limit on my account",
        "approved limit", "job", "work", "career", "occupation", "employment",
        "field", "sector",
        "درجة الائتمان", "درجتي", "دخلي", "راتبي",
        "رصيدي", "ملفي", "تقييمي", "الحد الأقصى", "المبلغ المعتمد", "مهنتي", "الدخل الشهري",
        "الحد لحسابي", "حدي الأقصى", "حد حسابي", "وظيفتي", "عملي"
    }),
]


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

    # 2. Priority exact matching: DTI > FINANCIAL_ADVICE > FULL_REVIEW > TRANSACTIONS > PROFILE_LIGHT
    for intent_type, kw_set in _KEYWORD_GROUPS:
        if any(kw in message_lower for kw in kw_set):
            if intent_type == IntentType.TRANSACTIONS:
                filters = _extract_transaction_filters(message_lower, is_fuzzy=False)
                return IntentResult(intent=IntentType.TRANSACTIONS, filters=filters)
            return IntentResult(intent=intent_type)

    # 3. Fuzzy matching fallback (only for short messages to avoid false positives)
    if len(message_lower) < 200:
        for intent_type, kw_set in _KEYWORD_GROUPS:
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
