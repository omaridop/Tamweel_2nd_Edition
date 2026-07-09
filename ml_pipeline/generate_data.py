import os
import random
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Dict, Any, Optional

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ─── 1. SUPABASE CONFIG ───────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# If SUPABASE_URL or SUPABASE_KEY is not set, we skip the upload part
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Optional[Client] = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        supabase = None
except Exception as e:
    logger.error("Failed to initialize Supabase client", exc_info=True)
    supabase = None

# Scoring Constants
INCOME_SCORE_MAX = 40
INCOME_STABILITY_WEIGHT = 25
AVG_INCOME_CAP = 500
AVG_INCOME_WEIGHT = 10
INCOME_SOURCES_CAP = 3
INCOME_SOURCES_WEIGHT = 5

BILL_SCORE_MAX = 30
BILL_RELIABILITY_WEIGHT = 25
LATE_BILLS_CAP = 6
LATE_BILLS_WEIGHT = 5

HEALTH_SCORE_MAX = 30
BTI_CAP = 2
BTI_WEIGHT = 12
TX_COUNT_CAP = 30
TX_COUNT_WEIGHT = 10
TX_VOL_CAP = 500
TX_VOL_WEIGHT = 8

# ─── 2. JORDAN MARKET CONSTANTS ──────────────────────────────────────────────
PROFESSIONS = [
    ("Freelance Graphic Designer",   "freelance",  150, 400),
    ("Upwork Developer",             "freelance",  200, 600),
    ("Khamsat Content Writer",       "freelance",  100, 300),
    ("Uber/Careem Driver",           "gig",        180, 350),
    ("Food Delivery Rider",          "gig",        120, 280),
    ("Home-based Business Owner",    "business",   200, 500),
    ("Instagram Store Owner",        "business",   150, 450),
    ("Daily Construction Worker",    "daily",       80, 220),
    ("Market Vendor",                "daily",       90, 200),
    ("Freelance Photographer",       "freelance",  120, 380),
    ("Online Tutor",                 "freelance",  100, 300),
    ("TikTok Content Creator",       "gig",         80, 400),
]

LOAN_PURPOSES = [
    "شراء لابتوب للعمل",
    "معدات تصوير",
    "رأس مال لمشروع صغير",
    "شراء دراجة نارية للتوصيل",
    "تطوير متجر إلكتروني",
    "شراء هاتف للعمل",
    "معدات مطبخ منزلي",
    "شراء أدوات نجارة",
    "إيجار مكتب صغير",
    "تمويل دورة تدريبية",
]

ARABIC_NAMES = [
    "أحمد الخالدي", "محمد العمري", "خالد الزعبي", "عمر الرشيد",
    "يوسف الحمود", "إبراهيم السالم", "علي المجالي", "حسن الطراونة",
    "سامر العجلوني", "نادر البطاينة", "فارس الحوراني", "كريم الدباس",
    "تامر الصرايرة", "وليد الكيلاني", "رامي النعيمات", "زياد الحمدان",
    "نور الحداد", "سارة المجالي", "ليلى الخزوم", "رنا العبادي",
    "دانا الزيود", "هند الفايز", "مي الشوبكي", "لارا البواب",
    "ريم الحموري", "نادية السعد", "أميرة الجازي", "شيماء الوهيدات",
]

# ─── 3. CORE GENERATOR FUNCTIONS ─────────────────────────────────────────────

