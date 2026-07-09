import re
import os

def refactor_hybrid():
    file_path = "backend/app/ml/hybrid_engine.py"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Imports and constants
    content = content.replace("""import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

import sys
import os""", """import os
import json
import joblib
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Union
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

import sys""")

    content = content.replace("""load_dotenv()

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
    supabase = None""", """load_dotenv()
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
    supabase = None""")

    # 2. prints to logger.info
    content = content.replace("""        print("  Initializing Tamweel Hybrid Engine...")""", """        logger.info("Initializing Tamweel Hybrid Engine...")""")

    # Type hints for methods
    content = content.replace("""    def preprocess(self, user_data):""", """    def preprocess(self, user_data: Dict[str, Any]) -> np.ndarray:""")
    content = content.replace("""    def predict_ml(self, user_data):""", """    def predict_ml(self, user_data: Dict[str, Any]) -> float:""")
    content = content.replace("""    def validate_rules(self, result, user_data):""", """    def validate_rules(self, result: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:""")
    content = content.replace("""    def get_confidence(self, score, ml_score=None):""", """    def get_confidence(self, score: float, ml_score: Optional[float] = None) -> str:""")
    content = content.replace("""    def run_pipeline(self, user_data, financial_metrics=None):""", """    def run_pipeline(self, user_data: Dict[str, Any], financial_metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:""")


    # Magic numbers in validate_rules
    content = content.replace("""        requested_amount = user_data.get('requested_amount_jod', 500)
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
            
        if user_data.get('avg_monthly_income_jod', 0) < 50:""", """        requested_amount = user_data.get('requested_amount_jod', DEFAULT_REQUESTED_AMOUNT)
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
            
        if user_data.get('avg_monthly_income_jod', 0) < MIN_INCOME_THRESHOLD:""")


    # run_pipeline magic numbers
    content = content.replace("""        # Apply Transaction Analytics Penalties / Bonuses
        if financial_metrics:
            savings_rate = financial_metrics.get('savings_rate', 0)
            volatility = financial_metrics.get('volatility', 0)
            reliability = financial_metrics.get('reliability', 0)
            
            if savings_rate < 0.10 or volatility > 500:
                ml_score -= 5
            if reliability >= 3:
                ml_score += 5
                
            ml_score = max(0, min(100, ml_score))
        
        # ── 2. Deterministic Score Breakdown ───────────────────────────────────
        # Computed before LLM involvement — this value is immutable from this point.
        score_breakdown = compute_score_breakdown(ml_score)

        # ── 3. Check Edge Zone ─────────────────────────────────────────────────
        edge_zones = [(28, 32), (43, 47), (58, 62), (78, 82)]
        is_edge = any(low <= ml_score <= high for low, high in edge_zones)""", """        # Apply Transaction Analytics Penalties / Bonuses
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
        is_edge = any(low <= ml_score <= high for low, high in EDGE_ZONES)""")

    # Prints for errors in run_pipeline
    content = content.replace("""        if asserted_email and applicant_email and asserted_email != applicant_email:
            # Ownership mismatch — refuse to write audit record under wrong identity
            print(
                f"  ⛔ AUDIT WRITE BLOCKED: authenticated email '{asserted_email}' "
                f"does not match applicant_email '{applicant_email}'. Skipping DB write."
            )
            return final_result""", """        if asserted_email and applicant_email and asserted_email != applicant_email:
            # Ownership mismatch — refuse to write audit record under wrong identity
            logger.warning(
                f"AUDIT WRITE BLOCKED: authenticated email '{asserted_email}' "
                f"does not match applicant_email '{applicant_email}'. Skipping DB write."
            )
            return final_result""")

    content = content.replace("""                    try:
                        supabase.table("credit_decision_audit_log").insert(audit_record).execute()
                    except Exception as audit_e:
                        # Audit log write failure is non-fatal but must be logged
                        print(f"  ⚠️ Audit Log Write Error (run credit_decision_audit_log.sql first): {audit_e}")

            except Exception as e:
                print(f"  ⚠️ Supabase Save Error: {e}")""", """                    try:
                        supabase.table("credit_decision_audit_log").insert(audit_record).execute()
                    except Exception as audit_e:
                        # Audit log write failure is non-fatal but must be logged
                        logger.error(f"Audit Log Write Error (run credit_decision_audit_log.sql first): {audit_e}", exc_info=True)

            except Exception as e:
                logger.error(f"Supabase Save Error: {e}", exc_info=True)""")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

refactor_hybrid()
print("hybrid_engine.py refactored successfully")
