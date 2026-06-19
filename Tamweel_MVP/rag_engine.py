import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# ─── 1. CONFIGURATION ────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=ANTHROPIC_API_KEY)

# ─── 2. RAG KNOWLEDGE BASE ───────────────────────────────────────────────────
RAG_KNOWLEDGE_BASE = {
    "market_benchmarks": """
Jordan Informal Economy Credit Context:
Market Benchmarks:
- Minimum wage: 260 JOD/month
- Average informal worker income: 150-400 JOD/month
- ZainCash avg monthly transaction: 180 JOD
- CliQ avg monthly transfer: 220 JOD
- Microloan range: 100-1000 JOD
""",
    "score_thresholds": """
Score Thresholds:
- 80-100: Excellent → Approved up to 1000 JOD
- 60-79:  Good → Approved up to 600 JOD
- 45-59:  Fair → Conditional Approval up to 300 JOD
- 30-44:  Poor → Conditional Approval up to 150 JOD
- 0-29:   High Risk → Rejected
""",
    "scoring_weights": """
Scoring Weights:
- Income Stability: 40%
- Bill Payment History: 30%
- Financial Health: 30%
""",
    "red_flags": """
Red Flags:
- 3+ late bill payments: -25 points
- Balance near zero consistently: -15 points
- Zero income transfers 30+ days: -20 points
""",
    "freelance_pattern": """
Upwork/Freelancer Income Patterns Jordan:
- irregular, traceable 1-4 weeks
- Payment regularity varies based on project milestones
""",
    "gig_pattern": """
Gig Economy Patterns Jordan (Uber/Careem/Delivery):
- daily small amounts, highly regular
- Daily income peaks on weekends
"""
}

# ─── 3. RAG RETRIEVAL ────────────────────────────────────────────────────────

def retrieve_context(user_data):
    """
    Retrieves relevant chunks from knowledge base based on user data.
    """
    context_chunks = [
        RAG_KNOWLEDGE_BASE["market_benchmarks"],
        RAG_KNOWLEDGE_BASE["score_thresholds"],
        RAG_KNOWLEDGE_BASE["scoring_weights"]
    ]
    
    if user_data.get('late_bills_count', 0) > 2:
        context_chunks.append(RAG_KNOWLEDGE_BASE["red_flags"])
        
    profession = user_data.get('profession_category', '').lower()
    if 'freelance' in profession:
        context_chunks.append(RAG_KNOWLEDGE_BASE["freelance_pattern"])
    elif 'gig' in profession:
        context_chunks.append(RAG_KNOWLEDGE_BASE["gig_pattern"])
        
    return "\n".join(context_chunks)

# ─── 4. CLAUDE INTEGRATION ───────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are Tamweel AI, an expert credit analyst specializing in Jordan's informal economy.
Your task is to review a credit application and provide a final score and explanation.

RAG CONTEXT:
{context}

RULES:
1. Use the provided XGBoost ML Score as the base.
2. You can adjust the ML score by a MAXIMUM of ±5 points based on the context.
3. Scoring weights: Income Stability (40%), Bill History (30%), Financial Health (30%).
4. Return ONLY a valid JSON object.
5. Provide a professional explanation in Arabic. STRICT CONSTRAINTS: The explanation must be exactly 1 to 3 lines long. ABSOLUTELY NO EMOJIS or informal symbols.
6. Decision tiers:
   - 80-100: Approved (Max 1000 JOD)
   - 60-79: Approved (Max 600 JOD)
   - 45-59: Conditional Approval (Max 300 JOD)
   - 30-44: Conditional Approval (Max 150 JOD)
   - 0-29: Rejected (0 JOD)

EXAMPLES:
1. Excellent:
   Input: ML Score 85, Stable income, No late bills.
   Output: {{"ml_score": 85, "llm_adjusted_score": 87, "final_score": 87, "risk_level": "Low", "decision": "Approved", "approved_amount_jod": 1000, "key_strengths": ["استقرار الدخل"], "key_risks": [], "reason": "يظهر ملفك المالي التزاماً استثنائياً واستقراراً عالياً في الدخل، مما يجعلك مؤهلاً للحصول على التمويل."}}

2. Fair:
   Input: ML Score 50, Irregular income, 1 late bill.
   Output: {{"ml_score": 50, "llm_adjusted_score": 48, "final_score": 48, "risk_level": "Medium", "decision": "Conditional Approval", "approved_amount_jod": 250, "key_strengths": ["نشاط الحساب"], "key_risks": ["تأخير السداد"], "reason": "تمت الموافقة المشروطة نظراً لتأخر السداد الأخير وتذبذب الرصيد الشهري. يرجى الالتزام لتحسين التقييم."}}

3. Poor:
   Input: ML Score 25, Many late bills, Zero balance.
   Output: {{"ml_score": 25, "llm_adjusted_score": 22, "final_score": 22, "risk_level": "High", "decision": "Rejected", "approved_amount_jod": 0, "key_strengths": [], "key_risks": ["تراكم الديون", "رصيد صفري"], "reason": "نعتذر عن تلبية طلبك بسبب تراكم الديون وتكرار التأخير في السداد. يرجى تصويب الأوضاع المالية أولاً."}}
