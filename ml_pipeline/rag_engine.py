import os
import json
import logging
from anthropic import Anthropic
from dotenv import load_dotenv
from typing import Dict, Any, Optional

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def retrieve_context(user_data: Dict[str, Any]) -> str:
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

# ─── 4. SCORE BREAKDOWN (DETERMINISTIC) ──────────────────────────────────────

def compute_score_breakdown(ml_score: float) -> Dict[str, float]:
    """
    Computes a deterministic, proportional score breakdown from the ML score.
    This is NEVER modified by the LLM — it is set once here and passed read-only
    to generate_explanation().
    """
    return {
        "income_stability": round(ml_score * 0.4, 1),
        "bill_history": round(ml_score * 0.3, 1),
        "financial_health": round(ml_score * 0.3, 1),
    }

# ─── 5. EXPLANATION SYSTEM PROMPT (explanation-only — score is read-only) ────

# ARCHITECTURAL NOTE (Part B remediation):
# The LLM receives the final_score as a FIXED INPUT. It is forbidden from returning
# a numeric score field — only text explanation fields are parsed from its response.
# The `ml_score` and `final_score` in the result dict are ALWAYS sourced from the
# deterministic ML pipeline in hybrid_engine.py, never from this function.

EXPLANATION_SYSTEM_PROMPT = """
You are Tamweel AI, an expert credit analyst specializing in Jordan's informal economy.
Your ONLY task is to generate a human-readable explanation for a credit decision that
has ALREADY been made by a validated statistical model. You do NOT produce, adjust, or
influence the score in any way.

RAG CONTEXT:
{context}

STRICT RULES:
1. The credit score, decision, and approved amount have already been determined by the
   XGBoost ML model + hard business rules. You MUST accept them as-is — DO NOT suggest
   different scores, decisions, or amounts.
2. Your output is a JSON with ONLY the explanation fields listed below.
3. Provide a professional explanation in Arabic. STRICT CONSTRAINTS: exactly 1 to 3 lines.
   ABSOLUTELY NO EMOJIS or informal symbols.
4. Strengths and risks must reference only facts explicitly present in the user data.
   Do NOT invent statistics or make up reasons.
"""

def generate_explanation(user_data: Dict[str, Any], ml_score: float, financial_metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generates a human-readable Arabic explanation for a credit decision.

    ARCHITECTURAL CONTRACT (Part B remediation):
    - This function receives the final `ml_score` from the XGBoost model as a fixed input.
    - It returns ONLY explanation text fields: `key_strengths`, `key_risks`, `reason`.
    - It does NOT return `ml_score`, `llm_adjusted_score`, or `final_score`.
    - The caller (hybrid_engine.py `run_pipeline`) is solely responsible for setting
      all numeric score fields from the ML model output. This function has NO write
      access to those fields — they are merged AFTER this function returns.
    - Any attempt by the LLM to output numeric scores is explicitly ignored by the
      parser below, which only extracts the three allowed text fields.
    """
    context = retrieve_context(user_data)
    
    financial_str = ""
    if financial_metrics:
        financial_str = f"""
TRANSACTION INSIGHTS (for narrative context only):
- Savings Rate: {financial_metrics.get('savings_rate', 0)}
- Spending Volatility: {financial_metrics.get('volatility', 0)}
- Bill Reliability: {financial_metrics.get('reliability', 0)}
- Top Expense Category: {financial_metrics.get('top_category', 'None')}
"""

    # Derive decision label from ml_score for grounding the explanation
    if ml_score >= 80:
        decision_label, risk_label = "Approved (up to 1000 JOD)", "Low"
    elif ml_score >= 60:
        decision_label, risk_label = "Approved (up to 600 JOD)", "Low"
    elif ml_score >= 45:
        decision_label, risk_label = "Conditional Approval (up to 300 JOD)", "Medium"
    elif ml_score >= 30:
        decision_label, risk_label = "Conditional Approval (up to 150 JOD)", "Medium"
    else:
        decision_label, risk_label = "Rejected", "High"

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

FINAL CREDIT SCORE (ML model output, fixed): {ml_score:.1f}/100
DECISION (already determined): {decision_label}
RISK LEVEL (already determined): {risk_label}

TASK — Generate explanation text ONLY:
1. Identify 2 key strengths from the data above that support this score.
2. Identify 2 key risks from the data above that explain limitations.
3. Write a professional Arabic reason (1-3 lines, no emojis) explaining the decision
   to the applicant. Reference the actual decision label and specific data points.

Return ONLY this JSON (no score fields, no numeric adjustments):
{{
    "key_strengths": ["strength 1 in Arabic", "strength 2 in Arabic"],
    "key_risks": ["risk 1 in Arabic", "risk 2 in Arabic"],
    "reason": "Professional Arabic explanation referencing the decision and specific data."
}}
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            system=EXPLANATION_SYSTEM_PROMPT.format(context=context),
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        content = response.content[0].text
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        parsed = json.loads(content)

        # --- SCORE FIREWALL ---
        # Explicitly strip any numeric score fields the LLM might have included.
        # The caller sets these from the deterministic ML pipeline only.
        for forbidden_key in ("ml_score", "llm_adjusted_score", "final_score",
                              "decision", "approved_amount_jod", "risk_level"):
            parsed.pop(forbidden_key, None)

        return {
            "key_strengths": parsed.get("key_strengths", []),
            "key_risks": parsed.get("key_risks", []),
            "reason": parsed.get("reason", ""),
        }

    except Exception as e:
        logger.error(f"Claude API Error in generate_explanation: {e}", exc_info=True)
        # Deterministic fallback — still text only, no score influence
        if ml_score >= 80:
            strengths = ["استقرار دخل ممتاز", "التزام تام بسداد الفواتير"]
            risks = ["تنوع مصادر الدخل يمكن أن يتحسن"]
            reason = "يظهر ملفك المالي التزاماً استثنائياً واستقراراً عالياً في الدخل، مما يجعلك مؤهلاً للحصول على الحد الأقصى للتمويل."
        elif ml_score >= 60:
            strengths = ["دخل شهري منتظم", "نسبة سيولة جيدة"]
            risks = ["تأخير بسيط في فواتير المرافق"]
            reason = "لديك ملف ائتماني جيد جداً مع تدفقات نقدية مستقرة تدعم قدرتك على السداد بانتظام."
        elif ml_score >= 45:
            strengths = ["نشاط جيد في المحفظة الإلكترونية"]
            risks = ["تذبذب في الرصيد الشهري", "تأخير متكرر في الفواتير"]
            reason = "تمت الموافقة المشروطة نظراً لوجود بعض التذبذب في الدخل، ننصح بزيادة الاستقرار المالي لرفع السقف مستقبلاً."
        elif ml_score >= 30:
            strengths = ["وجود مصدر دخل ثابت"]
            risks = ["عدد الفواتير المتأخرة مرتفع", "نسبة الدين إلى الدخل عالية"]
            reason = "هناك مخاطر متوسطة مرتبطة بسجل السداد، تمت الموافقة على مبلغ محدود لبناء الثقة الائتمانية."
        else:
            strengths = ["البيانات المالية الأساسية متوفرة"]
            risks = ["سجل المدفوعات محدود", "مستوى المخاطرة مرتفع"]
            reason = "تم اتخاذ القرار بناءً على التحليل الرقمي المباشر للبيانات المالية البديلة المتوفرة."

        return {
            "key_strengths": strengths,
            "key_risks": risks,
            "reason": reason,
        }
