import pandas as pd
import os

def init_schemas():
    os.makedirs('data/labels', exist_ok=True)
    
    # 1. verified_events.csv
    verified_cols = [
        'event_id',
        'verified_class',
        'label_tier',
        'verification_status',
        'verification_source',
        'verification_method',
        'confidence',
        'review_notes',
        'reviewer_id',
        'verification_date'
    ]
    pd.DataFrame(columns=verified_cols).to_csv('data/labels/verified_events.csv', index=False)
    
    # 2. disputed_events.csv
    disputed_cols = [
        'event_id',
        'candidate_class',
        'reviewer_1_class',
        'reviewer_2_class',
        'dispute_reason',
        'reviewer_1_id',
        'reviewer_2_id',
        'date_logged'
    ]
    pd.DataFrame(columns=disputed_cols).to_csv('data/labels/disputed_events.csv', index=False)
    
    # 3. label_provenance.csv
    provenance_cols = [
        'event_id',
        'original_weak_label',
        'original_weak_label_source',
        'verified_class',
        'verification_date',
        'evidence_chain_hash'
    ]
    pd.DataFrame(columns=provenance_cols).to_csv('data/labels/label_provenance.csv', index=False)
    
    print("Empty verification schemas initialized.")

if __name__ == "__main__":
    init_schemas()
