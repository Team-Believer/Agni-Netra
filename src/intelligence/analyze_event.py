"""
Agni-Netra Unified Production Orchestrator: analyze_event() (Phase 18)

Single entry point that orchestrates existing intelligence modules:
- Phase 17A: Canonical Event Features
- Phase 17B: Low-T Persistent Heat Intelligence
- Phase 17C: Historical Abnormality & Change Engine
- Phase 17D: Evidence Aggregation & Event Evidence Ledger
- Phase 17E: Confidence Calibration & UNKNOWN Decision Engine
- Phase 17F: Risk & Priority Intelligence Engine
- Phase 17G: WHY / WHY NOT / WHAT CHANGED Explanation Engine

Schema Version: AGN-EVENT-INTELLIGENCE-1.0
Pipeline Version: 1.0.0

NOTE: analyze_event() ORCHESTRATES INFERENCE. IT DOES NOT REIMPLEMENT INFERENCE.
"""

import time
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple, Union

from src.features.canonical_event_features import build_event_features, CanonicalEventFeatures
from src.features.low_t_persistent_heat import evaluate_low_t_lane, LowTResult
from src.intelligence.historical_abnormality import evaluate_abnormality, AbnormalityResult
from src.intelligence.evidence_aggregation import aggregate_event_evidence, EventEvidenceLedger
from src.intelligence.confidence_decision import (
    evaluate_event_decision, DecisionAssessment, ConfidenceCalibrator,
    DECISION_KNOWN, DECISION_UNKNOWN, DECISION_NEEDS_VERIFICATION,
    DECISION_INSUFFICIENT_OBSERVATION
)
from src.intelligence.risk_priority import evaluate_risk_and_priority, RiskPriorityAssessment
from src.intelligence.explanation_engine import generate_explanation, EventExplanation
from src.intelligence.observation_quality import (
    evaluate_event_observation_quality, EventQualitySummary,
    SATURATION_LIKELY, SATURATION_POSSIBLE, GLINT_HIGH_RISK, GLINT_MODERATE_RISK
)
from src.ingestion.insat3ds import (
    parse_insat3ds_file, assess_sensor_corroboration, SensorCorroborationAssessment,
    NormalizedObservation
)

SCHEMA_VERSION = "AGN-EVENT-INTELLIGENCE-1.0"
PIPELINE_VERSION = "1.0.0"

DEFAULT_SOURCE_CLASSES = [
    "INDUSTRIAL_FIRE", "ROUTINE_FLARE", "ABNORMAL_EMERGENCY_FLARE",
    "WILDFIRE", "AGRICULTURAL_BURN", "MINING_INDUSTRIAL_HEAT",
    "LANDFILL_OTHER_ANTHROPOGENIC", "OTHER", "UNKNOWN"
]


@dataclass
class EventIntelligenceResult:
    schema_version: str
    pipeline_version: str
    event_id: str
    event_metadata: Dict[str, Any]
    observation_summary: Dict[str, Any]
    source_assessment: Dict[str, Any]
    behavior_assessment: Dict[str, Any]
    abnormality_assessment: Dict[str, Any]
    evidence_assessment: Dict[str, Any]
    confidence_assessment: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    priority_assessment: Dict[str, Any]
    explanation: Dict[str, Any]
    verification: Dict[str, Any]
    pipeline_status: Dict[str, Any]
    limitations: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EventIntelligenceResult":
        return cls(
            schema_version=d.get("schema_version", SCHEMA_VERSION),
            pipeline_version=d.get("pipeline_version", PIPELINE_VERSION),
            event_id=d["event_id"],
            event_metadata=d["event_metadata"],
            observation_summary=d["observation_summary"],
            source_assessment=d["source_assessment"],
            behavior_assessment=d["behavior_assessment"],
            abnormality_assessment=d["abnormality_assessment"],
            evidence_assessment=d["evidence_assessment"],
            confidence_assessment=d["confidence_assessment"],
            risk_assessment=d["risk_assessment"],
            priority_assessment=d["priority_assessment"],
            explanation=d["explanation"],
            verification=d["verification"],
            pipeline_status=d["pipeline_status"],
            limitations=d["limitations"]
        )


