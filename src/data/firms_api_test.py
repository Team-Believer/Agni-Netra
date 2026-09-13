import os
import urllib.request
import urllib.error
import json
from datetime import datetime
from dotenv import load_dotenv

def test_firms_auth():
    load_dotenv()
    map_key = os.getenv('MAP_KEY')
    
    if not map_key:
        return {
            "map_key_configured": False,
            "authentication_status": "FAILED",
            "http_status": None,
            "response_received": False,
            "records_returned": 0,
            "schema_valid": False,
            "tested_at": datetime.utcnow().isoformat(),
            "error_category": "AUTHENTICATION_FAILURE"
        }
        
    # Small geographic area (1x1 degree), 1 day of NRT data to just test auth
    # Bounding Box: min_x, min_y, max_x, max_y (lon, lat, lon, lat)
    # 70,20,71,21
    source = "VIIRS_SNPP_NRT"
    bbox = "70,20,71,21"
    day_range = "1"
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{map_key}/{source}/{bbox}/{day_range}"
    
    result = {
        "map_key_configured": True,
        "tested_at": datetime.utcnow().isoformat(),
        "endpoint": "https://firms.modaps.eosdis.nasa.gov/api/area/csv/[REDACTED]/VIIRS_SNPP_NRT/70,20,71,21/1",
        "error_category": None
    }
    
    try:
        response = urllib.request.urlopen(url)
        http_status = response.getcode()
        content = response.read().decode('utf-8')
        
        result["http_status"] = http_status
        result["response_received"] = True
        
        if http_status == 200:
            lines = content.strip().split('\n')
            if len(lines) > 0 and 'latitude' in lines[0] and 'longitude' in lines[0]:
                result["authentication_status"] = "SUCCESS"
                result["schema_valid"] = True
                result["records_returned"] = len(lines) - 1 # exclude header
            elif "Invalid MAP_KEY" in content or "401" in content or "403" in content:
                result["authentication_status"] = "FAILED"
                result["schema_valid"] = False
                result["records_returned"] = 0
                result["error_category"] = "AUTHENTICATION_FAILURE"
            else:
                result["authentication_status"] = "UNKNOWN"
                result["schema_valid"] = False
                result["records_returned"] = 0
                result["error_category"] = "EMPTY_VALID_RESPONSE"
        else:
            result["authentication_status"] = "FAILED"
            result["schema_valid"] = False
            result["records_returned"] = 0
            result["error_category"] = "OTHER"
            
    except urllib.error.HTTPError as e:
        result["http_status"] = e.code
        result["response_received"] = False
        result["records_returned"] = 0
        result["schema_valid"] = False
        
        if e.code in [401, 403]:
            result["authentication_status"] = "FAILED"
            result["error_category"] = "AUTHENTICATION_FAILURE"
        elif e.code == 429:
            result["authentication_status"] = "UNKNOWN"
            result["error_category"] = "RATE_LIMIT"
        elif e.code == 404:
            result["authentication_status"] = "UNKNOWN"
            result["error_category"] = "ENDPOINT_FAILURE"
        else:
            result["authentication_status"] = "FAILED"
            result["error_category"] = "OTHER"
            
    except urllib.error.URLError as e:
        result["http_status"] = None
        result["response_received"] = False
        result["records_returned"] = 0
        result["schema_valid"] = False
        result["authentication_status"] = "FAILED"
        result["error_category"] = "NETWORK_FAILURE"
        
    except Exception as e:
        result["http_status"] = None
        result["response_received"] = False
        result["records_returned"] = 0
        result["schema_valid"] = False
        result["authentication_status"] = "FAILED"
        result["error_category"] = "INVALID_REQUEST"
        
    os.makedirs('data/processed', exist_ok=True)
    with open('data/processed/firms_api_auth_test.json', 'w') as f:
        json.dump(result, f, indent=4)
        
    return result

if __name__ == "__main__":
    test_firms_auth()
