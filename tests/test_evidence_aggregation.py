import pytest
import numpy as np
from src.features.canonical_event_features import CanonicalEventFeatures
from src.features.low_t_persistent_heat import LowTResult
from src.intelligence.historical_abnormality import AbnormalityResult, ChangeIndicators, DeviationComponents, HistorySupport
from src.intelligence.evidence_aggregation import aggregate_event_evidence

def create_mock_low_t(state="LOW_T_PERSISTENT"):
    return LowTResult(
        low_t_state=state, low_t_score=0.8, low_t_applicable=1,
        low_t_features={}, low_t_supporting_evidence=[],
        low_t_missing_evidence=[], low_t_conflicting_evidence=[],
        low_t_evidence_completeness=1.0, low_t_data_quality=1.0
    )

def create_mock_abnormality(state="UNUSUAL"):
    return AbnormalityResult(
        abnormality_state=state, abnormality_score=0.5,
        supporting_evidence=[], conflicting_evidence=[], missing_evidence=[],
        deviation_components=DeviationComponents(0.1, 0.1, 0.1, 0.1, 0.1, 0.1),
        change_indicators=ChangeIndicators(1, 0, 0, 0),
        history_support=HistorySupport("HISTORY_TIER_A", 1, 1.0),
        confidence=1.0
    )

def test_supporting_evidence_mapped():
    # 1. Actual supporting evidence becomes SUPPORTING.
    canon = CanonicalEventFeatures(current_mean_frp=50.0, observation_count_so_far=10, sentinel_available=1)
    ledger = aggregate_event_evidence("ev-1", canon)
    supports = [i for i in ledger.evidence_items if i.direction == "SUPPORTING"]
    assert any(i.evidence_family == "THERMAL" for i in supports)
    assert any(i.evidence_family == "SENTINEL" for i in supports)

def test_conflicting_evidence_mapped():
    # 2. Contradictory evidence becomes CONFLICTING.
    canon = CanonicalEventFeatures(current_mean_frp=50.0, nearby_industrial_flag=0, land_context=0, missing_context_indicator=0)
    # Since it's not industrial context, the context evidence defaults to CONFLICTING (forest/veg)
    ledger = aggregate_event_evidence("ev-2", canon)
    conflicts = [i for i in ledger.evidence_items if i.direction == "CONFLICTING"]
    assert any(i.evidence_family == "CONTEXT" for i in conflicts)

def test_missing_evidence_semantics():
    # 3. Unavailable evidence becomes MISSING/UNAVAILABLE rather than negative evidence.
    canon = CanonicalEventFeatures(sentinel_available=0, missing_context_indicator=1)
    ledger = aggregate_event_evidence("ev-3", canon)
    missing = [i for i in ledger.evidence_items if i.direction == "MISSING"]
    assert any(i.evidence_family == "SENTINEL" for i in missing)
    assert any(i.evidence_family == "CONTEXT" for i in missing)
    # Ensure they are not counted as CONFLICTING
    conflicts = [i for i in ledger.evidence_items if i.direction == "CONFLICTING"]
    assert not any(i.evidence_family == "SENTINEL" for i in conflicts)

def test_independence_awareness():
    # 4. Multiple correlated thermal features do not count as independent evidence families.
    canon = CanonicalEventFeatures(current_mean_frp=50.0, frp_std=10.0, frp_change_rate=1.0)
    ledger = aggregate_event_evidence("ev-4", canon)
    # Thermal family should appear just once (or be merged) rather than inflating convergence
    thermal_items = [i for i in ledger.evidence_items if i.evidence_family == "THERMAL"]
    assert len(thermal_items) == 1

def test_low_t_does_not_create_industrial_fire():
    # 5. Low-T does not automatically create Industrial Fire.
    canon = CanonicalEventFeatures()
    low_t = create_mock_low_t("LOW_T_PERSISTENT")
    ledger = aggregate_event_evidence("ev-5", canon, low_t_result=low_t, source_classes=["UNKNOWN", "INDUSTRIAL_FIRE"])
    behaviors = [i for i in ledger.evidence_items if i.evidence_family == "BEHAVIOR" and i.direction == "SUPPORTING"]
    assert len(behaviors) == 1
    assert "Industrial Fire" not in behaviors[0].description
    assert behaviors[0].description == "Persistent moderate-intensity thermal activity detected."

def test_historical_abnormality_integrates():
    # 6. Historical abnormality integrates correctly.
    canon = CanonicalEventFeatures()
    abn = create_mock_abnormality("HIGHLY_ABNORMAL")
    ledger = aggregate_event_evidence("ev-6", canon, abnormality_result=abn)
    anom_items = [i for i in ledger.evidence_items if i.evidence_family == "ANOMALY"]
    assert len(anom_items) > 0
    assert "highly abnormal" in anom_items[0].description

def test_model_explicitly_labeled():
    # 7. Model output is explicitly marked MODEL-DERIVED.
    canon = CanonicalEventFeatures()
    probs = np.array([0.9, 0.1])
    classes = ["INDUSTRIAL_FIRE", "UNKNOWN"]
    ledger = aggregate_event_evidence("ev-7", canon, model_probs=probs, source_classes=classes)
    model_items = [i for i in ledger.evidence_items if i.evidence_family == "MODEL"]
    assert len(model_items) == 1
    assert model_items[0].status == "DERIVED"
    assert "MODEL-DERIVED" in model_items[0].description

def test_completeness_decreases_with_missing():
    # 10. Evidence completeness decreases when expected evidence is unavailable.
    canon_full = CanonicalEventFeatures(sentinel_available=1, missing_context_indicator=0)
    ledger_full = aggregate_event_evidence("ev-8a", canon_full)
    
    canon_miss = CanonicalEventFeatures(sentinel_available=0, missing_context_indicator=1)
    ledger_miss = aggregate_event_evidence("ev-8b", canon_miss)
    
    assert ledger_miss.global_evidence_completeness < ledger_full.global_evidence_completeness

def test_identical_input_deterministic():
    # 12. Identical input is deterministic.
    canon = CanonicalEventFeatures(current_mean_frp=50.0, observation_count_so_far=10, sentinel_available=1)
    l1 = aggregate_event_evidence("ev-id", canon)
    l2 = aggregate_event_evidence("ev-id", canon)
    assert len(l1.evidence_items) == len(l2.evidence_items)
    assert l1.global_evidence_completeness == l2.global_evidence_completeness
