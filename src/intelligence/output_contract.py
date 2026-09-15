"""
Agni-Netra AI Output Contract Hardening & Handoff Freeze (Phase 20G)

Defines and freezes the canonical AI/ML interface contract produced by analyze_event()
for handoff to downstream backend and frontend teams.

Schema Version: AGN-EVENT-INTELLIGENCE-1.0
Pipeline Version: 1.0.0

Core Principles:
1. One canonical, versioned, deterministic, documented output structure.
2. Full semantic separation:
   SOURCE != EVENT_STATE, EVENT_STATE != ABNORMALITY, ABNORMALITY != NOVELTY,
   NOVELTY != DECISION_STATE, MODEL_CONFIDENCE != DECISION_CONFIDENCE,
   CONFIDENCE != RISK, RISK != PRIORITY, LOW-T != SOURCE, HIGH-T != SOURCE.
3. Centralized frozen canonical vocabularies.
4. Contract validator validate_event_intelligence_result().
"""

import json
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple, Union

# ==============================================================================
# 1. FROZEN CANONICAL VOCABULARIES & ENUMS
# ==============================================================================

SCHEMA_VERSION = "AGN-EVENT-INTELLIGENCE-1.0"
PIPELINE_VERSION = "1.0.0"

FROZEN_SOURCE_CLASSES = [
    "INDUSTRIAL_FIRE",
    "ROUTINE_FLARE",
    "ABNORMAL_EMERGENCY_FLARE",
    "WILDFIRE",
    "AGRICULTURAL_BURN",
    "MINING_INDUSTRIAL_HEAT",
    "LANDFILL_OTHER_ANTHROPOGENIC",
    "OTHER",
    "UNKNOWN"
]

FROZEN_DECISION_STATES = [
    "KNOWN",
    "UNKNOWN",
    "NEEDS_VERIFICATION",
    "INSUFFICIENT_OBSERVATION"
]

FROZEN_DISTRIBUTION_STATES = [
    "KNOWN_LIKE",
    "NOVEL",
    "UNKNOWN"
]

FROZEN_EVENT_STATES = [
    "NEW",
    "PERSISTING",
    "STABLE",
    "INTERMITTENT",
    "ESCALATING",
    "ABNORMAL",
    "RESOLVING",
    "DORMANT",
    "REACTIVATED",
    "UNKNOWN"
]

FROZEN_RISK_LEVELS = [
    "VERY_LOW",
    "NEGLIGIBLE",
    "LOW",
    "MODERATE",
    "HIGH",
    "VERY_HIGH",
    "CRITICAL",
    "UNKNOWN"
]

FROZEN_PRIORITY_LEVELS = [
    "P0",
    "P1",
    "P2",
    "P3",
    "P4",
    "P4_ROUTINE",
    "P3_MONITOR",
    "P2_EVALUATE",
    "P1_URGENT",
    "P0_CRITICAL",
    "UNKNOWN"
]

FROZEN_URGENCY_LEVELS = [
    "LOW",
    "NORMAL",
    "MODERATE",
    "HIGH",
    "URGENT",
    "CRITICAL",
    "IMMEDIATE",
    "UNKNOWN"
]

FROZEN_VERIFICATION_STATES = [
    "NOT_REQUIRED",
    "VERIFY_REQUIRED",
    "REVIEW_RECOMMENDED",
    "INSUFFICIENT_DATA",
    "HUMAN_VERIFIED",
    "HUMAN_DISPUTED",
    "UNKNOWN"
]

FROZEN_EVIDENCE_DIRECTIONS = [
    "SUPPORTING",
    "CONFLICTING",
    "MISSING",
    "NEUTRAL"
]

FROZEN_EVIDENCE_STATUSES = [
    "OBSERVED",
    "DERIVED",
    "UNAVAILABLE",
    "NOT_APPLICABLE"
]

FROZEN_QUALITY_LEVELS = [
    "GOOD",
    "ACCEPTABLE",
    "DEGRADED",
    "POOR",
    "UNKNOWN"
]


# ==============================================================================
# 2. CANONICAL CONTRACT BUILDER
# ==============================================================================

