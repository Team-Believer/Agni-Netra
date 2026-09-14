import pandas as pd
import numpy as np
import os
import json
import xgboost as xgb

def run_decision_pipeline(filepath, output_dir):
    print(f"Running Decision Pipeline on {filepath}...")
    df = pd.read_csv(filepath)
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. B2 Classification State (Re-running the 13D pipeline internally to get states)
    unknown_gate = xgb.XGBClassifier()
    unknown_gate.load_model('models/b2_precision_optimized/unknown_gate.json')
    macro_classifier = xgb.XGBClassifier()
    macro_classifier.load_model('models/b2_optimized/hierarchical_l1.json')
    specialist_v2 = xgb.XGBClassifier()
    specialist_v2.load_model('models/b2_precision_optimized/industrial_specialist_v2.json')
    
    features = [
        'current_max_frp', 'current_duration', 'observation_count_so_far', 
        'proxy_industrial_context', 'proxy_vegetation_context',
        'frp_slope_online', 'burstiness_online', 
        'current_vs_baseline_deviation_online', 'evidence_completeness_v2',
        'sentinel_available_flag', 'evidence_strength', 'evidence_contradiction', 'evidence_convergence'
    ]
    old_features = [
        'current_max_frp', 'current_duration', 'observation_count_so_far', 
        'proxy_industrial_context', 'proxy_vegetation_context',
        'frp_slope_online', 'burstiness_online', 
        'current_vs_baseline_deviation_online', 'evidence_completeness_score',
        'sentinel_available_flag'
    ]
    
    X = df[features]
    prob_unknown = unknown_gate.predict_proba(X)[:, 1]
    prob_macro = macro_classifier.predict_proba(df[old_features])
    prob_specialist = specialist_v2.predict_proba(X)[:, 1]
    
    classifications = []
    class_confidences = []
    
    for i in range(len(df)):
        if df.iloc[i]['evidence_convergence'] < 0.20:
            classifications.append('Insufficient Evidence')
            class_confidences.append(0.0)
            continue
        if prob_unknown[i] < 0.60:
            classifications.append('Unknown')
            class_confidences.append(prob_unknown[i])
            continue
            
        p_m = prob_macro[i]
        if abs(p_m[0] - p_m[1]) < 0.15:
            classifications.append('Needs Verification')
            class_confidences.append(max(p_m))
            continue
            
        if np.argmax(p_m) == 0: # Fire-like
            if prob_specialist[i] >= 0.65:
                classifications.append('Industrial Fire')
                class_confidences.append(prob_specialist[i])
            else:
                classifications.append('Wildfire / Other Fire')
                class_confidences.append(1.0 - prob_specialist[i])
        elif np.argmax(p_m) == 1:
            classifications.append('Routine Flare / Persistent')
            class_confidences.append(p_m[1])
        else:
            classifications.append('Unknown')
            class_confidences.append(p_m[2])
            
    df['classification_state'] = classifications
    df['classification_confidence'] = class_confidences
    
    # 2. Data Quality & Evidence Completeness
    df['data_quality_score'] = df['evidence_contradiction'].apply(lambda x: 1.0 - x)
    df['evidence_completeness'] = df['evidence_completeness_v2']
    
    # 3. Severity Engine (Intensity/Duration)
    # Normalized FRP * Normalized Duration
    norm_frp = (np.log1p(df['current_max_frp']) / np.log1p(200.0)).clip(0, 1)
    norm_dur = (df['current_duration'] / 48.0).clip(0, 1)
    df['severity_score'] = (norm_frp * 0.7) + (norm_dur * 0.3)
    
    # 4. Impact Engine (Exposure / Consequence)
    # Using the generated observable proxies
    df['exposure_score'] = df[['obs_facility_importance', 'obs_critical_infrastructure_proximity']].max(axis=1)
    df['consequence_score'] = df[['obs_population_density', 'obs_environmental_sensitivity']].max(axis=1)
    df['impact_score'] = (df['exposure_score'] * 0.6) + (df['consequence_score'] * 0.4)
    
    # 5. Hazard Engine (Severity + Classification)
    hazard = []
    for i in range(len(df)):
        cls = df.iloc[i]['classification_state']
        sev = df.iloc[i]['severity_score']
        if cls == 'Industrial Fire':
            hazard.append(min(1.0, sev + 0.3))
        elif cls == 'Routine Flare / Persistent':
            hazard.append(sev * 0.4) # Flares are low hazard
        elif cls == 'Wildfire / Other Fire':
            hazard.append(sev * 0.8)
        else:
            hazard.append(sev * 0.6) # Unknowns inherit base severity hazard
    df['hazard_score'] = hazard
    
    # 6. Risk Engine (Base Risk & Risk Confidence)
    df['base_risk_score'] = df['hazard_score'] * df['impact_score']
    
    # Risk Confidence = f(data_quality, evidence_completeness, classification_confidence)
    df['risk_confidence'] = (df['data_quality_score'] * 0.3) + (df['evidence_completeness'] * 0.4) + (df['classification_confidence'] * 0.3)
    df['uncertainty_score'] = 1.0 - df['risk_confidence']
    
    # 7. Priority Engine
    priority_scores = []
    priority_classes = []
    for i in range(len(df)):
        risk = df.iloc[i]['base_risk_score']
        conf = df.iloc[i]['risk_confidence']
        urgency = df.iloc[i]['obs_time_urgency']
        
        # Base Priority is Risk + Urgency
        p_score = (risk * 0.7) + (urgency * 0.3)
        priority_scores.append(p_score)
        
        # Priority Routing Logic
        if risk >= 0.7 and conf >= 0.7:
            priority_classes.append('P0 - IMMEDIATE REVIEW')
        elif risk >= 0.7 and conf < 0.7:
            priority_classes.append('P1 - HIGH VERIFICATION PRIORITY')
        elif risk >= 0.4 and df.iloc[i]['frp_slope_online'] > 0.5: # Rapid escalation
            priority_classes.append('P1 - HIGH PRIORITY (ESCALATING)')
        elif risk >= 0.4:
            priority_classes.append('P2 - MONITOR')
        elif risk < 0.4 and conf < 0.5:
            priority_classes.append('P3 - REQUEST MORE DATA')
        else:
            priority_classes.append('P4 - INFORMATIONAL')
            
    df['priority_score'] = priority_scores
    df['priority_class'] = priority_classes
    
    # 8. Lifecycle Engine
    lifecycle = []
    for i in range(len(df)):
        obs_count = df.iloc[i]['observation_count_so_far']
        slope = df.iloc[i]['frp_slope_online']
        if obs_count <= 2:
            lifecycle.append('NEW')
        elif slope > 0.2:
            lifecycle.append('ESCALATING')
        elif slope < -0.2:
            lifecycle.append('DE-ESCALATING')
        else:
            lifecycle.append('STABLE')
    df['event_lifecycle_state'] = lifecycle
    
    # 9. Explanation Engine
    why = []
    why_not = []
    what_changed = []
    what_unknown = []
    recommended_action = []
    
    for i in range(len(df)):
        row = df.iloc[i]
        
        # WHY
        w = []
        if row['thermal_support'] > 0.7: w.append("FRP is substantially above the historical baseline.")
        if row['obs_facility_importance'] > 0.7: w.append("High exposure context detected (critical facility proximity).")
        if row['sentinel_support'] > 0.7: w.append("Sentinel-2 corroborates anomalous thermal signature.")
        if row['classification_state'] == 'Industrial Fire': w.append("Behavioral signature strongly aligns with Industrial Fire.")
        why.append(" | ".join(w) if w else "Routine thermal behavior.")
        
        # WHY NOT
        wn = []
        if row['classification_state'] == 'Routine Flare / Persistent': wn.append("Thermal signature matches historical persistent flare pattern.")
        if row['classification_confidence'] < 0.6: wn.append("Classification confidence is below actionable threshold.")
        if row['evidence_contradiction'] > 0.4: wn.append("Evidence streams are heavily contradictory.")
        if pd.isna(row['S2_NDVI_online']): wn.append("Sentinel-2 imagery is unavailable or cloudy.")
        why_not.append(" | ".join(wn) if wn else "No strong mitigating factors identified.")
        
        # WHAT CHANGED
        wc = []
        if row['frp_slope_online'] > 0.5: wc.append("Rapid increase in FRP detected.")
        if row['current_vs_baseline_deviation_online'] > 2.0: wc.append("Thermal intensity deviates >2 std dev from historical norm.")
        what_changed.append(" | ".join(wc) if wc else "No significant behavioral changes detected.")
        
        # WHAT IS UNKNOWN
        wu = []
        if pd.isna(row['S2_NDVI_online']): wu.append("Missing Sentinel-2 imagery.")
        if row['observation_count_so_far'] < 3: wu.append("Event is immature (insufficient temporal history).")
        if row['classification_state'] in ['Unknown', 'Needs Verification', 'Insufficient Evidence']: wu.append(f"Classification unresolved ({row['classification_state']}).")
        what_unknown.append(" | ".join(wu) if wu else "All critical evidence streams are present.")
        
        # RECOMMENDED ACTION
        p_class = row['priority_class']
        if 'P0' in p_class:
            recommended_action.append('ESCALATE_FOR_OPERATOR_REVIEW')
        elif 'VERIFICATION' in p_class or 'REQUEST' in p_class:
            recommended_action.append('VERIFY_SOURCE_AND_CLASS')
        elif 'P2' in p_class:
            recommended_action.append('MONITOR')
        else:
            recommended_action.append('CLOSE_AS_LOW_PRIORITY')
            
    df['why'] = why
    df['why_not'] = why_not
    df['what_changed'] = what_changed
    df['what_is_unknown'] = what_unknown
    df['recommended_action'] = recommended_action
    
    # Save Decision Table
    out_cols = [
        'TRUE_DEPLOYMENT_SIM_CLASS', 'severity_score', 'exposure_score', 'consequence_score', 'impact_score',
        'hazard_score', 'base_risk_score', 'risk_confidence', 'uncertainty_score',
        'priority_score', 'priority_class', 'classification_state', 'classification_confidence',
        'evidence_completeness', 'data_quality_score', 'event_lifecycle_state',
        'why', 'why_not', 'what_changed', 'what_is_unknown', 'recommended_action'
    ]
    df[out_cols].to_csv(os.path.join(output_dir, 'decision_table.csv'), index=False)
    print("Decision Pipeline Complete. Table saved.")

if __name__ == "__main__":
    run_decision_pipeline('data/synthetic/deployment_realistic/unseen_deployment_C.csv', 'data/processed/decision_intelligence')
