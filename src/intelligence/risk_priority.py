"""
Agni-Netra Risk & Priority Intelligence Engine (Phase 17F)

Production Risk and Operational Priority layer built on top of:
- Canonical feature pipeline
- Low-T persistent heat intelligence
- Historical abnormality/change intelligence
- Evidence aggregation + Event Evidence Ledger
- Confidence/calibration + UNKNOWN decision engine

Preserves core product principles:
Source != Behavior != Abnormality != Evidence != Confidence != Severity != Impact != Risk != Priority

Hazard * Impact = Base Risk
Uncertainty -> Risk Confidence & Priority (Verification Need)
"""

import math
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple

from src.features.canonical_event_features import CanonicalEventFeatures
from src.features.low_t_persistent_heat import LowTResult
from src.intelligence.historical_abnormality import AbnormalityResult
from src.intelligence.evidence_aggregation import EventEvidenceLedger
from src.intelligence.confidence_decision import (
    DecisionAssessment, ConfidenceAssessment,
    DECISION_KNOWN, DECISION_UNKNOWN, DECISION_NEEDS_VERIFICATION,
    DECISION_INSUFFICIENT_OBSERVATION
)

# Risk Levels
RISK_VERY_LOW = "VERY_LOW"
RISK_LOW = "LOW"
RISK_MODERATE = "MODERATE"
RISK_HIGH = "HIGH"
RISK_VERY_HIGH = "VERY_HIGH"

# Priority Levels
PRIORITY_P0 = "P0"  # CRITICAL / IMMEDIATE ATTENTION
PRIORITY_P1 = "P1"  # HIGH PRIORITY
PRIORITY_P2 = "P2"  # MODERATE PRIORITY
PRIORITY_P3 = "P3"  # LOW PRIORITY
PRIORITY_P4 = "P4"  # INFORMATIONAL / MONITOR

# Urgency Levels
URGENCY_URGENT = "URGENT"
URGENCY_HIGH = "HIGH"
URGENCY_NORMAL = "NORMAL"
URGENCY_LOW = "LOW"

# Operational Actions
ACTION_IMMEDIATE_REVIEW = "IMMEDIATE_REVIEW"
ACTION_PRIORITY_REVIEW = "PRIORITY_REVIEW"
ACTION_VERIFY = "VERIFY"
ACTION_MONITOR = "MONITOR"
ACTION_INFORMATIONAL = "INFORMATIONAL"

# Machine-Readable Priority Reason Codes
CODE_HIGH_HAZARD = "HIGH_HAZARD"
CODE_HIGH_IMPACT_CONTEXT = "HIGH_IMPACT_CONTEXT"
CODE_RAPID_THERMAL_INCREASE = "RAPID_THERMAL_INCREASE"
CODE_ABNORMAL_CHANGE_DETECTED = "ABNORMAL_CHANGE_DETECTED"
CODE_PERSISTENT_ACTIVITY = "PERSISTENT_ACTIVITY"
CODE_EMERGENCY_FLARE_SIGNAL = "EMERGENCY_FLARE_SIGNAL"
CODE_CRITICAL_FACILITY_PROXIMITY = "CRITICAL_FACILITY_PROXIMITY"
CODE_HIGH_EXPOSURE_CONTEXT = "HIGH_EXPOSURE_CONTEXT"
CODE_VERIFICATION_REQUIRED = "VERIFICATION_REQUIRED"
CODE_STRONG_EVIDENCE_CONFLICT = "STRONG_EVIDENCE_CONFLICT"
CODE_LOW_CONFIDENCE = "LOW_CONFIDENCE"
CODE_INSUFFICIENT_OBSERVATION = "INSUFFICIENT_OBSERVATION"

# Inherent Source Base Hazard Weights (Decoupled from confidence & impact)
SOURCE_BASE_HAZARD = {
    "ABNORMAL_EMERGENCY_FLARE": 0.75,
    "INDUSTRIAL_FIRE": 0.70,
    "WILDFIRE": 0.65,
    "LANDFILL_OTHER_ANTHROPOGENIC": 0.45,
    "AGRICULTURAL_BURN": 0.35,
    "MINING_INDUSTRIAL_HEAT": 0.30,
    "ROUTINE_FLARE": 0.25,
    "OTHER": 0.30,
    "UNKNOWN": 0.40  # Bounded unresolved baseline, NOT 0 and NOT max 1.0
}


@dataclass
class RiskPriorityConfig:
    """Centralized configurable threshold parameters."""
    high_frp_threshold: float = 100.0
    high_hazard_threshold: float = 0.70
    high_impact_threshold: float = 0.70
    p0_threshold: float = 0.85
    p1_threshold: float = 0.70
    p2_threshold: float = 0.50
    p3_threshold: float = 0.30


