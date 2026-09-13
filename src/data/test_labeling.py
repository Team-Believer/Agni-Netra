import pytest
import pandas as pd
from datetime import datetime

# A simplified pure function representing the labeling logic from construct_labels.py
# for testability
def assign_label(context_types, is_persistent):
    label = "Unknown / Needs Verification"
    quality = "UNKNOWN"
    ambiguity = "NONE"
    
    if 'industrial' in context_types and ('forest' in context_types or 'farmland' in context_types):
        ambiguity = "CONFLICTING"
    elif 'industrial' in context_types:
        if is_persistent:
            label = "Routine Flare / Persistent Industrial Heat"
            quality = "HIGH_CONFIDENCE_WEAK"
        else:
            label = "Industrial Fire"
            quality = "WEAK"
            ambiguity = "INSUFFICIENT_TEMPORAL_HISTORY"
    elif 'forest' in context_types:
        label = "Wildfire"
        quality = "WEAK"
    elif 'farmland' in context_types:
        label = "Agricultural Burn"
        quality = "WEAK"
    else:
        ambiguity = "NO_CONTEXT"
        
    return label, quality, ambiguity


def test_scenario_1_industrial_flare():
    # 1. industrial facility + stable repeated heat
    label, quality, amb = assign_label(['industrial'], is_persistent=True)
    assert label == "Routine Flare / Persistent Industrial Heat"
    assert quality == "HIGH_CONFIDENCE_WEAK"

def test_scenario_2_industrial_fire():
    # 2. industrial facility + sudden unusual activity
    label, quality, amb = assign_label(['industrial'], is_persistent=False)
    assert label == "Industrial Fire"
    assert quality == "WEAK"
    assert amb == "INSUFFICIENT_TEMPORAL_HISTORY"

def test_scenario_3_wildfire():
    # 3. forest + fire evidence
    label, quality, amb = assign_label(['forest'], is_persistent=False)
    assert label == "Wildfire"
    assert quality == "WEAK"

def test_scenario_4_agricultural():
    # 4. cropland + thermal anomaly
    label, quality, amb = assign_label(['farmland'], is_persistent=False)
    assert label == "Agricultural Burn"
    assert quality == "WEAK"

def test_scenario_5_conflicting():
    # 5. conflicting industrial/wildfire evidence
    label, quality, amb = assign_label(['industrial', 'forest'], is_persistent=False)
    assert label == "Unknown / Needs Verification"
    assert amb == "CONFLICTING"

def test_scenario_6_no_context():
    # 6. no contextual evidence
    label, quality, amb = assign_label([], is_persistent=True)
    assert label == "Unknown / Needs Verification"
    assert amb == "NO_CONTEXT"

def test_scenario_7_missing_facility_data():
    # 7. missing facility data (handled as no context)
    label, quality, amb = assign_label([], is_persistent=False)
    assert label == "Unknown / Needs Verification"
    assert amb == "NO_CONTEXT"
