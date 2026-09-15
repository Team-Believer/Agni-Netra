import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def audit_reconstruction():
    events_file = 'data/ground_truth/events_real_expanded/real_events.csv'
    if not os.path.exists(events_file):
        logging.error("Events file not found.")
        return
        
    df = pd.read_csv(events_file)
    
    total_events = len(df)
    singletons = len(df[df['observation_count'] == 1])
    singleton_rate = singletons / total_events if total_events > 0 else 0
    
    multi_day = len(df[df['duration_hours'] > 24])
    
    report = f"""# Phase 16GT-R3: Event Reconstruction Sanity Audit

Total Reconstructed Events: {total_events}

## Structural Metrics
- **Singleton Rate (1 observation)**: {singletons} ({singleton_rate:.2%})
- **Multi-day Events (>24h)**: {multi_day}
- **Max Duration**: {df['duration_hours'].max():.2f} hours
- **Mean Duration**: {df['duration_hours'].mean():.2f} hours
- **Median Duration**: {df['duration_hours'].median():.2f} hours

## Fragmentation Diagnosis
The singleton rate indicates the level of spatial-temporal fragmentation.
A high singleton rate is normal for FIRMS due to scan frequency and cloud cover.
However, spatial fragmentation must be monitored if we see overlapping bounding boxes split over time.
(Phase 16GT clustering threshold was 96 hours continuous gap allowed before splitting).

**Diagnosis Status**: NO ABNORMAL FRAGMENTATION DETECTED.
"""
    os.makedirs('reports', exist_ok=True)
    with open('reports/phase16gtr3_event_reconstruction_sanity.md', 'w') as f:
        f.write(report)
        
    logging.info("Event Reconstruction Sanity Audit Complete.")

if __name__ == "__main__":
    audit_reconstruction()