@dataclass
class RiskPriorityAssessment:
    event_id: str
    risk: Dict[str, Any]
    priority: Dict[str, Any]
    drivers: Dict[str, List[str]]
    uncertainty: Dict[str, Any]
    limitations: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "RiskPriorityAssessment":
        return cls(
            event_id=d["event_id"],
            risk=d["risk"],
            priority=d["priority"],
            drivers=d["drivers"],
            uncertainty=d["uncertainty"],
            limitations=d["limitations"]
        )


def _score_to_level(score: float) -> str:
    if score >= 0.85:
        return RISK_VERY_HIGH
    elif score >= 0.70:
        return RISK_HIGH
    elif score >= 0.50:
        return RISK_MODERATE
    elif score >= 0.30:
        return RISK_LOW
    else:
        return RISK_VERY_LOW


def calculate_hazard(
    predicted_source_class: str,
    canon: Optional[CanonicalEventFeatures] = None,
    low_t_result: Optional[LowTResult] = None,
    abnormality_result: Optional[AbnormalityResult] = None
) -> Tuple[float, str, List[str]]:
    """
    Computes physical hazard score based on source class baseline, thermal intensity, growth,
    abnormality, and persistence behavior.
    """
    hazard_drivers = []
    base_class_hazard = SOURCE_BASE_HAZARD.get(predicted_source_class, 0.35)
    hazard_drivers.append(f"Source class '{predicted_source_class}' base hazard factor ({base_class_hazard:.2f})")

    # Thermal Intensity & FRP Spike
    frp_contrib = 0.0
    if canon is not None:
        frp = canon.current_max_frp if not np.isnan(canon.current_max_frp) else canon.current_mean_frp
        if not np.isnan(frp) and frp > 0:
            if frp >= 200.0:
                frp_contrib = 0.30
                hazard_drivers.append(f"Extreme FRP intensity ({frp:.1f} MW)")
            elif frp >= 100.0:
                frp_contrib = 0.20
                hazard_drivers.append(f"High FRP intensity ({frp:.1f} MW)")
            elif frp >= 50.0:
                frp_contrib = 0.10
                hazard_drivers.append(f"Moderate FRP intensity ({frp:.1f} MW)")

        if getattr(canon, 'frp_change_rate', 0.0) > 2.0:
            frp_contrib += 0.10
            hazard_drivers.append("Rapid FRP change rate detected")

        if getattr(canon, 'footprint_change', 0.0) > 1.5:
            frp_contrib += 0.10
            hazard_drivers.append("Expanding spatial footprint")

    # Abnormality contribution
    abnormality_contrib = 0.0
    if abnormality_result is not None:
        if abnormality_result.abnormality_state in ["UNUSUAL", "HIGHLY_ABNORMAL"]:
            abnormality_contrib = 0.15 * abnormality_result.abnormality_score
            hazard_drivers.append(f"Historical thermal abnormality ({abnormality_result.abnormality_state.lower().replace('_', ' ')})")

    # Low-T persistence contribution
    persistence_contrib = 0.0
    if low_t_result is not None and low_t_result.low_t_state == "LOW_T_PERSISTENT":
        persistence_contrib = 0.05
        hazard_drivers.append("Persistent moderate-intensity thermal behavior")

    raw_hazard = base_class_hazard + frp_contrib + abnormality_contrib + persistence_contrib
    hazard_score = max(0.0, min(1.0, raw_hazard))
    hazard_level = _score_to_level(hazard_score)

    return hazard_score, hazard_level, hazard_drivers


def calculate_impact(
    canon: Optional[CanonicalEventFeatures] = None,
    evidence_ledger: Optional[EventEvidenceLedger] = None
) -> Tuple[float, str, List[str], Dict[str, Any]]:
    """
    Computes contextual impact and exposure score based on proximity to industrial facilities,
    land context, infrastructure, and footprint.
    """
    impact_drivers = []
    limitations = {"missing_context": False, "context_note": ""}

    base_impact = 0.20

    if canon is not None:
        if getattr(canon, 'missing_context_indicator', 0) == 1:
            limitations["missing_context"] = True
            limitations["context_note"] = "Facility/Context operating state missing or unavailable"
            base_impact = 0.35  # Bounded fallback, not zero
            impact_drivers.append("Context missing: using bounded fallback impact baseline (0.35)")
        else:
            if canon.nearby_industrial_flag == 1 or canon.facility_context_type > 0:
                base_impact = 0.70
                impact_drivers.append("Proximity to critical industrial facility infrastructure")
            elif canon.land_context == 1:
                base_impact = 0.55
                impact_drivers.append("Commercial/Industrial land context")
            else:
                base_impact = 0.30
                impact_drivers.append("Vegetation/Forest land context")

        # Extent modifier
        if getattr(canon, 'spatial_extent', 0.0) > 2.0:
            base_impact += 0.10
            impact_drivers.append(f"Large spatial extent ({canon.spatial_extent:.1f} km²)")

    elif evidence_ledger is not None:
        ctx_items = [e for e in evidence_ledger.evidence_items if e.evidence_family in ["CONTEXT", "FACILITY"]]
        if any(e.direction == "SUPPORTING" for e in ctx_items):
            base_impact = 0.70
            impact_drivers.append("Facility context observed in evidence ledger")
        else:
            base_impact = 0.35
            impact_drivers.append("Standard contextual impact baseline")

    impact_score = max(0.0, min(1.0, base_impact))
    impact_level = _score_to_level(impact_score)

    return impact_score, impact_level, impact_drivers, limitations


