import os
import json
import glob
import logging
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def freeze_dataset():
    manifest_path = 'data/ground_truth/firms_real_expanded/acquisition_manifest.json'
    canonical_manifest_path = 'data/ground_truth/firms_real_expanded/canonical_observation_manifest.csv'
    
    if not os.path.exists(manifest_path):
        logging.error("Acquisition manifest not found.")
        return
        
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    all_files = glob.glob('data/ground_truth/firms_real_expanded/*.csv')
    
    records = []
    
    # 1. Process Manifest Entries
    for key, data in manifest.items():
        status = data.get('status')
        fpath = data.get('file_path')
        
        mark = "EXCLUDE_UNKNOWN"
        if status == 'UNAVAILABLE_PRODUCT_DATE':
            mark = "UNAVAILABLE"
        elif status == 'FAILED' or status == 'FAILED_RETAINED':
            mark = "FAILED"
        elif status == 'EMPTY_VALID_RESPONSE':
            mark = "EMPTY"
        elif status == 'SUCCESS':
            mark = "INCLUDE"
            
        records.append({
            'batch_id': key,
            'file_path': fpath,
            'status': status,
            'mark': mark,
            'date': data.get('date'),
            'product': data.get('sensor_product')
        })
        
    # 2. Process Aggregate/Other files
    known_paths = [r['file_path'] for r in records if r['file_path']]
    for f in all_files:
        f = f.replace('\\', '/')
        if f not in known_paths:
            # Check if it's the aggregate
            if 'firms_historical_expanded_normalized.csv' in f:
                records.append({
                    'batch_id': 'AGGREGATE_NORMALIZED',
                    'file_path': f,
                    'status': 'LOCAL_AGGREGATE',
                    'mark': 'EXCLUDE_AGGREGATE',
                    'date': None,
                    'product': None
                })
            else:
                # Some other file? Mark as EXCLUDE_UNKNOWN
                records.append({
                    'batch_id': os.path.basename(f),
                    'file_path': f,
                    'status': 'UNKNOWN_LOCAL_FILE',
                    'mark': 'EXCLUDE_UNKNOWN',
                    'date': None,
                    'product': None
                })
                
    canonical_df = pd.DataFrame(records)
    canonical_df.to_csv(canonical_manifest_path, index=False)
    
    # 3. Read included files to compute freeze stats
    include_files = canonical_df[canonical_df['mark'] == 'INCLUDE']['file_path'].tolist()
    
    total_obs = 0
    total_bytes = 0
    satellites = set()
    instruments = set()
    dates = set()
    products = set()
    
    # Duplicate checking across included files
    # We will build a set of hashes or unique identifiers to check row-level duplication
    unique_rows = set()
    exact_duplicates = 0
    
    for f in include_files:
        if os.path.exists(f):
            total_bytes += os.path.getsize(f)
            df = pd.read_csv(f)
            
            # Record metadata
            if 'satellite' in df.columns: satellites.update(df['satellite'].unique())
            if 'instrument' in df.columns: instruments.update(df['instrument'].unique())
            if 'acq_date' in df.columns: dates.update(df['acq_date'].unique())
            
            # Row level duplicate detection
            for _, row in df.iterrows():
                row_tuple = (row['latitude'], row['longitude'], row['acq_date'], row['acq_time'], row.get('satellite', ''))
                if row_tuple in unique_rows:
                    exact_duplicates += 1
                else:
                    unique_rows.add(row_tuple)
                    
            total_obs += len(df)
            
    products = set(canonical_df[canonical_df['mark'] == 'INCLUDE']['product'].unique())
    
    min_date = min(dates) if dates else None
    max_date = max(dates) if dates else None
    
    # 4. Generate report
    report = f"""# Phase 16GT-R2 Dataset Freeze

## Overview
- **Total CSV Files Included**: {len(include_files)}
- **Total Observations (Raw)**: {total_obs}
- **Total Observations (Unique)**: {len(unique_rows)}
- **Exact Row Duplicates**: {exact_duplicates}
- **Total Bytes**: {total_bytes} ({round(total_bytes/1024/1024, 2)} MB)
- **Min Date**: {min_date}
- **Max Date**: {max_date}
- **Unique Dates**: {len(dates)}

## Sources
- **Products**: {', '.join(products)}
- **Satellites**: {', '.join(satellites)}
- **Instruments**: {', '.join(instruments)}

## File Level Statistics
- **SUCCESS (INCLUDE)**: {len(canonical_df[canonical_df['mark'] == 'INCLUDE'])}
- **EMPTY_VALID_RESPONSE**: {len(canonical_df[canonical_df['mark'] == 'EMPTY'])}
- **UNAVAILABLE_PRODUCT_DATE**: {len(canonical_df[canonical_df['mark'] == 'UNAVAILABLE'])}
- **GENUINE FAILURES**: {len(canonical_df[canonical_df['mark'] == 'FAILED'])}
- **EXCLUDED AGGREGATES**: {len(canonical_df[canonical_df['mark'] == 'EXCLUDE_AGGREGATE'])}

Dataset frozen on {datetime.utcnow().isoformat()}
"""

    os.makedirs('reports', exist_ok=True)
    with open('reports/phase16gtr2_dataset_freeze.md', 'w') as f:
        f.write(report)
        
    logging.info("Dataset freeze complete.")

if __name__ == "__main__":
    freeze_dataset()