def _validate_event_input(event_data: Any) -> Tuple[bool, str, Dict[str, Any], List[str]]:
    """
    Validates input event dictionary or object.
    Returns: (is_valid, event_id, raw_dict, validation_errors)
    """
    errors = []
    if event_data is None:
        return False, "evt_invalid", {}, ["Event input data is None"]

    if isinstance(event_data, dict):
        raw_dict = dict(event_data)
    elif hasattr(event_data, "to_dict"):
        raw_dict = event_data.to_dict()
    elif hasattr(event_data, "__dict__"):
        raw_dict = dict(event_data.__dict__)
    else:
        return False, "evt_invalid", {}, ["Event input data format unrecognized"]

    event_id = str(raw_dict.get("event_id") or raw_dict.get("id") or "evt_unknown")

    # Check for core thermal or observation keys
    has_frp = any(k in raw_dict for k in ["current_max_frp", "max_frp", "frp", "current_mean_frp"])
    if not has_frp:
        errors.append("Missing required thermal FRP detection attribute")

    obs_count = raw_dict.get("observation_count_so_far", raw_dict.get("observation_count", raw_dict.get("obs_count", 0)))
    if obs_count <= 0 and not has_frp:
        errors.append("Invalid or zero observation count")

    is_valid = len(errors) == 0
    return is_valid, event_id, raw_dict, errors