def calculate_urgency(
    canon: Optional[CanonicalEventFeatures] = None,
    abnormality_result: Optional[AbnormalityResult] = None,
    decision_assessment: Optional[DecisionAssessment] = None
) -> Tuple[str, List[str]]:
    """
    Determines operational urgency (URGENT, HIGH, NORMAL, LOW) based on rapid change,
    emergency signals, and verification requirements.
    """
    urgency_drivers = []

    is_urgent = False
    is_high = False

    if decision_assessment is not None:
        if decision_assessment.predicted_source_class == "ABNORMAL_EMERGENCY_FLARE":
            is_urgent = True
            urgency_drivers.append("Emergency/Abnormal flare class signal detected")

        if decision_assessment.decision_state == DECISION_NEEDS_VERIFICATION:
            is_high = True
            urgency_drivers.append("Operational decision state NEEDS_VERIFICATION due to evidence conflict/uncertainty")

    if canon is not None:
        if getattr(canon, 'frp_change_rate', 0.0) > 2.0 or getattr(canon, 'change_point_indicator', 0) == 1:
            is_urgent = True
            urgency_drivers.append("Rapid thermal FRP increase / change point detected")

        if getattr(canon, 'footprint_change', 0.0) > 2.0:
            is_high = True
            urgency_drivers.append("Rapid spatial footprint expansion")

    if abnormality_result is not None and abnormality_result.change_indicators.frp_spike == 1:
        is_high = True
        urgency_drivers.append("Sudden historical FRP spike indicator")

    if is_urgent:
        return URGENCY_URGENT, urgency_drivers
    elif is_high:
        return URGENCY_HIGH, urgency_drivers
    else:
        return URGENCY_NORMAL, urgency_drivers if urgency_drivers else ["Stable detection pattern observed"]


