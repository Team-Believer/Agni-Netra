import os
import json
import xgboost as xgb
import pandas as pd
from datetime import datetime

class AgniNetraB0Inference:
    def __init__(self, model_dir='models/b0'):
        self.model = xgb.Booster()
        self.model.load_model(f'{model_dir}/xgboost_b0.json')
        
        with open(f'{model_dir}/label_mapping.json', 'r') as f:
            mapping = json.load(f)
            # JSON keys are strings, convert back to int
            self.label_mapping = {int(k): v for k, v in mapping.items()}
            
        with open(f'{model_dir}/model_config.json', 'r') as f:
            self.config = json.load(f)
            self.features = self.config['features']
            
    def predict_event(self, event_features: dict):
        df = pd.DataFrame([event_features])
        df = df[self.features] # ensure ordering
        
        dtest = xgb.DMatrix(df)
        preds_proba = self.model.predict(dtest)[0]
        
        top_idx = preds_proba.argmax()
        top_label = self.label_mapping[top_idx]
        top_conf = float(preds_proba[top_idx])
        
        top_3 = []
        sorted_indices = preds_proba.argsort()[::-1][:3]
        for idx in sorted_indices:
            top_3.append({
                "label": self.label_mapping[idx],
                "probability": float(preds_proba[idx])
            })
        
        return {
            "event_id": event_features.get("event_id", "UNKNOWN"),
            "classification": {
                "label": top_label,
                "confidence": top_conf
            },
            "model_status": "WEAK_LABEL_POC",
            "top_3": top_3,
            "inference_timestamp": datetime.utcnow().isoformat()
        }

if __name__ == "__main__":
    inf = AgniNetraB0Inference()
    X = pd.read_csv('data/interim/features/X_event_features.csv')
    y = pd.read_csv('data/interim/features/y_label.csv')
    
    # Test one Industrial Fire
    idx_ind = y[y['label'] == 'Industrial Fire'].index[0]
    sample_ind = X.iloc[idx_ind].to_dict()
    sample_ind['event_id'] = y.iloc[idx_ind]['event_id']
    print(json.dumps(inf.predict_event(sample_ind), indent=2))
