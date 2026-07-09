import re

def refactor_train():
    file_path = "ml_pipeline/train_model.py"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Imports and constants
    content = content.replace("""import os
import json
import random
from datetime import datetime
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns""", """import os
import json
import random
import logging
from datetime import datetime
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, List, Dict, Any""")

    content = content.replace("""# ─── 1. CONFIGURATION ────────────────────────────────────────────────────────
np.random.seed(42)""", """logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ─── 1. CONFIGURATION ────────────────────────────────────────────────────────
np.random.seed(42)""")


    # 2. Memory efficiency in load_and_preprocess
    # old:
    #     df = pd.read_csv(DATA_PATH)
    #     
    #     X = df[FEATURES].copy()
    #     y = df[TARGET].copy()
    #     
    #     # Apply Log Transformations to right-skewed continuous variables
    #     skewed_features = ['avg_monthly_income_jod', 'current_balance_jod', 'wallet_total_volume_jod']
    #     for feat in skewed_features:
    #         X[feat] = np.log1p(X[feat])
    #     
    #     # Handle categorical: profession_category
    #     le = LabelEncoder()
    #     X['profession_category'] = le.fit_transform(X['profession_category'])
    #     joblib.dump(le, f"{MODELS_DIR}/label_encoder.pkl")
    #     
    #     # Handle missing values to match production inference behavior
    #     X_imputed = X.fillna(0)
    #     
    #     # Split: 80% train, 10% val, 10% test (Stratified to maintain class balance)
    #     X_train, X_temp, y_train, y_temp = train_test_split(X_imputed, y, test_size=0.2, random_state=42, stratify=y)
    
    # new:
    new_load = """    logger.info(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # Avoid unnecessary copy by operating directly on df before extracting X and y
    skewed_features = ['avg_monthly_income_jod', 'current_balance_jod', 'wallet_total_volume_jod']
    for feat in skewed_features:
        df[feat] = np.log1p(df[feat])
    
    # Handle categorical: profession_category
    le = LabelEncoder()
    df['profession_category'] = le.fit_transform(df['profession_category'])
    joblib.dump(le, f"{MODELS_DIR}/label_encoder.pkl")
    
    # Handle missing values in-place
    df.fillna(0, inplace=True)
    
    X = df[FEATURES]
    y = df[TARGET]
    
    # Split: 80% train, 10% val, 10% test (Stratified to maintain class balance)
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)"""
    
    content = re.sub(
        r'    print\(f"\\n  Loading data from \{DATA_PATH\}\.\.\."\).*?X_train, X_temp, y_train, y_temp = train_test_split\(X_imputed, y, test_size=0\.2, random_state=42, stratify=y\)',
        new_load,
        content,
        flags=re.DOTALL
    )

    # 3. Type hints
    content = content.replace("def load_and_preprocess():", "def load_and_preprocess() -> Tuple[np.ndarray, np.ndarray, np.ndarray, pd.Series, pd.Series, pd.Series, List[str]]:")
    content = content.replace("def train_xgb(X_train, y_train, X_val, y_val):", "def train_xgb(X_train: np.ndarray, y_train: pd.Series, X_val: np.ndarray, y_val: pd.Series) -> CalibratedClassifierCV:")
    content = content.replace("def evaluate(model, X_test, y_test, feature_names):", "def evaluate(model: CalibratedClassifierCV, X_test: np.ndarray, y_test: pd.Series, feature_names: List[str]) -> Dict[str, Any]:")
    content = content.replace("def cross_val_and_learning_curve(model, X, y):", "def cross_val_and_learning_curve(model: CalibratedClassifierCV, X: np.ndarray, y: pd.Series) -> None:")

    # 4. print -> logger.info
    content = content.replace("""    print("  Training XGBoost Classifier...")""", """    logger.info("Training XGBoost Classifier...")""")
    content = content.replace("""    print("  Calibrating Probabilities...")""", """    logger.info("Calibrating Probabilities...")""")
    content = content.replace("""    print("  Evaluating model...")""", """    logger.info("Evaluating model...")""")
    content = content.replace("""    print("  Running Cross-Validation and Learning Curve...")""", """    logger.info("Running Cross-Validation and Learning Curve...")""")
    
    content = content.replace("""    print(f"\n{'─'*40}")
    print(f"  MODEL PERFORMANCE (CLASSIFICATION)")
    print(f"{'─'*40}")
    for k, v in metrics.items():
        print(f"  {k:<25}: {v}")
    
    print("\n  Confusion Matrix:")
    print(f"  TN: {cm[0][0]:<5} FP: {cm[0][1]}")
    print(f"  FN: {cm[1][0]:<5} TP: {cm[1][1]}")""", """    logger.info(f"\\n{'─'*40}\\n  MODEL PERFORMANCE (CLASSIFICATION)\\n{'─'*40}")
    for k, v in metrics.items():
        logger.info(f"  {k:<25}: {v}")
    
    logger.info(f"\\n  Confusion Matrix:\\n  TN: {cm[0][0]:<5} FP: {cm[0][1]}\\n  FN: {cm[1][0]:<5} TP: {cm[1][1]}")""")

    content = content.replace("""    print(f"  CV F1 Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")""", """    logger.info(f"CV F1 Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")""")

    content = content.replace("""        print(f"  ❌ Data not found at {DATA_PATH}. Run generate_data.py first.")""", """        logger.error(f"Data not found at {DATA_PATH}. Run generate_data.py first.")""")
    content = content.replace("""        print(f"\\n  ✅ Training complete! Artifacts saved to {MODELS_DIR}/")""", """        logger.info(f"Training complete! Artifacts saved to {MODELS_DIR}/")""")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

refactor_train()
print("train_model.py refactored successfully")