"""

def generate_explanation(user_data, ml_score, financial_metrics=None):
    """
    Generates professional Arabic explanation using Claude with RAG.
    """
    context = retrieve_context(user_data)
    
    financial_str = ""
    if financial_metrics:
        financial_str = f"""
TRANSACTION INSIGHTS:
- Savings Rate: {financial_metrics.get('savings_rate', 0)}
- Spending Volatility: {financial_metrics.get('volatility', 0)}
- Bill Reliability: {financial_metrics.get('reliability', 0)}
- Top Expense Category: {financial_metrics.get('top_category', 'None')}
"""

    user_prompt = f"""
USER FINANCIAL DATA:
- Profession Category: {user_data.get('profession_category')}
- Avg Monthly Income: {user_data.get('avg_monthly_income_jod')} JOD
- Income Stability: {user_data.get('income_stability_score')}
- Late Bills: {user_data.get('late_bills_count')}
- Bill Reliability: {user_data.get('bill_reliability_pct')}%
- Current Balance: {user_data.get('current_balance_jod')} JOD
- Balance/Income Ratio: {user_data.get('balance_to_income_ratio')}
- Wallet Volume: {user_data.get('wallet_total_volume_jod')} JOD
{financial_str}

XGBOOST ML SCORE: {ml_score}

TASK:
1. Perform Chain-of-Thought analysis.
2. Adjust ML score by max ±5 points.
3. Determine risk level, decision, and approved amount.
4. Provide score breakdown.
5. Provide 2 strengths and 2 risks.
6. Write a professional Arabic reason. It MUST be 1 to 3 lines maximum. NO EMOJIS ALLOWED.
7. You MUST mention a specific spending category from the TRANSACTION INSIGHTS in your explanation (e.g., "Your high investment in Business Supplies indicates growth potential...").
8. Return JSON ONLY.
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=SYSTEM_PROMPT.format(context=context),
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Extract JSON from response
        content = response.content[0].text
        # Clean up in case Claude adds markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)
    except Exception as e:
        print(f"  ❌ Claude API Error: {e}")
        # Improved Fallback based on ML Score tiers
        decision = "Rejected"
        amount = 0
        risk = "High"
        strengths = ["البيانات المالية الأساسية متوفرة"]
        risks = ["سجل المدفوعات محدود"]
        reason = "تم اتخاذ القرار بناءً على التحليل الرقمي المباشر للبيانات المالية البديلة المتوفرة."

        if ml_score >= 80:
            decision, amount, risk = "Approved", 1000, "Low"
            strengths = ["استقرار دخل ممتاز", "التزام تام بسداد الفواتير"]
            risks = ["تنوع مصادر الدخل يمكن أن يتحسن"]
            reason = "يظهر ملفك المالي التزاماً استثنائياً واستقراراً عالياً في الدخل، مما يجعلك مؤهلاً للحصول على الحد الأقصى للتمويل."
        elif ml_score >= 60:
            decision, amount, risk = "Approved", 600, "Low"
            strengths = ["دخل شهري منتظم", "نسبة سيولة جيدة"]
            risks = ["تأخير بسيط في فواتير المرافق"]
            reason = "لديك ملف ائتماني جيد جداً مع تدفقات نقدية مستقرة تدعم قدرتك على السداد بانتظام."
        elif ml_score >= 45:
            decision, amount, risk = "Conditional Approval", 300, "Medium"
            strengths = ["نشاط جيد في المحفظة الإلكترونية"],
            risks = ["تذبذب في الرصيد الشهري", "تأخير متكرر في الفواتير"]
            reason = "تمت الموافقة المشروطة نظراً لوجود بعض التذبذب في الدخل، ننصح بزيادة الاستقرار المالي لرفع السقف مستقبلاً."
        elif ml_score >= 30:
            decision, amount, risk = "Conditional Approval", 150, "Medium"
            strengths = ["وجود مصدر دخل ثابت"]
            risks = ["عدد الفواتير المتأخرة مرتفع", "نسبة الدين إلى الدخل عالية"]
            reason = "هناك مخاطر متوسطة مرتبطة بسجل السداد، تمت الموافقة على مبلغ محدود لبناء الثقة الائتمانية."

        return {
            "ml_score": int(ml_score),
            "llm_adjusted_score": int(ml_score),
            "final_score": int(ml_score),
            "risk_level": risk,
            "decision": decision,
            "approved_amount_jod": amount,
            "score_breakdown": {
                "income_stability": round(ml_score * 0.4, 1),
                "bill_history": round(ml_score * 0.3, 1),
                "financial_health": round(ml_score * 0.3, 1)
            },
            "key_strengths": strengths,
            "key_risks": risks,
            "reason": reason
        }