def generate_profile(profile_type: str) -> Dict[str, Any]:
    """
    Generates realistic financial signals based on profile type.
    profile_type: 'excellent' | 'good' | 'fair' | 'poor' | 'risky'
    """

    # ── Income parameters by profile type ──
    income_params = {
        "excellent": {"avg": (300, 500), "stability": (0.85, 0.98), "sources": (2, 4)},
        "good":      {"avg": (200, 350), "stability": (0.70, 0.88), "sources": (1, 3)},
        "fair":      {"avg": (150, 250), "stability": (0.50, 0.72), "sources": (1, 2)},
        "poor":      {"avg": (80,  180), "stability": (0.30, 0.55), "sources": (1, 2)},
        "risky":     {"avg": (40,  120), "stability": (0.10, 0.35), "sources": (1, 1)},
    }

    bill_params = {
        "excellent": {"on_time_rate": (0.90, 1.00), "total_bills": (6, 12)},
        "good":      {"on_time_rate": (0.75, 0.92), "total_bills": (6, 10)},
        "fair":      {"on_time_rate": (0.55, 0.78), "total_bills": (4, 8)},
        "poor":      {"on_time_rate": (0.30, 0.58), "total_bills": (4, 8)},
        "risky":     {"on_time_rate": (0.00, 0.35), "total_bills": (3, 6)},
    }

    balance_params = {
        "excellent": (200, 600),
        "good":      (100, 300),
        "fair":      (30,  150),
        "poor":      (5,   80),
        "risky":     (0,   30),
    }

    wallet_params = {
        "excellent": {"tx_count": (20, 50), "volume": (400, 900)},
        "good":      {"tx_count": (12, 25), "volume": (200, 500)},
        "fair":      {"tx_count": (6,  15), "volume": (100, 300)},
        "poor":      {"tx_count": (2,  8),  "volume": (30,  150)},
        "risky":     {"tx_count": (0,  4),  "volume": (0,   60)},
    }

    p = income_params[profile_type]
    b = bill_params[profile_type]
    bal = balance_params[profile_type]
    w = wallet_params[profile_type]

    # ── Generate features ──
    profession, prof_category, min_inc, max_inc = random.choice(PROFESSIONS)
    avg_income = round(random.uniform(*p["avg"]), 2)
    income_stability = round(random.uniform(*p["stability"]), 3)
    income_sources = random.randint(*p["sources"])

    total_bills = random.randint(*b["total_bills"])
    on_time_rate = random.uniform(*b["on_time_rate"])
    on_time_bills = int(total_bills * on_time_rate)
    late_bills = total_bills - on_time_bills
    bill_reliability_pct = round((on_time_bills / total_bills) * 100, 1) if total_bills > 0 else 100

    current_balance = round(random.uniform(*bal), 2)
    wallet_tx_count = random.randint(*w["tx_count"])
    wallet_volume = round(random.uniform(*w["volume"]), 2)
    balance_to_income = round(current_balance / avg_income, 3) if avg_income > 0 else 0

    existing_loans = random.choices([0, 1, 2], weights=[0.65, 0.25, 0.10])[0]

    # ── Calculate hidden latent risk score (log-odds) ──
    # Base risk (prior log-odds)
    latent_risk = -1.5 

    # Risk penalties (increase default probability)
    latent_risk += (late_bills * 0.8)
    latent_risk += (existing_loans * 0.6)

    # Risk mitigants (decrease default probability)
    latent_risk -= (income_stability * 2.0)
    latent_risk -= (bill_reliability_pct / 100.0 * 1.5)
    latent_risk -= (min(balance_to_income, 3.0) * 0.5)
    latent_risk -= (min(income_sources, 3) * 0.3)
    latent_risk -= (min(wallet_tx_count, 40) / 40.0 * 0.5)
    latent_risk -= (min(wallet_volume, 800) / 800.0 * 0.5)

    # Add realistic stochastic noise
    noise = random.normalvariate(0, 0.5)
    latent_risk += noise

    # ── Calculate Probability of Default (PD) using sigmoid ──
    pd_val = 1.0 / (1.0 + np.exp(-latent_risk))

    # ── Sample Default Label ──
    default_label = int(np.random.binomial(1, pd_val))

    # ── Credit Score Generation (derived from PD) ──
    # Higher repayment probability = higher credit score
    base_score = (1.0 - pd_val) * 100.0
    
    # Jitter to prevent perfectly monotonic relation
    score_noise = random.uniform(-3, 3)
    credit_score = int(max(0, min(100, round(base_score + score_noise))))

    # ── Maintain Computed Sub-scores for schema consistency ──
    income_score = min(INCOME_SCORE_MAX, round(
        (income_stability * INCOME_STABILITY_WEIGHT) +
        (min(avg_income, AVG_INCOME_CAP) / AVG_INCOME_CAP * AVG_INCOME_WEIGHT) +
        (min(income_sources, INCOME_SOURCES_CAP) / INCOME_SOURCES_CAP * INCOME_SOURCES_WEIGHT)
    , 1))

    bill_score = min(BILL_SCORE_MAX, round(
        (bill_reliability_pct / 100 * BILL_RELIABILITY_WEIGHT) +
        (max(0, (LATE_BILLS_CAP - late_bills) / LATE_BILLS_CAP) * LATE_BILLS_WEIGHT)
    , 1))

    health_score = min(HEALTH_SCORE_MAX, round(
        (min(balance_to_income, BTI_CAP) / BTI_CAP * BTI_WEIGHT) +
        (min(wallet_tx_count, TX_COUNT_CAP) / TX_COUNT_CAP * TX_COUNT_WEIGHT) +
        (min(wallet_volume, TX_VOL_CAP) / TX_VOL_CAP * TX_VOL_WEIGHT)
    , 1))

    # ── Determine decision based on score ──
    if credit_score >= 80:
        decision = "Approved"
        approved_amount = min(1000, random.randint(600, 1000))
        risk_level = "Low"
    elif credit_score >= 60:
        decision = "Approved"
        approved_amount = random.randint(400, 600)
        risk_level = "Low"
    elif credit_score >= 45:
        decision = "Conditional Approval"
        approved_amount = random.randint(150, 300)
        risk_level = "Medium"
    elif credit_score >= 30:
        decision = "Conditional Approval"
        approved_amount = random.randint(50, 150)
        risk_level = "Medium"
    else:
        decision = "Rejected"
        approved_amount = 0
        risk_level = "High"

    return {
        # Identity
        "name": random.choice(ARABIC_NAMES),
        "profession": profession,
        "profession_category": prof_category,
        "loan_purpose": random.choice(LOAN_PURPOSES),
        "requested_amount_jod": random.choice([200, 300, 500, 700, 1000]),
        "existing_loans": existing_loans,

        # Income features
        "avg_monthly_income_jod": avg_income,
        "income_stability_score": income_stability,
        "income_source_count": income_sources,

        # Bill features
        "total_bills_checked": total_bills,
        "on_time_bills": on_time_bills,
        "late_bills_count": late_bills,
        "bill_reliability_pct": bill_reliability_pct,

        # Wallet features
        "current_balance_jod": current_balance,
        "wallet_tx_count": wallet_tx_count,
        "wallet_total_volume_jod": wallet_volume,
        "balance_to_income_ratio": balance_to_income,

        # Computed sub-scores
        "income_stability_pts": income_score,
        "bill_history_pts": bill_score,
        "financial_health_pts": health_score,

        # Target labels
        "credit_score": credit_score,
        "risk_level": risk_level,
        "decision": decision,
        "approved_amount_jod": approved_amount,
        "default": default_label,

        # Metadata
        "profile_type": profile_type,
        "generated_at": datetime.now().isoformat(),
    }


