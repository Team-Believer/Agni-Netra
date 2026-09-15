import os
import urllib.request
import urllib.error
import json
import logging
import time
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import io

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BBOX_INDIA = "68,6,98,36"
INITIAL_BACKFILL_TARGET = 365
MANIFEST_FILE = 'data/ground_truth/firms_real_expanded/acquisition_manifest.json'

SOURCES_PREFERENCE = [
    ("VIIRS_NOAA21_NRT", None), # NOAA-21 currently has no SP in availability
    ("VIIRS_NOAA20_SP", "VIIRS_NOAA20_NRT"),
    ("VIIRS_SNPP_SP", "VIIRS_SNPP_NRT")
]

def load_manifest():
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_manifest(manifest):
    os.makedirs(os.path.dirname(MANIFEST_FILE), exist_ok=True)
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=4)

def fix_manifest(manifest):
    # Fix old NOAA21_SP entries that failed because they don't exist
    for key, data in manifest.items():
        if data.get('sensor_product') == 'VIIRS_NOAA21_SP' and data.get('status') == 'FAILED':
            data['status'] = 'UNAVAILABLE_PRODUCT_DATE'
            data['error_category'] = None
    save_manifest(manifest)
    return manifest

def get_data_availability(map_key):
    url = f"https://firms.modaps.eosdis.nasa.gov/api/data_availability/csv/{map_key}/ALL"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Agni-Netra-Acquisition/1.0'})
        response = urllib.request.urlopen(req, timeout=30)
        if response.getcode() == 200:
            csv_content = response.read().decode('utf-8')
            df = pd.read_csv(io.StringIO(csv_content))
            
            avail = {}
            for _, row in df.iterrows():
                try:
                    min_dt = pd.to_datetime(row['min_date']).date()
                    max_dt = pd.to_datetime(row['max_date']).date()
                    avail[row['data_id']] = (min_dt, max_dt)
                except:
                    pass
            return avail
    except Exception as e:
        logging.error(f"Failed to fetch data availability: {e}")
    return {}

def is_available(avail_dict, product, date_str):
    if not product:
        return False
    if product not in avail_dict:
        return False
    
    target_dt = pd.to_datetime(date_str).date()
    min_dt, max_dt = avail_dict[product]
    return min_dt <= target_dt <= max_dt

def download_batch(map_key, source, date_str, day_range=1):
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{map_key}/{source}/{BBOX_INDIA}/{day_range}/{date_str}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Agni-Netra-Acquisition/1.0'})
        response = urllib.request.urlopen(req, timeout=45)
        if response.getcode() == 200:
            return response.read().decode('utf-8'), 200
        return None, response.getcode()
    except urllib.error.HTTPError as e:
        return None, e.code
    except Exception as e:
        logging.error(f"Error downloading {source} for {date_str}: {str(e)}")
        return None, 500

