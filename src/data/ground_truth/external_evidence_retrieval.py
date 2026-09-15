import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

EXPECTED_COLUMNS = [
    'incident_id',
    'date',
    'location_name',
    'latitude',
    'longitude',
    'tier',
    'source_url',
    'description'
]

VALID_TIERS = ['Tier 1', 'Tier 2', 'Tier 3', 'Tier 4']

def ingest_external_evidence():
    input_file = 'data/raw/external_evidence.csv'
    output_dir = 'data/ground_truth/external_evidence'
    
    if not os.path.exists(input_file):
        logging.warning(f"No external evidence file found at {input_file}. Creating empty schema file.")
        os.makedirs(os.path.dirname(input_file), exist_ok=True)
        pd.DataFrame(columns=EXPECTED_COLUMNS).to_csv(input_file, index=False)
        return
        
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        logging.error(f"Failed to read {input_file}: {e}")
        return
        
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        logging.error(f"Missing required columns in external evidence: {missing_cols}")
        return
        
    # Validate Tiers
    invalid_tiers = df[~df['tier'].isin(VALID_TIERS)]
    if not invalid_tiers.empty:
        logging.error(f"Found invalid tiers. Allowed: {VALID_TIERS}. Invalid:\n{invalid_tiers['tier'].values}")
        return
        
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    if df['date'].isnull().any():
        logging.error("Some dates could not be parsed.")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    out_path = f"{output_dir}/validated_external_evidence.csv"
    df.to_csv(out_path, index=False)
    
    logging.info(f"Successfully ingested and validated {len(df)} external evidence records to {out_path}.")

if __name__ == "__main__":
    ingest_external_evidence()
