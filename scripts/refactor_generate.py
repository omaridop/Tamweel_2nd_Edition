import re

def refactor_generate():
    file_path = "ml_pipeline/generate_data.py"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Imports and constants
    content = content.replace("""import os
import random
import numpy as np
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client""", """import os
import random
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Dict, Any, Optional""")

    content = content.replace("""load_dotenv()

# ─── 1. SUPABASE CONFIG ───────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# If SUPABASE_URL or SUPABASE_KEY is not set, we skip the upload part
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        supabase = None
except Exception:
    supabase = None""", """load_dotenv()

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
TX_VOL_WEIGHT = 8""")


    content = content.replace("""    # ── Maintain Computed Sub-scores for schema consistency ──
    income_score = min(40, round(
        (income_stability * 25) +
        (min(avg_income, 500) / 500 * 10) +
        (min(income_sources, 3) / 3 * 5)
    , 1))

    bill_score = min(30, round(
        (bill_reliability_pct / 100 * 25) +
        (max(0, (6 - late_bills) / 6) * 5)
    , 1))

    health_score = min(30, round(
        (min(balance_to_income, 2) / 2 * 12) +
        (min(wallet_tx_count, 30) / 30 * 10) +
        (min(wallet_volume, 500) / 500 * 8)
    , 1))""", """    # ── Maintain Computed Sub-scores for schema consistency ──
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
    , 1))""")

    # 2. Type hints
    content = content.replace("def generate_profile(profile_type: str) -> dict:", "def generate_profile(profile_type: str) -> Dict[str, Any]:")
    content = content.replace("def upload_to_supabase(df: pd.DataFrame, batch_size: int = 500):", "def upload_to_supabase(df: pd.DataFrame, batch_size: int = 500) -> None:")

    # 3. Print -> logger.info / logger.error
    content = content.replace("""    print(f"\\n{'='*55}")
    print(f"  TAMWEEL — Synthetic Data Generator")
    print(f"{'='*55}")
    print(f"  Generating {total:,} profiles...\\n")""", """    logger.info(f"TAMWEEL — Synthetic Data Generator\\nGenerating {total:,} profiles...")""")
    
    content = content.replace("""        print(f"  [{profile_type.upper():<10}] Generating {count:,} profiles...")""", """        logger.info(f"[{profile_type.upper():<10}] Generating {count:,} profiles...")""")
    
    content = content.replace("""        print("\\n  ⚠️ Skip uploading to Supabase: No URL/Key provided.")""", """        logger.warning("Skip uploading to Supabase: No URL/Key provided.")""")
    
    content = content.replace("""    print(f"\\n  Uploading to Supabase...")
    print(f"  Table: tamweel_training_data")
    print(f"  Total rows: {len(df):,}")
    print(f"  Batch size: {batch_size}\\n")""", """    logger.info(f"Uploading to Supabase... Table: tamweel_training_data, Total rows: {len(df):,}, Batch size: {batch_size}")""")
    
    content = content.replace("""            print(f"  [{bar}] {pct:.0f}% — Batch {batch_num}/{total_batches} ✅")""", """            logger.info(f"[{bar}] {pct:.0f}% — Batch {batch_num}/{total_batches} ✅")""")
    
    content = content.replace("""        except Exception as e:
            print(f"  ❌ Batch {batch_num} failed: {e}")""", """        except Exception as e:
            logger.error(f"Batch {batch_num} failed: {e}", exc_info=True)""")
            
    content = content.replace("""    print(f"\\n  ✅ Upload complete! {success_count:,} records uploaded.")""", """    logger.info(f"Upload complete! {success_count:,} records uploaded.")""")
    
    content = content.replace("""    # Print summary stats
    print(f"\\n{'='*55}")
    print(f"  DATASET SUMMARY")
    print(f"{'='*55}")
    print(f"  Total records    : {len(df):,}")
    print(f"  Avg credit score : {df['credit_score'].mean():.1f}")
    print(f"  Score std dev    : {df['credit_score'].std():.1f}")
    print(f"\\n  Decision breakdown:")
    for decision, count in df['decision'].value_counts().items():
        pct = count / len(df) * 100
        print(f"  {decision:<25}: {count:,} ({pct:.1f}%)")""", """    # Print summary stats
    logger.info(f"DATASET SUMMARY\\nTotal records    : {len(df):,}\\nAvg credit score : {df['credit_score'].mean():.1f}\\nScore std dev    : {df['credit_score'].std():.1f}")
    for decision, count in df['decision'].value_counts().items():
        pct = count / len(df) * 100
        logger.info(f"Decision {decision:<25}: {count:,} ({pct:.1f}%)")""")

    content = content.replace("""    print(f"\\n  💾 CSV saved → {csv_path}")""", """    logger.info(f"CSV saved → {csv_path}")""")
    
    content = content.replace("""    print(f"\\n{'='*55}")
    print(f"  🎉 Done! Next step: run train_model.py")
    print(f"{'='*55}\\n")""", """    logger.info("Done! Next step: run train_model.py")""")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

refactor_generate()
print("generate_data.py refactored successfully")
