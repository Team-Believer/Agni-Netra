import pandas as pd
import numpy as np
import os
import json

class VirtualReviewer:
    def __init__(self, name, strictness):
        self.name = name
        self.strictness = strictness  # 'conservative', 'balanced', 'sensitive'
        
        if strictness == 'conservative':
            self.unknown_threshold = 0.60
            self.confidence_multiplier = 0.8
        elif strictness == 'sensitive':
            self.unknown_threshold = 0.35
            self.confidence_multiplier = 1.2
        else: # balanced
            self.unknown_threshold = 0.45
            self.confidence_multiplier = 1.0

    def evaluate(self, packet, model_assistance_prediction=None, model_assistance_influence=0.0):
        # 1. Base Evidence Scoring
        # The scores are unnormalized support logits for each class
        scores = {
            'Industrial Fire': 0.0,
            'Routine Flare / Persistent Industrial Heat': 0.0,
            'Wildfire': 0.0,
            'Agricultural Burn': 0.0,
            'Other Thermal Source': 0.1 # Baseline
        }
        
        support_reasons = {}
        contradictions = []
        
        # Thermal & Behavior Support
        frp = packet['current_max_frp']
        duration = packet['current_duration']
        
        if frp > 50:
            scores['Wildfire'] += 2.0
            scores['Industrial Fire'] += 1.0
            support_reasons['thermal_support'] = 'High FRP suggests large-scale event.'
        elif frp > 15:
            scores['Routine Flare / Persistent Industrial Heat'] += 1.0
            scores['Industrial Fire'] += 0.5
            scores['Other Thermal Source'] += 0.5
            support_reasons['thermal_support'] = 'Moderate FRP.'
        else:
            scores['Agricultural Burn'] += 1.0
            support_reasons['thermal_support'] = 'Low FRP.'
            
        if duration > 100:
            scores['Routine Flare / Persistent Industrial Heat'] += 3.0
            scores['Other Thermal Source'] += 0.5
            contradictions.append("Wildfire/Ag Burn highly unlikely due to extreme duration.")
            scores['Wildfire'] -= 2.0
            scores['Agricultural Burn'] -= 2.0
            support_reasons['behavior_support'] = 'Extreme persistence indicates continuous operation.'
        elif duration < 12:
            scores['Agricultural Burn'] += 2.0
            scores['Wildfire'] += 1.0
            scores['Routine Flare / Persistent Industrial Heat'] -= 1.0
            support_reasons['behavior_support'] = 'Transient behavior.'
            
        # Context Support
        if packet['proxy_industrial_context'] > 0.6:
            scores['Industrial Fire'] += 1.5
            scores['Routine Flare / Persistent Industrial Heat'] += 2.0
            scores['Wildfire'] -= 1.0
            support_reasons['context_support'] = 'Strong industrial built-up proximity.'
        
        if packet['proxy_vegetation_context'] > 0.6:
            scores['Wildfire'] += 1.5
            scores['Agricultural Burn'] += 1.5
            scores['Routine Flare / Persistent Industrial Heat'] -= 1.0
            support_reasons['context_support'] = 'Strong vegetative/rural proximity.'
            
        # Sentinel Support
        has_sentinel = not np.isnan(packet['S2_NDVI_online'])
        if has_sentinel:
            if packet['S2_NDVI_online'] < 0.2 and packet['proxy_industrial_context'] > 0.5:
                scores['Routine Flare / Persistent Industrial Heat'] += 1.0
                support_reasons['sentinel_support'] = 'Low NDVI corroborates built-up/industrial scene.'
            elif packet['S2_NDVI_online'] > 0.5:
                scores['Wildfire'] += 1.0
                scores['Agricultural Burn'] += 1.0
                support_reasons['sentinel_support'] = 'High NDVI corroborates vegetation.'
        else:
            support_reasons['missing_evidence'] = 'Sentinel-2 optical data unavailable.'
            
        # Add random decision noise strictly for reviewer uniqueness (simulating human subjectivity)
        # Seeded deterministically by event_id and reviewer name
        np.random.seed(int(packet['event_id'].split('-')[-1]) + hash(self.name) % 10000)
        for k in scores:
            scores[k] += np.random.normal(0, 0.2)
            
        # Softmax to get confidence
        exp_scores = np.exp(np.array(list(scores.values())))
        probs = exp_scores / exp_scores.sum()
        prob_dict = {k: p for k, p in zip(scores.keys(), probs)}
        
        # 2. Model Assistance Application
        if model_assistance_prediction and model_assistance_influence > 0:
            for k in prob_dict:
                prob_dict[k] = prob_dict[k] * (1 - model_assistance_influence)
            if model_assistance_prediction in prob_dict:
                prob_dict[model_assistance_prediction] += model_assistance_influence
                
            # Re-normalize
            total = sum(prob_dict.values())
            for k in prob_dict:
                prob_dict[k] /= total
                
        # 3. Final Decision
        best_class = max(prob_dict, key=prob_dict.get)
        confidence = prob_dict[best_class] * self.confidence_multiplier
        
        if confidence < self.unknown_threshold:
            best_class = 'Unknown'
            
        return {
            'reviewer_id': self.name,
            'class_guess': best_class,
            'confidence': min(confidence, 1.0),
            'thermal_support': support_reasons.get('thermal_support', ''),
            'behavior_support': support_reasons.get('behavior_support', ''),
            'context_support': support_reasons.get('context_support', ''),
            'sentinel_support': support_reasons.get('sentinel_support', ''),
            'contradictory_evidence': '; '.join(contradictions),
            'missing_evidence': support_reasons.get('missing_evidence', '')
        }

