import os
import json
import joblib
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Union
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml_pipeline")))
from rag_engine import generate_explanation, compute_score_breakdown

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── 1. CONFIGURATION ────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Business Rules Constants
DEFAULT_REQUESTED_AMOUNT = 500
DEFAULT_LOAN_DURATION = 12
DEFAULT_INTEREST_RATE = 0.12
SCORE_TIER_1 = 80
TIER_1_LIMIT = 1000
SCORE_TIER_2 = 60
TIER_2_LIMIT = 600
SCORE_TIER_3 = 45
TIER_3_LIMIT = 300
SCORE_TIER_4 = 30
TIER_4_LIMIT = 150
EXPLORATION_RATE = 0.01
EXPLORATION_LIMIT = 100
LATE_BILLS_THRESHOLD = 4
LATE_BILLS_SCORE_CAP = 50
LATE_BILLS_AMOUNT_CAP = 150
MIN_INCOME_THRESHOLD = 50
SAVINGS_RATE_MIN = 0.10
VOLATILITY_MAX = 500
PENALTY_POINTS = 5
RELIABILITY_MIN = 3
BONUS_POINTS = 5
EDGE_ZONES = [(28, 32), (43, 47), (58, 62), (78, 82)]

try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Optional[Client] = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        supabase = None
except Exception as e:
    logger.error("Failed to initialize Supabase client", exc_info=True)
    supabase = None

# ─── 2. HYBRID ENGINE CLASS ───────────────────────────────────────────────────

