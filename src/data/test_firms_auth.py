import pytest
import os
import json
import logging

def test_map_key_is_not_printed_or_logged():
    # Verify our scripts don't print the MAP_KEY
    with open('src/data/firms_api_test.py', 'r') as f:
        content = f.read()
    assert "print(map_key)" not in content
    assert "logging.info(map_key)" not in content

def test_map_key_not_in_report():
    report_path = 'data/processed/firms_api_auth_test.json'
    if os.path.exists(report_path):
        with open(report_path, 'r') as f:
            content = f.read()
        
        # Load env to see what the actual key is
        from dotenv import load_dotenv
        load_dotenv()
        actual_key = os.getenv('MAP_KEY')
        
        if actual_key and len(actual_key) > 5:
            assert actual_key not in content, "MAP_KEY leaked into JSON report!"
            
def test_authentication_status_safe_representation():
    report_path = 'data/processed/firms_api_auth_test.json'
    if os.path.exists(report_path):
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        assert report.get("authentication_status") in ["SUCCESS", "FAILED", "UNKNOWN"]
        assert "map_key" not in report
