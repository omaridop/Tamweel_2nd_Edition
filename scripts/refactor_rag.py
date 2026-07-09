import re
import os

def refactor_rag():
    file_path = "ml_pipeline/rag_engine.py"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Imports and constants
    content = content.replace("""import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# ─── 1. CONFIGURATION ────────────────────────────────────────────────────────""", """import os
import json
import logging
from anthropic import Anthropic
from dotenv import load_dotenv
from typing import Dict, Any, Optional

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── 1. CONFIGURATION ────────────────────────────────────────────────────────""")

    # 2. Type hints
    content = content.replace("""def retrieve_context(user_data):""", """def retrieve_context(user_data: Dict[str, Any]) -> str:""")
    content = content.replace("""def generate_explanation(user_data: dict, ml_score: float, financial_metrics=None) -> dict:""", """def generate_explanation(user_data: Dict[str, Any], ml_score: float, financial_metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:""")
    content = content.replace("""def compute_score_breakdown(ml_score: float) -> dict:""", """def compute_score_breakdown(ml_score: float) -> Dict[str, float]:""")

    # 3. Print to logger
    content = content.replace("""    except Exception as e:
        print(f"  ❌ Claude API Error in generate_explanation: {e}")""", """    except Exception as e:
        logger.error(f"Claude API Error in generate_explanation: {e}", exc_info=True)""")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

refactor_rag()
print("rag_engine.py refactored successfully")