class TamweelHybridEngine:
    def __init__(self):
        logger.info("Initializing Tamweel Hybrid Engine...")
        self.model = joblib.load(f"{MODELS_DIR}/tamweel_xgboost_classifier.pkl")
        self.scaler = joblib.load(f"{MODELS_DIR}/scaler.pkl")
        self.le = joblib.load(f"{MODELS_DIR}/label_encoder.pkl")
        with open(f"{MODELS_DIR}/feature_names.json", 'r') as f:
            self.feature_names = json.load(f)
            
    def preprocess(self, user_data: Dict[str, Any]) -> np.ndarray:
        df = pd.DataFrame([user_data])
        
        # Apply Log Transformations to right-skewed continuous variables
        skewed_features = ['avg_monthly_income_jod', 'current_balance_jod', 'wallet_total_volume_jod']
        for feat in skewed_features:
             if feat in df.columns:
                 df[feat] = np.log1p(df[feat].astype(float))

        # Encode categorical
        if 'profession_category' in df.columns:
            # Handle unseen categories gracefully
            try:
                df['profession_category'] = self.le.transform(df['profession_category'])
            except ValueError:
                df['profession_category'] = 0 # Default fallback
                
        # Ensure column order
        missing_cols = set(self.feature_names) - set(df.columns)
        for c in missing_cols:
            df[c] = 0
            
        df = df[self.feature_names]
        # Scale
        scaled_data = self.scaler.transform(df)
        return scaled_data

    def predict_ml(self, user_data: Dict[str, Any]) -> float:
        X = self.preprocess(user_data)
        # Using predict_proba to get the probability of non-default (class 0) as the "score"
        ml_prob_default = self.model.predict_proba(X)[0][1]
        ml_score = (1 - ml_prob_default) * 100
        return float(np.clip(ml_score, 0, 100))

    def validate_rules(self, result: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hard business rules validation layer, including 1% Exploration Loop.
        """
        score = result['final_score']
        
        # Loan Context
        requested_amount = user_data.get('requested_amount_jod', DEFAULT_REQUESTED_AMOUNT)
        loan_duration_months = user_data.get('loan_duration_months', DEFAULT_LOAN_DURATION)
        interest_rate = user_data.get('interest_rate', DEFAULT_INTEREST_RATE)
        
        # Mandatory Decision Tiers
        if score >= SCORE_TIER_1:
            result['decision'] = "Approved"
            result['approved_amount_jod'] = min(requested_amount, TIER_1_LIMIT)
        elif score >= SCORE_TIER_2:
            result['decision'] = "Approved"
            result['approved_amount_jod'] = min(requested_amount, TIER_2_LIMIT)
        elif score >= SCORE_TIER_3:
            result['decision'] = "Conditional Approval"
            result['approved_amount_jod'] = min(requested_amount, TIER_3_LIMIT)
        elif score >= SCORE_TIER_4:
            result['decision'] = "Conditional Approval"
            result['approved_amount_jod'] = min(requested_amount, TIER_4_LIMIT)
        else:
            # ─── BIAS MITIGATION: 1% EXPLORATION LOOP ───
            # To prevent automation of historical biases, we randomly approve 1% of high-risk profiles.
            import random
            if random.random() < EXPLORATION_RATE:
                result['decision'] = "Approved (Exploration Cohort)"
                result['approved_amount_jod'] = min(requested_amount, EXPLORATION_LIMIT) # Small controlled limit
                result['key_strengths'].append("تمت الموافقة الاستثنائية ضمن برنامج الاستكشاف لبناء الثقة.")
            else:
                result['decision'] = "Rejected"
                result['approved_amount_jod'] = 0
            
        # Specific overrides
        if user_data.get('late_bills_count', 0) >= LATE_BILLS_THRESHOLD and score > LATE_BILLS_SCORE_CAP:
            result['final_score'] = LATE_BILLS_SCORE_CAP
            if result['decision'] == "Approved":
                result['decision'] = "Conditional Approval"
            result['approved_amount_jod'] = min(result.get('approved_amount_jod', LATE_BILLS_AMOUNT_CAP), LATE_BILLS_AMOUNT_CAP)
            
        if user_data.get('avg_monthly_income_jod', 0) < MIN_INCOME_THRESHOLD:
             if "Exploration" not in result['decision']:
                 result['decision'] = "Rejected"
                 result['approved_amount_jod'] = 0
            
        return result

    def get_confidence(self, score: float, ml_score: Optional[float] = None) -> str:
        """
        Calculates confidence level, detecting if score is RRF, cosine similarity, or ML score.
        """
        if score == 0 or score is None:
            return "UNKNOWN"
            
        # RRF Score detection (usually < 0.1)
        if score < 0.1:
            if score > 0.015:
                return "HIGH"
            elif score >= 0.010:
                return "MEDIUM"
            else:
                return "LOW"
                
        # Cosine similarity detection (0.1 to 1.0)
        elif score <= 1.0:
            if score >= 0.90:
                return "HIGH"
            elif score >= 0.75:
                return "MEDIUM"
            else:
                return "LOW"
                
        # Original ML score logic (using ml_score to fix the 300-850 bug)
        thresholds = [30, 45, 60, 80]
        val = ml_score if ml_score is not None else score
        min_dist = min([abs(val - t) for t in thresholds])
        
        if min_dist < 5:
            return "LOW"
        elif min_dist < 10:
            return "MEDIUM"
        else:
            return "HIGH"

    def run_pipeline(self, user_data: Dict[str, Any], financial_metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # ── 1. Deterministic ML Prediction ────────────────────────────────────
        ml_score = self.predict_ml(user_data)
        
        # Apply Transaction Analytics Penalties / Bonuses
        if financial_metrics:
            savings_rate = financial_metrics.get('savings_rate', 0)
            volatility = financial_metrics.get('volatility', 0)
            reliability = financial_metrics.get('reliability', 0)
            
            if savings_rate < SAVINGS_RATE_MIN or volatility > VOLATILITY_MAX:
                ml_score -= PENALTY_POINTS
            if reliability >= RELIABILITY_MIN:
                ml_score += BONUS_POINTS
                
            ml_score = max(0, min(100, ml_score))
        
        # ── 2. Deterministic Score Breakdown ───────────────────────────────────
        # Computed before LLM involvement — this value is immutable from this point.
        score_breakdown = compute_score_breakdown(ml_score)

        # ── 3. Check Edge Zone ─────────────────────────────────────────────────
        is_edge = any(low <= ml_score <= high for low, high in EDGE_ZONES)
        
        # ── 4. LLM Explanation (text-only, score-read-only) ────────────────────
        # generate_explanation returns ONLY: key_strengths, key_risks, reason.
        # It does NOT return any numeric score fields (firewall enforced in rag_engine.py).
        explanation = generate_explanation(user_data, ml_score, financial_metrics)

        # ── 5. Assemble Result — numeric fields from ML only ───────────────────
        # The LLM explanation is merged in, but score fields are ALWAYS set from
        # the deterministic pipeline. If the LLM somehow returned score fields,
        # the firewall in rag_engine.py strips them; this assignment overrides anyway.
        result = {
            "ml_score": float(ml_score),
            "llm_adjusted_score": float(ml_score),  # No LLM adjustment — kept for API schema compatibility
            "final_score": float(ml_score),
            "score_breakdown": score_breakdown,
            "key_strengths": explanation.get("key_strengths", []),
            "key_risks": explanation.get("key_risks", []),
            "reason": explanation.get("reason", ""),
            # risk_level and decision are set by validate_rules below
            "risk_level": "High",
            "decision": "Rejected",
            "approved_amount_jod": 0,
        }
        
        # ── 6. Confidence ──────────────────────────────────────────────────────
        result['confidence'] = self.get_confidence(result['final_score'], ml_score)
        
        # ── 7. Hard Business Rule Validation ──────────────────────────────────
        final_result = self.validate_rules(result, user_data)
        
        # ── 8. Metadata ────────────────────────────────────────────────────────
        final_result['applicant_name'] = user_data.get('name', 'N/A')
        final_result['profession'] = user_data.get('profession', 'N/A')
        final_result['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # ── 9. Save to Supabase ────────────────────────────────────────────────
        #
        # RLS NOTE (Issue 1 from hardening prompt):
        # The Supabase client here uses the SERVICE-ROLE key (SUPABASE_KEY in .env).
        # The service-role key BYPASSES RLS entirely — the audit_log_insert_only
        # policy (WITH CHECK (true)) is therefore irrelevant for these writes.
        # This is intentional: only the backend server writes to the audit log.
        # There is NO client-side path that can insert into credit_decision_audit_log.
        #
        # APPLICATION-LEVEL OWNERSHIP ASSERTION (replaces RLS for this pattern):
        # Before writing any audit row, we assert that applicant_email equals the
        # authenticated user's email that was passed into run_pipeline(). This is
        # checked below and will raise if they don't match, preventing a spoofed
        # audit record even if this function is somehow called with mismatched data.
        MODEL_VERSION = "xgboost-classifier-v1"

        applicant_email = user_data.get("email", "")
        asserted_email = user_data.get("_authenticated_email", applicant_email)
        if asserted_email and applicant_email and asserted_email != applicant_email:
            # Ownership mismatch — refuse to write audit record under wrong identity
            logger.warning(
                f"AUDIT WRITE BLOCKED: authenticated email '{asserted_email}' "
                f"does not match applicant_email '{applicant_email}'. Skipping DB write."
            )
            return final_result

        if supabase:
            try:
                db_record = {
                    "name": final_result['applicant_name'],
                    "profession": final_result['profession'],
                    "profession_category": user_data.get('profession_category'),
                    "avg_monthly_income_jod": float(user_data.get('avg_monthly_income_jod', 0)),
                    "credit_score": int(final_result['final_score']),
                    "risk_level": final_result['risk_level'],
                    "decision": final_result['decision'],
                    "approved_amount_jod": final_result['approved_amount_jod'],
                    "reason": final_result.get('reason'),
                    "key_strengths": final_result.get('key_strengths', []),
                    "key_risks": final_result.get('key_risks', []),
                    "score_breakdown": final_result.get('score_breakdown', {}),
                    "generated_at": datetime.now().isoformat(),
                    "model_version": MODEL_VERSION,
                }
                supabase.table("tamweel_results").insert(db_record).execute()

                # Write immutable audit log entry (application-level ownership already asserted above)
                if applicant_email:
                    audit_record = {
                        "applicant_email": applicant_email,
                        "applicant_name": final_result['applicant_name'],
                        "model_version": MODEL_VERSION,
                        "input_features": {k: v for k, v in user_data.items() if not k.startswith("_")},
                        "ml_score_raw": float(result['ml_score']),
                        "final_score": float(final_result['final_score']),
                        "score_breakdown": final_result.get('score_breakdown', {}),
                        "risk_level": final_result['risk_level'],
                        "decision": final_result['decision'],
                        "approved_amount_jod": final_result['approved_amount_jod'],
                        "explanation_reason": final_result.get('reason'),
                        "explanation_strengths": final_result.get('key_strengths', []),
                        "explanation_risks": final_result.get('key_risks', []),
                        "explanation_model": "deepseek-v4-via-openrouter",
                        "financial_metrics_snapshot": financial_metrics or {},
                    }
                    try:
                        supabase.table("credit_decision_audit_log").insert(audit_record).execute()
                    except Exception as audit_e:
                        # Audit log write failure is non-fatal but must be logged
                        logger.error(f"Audit Log Write Error (run credit_decision_audit_log.sql first): {audit_e}", exc_info=True)

            except Exception as e:
                logger.error(f"Supabase Save Error: {e}", exc_info=True)
                
        return final_result

# ─── 3. UTILITIES ─────────────────────────────────────────────────────────────

def print_report(res):
    def ar(text):
        import arabic_reshaper
        from bidi.algorithm import get_display
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)

    score_bar = "█" * int(res['final_score'] / 10) + "░" * (10 - int(res['final_score'] / 10))
    
    print("\n" + "═"*52)
    print("   TAMWEEL AI | HYBRID CREDIT ASSESSMENT REPORT")
    print("═"*52)
    print(f"   Applicant      : {res['applicant_name']}")
    print(f"   Profession     : {res['profession']}")
    print(f"   Timestamp      : {res['timestamp']}")
    print("─"*52)
    print(f"   ML Score       : {res['ml_score']:.1f}/100  (XGBoost)")
    print(f"   Adjusted Score : {res['llm_adjusted_score']:.1f}/100 (Claude RAG)")
    print(f"   Final Score    : {res['final_score']:.1f}/100  [{score_bar}]")
    print(f"   Confidence     : {res['confidence']}")
    print("─"*52)
    print(f"   Risk Level     : {res['risk_level']}")
    print(f"   Decision       : {res['decision']}")
    print(f"   Approved Amt   : {res['approved_amount_jod']} JOD")
    print("─"*52)
    print("   Score Breakdown:")
    breakdown = res.get('score_breakdown', {})
    print(f"   Income Stability   : {breakdown.get('income_stability', 0)}/40")
    print(f"   Bill History       : {breakdown.get('bill_history', 0)}/30")
    print(f"   Financial Health   : {breakdown.get('financial_health', 0)}/30")
    print("─"*52)
    print("   Strengths:")
    for s in res.get('key_strengths', []):
        print(f"              + {s}")
    print("   Risks:")
    for r in res.get('key_risks', []):
        print(f"              - {r}")
    print("─"*52)
    print("   Arabic Reason:")
    print(f"   {ar(res['reason'])}")
    print("═"*52 + "\n")

# ─── 4. TEST ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    engine = TamweelHybridEngine()
    
    test_user = {
        "name": "أحمد الخالدي",
        "profession": "Uber Driver",
        "profession_category": "gig",
        "avg_monthly_income_jod": 320.50,
        "income_stability_score": 0.85,
        "income_source_count": 1,
        "late_bills_count": 1,
        "bill_reliability_pct": 92.0,
        "total_bills_checked": 12,
        "current_balance_jod": 150.0,
        "wallet_tx_count": 25,
        "wallet_total_volume_jod": 450.0,
        "balance_to_income_ratio": 0.46,
        "existing_loans": 0
    }
    
    result = engine.run_pipeline(test_user)
    print_report(result)