# ─── 4. GENERATE 10,000 PROFILES ─────────────────────────────────────────────

def generate_dataset(n: int = 10000) -> pd.DataFrame:
    distribution = {
        "excellent": int(n * 0.20),
        "good":      int(n * 0.25),
        "fair":      int(n * 0.25),
        "poor":      int(n * 0.20),
        "risky":     int(n * 0.10),
    }

    records = []
    total = sum(distribution.values())

    logger.info(f"TAMWEEL — Synthetic Data Generator\nGenerating {total:,} profiles...")

    for profile_type, count in distribution.items():
        logger.info(f"[{profile_type.upper():<10}] Generating {count:,} profiles...")
        for _ in range(count):
            records.append(generate_profile(profile_type))

    df = pd.DataFrame(records)

    # Shuffle the dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df.index.name = "id"

    return df


# ─── 5. UPLOAD TO SUPABASE ────────────────────────────────────────────────────

def upload_to_supabase(df: pd.DataFrame, batch_size: int = 500) -> None:
    if not supabase:
        logger.warning("Skip uploading to Supabase: No URL/Key provided.")
        return

    logger.info(f"Uploading to Supabase... Table: tamweel_training_data, Total rows: {len(df):,}, Batch size: {batch_size}")

    records = df.reset_index().to_dict(orient="records")
    total_batches = (len(records) + batch_size - 1) // batch_size
    success_count = 0

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        batch_num = (i // batch_size) + 1

        try:
            supabase.table("tamweel_training_data").insert(batch).execute()
            success_count += len(batch)
            pct = (batch_num / total_batches) * 100
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            logger.info(f"[{bar}] {pct:.0f}% — Batch {batch_num}/{total_batches} ✅")
        except Exception as e:
            logger.error(f"Batch {batch_num} failed: {e}", exc_info=True)

    logger.info(f"Upload complete! {success_count:,} records uploaded.")


# ─── 6. MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Generate dataset
    df = generate_dataset(10000)

    # Print summary stats
    logger.info(f"DATASET SUMMARY\nTotal records    : {len(df):,}\nAvg credit score : {df['credit_score'].mean():.1f}\nScore std dev    : {df['credit_score'].std():.1f}")
    for decision, count in df['decision'].value_counts().items():
        pct = count / len(df) * 100
        logger.info(f"Decision {decision:<25}: {count:,} ({pct:.1f}%)")

    # Save to CSV
    csv_path = "data/tamweel_training_data.csv"
    os.makedirs("data", exist_ok=True)
    df.to_csv(csv_path, index=True, encoding="utf-8-sig")
    logger.info(f"CSV saved → {csv_path}")

    # Upload to Supabase
    upload_to_supabase(df)

    logger.info("Done! Next step: run train_model.py")
