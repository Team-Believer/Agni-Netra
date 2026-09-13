import os
import urllib.request
import urllib.error
import json
import logging
import time
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BBOX_INDIA = "68,6,98,36"
TOTAL_DAYS = 90
MANIFEST_FILE = 'data/raw/firms/historical_real/acquisition_manifest.json'

# According to NASA FIRMS, older archives should use Standard Processing (SP)
# However, NRT might still work for the recent past. To ensure safety, we stick to NRT for recent 90 days.
SOURCES = ["VIIRS_SNPP_NRT", "VIIRS_NOAA20_NRT", "VIIRS_NOAA21_NRT"]

def load_manifest():
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_manifest(manifest):
    os.makedirs(os.path.dirname(MANIFEST_FILE), exist_ok=True)
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=4)

def download_batch(map_key, source, date_str):
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{map_key}/{source}/{BBOX_INDIA}/1/{date_str}"
    try:
        response = urllib.request.urlopen(url, timeout=30)
        if response.getcode() == 200:
            return response.read().decode('utf-8'), 200
        return None, response.getcode()
    except urllib.error.HTTPError as e:
        return None, e.code
    except Exception as e:
        logging.error(f"Error downloading {source} for {date_str}: {str(e)}")
        return None, 500

def run_acquisition():
    load_dotenv()
    map_key = os.getenv('MAP_KEY') or os.getenv('FIRMS_MAP_KEY')
    if not map_key:
        logging.error("No MAP_KEY found.")
        return
        
    end_date = datetime.utcnow().date() - timedelta(days=1)
    target_dates = [(end_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(TOTAL_DAYS)]
    
    manifest = load_manifest()
    
    # 1. Backfill already existing downloaded files from Phase 7B into manifest if not present
    for date_str in target_dates:
        for source in SOURCES:
            key = f"{source}_{date_str}"
            raw_filename = f"data/raw/firms/historical_real/{key}.csv"
            if key not in manifest and os.path.exists(raw_filename):
                try:
                    df = pd.read_csv(raw_filename)
                    manifest[key] = {
                        "batch_id": key,
                        "sensor_product": source,
                        "date": date_str,
                        "requested_bbox": BBOX_INDIA,
                        "status": "SUCCESS",
                        "record_count": len(df),
                        "download_timestamp": datetime.utcnow().isoformat(),
                        "file_path": raw_filename
                    }
                except:
                    pass
    
    save_manifest(manifest)
    
    success_count = 0
    failure_count = 0
    rate_limit_hit = False
    
    # 2. Acquire missing
    for date_str in target_dates:
        if rate_limit_hit:
            break
            
        for source in SOURCES:
            key = f"{source}_{date_str}"
            
            if key in manifest and manifest[key].get("status") in ["SUCCESS", "EMPTY_VALID_RESPONSE"]:
                continue
                
            raw_filename = f"data/raw/firms/historical_real/{key}.csv"
            logging.info(f"Downloading {key}...")
            
            csv_content, status = download_batch(map_key, source, date_str)
            
            record = {
                "batch_id": key,
                "sensor_product": source,
                "date": date_str,
                "requested_bbox": BBOX_INDIA,
                "download_timestamp": datetime.utcnow().isoformat(),
                "file_path": raw_filename,
            }
            
            if status == 200 and csv_content:
                lines = csv_content.strip().split('\n')
                # If headers exist but no data, it's length 1
                if len(lines) > 0 and 'latitude' in lines[0]:
                    with open(raw_filename, 'w', encoding='utf-8') as f:
                        f.write(csv_content)
                        
                    rc = len(lines) - 1
                    record["status"] = "SUCCESS" if rc > 0 else "EMPTY_VALID_RESPONSE"
                    record["record_count"] = rc
                    manifest[key] = record
                    success_count += 1
                else:
                    record["status"] = "FAILED"
                    record["error_category"] = "INVALID_SCHEMA"
                    manifest[key] = record
                    failure_count += 1
            elif status == 429:
                logging.error("Rate limit hit! Stopping acquisition.")
                record["status"] = "FAILED"
                record["error_category"] = "RATE_LIMIT"
                manifest[key] = record
                rate_limit_hit = True
                break
            else:
                record["status"] = "FAILED"
                record["error_category"] = f"HTTP_{status}"
                manifest[key] = record
                failure_count += 1
                
            save_manifest(manifest)
            
            # Rate limit protection
            time.sleep(0.5)
            
    logging.info(f"Acquisition loop finished. Successes this run: {success_count}, Failures: {failure_count}")
    
    # 3. Normalization
    normalize_dataset(manifest)

def normalize_dataset(manifest):
    logging.info("Normalizing successful batches...")
    df_list = []
    total_observations = 0
    unique_dates = set()
    
    for key, data in manifest.items():
        if data.get("status") == "SUCCESS" and os.path.exists(data.get("file_path")):
            try:
                df = pd.read_csv(data["file_path"])
                if not df.empty:
                    # Synthetic check
                    if 'history_sufficiency' in df.columns or df['frp'].max() > 9000:
                        logging.error(f"SYNTHETIC DATA DETECTED IN {data['file_path']}! SKIPPING!")
                        continue
                    
                    df['provenance_status'] = 'REAL_SOURCE'
                    df['source'] = data['sensor_product']
                    df_list.append(df)
                    total_observations += len(df)
                    unique_dates.add(data["date"])
            except Exception as e:
                logging.error(f"Error reading {data['file_path']}: {e}")
                
    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)
        # Check geographic sanity
        outside_bounds = combined_df[
            (combined_df['latitude'] < 6) | (combined_df['latitude'] > 36) |
            (combined_df['longitude'] < 68) | (combined_df['longitude'] > 98)
        ]
        if len(outside_bounds) > 0:
            logging.warning(f"Found {len(outside_bounds)} records outside requested BBOX!")
            
        normalized_path = 'data/interim/firms_historical_real_normalized.csv'
        combined_df.to_csv(normalized_path, index=False)
        logging.info(f"Normalized dataset saved to {normalized_path} with {len(combined_df)} records.")
        
        # Save metadata
        metadata = {
            "dataset_version": "firms-india-90d-v1",
            "provenance": "REAL_SOURCE",
            "requested_bbox": BBOX_INDIA,
            "sensors": SOURCES,
            "row_count": total_observations,
            "unique_dates": len(unique_dates),
            "creation_timestamp": datetime.utcnow().isoformat()
        }
        with open('data/processed/historical_dataset_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=4)
            
if __name__ == "__main__":
    run_acquisition()
