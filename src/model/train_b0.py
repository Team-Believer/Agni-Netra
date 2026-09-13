import os
import json
import traceback
import pandas as pd
import numpy as np
import xgboost as xgb
from datetime import datetime

# Optional dependencies
def get_gpu_info():
    gpu_report = {
        "framework": "XGBoost",
        "xgboost_version": xgb.__version__,
        "cuda_status": "NOT_AVAILABLE",
        "gpu_available": False,
        "gpu_used": False,
        "gpu_model": "None",
        "vram_gb": 0,
        "device_parameter": "cpu",
        "tree_method": "hist",
        "fallback_reason": "Torch import hangs, skipping GPU for this small 40-row dataset."
    }
    return gpu_report

def train_b0():
    print("Initializing B0 Pipeline Smoke Test...")
    os.makedirs('models/b0', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # 1. GPU Check
    gpu_report = get_gpu_info()
    
    X_full = pd.read_csv('data/interim/features/X_event_features.csv')
    y_full = pd.read_csv('data/interim/features/y_label.csv')
    
    # Verify no target leakage in X
    assert 'label' not in X_full.columns, "Target leakage detected!"
    assert 'label_quality' not in X_full.columns, "Target leakage detected!"
    
    # 2. Filter valid training samples
    # We exclude Unknown and Ambiguous
    valid_mask = ~y_full['label'].isin(["Unknown / Needs Verification", "AMBIGUOUS"])
    valid_mask = valid_mask & (y_full['label_quality'] == "WEAK_AGGREGATED")
    
    X_train = X_full[valid_mask].copy()
    y_train_raw = y_full[valid_mask].copy()
    
    event_ids = X_train['event_id'].values
    X_train = X_train.drop(columns=['event_id'])
    
    # Ensure dataset is large enough for XGBoost to even compile
    if len(X_train) == 0:
        raise ValueError("No valid weak labels found for training!")
        
    # Drop constant object columns that XGBoost rejects
    if 'history_sufficiency' in X_train.columns:
        X_train = X_train.drop(columns=['history_sufficiency'])
        
    print(f"Training on {len(X_train)} samples. THIS IS A SMOKE TEST ONLY. NOT VALID FOR GENERALIZATION.")
    
    # Map classes to integers
    unique_classes = sorted(y_train_raw['label'].unique().tolist())
    label_map = {name: i for i, name in enumerate(unique_classes)}
    y_train = y_train_raw['label'].map(label_map).values
    
    # Sample Weights (heuristic)
    # We'll just assign 1.0 to all WEAK_AGGREGATED for the smoke test
    weights = np.ones(len(y_train))
    
    # 3. Setup XGBoost
    params = {
        "objective": "multi:softprob",
        "num_class": len(unique_classes),
        "tree_method": gpu_report["tree_method"],
        "device": gpu_report["device_parameter"],
        "eval_metric": "mlogloss",
        "max_depth": 3,
        "learning_rate": 0.1,
        "seed": 42
    }
    
    start_time = datetime.now()
    try:
        dtrain = xgb.DMatrix(X_train, label=y_train, weight=weights)
        model = xgb.train(params, dtrain, num_boost_round=10)
    except Exception as e:
        print("GPU training failed, falling back to CPU.")
        gpu_report["gpu_used"] = False
        gpu_report["device_parameter"] = "cpu"
        gpu_report["fallback_reason"] = str(e)
        
        params["device"] = "cpu"
        dtrain = xgb.DMatrix(X_train, label=y_train, weight=weights)
        model = xgb.train(params, dtrain, num_boost_round=10)
        
    training_duration = (datetime.now() - start_time).total_seconds()
    gpu_report["training_duration_seconds"] = training_duration
    
    with open('data/processed/b0_gpu_report.json', 'w') as f:
        json.dump(gpu_report, f, indent=4)
        
    # 4. Save Model
    model.save_model('models/b0/xgboost_b0.json')
    
    with open('models/b0/label_mapping.json', 'w') as f:
        json.dump({v: k for k, v in label_map.items()}, f, indent=4)
        
    # Model Config
    config = {
        "model_type": "XGBoost",
        "training_mode": "MODE A - PIPELINE SMOKE TEST",
        "warning": "NOT VALID FOR GENERALIZATION. PROVISIONAL WEAK LABELS ONLY.",
        "params": params,
        "features": list(X_train.columns)
    }
    with open('models/b0/model_config.json', 'w') as f:
        json.dump(config, f, indent=4)
        
    # 5. Diagnostic Evaluation (Training Set Only)
    preds_proba = model.predict(dtrain)
    preds = np.argmax(preds_proba, axis=1)
    
    accuracy = (preds == y_train).mean()
    
    eval_report = {
        "mode": "MODE A - SMOKE TEST",
        "warning": "Evaluated on TRAINING data ONLY. Extreme overfitting expected.",
        "training_accuracy": float(accuracy),
        "total_samples": int(len(y_train)),
        "class_counts": {unique_classes[i]: int((y_train == i).sum()) for i in range(len(unique_classes))}
    }
    with open('models/b0/evaluation_report.json', 'w') as f:
        json.dump(eval_report, f, indent=4)
        
    # Feature Importance (Gain)
    importance = model.get_score(importance_type='gain')
    sorted_importance = {k: v for k, v in sorted(importance.items(), key=lambda item: item[1], reverse=True)}
    
    with open('models/b0/feature_importance.json', 'w') as f:
        json.dump(sorted_importance, f, indent=4)
        
    print("Training complete. Artifacts saved in models/b0/")

if __name__ == "__main__":
    train_b0()
