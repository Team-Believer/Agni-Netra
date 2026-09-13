import os
import urllib.request
import pandas as pd
from datetime import datetime
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_firms_data(output_dir: str = 'data/raw/firms'):
    os.makedirs(output_dir, exist_ok=True)
    
    # Check for credentials
    map_key = os.environ.get('MAP_KEY')
    if not map_key:
        logging.warning("No MAP_KEY environment variable found. Real credentials are required for custom API queries.")
        logging.info("Falling back to public unauthenticated 7-day rolling data for South Asia (VIIRS S-NPP and NOAA-20).")
        
        # Public 7-day URLs for South Asia (covers India)
        # Using S-NPP and NOAA-20 VIIRS 375m
        urls = {
            "suomi_npp_viirs": "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_South_Asia_7d.csv",
            "noaa_20_viirs": "https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_South_Asia_7d.csv"
        }
    else:
        # In the future, use the MAP_KEY to fetch specific historical data
        logging.info("MAP_KEY found. (API implementation pending)")
        return
        
    downloaded_files = []
    metadata = {
        "download_time": datetime.utcnow().isoformat(),
        "requested_geography": "South Asia (including India)",
        "sources": {}
    }

    for sensor, url in urls.items():
        try:
            logging.info(f"Downloading {sensor} data from {url}")
            filename = os.path.join(output_dir, f"{sensor}_south_asia_7d.csv")
            urllib.request.urlretrieve(url, filename)
            
            # Check if valid CSV
            df = pd.read_csv(filename)
            logging.info(f"Successfully downloaded {len(df)} rows for {sensor}")
            downloaded_files.append(filename)
            metadata["sources"][sensor] = {
                "url": url,
                "file": filename,
                "rows": len(df),
                "columns": list(df.columns)
            }
        except Exception as e:
            logging.error(f"Failed to download or read {sensor} data: {e}")

    # Save metadata
    with open(os.path.join(output_dir, "metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=4)
        
    logging.info("Download complete.")

if __name__ == "__main__":
    download_firms_data()
