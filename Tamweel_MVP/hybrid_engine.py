import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import arabic_reshaper
from bidi.algorithm import get_display
from rag_engine import generate_explanation

load_dotenv()

# ─── 1. CONFIGURATION ────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        supabase = None
except Exception:
    supabase = None

# ─── 2. HYBRID ENGINE CLASS ───────────────────────────────────────────────────

class TamweelHybridEngine:
    def __init__(self):
        print("  Initializing Tamweel Hybrid Engine...")
        self.model = joblib.load(f"{MODELS_DIR}/tamweel_xgboost_classifier.pkl")
        self.scaler = joblib.load(f"{MODELS_DIR}/scaler.pkl")
        self.le = joblib.load(f"{MODELS_DIR}/label_encoder.pkl")
        with open(f"{MODELS_DIR}/feature_names.json", 'r') as f:
            self.feature_names = json.load(f)
            
    def preprocess(self, user_data):
        df = pd.DataFrame([user_data])
        
        # Apply Log Transformations to right-skewed continuous variables
        skewed_features = ['avg_monthly_income_jod', 'current_balance_jod', 'wallet_total_volume_jod']
        for feat in skewed_features:
             if feat in df.columns:
                 df[feat] = np.log1p(df[feat])

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

    def predict_ml(self, user_data):
        X = self.preprocess(user_data)
        # Using predict_proba to get the probability of non-default (class 0) as the "score"
        ml_prob_default = self.model.predict_proba(X)[0][1]
        ml_score = (1 - ml_prob_default) * 100
        return float(np.clip(ml_score, 0, 100))

    def validate_rules(self, result, user_data):
        """
        Hard business rules validation layer, including 1% Exploration Loop.
        """
        score = result['final_score']
        
        # Loan Context
        requested_amount = user_data.get('requested_amount_jod', 500)
        loan_duration_months = user_data.get('loan_duration_months', 12)
        interest_rate = user_data.get('interest_rate', 0.12)
        
        # Mandatory Decision Tiers
        if score >= 80:
            result['decision'] = "Approved"
            result['approved_amount_jod'] = min(requested_amount, 1000)
        elif score >= 60:
            result['decision'] = "Approved"
            result['approved_amount_jod'] = min(requested_amount, 600)
        elif score >= 45:
            result['decision'] = "Conditional Approval"
            result['approved_amount_jod'] = min(requested_amount, 300)
        elif score >= 30:
            result['decision'] = "Conditional Approval"
            result['approved_amount_jod'] = min(requested_amount, 150)
        else:
            # ─── BIAS MITIGATION: 1% EXPLORATION LOOP ───
            # To prevent automation of historical biases, we randomly approve 1% of high-risk profiles.
            import random
            if random.random() < 0.01:
                result['decision'] = "Approved (Exploration Cohort)"
                result['approved_amount_jod'] = min(requested_amount, 100) # Small controlled limit
                result['key_strengths'].append("تمت الموافقة الاستثنائية ضمن برنامج الاستكشاف لبناء الثقة.")
            else:
                result['decision'] = "Rejected"
                result['approved_amount_jod'] = 0
            
        # Specific overrides
        if user_data.get('late_bills_count', 0) >= 4 and score > 50:
            result['final_score'] = 50
            if result['decision'] == "Approved":
                result['decision'] = "Conditional Approval"
            result['approved_amount_jod'] = min(result.get('approved_amount_jod', 150), 150)
            
        if user_data.get('avg_monthly_income_jod', 0) < 50:
             if "Exploration" not in result['decision']:
                 result['decision'] = "Rejected"
                 result['approved_amount_jod'] = 0
            
        return result

    def get_confidence(self, score, ml_score):
        """
        Calculates confidence level.
        """
        thresholds = [30, 45, 60, 80]
        min_dist = min([abs(score - t) for t in thresholds])
        
        if min_dist < 5:
            return "LOW"
        elif min_dist < 10:
            return "MEDIUM"
        else:
            return "HIGH"

    def run_pipeline(self, user_data, financial_metrics=None):
        # 1. ML Prediction
        ml_score = self.predict_ml(user_data)
        
        # Apply Transaction Analytics Penalties / Bonuses
        if financial_metrics:
            savings_rate = financial_metrics.get('savings_rate', 0)
            volatility = financial_metrics.get('volatility', 0)
            reliability = financial_metrics.get('reliability', 0)
            
            if savings_rate < 0.10 or volatility > 500:
                ml_score -= 5
            if reliability >= 3:
                ml_score += 5
                
            ml_score = max(0, min(100, ml_score))
        
        # 2. Check Edge Zone for LLM Review
        # Edge zones: 28-32, 43-47, 58-62, 78-82
        edge_zones = [(28, 32), (43, 47), (58, 62), (78, 82)]
        is_edge = any(low <= ml_score <= high for low, high in edge_zones)
        
        # 3. LLM Review & Explanation (Always run for explanation in this version)
        result = generate_explanation(user_data, ml_score, financial_metrics)
        
        # 4. Confidence
        result['confidence'] = self.get_confidence(result['final_score'], ml_score)
        
        # 5. Validation Rules
        final_result = self.validate_rules(result, user_data)
        
        # 6. Metadata
        final_result['applicant_name'] = user_data.get('name', 'N/A')
        final_result['profession'] = user_data.get('profession', 'N/A')
        final_result['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 7. Save to Supabase
        if supabase:
            try:
                # Map keys to table columns
                db_record = {
                    "name": final_result['applicant_name'],
                    "profession": final_result['profession'],
                    "profession_category": user_data.get('profession_category'),
                    "avg_monthly_income_jod": user_data.get('avg_monthly_income_jod'),
                    "credit_score": int(final_result['final_score']),
                    "risk_level": final_result['risk_level'],
                    "decision": final_result['decision'],
                    "approved_amount_jod": final_result['approved_amount_jod'],
                    "reason": final_result.get('reason'),
                    "key_strengths": final_result.get('key_strengths', []),
                    "key_risks": final_result.get('key_risks', []),
                    "score_breakdown": final_result.get('score_breakdown', {}),
                    "generated_at": datetime.now().isoformat()
                }
                supabase.table("tamweel_results").insert(db_record).execute()
            except Exception as e:
                print(f"  ⚠️ Supabase Save Error: {e}")
                
        return final_result

# ─── 3. UTILITIES ─────────────────────────────────────────────────────────────

def print_report(res):
    def ar(text):
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