def evaluate_risk_and_priority(
    event_id: str,
    decision_assessment: DecisionAssessment,
    evidence_ledger: EventEvidenceLedger,
    canon: Optional[CanonicalEventFeatures] = None,
    low_t_result: Optional[LowTResult] = None,
    abnormality_result: Optional[AbnormalityResult] = None,
    config: Optional[RiskPriorityConfig] = None
) -> RiskPriorityAssessment:
    """
    Evaluates physical risk, impact, operational urgency, and priority score while integrating
    decision uncertainty from Phase 17E.
    """
    if config is None:
        config = RiskPriorityConfig()

    predicted_source = decision_assessment.predicted_source_class

    # 1. Calculate Hazard
    hazard_score, hazard_level, hazard_drivers = calculate_hazard(
        predicted_source_class=predicted_source,
        canon=canon,
        low_t_result=low_t_result,
        abnormality_result=abnormality_result
    )

    # 2. Calculate Impact
    impact_score, impact_level, impact_drivers, limitations_dict = calculate_impact(
        canon=canon,
        evidence_ledger=evidence_ledger
    )

    # 3. Calculate Base Risk: BASE_RISK = sqrt(HAZARD * IMPACT)
    # Multiplicative monotonic formulation ensures increasing hazard or impact never reduces base risk
    base_risk_score = float(np.sqrt(hazard_score * impact_score))
    risk_level = _score_to_level(base_risk_score)

    # 4. Risk Confidence (Decoupled from classification_confidence)
    # Risk confidence reflects evidence quality and decision confidence for risk scoring
    risk_confidence = float(decision_assessment.confidence.overall_decision_confidence)

    # 5. Calculate Urgency
    urgency, urgency_drivers = calculate_urgency(
        canon=canon,
        abnormality_result=abnormality_result,
        decision_assessment=decision_assessment
    )

    # Map Urgency weight
    urgency_weight_map = {
        URGENCY_URGENT: 1.0,
        URGENCY_HIGH: 0.75,
        URGENCY_NORMAL: 0.40,
        URGENCY_LOW: 0.10
    }
    urg_weight = urgency_weight_map.get(urgency, 0.40)

    # Verification Need weight (increases priority when decision needs verification)
    verification_need = 0.0
    priority_drivers = []

    if decision_assessment.decision_state == DECISION_NEEDS_VERIFICATION:
        verification_need = 0.8
        priority_drivers.append(CODE_VERIFICATION_REQUIRED)
        if CODE_STRONG_EVIDENCE_CONFLICT in decision_assessment.abstention.get("abstention_reason_codes", []):
            priority_drivers.append(CODE_STRONG_EVIDENCE_CONFLICT)

    elif decision_assessment.decision_state == DECISION_UNKNOWN:
        verification_need = 0.6
        priority_drivers.append(CODE_VERIFICATION_REQUIRED)
        priority_drivers.append("UNRESOLVED_SOURCE_INTERPRETATION")

    elif decision_assessment.decision_state == DECISION_INSUFFICIENT_OBSERVATION:
        verification_need = 0.4
        priority_drivers.append(CODE_INSUFFICIENT_OBSERVATION)

    if hazard_score >= config.high_hazard_threshold:
        priority_drivers.append(CODE_HIGH_HAZARD)

    if impact_score >= config.high_impact_threshold:
        priority_drivers.append(CODE_HIGH_IMPACT_CONTEXT)
        if canon is not None and canon.nearby_industrial_flag == 1:
            priority_drivers.append(CODE_CRITICAL_FACILITY_PROXIMITY)

    if urgency in [URGENCY_URGENT, URGENCY_HIGH]:
        if "Rapid FRP" in str(urgency_drivers):
            priority_drivers.append(CODE_RAPID_THERMAL_INCREASE)
        if "Emergency" in str(urgency_drivers):
            priority_drivers.append(CODE_EMERGENCY_FLARE_SIGNAL)

    if abnormality_result is not None and abnormality_result.abnormality_state in ["UNUSUAL", "HIGHLY_ABNORMAL"]:
        priority_drivers.append(CODE_ABNORMAL_CHANGE_DETECTED)

    if low_t_result is not None and low_t_result.low_t_state == "LOW_T_PERSISTENT":
        priority_drivers.append(CODE_PERSISTENT_ACTIVITY)

    # 6. Operational Priority Score Calculation
    # Priority = 0.45 * Base_Risk + 0.30 * Urgency + 0.15 * Impact + 0.10 * Verification_Need
    raw_priority = 0.45 * base_risk_score + 0.30 * urg_weight + 0.15 * impact_score + 0.10 * verification_need
    priority_score = max(0.0, min(1.0, raw_priority))

    # Priority Level Mapping
    if priority_score >= config.p0_threshold:
        priority_level = PRIORITY_P0
        operational_action = ACTION_IMMEDIATE_REVIEW
    elif priority_score >= config.p1_threshold:
        priority_level = PRIORITY_P1
        operational_action = ACTION_PRIORITY_REVIEW
    elif priority_score >= config.p2_threshold:
        priority_level = PRIORITY_P2
        operational_action = ACTION_VERIFY
    elif priority_score >= config.p3_threshold:
        priority_level = PRIORITY_P3
        operational_action = ACTION_MONITOR
    else:
        priority_level = PRIORITY_P4
        operational_action = ACTION_INFORMATIONAL

    # Deduplicate priority drivers
    priority_drivers = sorted(list(set(priority_drivers)))

    # Structure Output
    return RiskPriorityAssessment(
        event_id=event_id,
        risk={
            "hazard_score": hazard_score,
            "hazard_level": hazard_level,
            "impact_score": impact_score,
            "impact_level": impact_level,
            "base_risk_score": base_risk_score,
            "risk_level": risk_level,
            "risk_confidence": risk_confidence
        },
        priority={
            "priority_score": priority_score,
            "priority_level": priority_level,
            "urgency": urgency,
            "operational_action": operational_action
        },
        drivers={
            "hazard_drivers": hazard_drivers,
            "impact_drivers": impact_drivers,
            "priority_drivers": priority_drivers,
            "urgency_drivers": urgency_drivers
        },
        uncertainty={
            "decision_state": decision_assessment.decision_state,
            "confidence_level": decision_assessment.confidence.confidence_level,
            "evidence_completeness": decision_assessment.confidence.evidence_completeness,
            "evidence_convergence": decision_assessment.confidence.evidence_convergence,
            "limiting_factors": decision_assessment.confidence.limiting_factors
        },
        limitations={
            "missing_context": limitations_dict.get("missing_context", False),
            "unavailable_evidence": decision_assessment.confidence.evidence_family_summary.get("missing_critical_families", []),
            "confidence_limitations": decision_assessment.abstention.get("limiting_factors", [])
        }
    )
