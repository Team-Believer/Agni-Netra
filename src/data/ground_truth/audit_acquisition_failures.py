import os
import json
import urllib.request
import urllib.error
import logging
import time
from datetime import datetime
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BBOX_INDIA = "68,6,98,36"
MANIFEST_FILE = 'data/ground_truth/firms_real_expanded/acquisition_manifest.json'

def load_manifest():
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_manifest(manifest):
    os.makedirs(os.path.dirname(MANIFEST_FILE), exist_ok=True)
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=4)

def download_batch(map_key, source, date_str, day_range=1):
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{map_key}/{source}/{BBOX_INDIA}/{day_range}/{date_str}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Agni-Netra-Acquisition/1.1'})
        response = urllib.request.urlopen(req, timeout=45)
        if response.getcode() == 200:
            return response.read().decode('utf-8'), 200
        return None, response.getcode()
    except urllib.error.HTTPError as e:
        return None, e.code
    except Exception as e:
        logging.error(f"Error downloading {source} for {date_str}: {str(e)}")
        return None, 500

def audit_failures():
    from dotenv import load_dotenv
    load_dotenv()
    map_key = os.getenv('MAP_KEY') or os.getenv('FIRMS_MAP_KEY')
    if not map_key:
        logging.error("No MAP_KEY found.")
        return
        
    manifest = load_manifest()
    
    # Identify failed records
    failed_keys = [k for k, v in manifest.items() if v.get('status') == 'FAILED']
    
    audit_results = []
    
    for key in failed_keys:
        data = manifest[key]
        product = data.get('sensor_product')
        date_str = data.get('date')
        err_cat = data.get('error_category')
        
        logging.info(f"Retrying failed request: {key} (Previous error: {err_cat})")
        
        csv_content, status = download_batch(map_key, product, date_str)
        time.sleep(1.2) # Rate limit backoff
        
        raw_filename = f"data/ground_truth/firms_real_expanded/{key}.csv"
        
        if status == 200 and csv_content is not None:
            lines = csv_content.strip().split('\n')
            if len(lines) > 0 and 'latitude' in lines[0]:
                with open(raw_filename, 'w', encoding='utf-8') as f:
                    f.write(csv_content)
                rc = len(lines) - 1
                if rc > 0:
                    data["status"] = "SUCCESS"
                else:
                    data["status"] = "EMPTY_VALID_RESPONSE"
                data["record_count"] = rc
                data["error_category"] = None
                audit_results.append({
                    "batch_id": key,
                    "product": product,
                    "date": date_str,
                    "previous_error": err_cat,
                    "new_status": data["status"]
                })
            else:
                data["status"] = "FAILED_RETAINED"
                data["error_category"] = "INVALID_SCHEMA"
                audit_results.append({
                    "batch_id": key,
                    "product": product,
                    "date": date_str,
                    "previous_error": err_cat,
                    "new_status": "FAILED_RETAINED"
                })
        else:
            data["status"] = "FAILED_RETAINED"
            data["error_category"] = f"HTTP_{status}"
            audit_results.append({
                "batch_id": key,
                "product": product,
                "date": date_str,
                "previous_error": err_cat,
                "new_status": "FAILED_RETAINED",
                "new_error": f"HTTP_{status}"
            })
            
        manifest[key] = data
        
    save_manifest(manifest)
    
    # Generate Report
    report = "# Phase 16GT-R2: Acquisition Failure Audit\n\n"
    report += f"Total failed records audited: {len(failed_keys)}\n\n"
    report += "## Results\n\n"
    
    if audit_results:
        df = pd.DataFrame(audit_results)
        report += df.to_markdown(index=False)
    else:
        report += "No failed records found to audit.\n"
        
    os.makedirs('reports', exist_ok=True)
    with open('reports/phase16gtr2_acquisition_failure_audit.md', 'w') as f:
        f.write(report)
        
    logging.info("Audit complete. Manifest and report updated.")

if __name__ == "__main__":
    audit_failures()
