import pandas as pd
import pytest
import os
from decision_pipeline import run_decision_pipeline

# We'll just load the generated decision table to verify the equations hold
@pytest.fixture
def decision_table():
    path = 'data/processed/decision_intelligence/decision_table.csv'
    if not os.path.exists(path):
        pytest.skip("Decision table not generated yet")
    return pd.read_csv(path)

def test_risk_monotonicity(decision_table):
    """If Hazard and Impact increase, Base Risk must increase or stay flat, never decrease."""
    # We can just check the formula holds
    base_risk = decision_table['base_risk_score']
    expected_risk = decision_table['hazard_score'] * decision_table['impact_score']
    pd.testing.assert_series_equal(base_risk, expected_risk, check_names=False)

def test_priority_separation(decision_table):
    """Priority must NOT just be Risk. It must incorporate Urgency."""
    # Ensure priority is strictly different from risk for at least some events
    diffs = (decision_table['priority_score'] - decision_table['base_risk_score']).abs()
    assert (diffs > 0).any(), "Priority score is perfectly identical to Risk score!"

def test_uncertainty_handling(decision_table):
    """High uncertainty should lower risk confidence, and route to Verification/More Data if Risk is low."""
    # Filter for High Risk, Low Confidence
    mask = (decision_table['base_risk_score'] >= 0.7) & (decision_table['risk_confidence'] < 0.7)
    if mask.any():
        assert all(decision_table.loc[mask, 'priority_class'] == 'P1 - HIGH VERIFICATION PRIORITY')
        assert all(decision_table.loc[mask, 'recommended_action'] == 'VERIFY_SOURCE_AND_CLASS')
        
    # Low Risk, Low Confidence
    mask2 = (decision_table['base_risk_score'] < 0.4) & (decision_table['risk_confidence'] < 0.5)
    if mask2.any():
        assert all(decision_table.loc[mask2, 'priority_class'] == 'P3 - REQUEST MORE DATA')
        assert all(decision_table.loc[mask2, 'recommended_action'] == 'VERIFY_SOURCE_AND_CLASS')

def test_unknown_preservation(decision_table):
    """Ensure WHAT IS UNKNOWN correctly flags missing Sentinel."""
    mask = decision_table['what_is_unknown'].str.contains("Missing Sentinel-2 imagery", na=False)
    # Just asserting the pipeline generated these strings somewhere
    assert mask.any(), "Pipeline failed to preserve missing Sentinel as UNKNOWN explanation"

def test_missing_data_certainty(decision_table):
    """Missing data should never create false certainty."""
    # If missing Sentinel, Data Quality or Completeness should be lower, thus confidence is lower
    missing_sentinel = decision_table[decision_table['what_is_unknown'].str.contains("Missing Sentinel-2", na=False)]
    has_sentinel = decision_table[~decision_table['what_is_unknown'].str.contains("Missing Sentinel-2", na=False)]
    
    if len(missing_sentinel) > 0 and len(has_sentinel) > 0:
        avg_conf_missing = missing_sentinel['risk_confidence'].mean()
        avg_conf_has = has_sentinel['risk_confidence'].mean()
        # It's highly likely average confidence is lower when Sentinel is missing
        assert avg_conf_missing <= avg_conf_has + 0.05, "Missing data is generating higher certainty!"

if __name__ == "__main__":
    pytest.main([__file__])