def run_acquisition(target_days=INITIAL_BACKFILL_TARGET):
    load_dotenv()
    map_key = os.getenv('MAP_KEY') or os.getenv('FIRMS_MAP_KEY')
    if not map_key:
        logging.error("No MAP_KEY found in environment.")
        return
        
    avail_dict = get_data_availability(map_key)
    if not avail_dict:
        logging.error("Could not retrieve product availability. Aborting.")
        return
        
    logging.info(f"Loaded availability for {len(avail_dict)} products.")
    
    end_date = datetime.utcnow().date() - timedelta(days=1)
    target_dates = [(end_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(target_days)]
    
    manifest = load_manifest()
    manifest = fix_manifest(manifest)
    
    success_count = 0
    failure_count = 0
    empty_count = 0
    unavailable_count = 0
    rate_limit_hit = False
    
    for date_str in target_dates:
        if rate_limit_hit:
            break
            
        for sp_source, nrt_source in SOURCES_PREFERENCE:
            primary_source = sp_source
            fallback_source = nrt_source
            
            # Check availability first
            primary_avail = is_available(avail_dict, primary_source, date_str)
            
            if not primary_avail:
                key_unavail = f"{primary_source}_{date_str}"
                # Log as unavailable if it was our primary and we had no fallback, or if we want to track it
                # Actually, only request fallback if primary is unavailable
                used_source = fallback_source
                
                # Update manifest for primary to explicitly mark as unavailable
                if primary_source:
                    manifest[key_unavail] = {
                        "batch_id": key_unavail,
                        "sensor_product": primary_source,
                        "date": date_str,
                        "status": "UNAVAILABLE_PRODUCT_DATE",
                        "download_timestamp": datetime.utcnow().isoformat()
                    }
                    unavailable_count += 1
            else:
                used_source = primary_source
                
            if not used_source:
                continue
                
            used_avail = is_available(avail_dict, used_source, date_str)
            key_used = f"{used_source}_{date_str}"
            
            if not used_avail:
                manifest[key_used] = {
                    "batch_id": key_used,
                    "sensor_product": used_source,
                    "date": date_str,
                    "status": "UNAVAILABLE_PRODUCT_DATE",
                    "download_timestamp": datetime.utcnow().isoformat()
                }
                unavailable_count += 1
                continue
                
            # If already successfully acquired, skip
            if key_used in manifest and manifest[key_used].get("status") in ["SUCCESS", "EMPTY_VALID_RESPONSE"]:
                if manifest[key_used].get("status") == "SUCCESS":
                    success_count += 1
                else:
                    empty_count += 1
                continue
                
            logging.info(f"Downloading {key_used}...")
            csv_content, status = download_batch(map_key, used_source, date_str)
            time.sleep(1.2)
            
            raw_filename = f"data/ground_truth/firms_real_expanded/{key_used}.csv"
            
            record = {
                "batch_id": key_used,
                "sensor_product": used_source,
                "date": date_str,
                "requested_bbox": BBOX_INDIA,
                "download_timestamp": datetime.utcnow().isoformat(),
                "file_path": raw_filename,
            }
            
            if status == 200 and csv_content is not None:
                lines = csv_content.strip().split('\n')
                if len(lines) > 0 and 'latitude' in lines[0]:
                    with open(raw_filename, 'w', encoding='utf-8') as f:
                        f.write(csv_content)
                    rc = len(lines) - 1
                    if rc > 0:
                        record["status"] = "SUCCESS"
                        success_count += 1
                    else:
                        record["status"] = "EMPTY_VALID_RESPONSE"
                        empty_count += 1
                    record["record_count"] = rc
                else:
                    record["status"] = "FAILED"
                    record["error_category"] = "INVALID_SCHEMA"
                    failure_count += 1
            elif status == 429:
                logging.error("Rate limit (HTTP 429) hit! Backing off.")
                record["status"] = "RATE_LIMITED"
                record["error_category"] = "RATE_LIMIT"
                rate_limit_hit = True
            elif status == 404:
                record["status"] = "FAILED"
                record["error_category"] = "NOT_FOUND"
                failure_count += 1
            else:
                record["status"] = "FAILED"
                record["error_category"] = f"HTTP_{status}"
                failure_count += 1
                
            manifest[key_used] = record
            save_manifest(manifest)
            
            if rate_limit_hit:
                break
                
    # Normalize
    normalize_expanded_dataset(manifest)
    
    # Generate report
    generate_report(avail_dict, manifest, target_days)

def normalize_expanded_dataset(manifest):
    df_list = []
    for key, data in manifest.items():
        if data.get("status") == "SUCCESS" and os.path.exists(data.get("file_path")):
            try:
                df = pd.read_csv(data["file_path"])
                if not df.empty:
                    df['provenance_status'] = 'REAL_SOURCE'
                    df['source'] = data['sensor_product']
                    df_list.append(df)
            except:
                pass
    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['latitude', 'longitude', 'acq_date', 'acq_time', 'satellite'])
        combined_df.to_csv('data/ground_truth/firms_real_expanded/firms_historical_expanded_normalized.csv', index=False)

def generate_report(avail_dict, manifest, target_days):
    noaa20_sp = "VIIRS_NOAA20_SP" in avail_dict
    snpp_sp = "VIIRS_SNPP_SP" in avail_dict
    noaa21_sp = "VIIRS_NOAA21_SP" in avail_dict
    noaa21_nrt = "VIIRS_NOAA21_NRT" in avail_dict
    
    v = list(manifest.values())
    total_planned = sum(1 for x in v if x.get('status') != 'UNAVAILABLE_PRODUCT_DATE' and x.get('status') is not None)
    
    unavail_count = sum(1 for x in v if x.get('status') == 'UNAVAILABLE_PRODUCT_DATE')
    http_400_count = sum(1 for x in v if x.get('status') == 'FAILED' and x.get('error_category') == 'HTTP_400')
    success_c = sum(1 for x in v if x.get('status') == 'SUCCESS')
    empty_c = sum(1 for x in v if x.get('status') == 'EMPTY_VALID_RESPONSE')
    failed_c = sum(1 for x in v if x.get('status') == 'FAILED')
    
    completion = 0
    if total_planned > 0:
        completion = round(((success_c + empty_c) / total_planned) * 100, 2)
        
    report = f"""# FIRMS Ground Truth Expansion Report

NOAA20_SP_AVAILABLE: {noaa20_sp}
SNPP_SP_AVAILABLE: {snpp_sp}
NOAA21_SP_AVAILABLE: {noaa21_sp}
NOAA21_NRT_AVAILABLE: {noaa21_nrt}

TOTAL_PLANNED_VALID_REQUESTS: {total_planned}
UNAVAILABLE_PRODUCT_DATE_COUNT: {unavail_count}
HTTP_400_COUNT_AFTER_FIX: {http_400_count}
SUCCESS_COUNT: {success_c}
EMPTY_VALID_COUNT: {empty_c}
FAILED_COUNT: {failed_c}

COMPLETION_PERCENTAGE: {completion}%
"""
    os.makedirs('reports', exist_ok=True)
    with open('reports/ground_truth_firms_expansion.md', 'w') as f:
        f.write(report)
        
if __name__ == "__main__":
    run_acquisition()
