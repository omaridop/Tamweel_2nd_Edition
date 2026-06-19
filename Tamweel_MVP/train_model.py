import os
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV, learning_curve, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.impute import SimpleImputer

# ─── 1. CONFIGURATION ────────────────────────────────────────────────────────
DATA_PATH = "data/tamweel_training_data.csv"
MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)

FEATURES = [
    'avg_monthly_income_jod',
    'income_stability_score',
    'income_source_count',
    'late_bills_count',
    'bill_reliability_pct',
    'total_bills_checked',
    'current_balance_jod',
    'wallet_tx_count',
    'wallet_total_volume_jod',
    'balance_to_income_ratio',
    'existing_loans',
    'profession_category'
]
TARGET = 'default' # Binary target for classification

# ─── 2. DATA PIPELINE ─────────────────────────────────────────────────────────

def load_and_preprocess():
    print(f"\n  Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    X = df[FEATURES].copy()
    y = df[TARGET].copy()
    
    # Apply Log Transformations to right-skewed continuous variables
    skewed_features = ['avg_monthly_income_jod', 'current_balance_jod', 'wallet_total_volume_jod']
    for feat in skewed_features:
        X[feat] = np.log1p(X[feat])
    
    # Handle categorical: profession_category
    le = LabelEncoder()
    X['profession_category'] = le.fit_transform(X['profession_category'])
    joblib.dump(le, f"{MODELS_DIR}/label_encoder.pkl")
    
    # Handle missing values
    imputer = SimpleImputer(strategy='median')
    X_imputed = imputer.fit_transform(X)
    
    # Split: 80% train, 10% val, 10% test (Stratified to maintain class balance)
    X_train, X_temp, y_train, y_temp = train_test_split(X_imputed, y, test_size=0.2, random_state=42, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)
    
    # Scale numerical features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    joblib.dump(scaler, f"{MODELS_DIR}/scaler.pkl")
    with open(f"{MODELS_DIR}/feature_names.json", 'w') as f:
        json.dump(FEATURES, f)
        
    return X_train_scaled, X_val_scaled, X_test_scaled, y_train, y_val, y_test, FEATURES

# ─── 3. XGBOOST TRAINING ──────────────────────────────────────────────────────

def train_xgb(X_train, y_train, X_val, y_val):
    print("  Training XGBoost Classifier...")
    
    # Calculate scale_pos_weight for imbalanced dataset
    neg_class = sum(y_train == 0)
    pos_class = sum(y_train == 1)
    scale_pos_weight = neg_class / pos_class if pos_class > 0 else 1.0

    xgb_params = {
        'objective': 'binary:logistic',
        'eval_metric': 'auc',
        'n_estimators': 300,
        'max_depth': 6,
        'learning_rate': 0.05,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'min_child_weight': 3,
        'gamma': 0.1,
        'reg_alpha': 0.1,
        'reg_lambda': 1.0,
        'scale_pos_weight': scale_pos_weight,
        'random_state': 42,
        'n_jobs': -1
    }
    
    model = XGBClassifier(**xgb_params)
    model.fit(
        X_train, y_train,
        verbose=False
    )
    
    joblib.dump(model, f"{MODELS_DIR}/tamweel_xgboost_classifier.pkl")
    return model

# ─── 4. EVALUATION ───────────────────────────────────────────────────────────

def evaluate(model, X_test, y_test, feature_names):
    print("  Evaluating model...")
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)
    
    cm = confusion_matrix(y_test, y_pred)
    
    metrics = {
        "Precision": round(float(precision), 4),
        "Recall": round(float(recall), 4),
        "F1_Score": round(float(f1), 4),
        "ROC_AUC": round(float(roc_auc), 4)
    }
    
    print(f"\n{'─'*40}")
    print(f"  MODEL PERFORMANCE (CLASSIFICATION)")
    print(f"{'─'*40}")
    for k, v in metrics.items():
        print(f"  {k:<25}: {v}")
    
    print("\n  Confusion Matrix:")
    print(f"  TN: {cm[0][0]:<5} FP: {cm[0][1]}")
    print(f"  FN: {cm[1][0]:<5} TP: {cm[1][1]}")

    with open(f"{MODELS_DIR}/model_metrics_clf.json", 'w') as f:
        json.dump(metrics, f)
        
    # Feature Importance
    plt.figure(figsize=(10, 6))
    importances = model.feature_importances_
    indices = np.argsort(importances)
    plt.title('Feature Importances (Classifier)')
    plt.barh(range(len(indices)), importances[indices], align='center')
    plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
    plt.xlabel('Relative Importance')
    plt.tight_layout()
    plt.savefig(f"{MODELS_DIR}/feature_importance_clf.png")
    
    return metrics

def cross_val_and_learning_curve(model, X, y):
    print("  Running Cross-Validation and Learning Curve...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y, cv=skf, scoring='f1')
    print(f"  CV F1 Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    train_sizes, train_scores, test_scores = learning_curve(
        model, X, y, cv=skf, scoring='f1',
        train_sizes=np.linspace(0.1, 1.0, 5), n_jobs=-1
    )
    
    plt.figure(figsize=(10, 6))
    plt.plot(train_sizes, train_scores.mean(axis=1), 'o-', label='Training F1')
    plt.plot(train_sizes, test_scores.mean(axis=1), 'o-', label='Validation F1')
    plt.title('Learning Curve (F1 Score)')
    plt.xlabel('Training Size')
    plt.ylabel('F1 Score')
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{MODELS_DIR}/learning_curve_clf.png")

# ─── 5. MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not os.path.exists(DATA_PATH):
        print(f"  ❌ Data not found at {DATA_PATH}. Run generate_data.py first.")
    else:
        X_train, X_val, X_test, y_train, y_val, y_test, feature_names = load_and_preprocess()
        
        best_model = train_xgb(X_train, y_train, X_val, y_val)
        evaluate(best_model, X_test, y_test, feature_names)
        
        X_full = np.vstack([X_train, X_val, X_test])
        y_full = np.concatenate([y_train, y_val, y_test])
        cross_val_and_learning_curve(best_model, X_full, y_full)
        
        print(f"\n  ✅ Training complete! Artifacts saved to {MODELS_DIR}/")