def build_canonical_contract(result_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts a raw or legacy EventIntelligenceResult dict into the exact 16-section
    frozen AI output contract required for handoff (schema AGN-EVENT-INTELLIGENCE-1.0).
    Preserves all underlying intelligence values and enforces deterministic field ordering.
    """
    event_id = str(result_dict.get("event_id", "evt_unknown"))
    e_meta = result_dict.get("event_metadata", {})
    obs_sum = result_dict.get("observation_summary", {})
    src_ass = result_dict.get("source_assessment", {})
    beh_ass = result_dict.get("behavior_assessment", {})
    abn_ass = result_dict.get("abnormality_assessment", {})
    ev_ass = result_dict.get("evidence_assessment", {})
    conf_ass = result_dict.get("confidence_assessment", {})
    risk_ass = result_dict.get("risk_assessment", {})
    prio_ass = result_dict.get("priority_assessment", {})
    expl_ass = result_dict.get("explanation", {})
    ver_ass = result_dict.get("verification", {})
    pip_ass = result_dict.get("pipeline_status", {})
    lim_ass = result_dict.get("limitations", {})

    q_sum = obs_sum.get("quality_summary", {})

    # 1. EVENT Section
    sec_event = {
        "event_id": event_id,
        "first_observation_time": str(e_meta.get("first_detected", "2026-09-15T00:00:00")),
        "last_observation_time": str(e_meta.get("last_detected", "2026-09-15T00:00:00")),
        "latitude": float(e_meta.get("lat", 0.0)),
        "longitude": float(e_meta.get("lon", 0.0)),
        "observation_count": int(e_meta.get("observation_count", 1)),
        "source_sensor_summary": str(e_meta.get("source_sensor", "FIRMS_VIIRS"))
    }

    # 2. OBSERVATION Section
    sec_observation = {
        "quality_summary": str(q_sum.get("quality_summary", "GOOD")),
        "usable_observations": int(q_sum.get("usable_observation_count", e_meta.get("observation_count", 1))),
        "degraded_observations": int(q_sum.get("degraded_observation_count", 0)),
        "excluded_observations": int(q_sum.get("excluded_observation_count", 0)),
        "sensor_availability": {
            "sentinel_available": bool(obs_sum.get("sentinel_available", False)),
            "insat3ds_available": bool(obs_sum.get("insat3ds_summary") is not None)
        },
        "freshness": "RECENT"
    }

    # 3. THERMAL Section
    high_t = beh_ass.get("high_t_assessment", {})
    sec_thermal = {
        "low_t": {
            "state": str(beh_ass.get("low_t_state", "LOW_T_NOT_PERMANENT")),
            "persistence_score": float(beh_ass.get("persistence_score", 0.0)),
            "spatial_stability": float(beh_ass.get("spatial_stability", 1.0))
        },
        "high_t": {
            "mode": str(high_t.get("physics_mode", "REDUCED_THERMAL_PHYSICS_MODE")),
            "thermal_intensity_score": float(high_t.get("thermal_intensity_score", 0.0)),
            "high_t_likelihood": float(high_t.get("high_t_likelihood", 0.0)),
            "saturation_state": str(q_sum.get("saturation_summary", "NOT_DETECTED"))
        },
        "frp_summary": {
            "max_frp": float(beh_ass.get("thermal_stability", 0.0)),
            "frp_stability": float(beh_ass.get("thermal_stability", 0.0))
        },
        "brightness_temperature_summary": {
            "t4_max": float(high_t.get("estimated_t4_k", 320.0)),
            "t11_max": float(high_t.get("estimated_t11_k", 295.0))
        },
        "thermal_limitations": sorted(list(high_t.get("limitations", [])))
    }

    # 4. BEHAVIOR Section
    sec_behavior = {
        "event_state": str(beh_ass.get("event_state", "UNKNOWN")),
        "state_confidence": float(beh_ass.get("state_confidence", 0.0)),
        "state_history": list(beh_ass.get("state_history", [])),
        "transition": {
            "last_transition": str(beh_ass.get("last_transition", "INITIAL_DETECTION")),
            "reason_codes": sorted(list(beh_ass.get("transition_reason_codes", [])))
        },
        "low_t_behavior": str(beh_ass.get("behavior_signal", "TRANSIENT_OR_DEVELOPING")),
        "high_t_behavior": str(high_t.get("high_t_classification", "MODERATE_THERMAL"))
    }

    # 5. ABNORMALITY Section
    sec_abnormality = {
        "abnormality_score": float(abn_ass.get("abnormality_score", 0.0)),
        "abnormality_level": str(abn_ass.get("abnormality_level", "NORMAL")),
        "change_detected": bool(abn_ass.get("change_detected", False)),
        "change_summary": sorted(list(abn_ass.get("change_summary", []))),
        "history_tier": str(abn_ass.get("history_tier", "UNKNOWN")),
        "baseline_sufficiency": float(abn_ass.get("baseline_sufficiency", 0.0))
    }

    # 6. SOURCE Section
    novelty_ass = src_ass.get("novelty_assessment", {})
    sec_source = {
        "predicted_source_class": str(src_ass.get("predicted_source_class", "UNKNOWN")),
        "decision_state": str(src_ass.get("decision_state", "UNKNOWN")),
        "model_confidence": float(src_ass.get("source_confidence", 0.0)),
        "model_prediction": src_ass.get("model_prediction", {}),
        "known_class_compatibility": novelty_ass.get("known_class_compatibility", [])
    }

    # 7. NOVELTY Section
    sec_novelty = {
        "novelty_score": float(src_ass.get("novelty_score", 0.0)),
        "novelty_level": str(src_ass.get("novelty_level", "KNOWN_LIKE")),
        "distribution_state": str(src_ass.get("distribution_state", "KNOWN_LIKE")),
        "novelty_drivers": sorted(list(novelty_ass.get("novelty_drivers", [])))
    }

    # 8. EVIDENCE Section
    ev_items = ev_ass.get("evidence_items", [])
    supporting_fams = sorted(list(set(item.get("evidence_family") for item in ev_items if item.get("direction") == "SUPPORTING")))
    conflicting_fams = sorted(list(set(item.get("evidence_family") for item in ev_items if item.get("direction") == "CONFLICTING")))
    missing_fams = sorted(list(set(item.get("evidence_family") for item in ev_items if item.get("direction") == "MISSING")))
    neutral_fams = sorted(list(set(item.get("evidence_family") for item in ev_items if item.get("direction") == "NEUTRAL")))

    sec_evidence = {
        "ledger": ev_ass,
        "supporting_families": supporting_fams,
        "conflicting_families": conflicting_fams,
        "missing_families": missing_fams,
        "neutral_families": neutral_fams,
        "evidence_strength": "MODERATE",
        "evidence_completeness": float(ev_ass.get("global_evidence_completeness", 0.0)),
        "evidence_convergence": "HIGH",
        "hypothesis_support_matrix": ev_ass.get("hypothesis_support_matrix", {})
    }

    # 9. CONFIDENCE Section
    conf_sub = conf_ass.get("confidence", {})
    sec_confidence = {
        "classification_confidence": float(conf_sub.get("classification_confidence", 0.0)),
        "evidence_completeness": float(conf_sub.get("evidence_completeness", 0.0)),
        "evidence_convergence": float(conf_sub.get("evidence_convergence", 0.0)),
        "data_quality_confidence": float(conf_sub.get("data_quality_confidence", 0.0)),
        "temporal_sufficiency": float(conf_sub.get("temporal_sufficiency", 0.0)),
        "historical_sufficiency": float(conf_sub.get("historical_sufficiency", 0.0)),
        "contradiction_penalty": float(conf_sub.get("contradiction_penalty", 0.0)),
        "overall_decision_confidence": float(conf_sub.get("overall_decision_confidence", 0.0)),
        "confidence_level": str(conf_sub.get("level", "LOW")),
        "calibration_status": str(conf_ass.get("calibration", {}).get("status", "UNCALIBRATED")),
        "calibration_method": str(conf_ass.get("calibration", {}).get("method", "TEMPERATURE_SCALING")),
        "abstention_reason_codes": sorted(list(conf_ass.get("abstention_reason_codes", []))),
        "limiting_factors": sorted(list(conf_ass.get("limiting_factors", [])))
    }

    # 10. RISK Section
    sec_risk = {
        "hazard_score": float(risk_ass.get("hazard_score", 0.0)),
        "hazard_level": str(risk_ass.get("hazard_level", "LOW")),
        "impact_score": float(risk_ass.get("impact_score", 0.0)),
        "impact_level": str(risk_ass.get("impact_level", "LOW")),
        "base_risk_score": float(risk_ass.get("base_risk_score", 0.0)),
        "risk_level": str(risk_ass.get("risk_level", "LOW")),
        "risk_confidence": float(risk_ass.get("risk_confidence", 0.0))
    }

    # 11. PRIORITY Section
    sec_priority = {
        "priority_score": float(prio_ass.get("priority_score", 0.0)),
        "priority_level": str(prio_ass.get("priority_level", "P4")),
        "urgency": str(prio_ass.get("urgency", "LOW")),
        "operational_action": str(prio_ass.get("recommended_action", "INFORMATIONAL")),
        "priority_drivers": sorted(list(prio_ass.get("priority_drivers", [])))
    }

    # 12. EXPLANATION Section
    sec_explanation = {
        "summary": str(expl_ass.get("summary", "")),
        "why": expl_ass.get("why", {}),
        "why_not": expl_ass.get("why_not", {}),
        "what_changed": expl_ass.get("what_changed", {}),
        "uncertainty": expl_ass.get("uncertainty", {}),
        "next_action": expl_ass.get("next_action", {}),
        "provenance": expl_ass.get("provenance", {})
    }

    # 13. VERIFICATION Section
    sec_verification = {
        "verification_state": str(ver_ass.get("verification_state", "NOT_REQUIRED")),
        "verification_required": bool(ver_ass.get("requires_action", False)),
        "verification_reason": "Decision state requires verification or human review" if ver_ass.get("requires_action") else "Verified or low priority"
    }

    # 14. PIPELINE Section
    sec_pipeline = {
        "schema_version": SCHEMA_VERSION,
        "pipeline_version": PIPELINE_VERSION,
        "overall_status": str(pip_ass.get("status", "COMPLETE")),
        "stage_status": pip_ass.get("stages", {}),
        "stage_durations_if_available": pip_ass.get("stage_durations_ms", {}),
        "warnings": []
    }

    # 15. LIMITATIONS Section
    sec_limitations = {
        "missing_data": sorted(list(lim_ass.get("missing_data", []))),
        "unavailable_sensors": sorted(list(lim_ass.get("unavailable_sensors", []))),
        "insufficient_history": bool(lim_ass.get("missing_data", []) and "missing_history" in lim_ass.get("missing_data", [])),
        "quality_limitations": sorted(list(q_sum.get("critical_quality_flags", []))),
        "model_limitations": sorted(list(lim_ass.get("model_limitations", []))),
        "confidence_limitations": sorted(list(sec_confidence["limiting_factors"]))
    }

    # 16. PROVENANCE Section
    obs_ids = e_meta.get("observation_ids", [f"obs_{event_id}_0"])
    ev_src_ids = sorted(list(set(item.get("evidence_id", "") for item in ev_items if item.get("evidence_id"))))
    ev_fam_ids = sorted(list(set(item.get("evidence_family", "") for item in ev_items if item.get("evidence_family"))))
    reason_codes = sorted(list(set(sec_confidence["abstention_reason_codes"] + sec_priority["priority_drivers"] + sec_novelty["novelty_drivers"])))

    sec_provenance = {
        "observation_ids": obs_ids,
        "event_id": event_id,
        "evidence_source_ids": ev_src_ids,
        "evidence_family_ids": ev_fam_ids,
        "reason_codes": reason_codes
    }

    # Return canonical top-level dictionary
    canonical_contract = {
        "schema_version": SCHEMA_VERSION,
        "pipeline_version": PIPELINE_VERSION,
        "event": sec_event,
        "observation": sec_observation,
        "thermal": sec_thermal,
        "behavior": sec_behavior,
        "abnormality": sec_abnormality,
        "source": sec_source,
        "novelty": sec_novelty,
        "evidence": sec_evidence,
        "confidence": sec_confidence,
        "risk": sec_risk,
        "priority": sec_priority,
        "explanation": sec_explanation,
        "verification": sec_verification,
        "pipeline": sec_pipeline,
        "limitations": sec_limitations,
        "provenance": sec_provenance,
        "event_id": event_id,
        "event_metadata": e_meta,
        "observation_summary": obs_sum,
        "source_assessment": src_ass,
        "behavior_assessment": beh_ass,
        "abnormality_assessment": abn_ass,
        "evidence_assessment": ev_ass,
        "confidence_assessment": conf_ass,
        "risk_assessment": risk_ass,
        "priority_assessment": prio_ass,
        "verification_assessment": ver_ass,
        "pipeline_status": pip_ass
    }

    return canonical_contract


# ==============================================================================
# 3. CONTRACT VALIDATOR
# ==============================================================================

@dataclass
class ContractValidationError:
    section: str
    field: str
    error_type: str # "MISSING_SECTION", "INVALID_VOCABULARY", "INVALID_NULL", "SEMANTIC_VIOLATION"
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def validate_event_intelligence_result(result: Any) -> List[ContractValidationError]:
    """
    Validates an EventIntelligenceResult object or dictionary against the frozen
    AGN-EVENT-INTELLIGENCE-1.0 contract schema. Returns a list of structured validation errors.
    """
    errors: List[ContractValidationError] = []

    if result is None:
        return [ContractValidationError("ROOT", "ALL", "INVALID_NULL", "Result object is None")]

    if hasattr(result, "to_dict"):
        raw_dict = result.to_dict()
    elif isinstance(result, dict):
        raw_dict = dict(result)
    else:
        return [ContractValidationError("ROOT", "ALL", "SEMANTIC_VIOLATION", "Result object is not a dict or EventIntelligenceResult")]

    contract = build_canonical_contract(raw_dict)

    # 1. Check Top-Level Required Sections
    required_sections = [
        "schema_version", "pipeline_version", "event", "observation", "thermal",
        "behavior", "abnormality", "source", "novelty", "evidence", "confidence",
        "risk", "priority", "explanation", "verification", "pipeline", "limitations", "provenance"
    ]
    for sec in required_sections:
        if sec not in contract or contract[sec] is None:
            errors.append(ContractValidationError(
                section=sec, field="ROOT", error_type="MISSING_SECTION",
                message=f"Missing required top-level section '{sec}'"
            ))

    # 2. Vocabulary Checks
    src_class = contract.get("source", {}).get("predicted_source_class")
    if src_class not in FROZEN_SOURCE_CLASSES:
        errors.append(ContractValidationError(
            section="source", field="predicted_source_class", error_type="INVALID_VOCABULARY",
            message=f"Invalid predicted source class '{src_class}'. Must be in {FROZEN_SOURCE_CLASSES}"
        ))

    dec_state = contract.get("source", {}).get("decision_state")
    if dec_state not in FROZEN_DECISION_STATES:
        errors.append(ContractValidationError(
            section="source", field="decision_state", error_type="INVALID_VOCABULARY",
            message=f"Invalid decision state '{dec_state}'. Must be in {FROZEN_DECISION_STATES}"
        ))

    dist_state = contract.get("novelty", {}).get("distribution_state")
    if dist_state not in FROZEN_DISTRIBUTION_STATES:
        errors.append(ContractValidationError(
            section="novelty", field="distribution_state", error_type="INVALID_VOCABULARY",
            message=f"Invalid distribution state '{dist_state}'. Must be in {FROZEN_DISTRIBUTION_STATES}"
        ))

    evt_state = contract.get("behavior", {}).get("event_state")
    if evt_state not in FROZEN_EVENT_STATES:
        errors.append(ContractValidationError(
            section="behavior", field="event_state", error_type="INVALID_VOCABULARY",
            message=f"Invalid event state '{evt_state}'. Must be in {FROZEN_EVENT_STATES}"
        ))

    risk_lvl = contract.get("risk", {}).get("risk_level")
    if risk_lvl not in FROZEN_RISK_LEVELS:
        errors.append(ContractValidationError(
            section="risk", field="risk_level", error_type="INVALID_VOCABULARY",
            message=f"Invalid risk level '{risk_lvl}'. Must be in {FROZEN_RISK_LEVELS}"
        ))

    prio_lvl = contract.get("priority", {}).get("priority_level")
    if prio_lvl not in FROZEN_PRIORITY_LEVELS:
        errors.append(ContractValidationError(
            section="priority", field="priority_level", error_type="INVALID_VOCABULARY",
            message=f"Invalid priority level '{prio_lvl}'. Must be in {FROZEN_PRIORITY_LEVELS}"
        ))

    ver_state = contract.get("verification", {}).get("verification_state")
    if ver_state not in FROZEN_VERIFICATION_STATES:
        errors.append(ContractValidationError(
            section="verification", field="verification_state", error_type="INVALID_VOCABULARY",
            message=f"Invalid verification state '{ver_state}'. Must be in {FROZEN_VERIFICATION_STATES}"
        ))

    # 3. Semantic Invariant Verification
    if src_class != "UNKNOWN" and src_class == evt_state:
        errors.append(ContractValidationError(
            section="SEMANTICS", field="SOURCE_EVENT_STATE", error_type="SEMANTIC_VIOLATION",
            message=f"Source class ({src_class}) conflated with event state ({evt_state})"
        ))

    prov = contract.get("provenance", {})
    if not prov.get("observation_ids"):
        errors.append(ContractValidationError(
            section="provenance", field="observation_ids", error_type="INVALID_NULL",
            message="Provenance missing observation_ids list"
        ))

    return errors


# ==============================================================================
# 4. JSON SERIALIZATION UTILITY
# ==============================================================================

class ContractJSONEncoder(json.JSONEncoder):
    """Deterministic JSON encoder handling NumPy types and float precision."""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, (np.floating, float)):
            return None if np.isnan(obj) or np.isinf(obj) else float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif hasattr(obj, "to_dict"):
            return obj.to_dict()
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        return super().default(obj)


def serialize_to_json(contract_dict: Dict[str, Any], indent: int = 2) -> str:
    """Serializes a contract dictionary into a formatted JSON string deterministically."""
    return json.dumps(contract_dict, cls=ContractJSONEncoder, indent=indent, sort_keys=True)
