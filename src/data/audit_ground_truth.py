import pandas as pd
import os
import json

def audit_ground_truth():
    report = {
        "candidate_count": 0,
        "verified_count": 0,
        "gold_count": 0,
        "disputed_count": 0,
        "independence_violations": 0,
        "duplicates_found": 0,
        "warnings": []
    }
    
    # 1. Audit Candidates
    try:
        candidates = pd.read_csv('data/labels/ground_truth_candidates.csv')
        report["candidate_count"] = len(candidates)
        if len(candidates['event_id'].unique()) != len(candidates):
            report["duplicates_found"] += (len(candidates) - len(candidates['event_id'].unique()))
            report["warnings"].append("Duplicate event_ids found in candidates.")
    except Exception as e:
        report["warnings"].append(f"Failed to read candidates: {e}")
        
    # 2. Audit Verified Schema
    try:
        verified = pd.read_csv('data/labels/verified_events.csv')
        report["verified_count"] = len(verified)
        
        gold_subset = verified[verified['label_tier'] == 'GOLD']
        report["gold_count"] = len(gold_subset)
        
        if len(verified['event_id'].unique()) != len(verified):
            report["duplicates_found"] += (len(verified) - len(verified['event_id'].unique()))
            report["warnings"].append("Duplicate event_ids found in verified_events.")
            
        # Independence Rule Check
        banned_sources = ['B2', 'B1', 'OSM heuristic', 'Phase 3', 'Phase 5']
        for _, row in gold_subset.iterrows():
            source = str(row['verification_source']).lower()
            for b in banned_sources:
                if b.lower() in source:
                    report["independence_violations"] += 1
                    report["warnings"].append(f"Independence violation for {row['event_id']}: Source contains '{b}'")
                    
    except Exception as e:
        report["warnings"].append(f"Failed to read verified events: {e}")
        
    # 3. Audit Disputed Schema
    try:
        disputed = pd.read_csv('data/labels/disputed_events.csv')
        report["disputed_count"] = len(disputed)
    except Exception as e:
        report["warnings"].append(f"Failed to read disputed events: {e}")
        
    # Document limitation since human review is pending
    if report["verified_count"] == 0:
        report["status"] = "PENDING_HUMAN_REVIEW"
        report["note"] = "Framework established. Actual GOLD/SILVER labels remain pending independent human/external verification."
    else:
        report["status"] = "PARTIALLY_VERIFIED"
        
    with open('data/labels/ground_truth_audit_report.json', 'w') as f:
        json.dump(report, f, indent=4)
        
    print(json.dumps(report, indent=4))
    
if __name__ == "__main__":
    audit_ground_truth()