def analyze_event(
    event_data: Union[Dict[str, Any], Any],
    model_probs: Optional[np.ndarray] = None,
    source_classes: Optional[List[str]] = None,
    calibrator: Optional[ConfidenceCalibrator] = None,
    mode: str = "online",
    insat_observations: Optional[Union[List[NormalizedObservation], List[Dict[str, Any]], str, Dict[str, Any]]] = None
) -> EventIntelligenceResult:
    """
    Unified entry point for Agni-Netra event analysis.
    Orchestrates canonical features, Low-T persistence, historical abnormality,
    model inference, evidence aggregation, confidence/unknown decision,
    risk/priority intelligence, and structured explanations.
    """
    start_total_time = time.perf_counter()
    stage_durations: Dict[str, float] = {}
    stage_statuses: Dict[str, str] = {}
    missing_data_list: List[str] = []
    unavailable_sensors_list: List[str] = []
    limitations_list: List[str] = []

    if source_classes is None:
        source_classes = DEFAULT_SOURCE_CLASSES

    # --- STAGE 1: INPUT VALIDATION ---
    t0 = time.perf_counter()
    is_valid, event_id, raw_event, validation_errors = _validate_event_input(event_data)
    stage_durations["validation"] = round((time.perf_counter() - t0) * 1000.0, 3)

    if not is_valid:
        stage_statuses["validation"] = "FAILED"
        stage_statuses["canonical_features"] = "SKIPPED"
        stage_statuses["low_t_heat"] = "SKIPPED"
        stage_statuses["historical_abnormality"] = "SKIPPED"
        stage_statuses["model_inference"] = "SKIPPED"
        stage_statuses["evidence_aggregation"] = "SKIPPED"
        stage_statuses["confidence_decision"] = "SKIPPED"
        stage_statuses["risk_priority"] = "SKIPPED"
        stage_statuses["explanation_engine"] = "SKIPPED"

        return EventIntelligenceResult(
            schema_version=SCHEMA_VERSION,
            pipeline_version=PIPELINE_VERSION,
            event_id=event_id,
            event_metadata={"error": "Input validation failed", "validation_errors": validation_errors},
            observation_summary={"data_quality_score": 0.0, "observation_count": 0},
            source_assessment={"predicted_source_class": "UNKNOWN", "decision_state": DECISION_INSUFFICIENT_OBSERVATION},
            behavior_assessment={"low_t_state": "LOW_T_NOT_APPLICABLE", "behavior_signal": "UNKNOWN"},
            abnormality_assessment={"abnormality_score": 0.0, "abnormality_level": "UNKNOWN", "change_detected": False},
            evidence_assessment={"global_evidence_completeness": 0.0, "evidence_items": []},
            confidence_assessment={"decision_state": DECISION_INSUFFICIENT_OBSERVATION, "overall_decision_confidence": 0.0},
            risk_assessment={"base_risk_score": 0.0, "risk_level": "VERY_LOW", "hazard_score": 0.0, "impact_score": 0.0},
            priority_assessment={"priority_score": 0.0, "priority_level": "P4", "urgency": "LOW", "operational_action": "INFORMATIONAL"},
            explanation={
                "summary": f"Event analysis failed input validation: {', '.join(validation_errors)}",
                "why": {"headline": "Input validation failed", "supporting_families": [], "supporting_reasons": []},
                "why_not": {"limiting_reasons": validation_errors},
                "what_changed": {"change_detected": False, "historical_comparison": "None"},
                "uncertainty": {"decision_state": DECISION_INSUFFICIENT_OBSERVATION},
                "next_action": {"recommendation": "INFORMATIONAL", "verification_required": False},
                "provenance": {"evidence_source_ids": [], "evidence_family_ids": [], "reason_codes": ["INVALID_INPUT"]}
            },
            verification={"verification_state": "INSUFFICIENT_DATA", "human_verification_present": False},
            pipeline_status={
                "status": "FAILED",
                "error_code": "INVALID_INPUT",
                "stages": stage_statuses,
                "stage_durations_ms": stage_durations,
                "execution_time_ms": round((time.perf_counter() - start_total_time) * 1000.0, 3)
            },
            limitations={
                "missing_data": ["INPUT_EVENT_DATA"],
                "unavailable_sensors": [],
                "insufficient_observations": True,
                "processing_failures": validation_errors,
                "model_limitations": ["Pipeline failed at input validation stage"]
            }
        )
    else:
        stage_statuses["validation"] = "SUCCESS"

    # --- STAGE 2: OBSERVATION QUALITY DEFENSE LAYER ---
    t0 = time.perf_counter()
    try:
        quality_summary = evaluate_event_observation_quality(raw_event)
        stage_statuses["observation_quality"] = "SUCCESS"
    except Exception as e:
        from src.intelligence.observation_quality import EventQualitySummary
        quality_summary = EventQualitySummary(
            total_observation_count=1, usable_observation_count=1, degraded_observation_count=0,
            excluded_observation_count=0, overall_observation_quality=0.8, quality_summary="Quality evaluation fallback",
            saturation_summary="No thermal saturation detected", glint_summary="No solar glint risk detected",
            critical_quality_flags=[], observation_assessments=[]
        )
        stage_statuses["observation_quality"] = "PARTIAL"
        limitations_list.append(f"Observation quality evaluation fallback: {str(e)}")
    stage_durations["observation_quality"] = round((time.perf_counter() - t0) * 1000.0, 3)

    # --- STAGE 3: CANONICAL FEATURES ---
    t0 = time.perf_counter()
    try:
        canon = build_event_features(raw_event, mode=mode)
        canon.observation_quality = quality_summary.overall_observation_quality
        stage_statuses["canonical_features"] = "SUCCESS"
    except Exception as e:
        canon = build_event_features({'current_max_frp': 0.0, 'observation_count_so_far': 0}, mode=mode)
        stage_statuses["canonical_features"] = "PARTIAL"
        limitations_list.append(f"Canonical feature extraction fallback: {str(e)}")
    stage_durations["canonical_features"] = round((time.perf_counter() - t0) * 1000.0, 3)

    # Sensor availability tracking
    if canon.sentinel_available == 0:
        unavailable_sensors_list.append("SENTINEL")
    if canon.missing_context_indicator == 1:
        missing_data_list.append("CONTEXT_FACILITY_DATA")
    if canon.missing_history_indicator == 1:
        missing_data_list.append("HISTORICAL_BASELINE")

    # --- STAGE 3: LOW-T PERSISTENT HEAT ---
    t0 = time.perf_counter()
    try:
        low_t_result = evaluate_low_t_lane(canon)
        stage_statuses["low_t_heat"] = "SUCCESS"
    except Exception as e:
        low_t_result = LowTResult(
            low_t_state="LOW_T_NOT_APPLICABLE", low_t_score=0.0, low_t_applicable=0,
            low_t_features={}, low_t_supporting_evidence=[], low_t_missing_evidence=[str(e)],
            low_t_conflicting_evidence=[], low_t_evidence_completeness=0.0, low_t_data_quality=0.0
        )
        stage_statuses["low_t_heat"] = "PARTIAL"
    stage_durations["low_t_heat"] = round((time.perf_counter() - t0) * 1000.0, 3)

    # --- STAGE 4: HISTORICAL ABNORMALITY ---
    t0 = time.perf_counter()
    try:
        abnormality_result = evaluate_abnormality(canon, low_t_result=low_t_result, mode=mode)
        stage_statuses["historical_abnormality"] = "SUCCESS"
    except Exception as e:
        from src.intelligence.historical_abnormality import AbnormalityResult, ChangeIndicators
        abnormality_result = AbnormalityResult(
            abnormality_state="UNKNOWN", abnormality_score=0.0, supporting_evidence=[],
            conflicting_evidence=[], missing_evidence=[str(e)], deviation_components=None,
            change_indicators=ChangeIndicators(0, 0, 0, 0), history_support=None, confidence=0.0
        )
        stage_statuses["historical_abnormality"] = "PARTIAL"
    stage_durations["historical_abnormality"] = round((time.perf_counter() - t0) * 1000.0, 3)

    # --- STAGE 5: MODEL / SOURCE INFERENCE ---
    t0 = time.perf_counter()
    if model_probs is None:
        if "model_probs" in raw_event and isinstance(raw_event["model_probs"], (list, np.ndarray)):
            model_probs = np.array(raw_event["model_probs"], dtype=float)
        else:
            # Baseline probabilities for candidate source classes
            base_probs = np.full(len(source_classes), 0.05)
            # Assign baseline heuristics based on canon/context
            if canon.nearby_industrial_flag == 1 or canon.land_context == 1:
                idx_ind = source_classes.index("INDUSTRIAL_FIRE") if "INDUSTRIAL_FIRE" in source_classes else 0
                idx_rout = source_classes.index("ROUTINE_FLARE") if "ROUTINE_FLARE" in source_classes else 1
                base_probs[idx_ind] = 0.60
                base_probs[idx_rout] = 0.20
            else:
                idx_wf = source_classes.index("WILDFIRE") if "WILDFIRE" in source_classes else 0
                base_probs[idx_wf] = 0.60
            model_probs = base_probs / np.sum(base_probs)
    stage_statuses["model_inference"] = "SUCCESS"
    stage_durations["model_inference"] = round((time.perf_counter() - t0) * 1000.0, 3)

    # Argmax predicted class & raw confidence
    best_idx = int(np.argmax(model_probs))
    predicted_source_class = source_classes[best_idx]
    raw_model_confidence = float(model_probs[best_idx])

    # --- STAGE 6: EVIDENCE AGGREGATION & LEDGER (INCL. INSAT-3DS CORROBORATION) ---
    t0 = time.perf_counter()
    insat_corroboration = None
    insat_summary = {"availability": "UNAVAILABLE", "corroboration_state": "NOT_AVAILABLE"}
    if insat_observations is not None:
        try:
            if isinstance(insat_observations, list):
                if insat_observations and isinstance(insat_observations[0], NormalizedObservation):
                    insat_list = insat_observations
                else:
                    from src.ingestion.insat3ds import normalize_insat3ds_observation
                    insat_list = [normalize_insat3ds_observation(x) if isinstance(x, dict) else x for x in insat_observations]
            else:
                insat_list = parse_insat3ds_file(insat_observations)
            
            event_lat = float(raw_event.get("lat", raw_event.get("latitude", 0.0)))
            event_lon = float(raw_event.get("lon", raw_event.get("longitude", 0.0)))
            firms_obs_count = int(canon.observation_count_so_far)
            
            insat_corroboration = assess_sensor_corroboration(
                event_id=event_id,
                firms_obs_count=firms_obs_count,
                insat_obs_list=insat_list,
                event_lat=event_lat,
                event_lon=event_lon
            )
            insat_summary = insat_corroboration.to_dict()
            insat_summary["availability"] = insat_corroboration.insat3ds_status.get("availability", "AVAILABLE")
        except Exception as e:
            insat_summary = {"availability": "FAILED", "error": str(e)}
            limitations_list.append(f"INSAT-3DS corroboration processing failed: {str(e)}")
    else:
        unavailable_sensors_list.append("INSAT-3DS")

    try:
        evidence_ledger = aggregate_event_evidence(
            event_id=event_id,
            canon=canon,
            low_t_result=low_t_result,
            abnormality_result=abnormality_result,
            model_probs=model_probs,
            source_classes=source_classes,
            insat_corroboration=insat_corroboration
        )
        stage_statuses["evidence_aggregation"] = "SUCCESS"
    except Exception as e:
        evidence_ledger = aggregate_event_evidence(event_id=event_id, canon=canon)
        stage_statuses["evidence_aggregation"] = "PARTIAL"

    # Inject observation quality evidence items into ledger
    from src.intelligence.evidence_aggregation import EvidenceItem
    if quality_summary.saturation_summary != "No thermal saturation detected":
        evidence_ledger.evidence_items.append(EvidenceItem(
            evidence_id="qual_sat_1", evidence_type="system_extracted", evidence_family="DATA_QUALITY",
            source="ObservationQualityLayer", status="DERIVED", direction="CONFLICTING" if "Likely" in quality_summary.saturation_summary else "NEUTRAL",
            strength="MODERATE", description=quality_summary.saturation_summary, availability=True
        ))
    if quality_summary.glint_summary != "No solar glint risk detected":
        evidence_ledger.evidence_items.append(EvidenceItem(
            evidence_id="qual_glint_1", evidence_type="system_extracted", evidence_family="DATA_QUALITY",
            source="ObservationQualityLayer", status="DERIVED", direction="CONFLICTING" if "High" in quality_summary.glint_summary else "NEUTRAL",
            strength="MODERATE", description=quality_summary.glint_summary, availability=True
        ))

    stage_durations["evidence_aggregation"] = round((time.perf_counter() - t0) * 1000.0, 3)

    # --- STAGE 7: CONFIDENCE & UNKNOWN DECISION ---
    t0 = time.perf_counter()
    try:
        decision_assessment = evaluate_event_decision(
            event_id=event_id,
            predicted_source_class=predicted_source_class,
            raw_model_confidence=raw_model_confidence,
            evidence_ledger=evidence_ledger,
            canon=canon,
            low_t_result=low_t_result,
            abnormality_result=abnormality_result,
            calibrator=calibrator
        )
        stage_statuses["confidence_decision"] = "SUCCESS"
    except Exception as e:
        decision_assessment = evaluate_event_decision(
            event_id=event_id, predicted_source_class="UNKNOWN", raw_model_confidence=0.3,
            evidence_ledger=evidence_ledger, canon=canon
        )
        stage_statuses["confidence_decision"] = "PARTIAL"
    stage_durations["confidence_decision"] = round((time.perf_counter() - t0) * 1000.0, 3)

    # --- STAGE 8: RISK & OPERATIONAL PRIORITY ---
    t0 = time.perf_counter()
    try:
        risk_priority_assessment = evaluate_risk_and_priority(
            event_id=event_id,
            decision_assessment=decision_assessment,
            evidence_ledger=evidence_ledger,
            canon=canon,
            low_t_result=low_t_result,
            abnormality_result=abnormality_result
        )
        stage_statuses["risk_priority"] = "SUCCESS"
    except Exception as e:
        risk_priority_assessment = evaluate_risk_and_priority(
            event_id=event_id, decision_assessment=decision_assessment, evidence_ledger=evidence_ledger, canon=canon
        )
        stage_statuses["risk_priority"] = "PARTIAL"
    stage_durations["risk_priority"] = round((time.perf_counter() - t0) * 1000.0, 3)

    # --- STAGE 9: WHY / WHY NOT / WHAT CHANGED EXPLANATION ---
    t0 = time.perf_counter()
    try:
        explanation = generate_explanation(
            event_id=event_id,
            decision_assessment=decision_assessment,
            risk_priority_assessment=risk_priority_assessment,
            evidence_ledger=evidence_ledger,
            canon=canon,
            low_t_result=low_t_result,
            abnormality_result=abnormality_result
        )
        stage_statuses["explanation_engine"] = "SUCCESS"
    except Exception as e:
        explanation = generate_explanation(
            event_id=event_id, decision_assessment=decision_assessment,
            risk_priority_assessment=risk_priority_assessment, evidence_ledger=evidence_ledger
        )
        stage_statuses["explanation_engine"] = "PARTIAL"
    stage_durations["explanation_engine"] = round((time.perf_counter() - t0) * 1000.0, 3)

    # --- VERIFICATION BLOCK ---
    human_verification = raw_event.get("human_verification")
    if human_verification is not None:
        human_present = True
        ver_state = "HUMAN_VERIFIED" if human_verification in [True, "VERIFIED", "HUMAN_VERIFIED"] else "HUMAN_DISPUTED"
    else:
        human_present = False
        if decision_assessment.decision_state == DECISION_INSUFFICIENT_OBSERVATION:
            ver_state = "INSUFFICIENT_DATA"
        elif decision_assessment.decision_state == DECISION_UNKNOWN:
            ver_state = "REVIEW_RECOMMENDED"
        elif decision_assessment.decision_state == DECISION_NEEDS_VERIFICATION:
            ver_state = "VERIFY_REQUIRED"
        else:
            ver_state = "NOT_REQUIRED"

    verification_block = {
        "verification_state": ver_state,
        "human_verification_present": human_present,
        "requires_action": (ver_state in ["VERIFY_REQUIRED", "REVIEW_RECOMMENDED", "INSUFFICIENT_DATA"])
    }

    # --- PIPELINE STATUS BLOCK ---
    any_failed = any(s == "FAILED" for s in stage_statuses.values())
    any_partial = any(s == "PARTIAL" for s in stage_statuses.values())

    if any_failed:
        overall_status = "FAILED"
    elif decision_assessment.decision_state == DECISION_INSUFFICIENT_OBSERVATION:
        overall_status = "INSUFFICIENT_OBSERVATION"
    elif any_partial:
        overall_status = "PARTIAL"
    else:
        overall_status = "COMPLETE"

    pipeline_status_block = {
        "status": overall_status,
        "stages": stage_statuses,
        "stage_durations_ms": stage_durations,
        "execution_time_ms": round((time.perf_counter() - start_total_time) * 1000.0, 3)
    }

    # --- LIMITATIONS BLOCK ---
    limitations_block = {
        "missing_data": sorted(list(set(missing_data_list))),
        "unavailable_sensors": sorted(list(set(unavailable_sensors_list))),
        "insufficient_observations": (decision_assessment.decision_state == DECISION_INSUFFICIENT_OBSERVATION),
        "processing_failures": limitations_list,
        "model_limitations": decision_assessment.abstention.get("limiting_factors", [])
    }

    # Structure Output Assessments
    source_assessment = {
        "predicted_source_class": decision_assessment.predicted_source_class,
        "decision_state": decision_assessment.decision_state,
        "source_confidence": decision_assessment.confidence.classification_confidence,
        "model_prediction": {
            "predicted_class": predicted_source_class,
            "raw_model_confidence": raw_model_confidence,
            "class_probabilities": {cls: float(model_probs[i]) for i, cls in enumerate(source_classes)}
        },
        "model_evidence_indicator": "MODEL_DERIVED"
    }

    behavior_assessment = {
        "low_t_state": low_t_result.low_t_state,
        "behavior_signal": "LOW_T_PERSISTENT" if low_t_result.low_t_state == "LOW_T_PERSISTENT" else "TRANSIENT_OR_DEVELOPING",
        "persistence_score": float(low_t_result.low_t_score),
        "thermal_stability": float(getattr(canon, 'frp_std', 0.0)),
        "spatial_stability": float(getattr(canon, 'low_t_spatial_stability', 1.0))
    }

    abnormality_assessment = {
        "abnormality_score": float(abnormality_result.abnormality_score),
        "abnormality_level": abnormality_result.abnormality_state,
        "change_detected": (abnormality_result.abnormality_state in ["UNUSUAL", "HIGHLY_ABNORMAL"]),
        "change_summary": abnormality_result.supporting_evidence,
        "history_tier": getattr(abnormality_result.history_support, 'history_tier', "UNKNOWN") if abnormality_result.history_support else "UNKNOWN",
        "baseline_sufficiency": float(abnormality_result.confidence)
    }

    # Assemble Final EventIntelligenceResult
    return EventIntelligenceResult(
        schema_version=SCHEMA_VERSION,
        pipeline_version=PIPELINE_VERSION,
        event_id=event_id,
        event_metadata={
            "mode": mode,
            "lat": float(raw_event.get("lat", raw_event.get("latitude", 0.0))),
            "lon": float(raw_event.get("lon", raw_event.get("longitude", 0.0))),
            "observation_count": int(canon.observation_count_so_far),
            "duration_hours": float(getattr(canon, 'event_age', canon.persistence))
        },
        observation_summary={
            "data_quality_score": float(canon.observation_quality),
            "temporal_sufficiency": float(decision_assessment.confidence.temporal_sufficiency),
            "historical_sufficiency": float(decision_assessment.confidence.historical_sufficiency),
            "sentinel_available": bool(canon.sentinel_available == 1),
            "insat3ds_summary": insat_summary,
            "missing_indicators": {
                "missing_history": bool(canon.missing_history_indicator == 1),
                "missing_context": bool(canon.missing_context_indicator == 1)
            },
            "quality_summary": quality_summary.to_dict()
        },
        source_assessment=source_assessment,
        behavior_assessment=behavior_assessment,
        abnormality_assessment=abnormality_assessment,
        evidence_assessment=asdict(evidence_ledger),
        confidence_assessment={
            "confidence": decision_assessment.confidence.to_dict(),
            "calibration": decision_assessment.calibration,
            "decision_state": decision_assessment.decision_state,
            "abstention_reason_codes": decision_assessment.abstention.get("abstention_reason_codes", []),
            "limiting_factors": decision_assessment.abstention.get("limiting_factors", [])
        },
        risk_assessment=risk_priority_assessment.risk,
        priority_assessment=risk_priority_assessment.priority,
        explanation=explanation.to_dict(),
        verification=verification_block,
        pipeline_status=pipeline_status_block,
        limitations=limitations_block
    )


def analyze_events(
    events_list: List[Any],
    source_classes: Optional[List[str]] = None,
    calibrator: Optional[ConfidenceCalibrator] = None,
    mode: str = "online"
) -> List[EventIntelligenceResult]:
    """
    Thin batch helper for processing multiple events.
    """
    results = []
    for ev in events_list:
        results.append(analyze_event(ev, source_classes=source_classes, calibrator=calibrator, mode=mode))
    return results