def simulate_expert_review():
    print("Starting Virtual Expert Simulation...")
    os.makedirs('data/synthetic', exist_ok=True)
    
    # Load observable data
    df = pd.read_csv('data/synthetic/synthetic_ground_truth.csv')
    
    # Provide fake B2 predictions strictly for the MODEL_ASSISTED experiment
    # In reality, this would be loaded from the b2_evaluation predictions, but we simulate it here by adding noise to true class
    # to represent an imperfect 80% accurate model.
    np.random.seed(999)
    def fake_b2(c):
        if np.random.rand() < 0.2:
            return np.random.choice(['Industrial Fire', 'Routine Flare / Persistent Industrial Heat', 'Wildfire', 'Agricultural Burn', 'Other Thermal Source'])
        return c
    df['simulated_b2_prediction'] = df['TRUE_SYNTHETIC_CLASS'].apply(fake_b2)
    
    reviewers = [
        VirtualReviewer('REVIEWER_A_CONSERVATIVE', 'conservative'),
        VirtualReviewer('REVIEWER_B_BALANCED', 'balanced'),
        VirtualReviewer('REVIEWER_C_SENSITIVE', 'sensitive')
    ]
    
    all_reviews = []
    consensus_labels = []
    
    for idx, row in df.iterrows():
        # Build strict evidence packet (stripping forbidden variables)
        packet = row[['event_id', 'current_max_frp', 'current_duration', 'proxy_industrial_context', 'proxy_vegetation_context', 'S2_NDVI_online']].to_dict()
        
        # Run BLIND mode
        blind_results = [r.evaluate(packet) for r in reviewers]
        for br in blind_results:
            br['event_id'] = packet['event_id']
            br['review_mode'] = 'BLIND'
            br['model_influence'] = 0.0
            all_reviews.append(br)
            
        # Run MODEL_ASSISTED mode
        assist_results = [r.evaluate(packet, model_assistance_prediction=row['simulated_b2_prediction'], model_assistance_influence=0.25) for r in reviewers]
        for ar in assist_results:
            ar['event_id'] = packet['event_id']
            ar['review_mode'] = 'MODEL_ASSISTED'
            ar['model_influence'] = 0.25
            all_reviews.append(ar)
            
        # Determine Consensus (Using BLIND mode for the formal synthetic labels)
        classes = [br['class_guess'] for br in blind_results]
        confs = [br['confidence'] for br in blind_results]
        
        # Consensus Rules
        unique_classes = set(c for c in classes if c != 'Unknown')
        
        if len(unique_classes) == 1 and classes.count(list(unique_classes)[0]) >= 2:
            final_class = list(unique_classes)[0]
            avg_conf = np.mean([confs[i] for i, c in enumerate(classes) if c == final_class])
            if avg_conf > 0.7:
                label_tier = 'SIMULATED_GOLD'
            else:
                label_tier = 'SIMULATED_SILVER'
        elif len(unique_classes) > 1:
            final_class = 'Unknown'
            label_tier = 'SIMULATED_DISPUTED'
        else:
            final_class = 'Unknown'
            label_tier = 'SIMULATED_UNKNOWN'
            
        consensus_labels.append({
            'event_id': packet['event_id'],
            'simulated_verified_class': final_class,
            'label_tier': label_tier,
            'label_source': 'VIRTUAL_EXPERT_SIMULATION',
            'reviewer_agreement': len(set(classes)) == 1
        })
        
    pd.DataFrame(all_reviews).to_csv('data/synthetic/simulated_expert_reviews.csv', index=False)
    pd.DataFrame(consensus_labels).to_csv('data/synthetic/simulated_expert_labels.csv', index=False)
    print(f"Simulation complete. Processed {len(df)} events.")

if __name__ == "__main__":
    simulate_expert_review()
