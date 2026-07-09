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

def classify_intent(message: str) -> IntentResult:
    message_lower = message.lower()
    
    # Explicit routing checks (Bug #1 Fix)
    policy_keywords = {
        "someone with", "for a score of", "what happens if", "maximum loan amount", 
        "loan requirements", "approval criteria", "average score", "what determines",
        "larger loan", "get a larger loan"
    }
    personal_keywords = {
        "my credit score", "my score", "my account", "my loan", "my credit limit", 
        "my transactions", "my spending", "my income", "my profile",
        "درجتي", "حسابي", "راتبي", "دخلي", "مصروفاتي", "معاملاتي"
    }
    
    is_policy = any(kw in message_lower for kw in policy_keywords)
    is_personal = any(kw in message_lower for kw in personal_keywords)
    
    if is_policy and is_personal:
        return IntentResult(intent=IntentType.HYBRID)
    if is_policy and not is_personal:
        return IntentResult(intent=IntentType.GENERIC)

    
    # Define keyword sets
    dti_keywords = {"afford", "loan", "borrow", "debt", "mortgage", "car loan", 
                    "monthly payment", "installment", "dti", "debt to income", "can i get", "car", "vehicle"}
    dti_keywords_ar = {
        "أتحمل", "قرض", "اقتراض", "دين", "رهن", "قسط",
        "دفعة شهرية", "تمويل", "هل أستطيع", "هل يمكنني",
        "سيارة", "تمويل سيارة", "نسبة الدين"
    }
    
    full_review_keywords = {"full review", "financial health", "overview", "summary", 
                            "everything", "overall", "approved", "rejected", "decision", "risk level",
                            "why was my application"}
    full_review_keywords_ar = {
        "مراجعة شاملة", "الصحة المالية", "نظرة عامة",
        "ملخص", "كل شيء", "بشكل عام", "وضعي المالي", "موافقة", "مرفوض", "قرار", "مستوى الخطر"
    }
    
    transaction_keywords = {"spend", "spent", "spending", "transactions", "bought", 
                            "purchases", "how much did i", "last month", "this month", 
                            "category", "food", "restaurant", "groceries", "uber", 
                            "transfer", "withdrawal"}
    transaction_keywords_ar = {
        "أنفقت", "إنفاق", "معاملات", "مشتريات", "اشتريت",
        "كم أنفقت", "الشهر الماضي", "هذا الشهر", "فئة",
        "طعام", "مطعم", "بقالة", "تحويل", "سحب"
    }
    
    profile_light_keywords = {"credit score", "my score", "my income", "my salary", 
                              "my balance", "my profile", "my rating", "maximum account limit",
                              "approved amount", "profession", "monthly income", "account limit",
                              "maximum limit", "limit for my account", "my limit", "limit on my account",
                              "approved limit", "job", "work", "career", "occupation", "employment", 
                              "field", "sector"}
    profile_light_keywords_ar = {
        "درجة الائتمان", "درجتي", "دخلي", "راتبي",
        "رصيدي", "ملفي", "تقييمي", "الحد الأقصى", "المبلغ المعتمد", "مهنتي", "الدخل الشهري",
        "الحد لحسابي", "حدي الأقصى", "حد حسابي", "وظيفتي", "عملي"
    }

    advice_keywords = {
        "save", "saving", "savings", "advice", "recommend", "improve", "plan",
        "budget", "cut", "reduce", "spend less", "help me", "what should i",
        "how can i", "tips", "suggestion", "raise my score", "score up",
        "financial plan", "money management", "where am i wasting", "better",
        "lower my spending", "increase my savings", "afford", "goal"
    }
    advice_keywords_ar = {
        "ادخر", "توفير", "ادخار", "نصيحة", "أنصحني", "خطة", "ميزانية",
        "كيف أحسن", "كيف أوفر", "ماذا أفعل", "ساعدني", "وين أخسر",
        "كيف أرفع", "تحسين", "نصائح", "اقتراح", "تقليل", "أوفر فلوس",
        "خطة مالية", "إدارة المال", "وفر", "رفع النقاط"
    }
    
    # Priority matching: DTI_ANALYSIS > FINANCIAL_ADVICE > FULL_REVIEW > TRANSACTIONS > PROFILE_LIGHT > GENERIC
    if any(kw in message_lower for kw in dti_keywords) or \
       any(kw in message_lower for kw in dti_keywords_ar):
        return IntentResult(intent=IntentType.DTI_ANALYSIS)
        
    if any(kw in message_lower for kw in advice_keywords) or \
       any(kw in message_lower for kw in advice_keywords_ar):
        return IntentResult(intent=IntentType.FINANCIAL_ADVICE)
        
    if any(kw in message_lower for kw in full_review_keywords) or \
       any(kw in message_lower for kw in full_review_keywords_ar):
        return IntentResult(intent=IntentType.FULL_REVIEW)
        
    if any(kw in message_lower for kw in transaction_keywords) or \
       any(kw in message_lower for kw in transaction_keywords_ar):
        filters = {}
        # Category detection
        if any(kw in message_lower for kw in ["food", "restaurant", "groceries", "طعام", "مطعم", "بقالة"]):
            filters["category"] = "food"
        elif any(kw in message_lower for kw in ["uber", "taxi", "transport", "gas", "تاكسي", "مواصلات", "وقود"]):
            filters["category"] = "transport"
        elif any(kw in message_lower for kw in ["netflix", "cinema", "entertainment", "سينما", "ترفيه"]):
            filters["category"] = "entertainment"
        return IntentResult(intent=IntentType.TRANSACTIONS, filters=filters)
        
    if any(kw in message_lower for kw in profile_light_keywords) or \
       any(kw in message_lower for kw in profile_light_keywords_ar):
        return IntentResult(intent=IntentType.PROFILE_LIGHT)
        
    # Fix 1: Fuzzy matching fallback
    if len(message_lower) < 200:
        keyword_groups = [
            (IntentType.DTI_ANALYSIS, dti_keywords.union(dti_keywords_ar)),
            (IntentType.FINANCIAL_ADVICE, advice_keywords.union(advice_keywords_ar)),
            (IntentType.FULL_REVIEW, full_review_keywords.union(full_review_keywords_ar)),
            (IntentType.TRANSACTIONS, transaction_keywords.union(transaction_keywords_ar)),
            (IntentType.PROFILE_LIGHT, profile_light_keywords.union(profile_light_keywords_ar))
        ]
        
        for intent_type, kw_set in keyword_groups:
            for kw in kw_set:
                if rapidfuzz.fuzz.partial_ratio(kw, message_lower) >= 82:
                    if intent_type == IntentType.TRANSACTIONS:
                        filters = {}
                        if any(rapidfuzz.fuzz.partial_ratio(c, message_lower) >= 82 for c in ["food", "restaurant", "groceries", "طعام", "مطعم", "بقالة"]):
                            filters["category"] = "food"
                        elif any(rapidfuzz.fuzz.partial_ratio(c, message_lower) >= 82 for c in ["uber", "taxi", "transport", "gas", "تاكسي", "مواصلات", "وقود"]):
                            filters["category"] = "transport"
                        elif any(rapidfuzz.fuzz.partial_ratio(c, message_lower) >= 82 for c in ["netflix", "cinema", "entertainment", "سينما", "ترفيه"]):
                            filters["category"] = "entertainment"
                        return IntentResult(intent=IntentType.TRANSACTIONS, filters=filters)
                    return IntentResult(intent=intent_type)
                    
    # Fix 2: Possessive fallback rule
    possessive_words = {'my', 'mine', 'i have', 'my account', 'لدي', 'حسابي', 'عندي'}
    if any(kw in message_lower for kw in possessive_words):
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
