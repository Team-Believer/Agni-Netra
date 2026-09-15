"""
Agni-Netra Confidence Calibration & Unknown Decision Engine (Phase 17E)

Production confidence and uncertainty layer that integrates:
- Classification / Model confidence (calibrated or raw fallback)
- Evidence completeness
- Evidence convergence (family-aware)
- Data quality / Observation quality
- Temporal sufficiency
- Historical sufficiency
- Evidence contradiction / penalty
- Source-agnostic abstention decision hierarchy (INSUFFICIENT_OBSERVATION, UNKNOWN, NEEDS_VERIFICATION, KNOWN)

Preserves the core Agni-Netra distinction:
prediction != confidence != evidence completeness != risk
"""

import math
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple

from src.features.canonical_event_features import CanonicalEventFeatures
from src.features.low_t_persistent_heat import LowTResult
from src.intelligence.historical_abnormality import AbnormalityResult
from src.intelligence.evidence_aggregation import EventEvidenceLedger, EvidenceItem

# Calibration Status Constants
CALIBRATED = "CALIBRATED"
FALLBACK = "FALLBACK"
UNCALIBRATED = "UNCALIBRATED"

CALIBRATION_METHOD_TEMPERATURE = "temperature"
CALIBRATION_METHOD_ISOTONIC = "isotonic"
CALIBRATION_METHOD_IDENTITY = "identity"
CALIBRATION_METHOD_UNAVAILABLE = "unavailable"

# Decision State Constants
DECISION_KNOWN = "KNOWN"
DECISION_UNKNOWN = "UNKNOWN"
DECISION_NEEDS_VERIFICATION = "NEEDS_VERIFICATION"
DECISION_INSUFFICIENT_OBSERVATION = "INSUFFICIENT_OBSERVATION"

# Reason Codes Constants
REASON_INSUFFICIENT_TEMPORAL_HISTORY = "INSUFFICIENT_TEMPORAL_HISTORY"
REASON_INSUFFICIENT_HISTORICAL_BASELINE = "INSUFFICIENT_HISTORICAL_BASELINE"
REASON_LOW_EVIDENCE_COMPLETENESS = "LOW_EVIDENCE_COMPLETENESS"
REASON_LOW_INDEPENDENT_CONVERGENCE = "LOW_INDEPENDENT_CONVERGENCE"
REASON_STRONG_EVIDENCE_CONFLICT = "STRONG_EVIDENCE_CONFLICT"
REASON_LOW_DATA_QUALITY = "LOW_DATA_QUALITY"
REASON_SOURCE_AMBIGUITY = "SOURCE_AMBIGUITY"
REASON_MODEL_UNCERTAINTY = "MODEL_UNCERTAINTY"
REASON_CRITICAL_EVIDENCE_MISSING = "CRITICAL_EVIDENCE_MISSING"

# Operational Actions
ACTION_AUTO_CLASSIFY = "AUTO_CLASSIFY"
ACTION_REVIEW_RECOMMENDED = "REVIEW_RECOMMENDED"
ACTION_VERIFY_REQUIRED = "VERIFY_REQUIRED"
ACTION_INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

CRITICAL_FAMILIES = {"SENTINEL", "HISTORICAL", "CONTEXT", "TEMPORAL"}


class ConfidenceCalibrator:
    """
    Pluggable calibration abstraction over classifier probabilities.
    Supports temperature scaling, isotonic scaling, or identity fallback.
    """

    def __init__(self, method: str = CALIBRATION_METHOD_IDENTITY, params: Optional[Dict[str, Any]] = None):
        self.method = method
        self.params = params or {}

    def calibrate(self, raw_confidence: float) -> Tuple[float, str, str]:
        """
        Calibrate raw model probability.
        Returns: (calibrated_confidence, calibration_status, calibration_method)
        """
        prob = max(0.0, min(1.0, float(raw_confidence)))

        if self.method == CALIBRATION_METHOD_TEMPERATURE and "temperature" in self.params:
            T = float(self.params["temperature"])
            if T > 0:
                # Temperature scaling on logit
                eps = 1e-7
                p_clipped = np.clip(prob, eps, 1.0 - eps)
                logit = np.log(p_clipped / (1.0 - p_clipped))
                calibrated_logit = logit / T
                calibrated_prob = float(1.0 / (1.0 + np.exp(-calibrated_logit)))
                return calibrated_prob, CALIBRATED, CALIBRATION_METHOD_TEMPERATURE

        elif self.method == CALIBRATION_METHOD_ISOTONIC and "mapping" in self.params:
            # Interpolate from piecewise linear isotonic mapping dict {"x": [...], "y": [...]}
            x_vals = np.array(self.params["mapping"].get("x", [0.0, 1.0]))
            y_vals = np.array(self.params["mapping"].get("y", [0.0, 1.0]))
            calibrated_prob = float(np.interp(prob, x_vals, y_vals))
            return calibrated_prob, CALIBRATED, CALIBRATION_METHOD_ISOTONIC

        elif self.method == CALIBRATION_METHOD_UNAVAILABLE:
            return prob, UNCALIBRATED, CALIBRATION_METHOD_UNAVAILABLE

        # Default Fallback: Identity / Pass-through fallback
        return prob, FALLBACK, CALIBRATION_METHOD_IDENTITY


@dataclass
class ConfidenceEngineConfig:
    """Centralized configurable threshold parameters."""
    min_data_quality: float = 0.4
    min_temporal_sufficiency: float = 0.3
    min_historical_sufficiency: float = 0.3
    min_evidence_completeness: float = 0.4
    min_evidence_convergence: float = 0.4
    min_model_confidence_known: float = 0.60
    min_decision_confidence_known: float = 0.65
    max_contradiction_penalty_known: float = 0.25
    max_contradiction_penalty_verification: float = 0.50


@dataclass
class ConfidenceAssessment:
    classification_confidence: float
    evidence_completeness: float
    evidence_convergence: float
    data_quality_confidence: float
    temporal_sufficiency: float
    historical_sufficiency: float
    contradiction_penalty: float
    overall_decision_confidence: float
    confidence_level: str
    decision_state: str
    abstention_reason: List[str]
    limiting_factors: List[str]
    evidence_family_summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DecisionAssessment:
    event_id: str
    predicted_source_class: str
    decision_state: str
    confidence: ConfidenceAssessment
    calibration: Dict[str, str]
    evidence_summary: Dict[str, Any]
    abstention: Dict[str, Any]
    operational_action: str

    def to_dict(self) -> Dict[str, Any]:
        res = asdict(self)
        return res

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DecisionAssessment":
        conf_dict = d["confidence"]
        conf_obj = ConfidenceAssessment(**conf_dict)
        return cls(
            event_id=d["event_id"],
            predicted_source_class=d["predicted_source_class"],
            decision_state=d["decision_state"],
            confidence=conf_obj,
            calibration=d["calibration"],
            evidence_summary=d["evidence_summary"],
            abstention=d["abstention"],
            operational_action=d["operational_action"]
        )


def _compute_confidence_level(score: float) -> str:
    if score >= 0.85:
        return "VERY_HIGH"
    elif score >= 0.70:
        return "HIGH"
    elif score >= 0.50:
        return "MODERATE"
    elif score >= 0.30:
        return "LOW"
    else:
        return "VERY_LOW"


def evaluate_event_decision(
    event_id: str,
    predicted_source_class: str,
    raw_model_confidence: float,
    evidence_ledger: EventEvidenceLedger,
    canon: Optional[CanonicalEventFeatures] = None,
    low_t_result: Optional[LowTResult] = None,
    abnormality_result: Optional[AbnormalityResult] = None,
    calibrator: Optional[ConfidenceCalibrator] = None,
    config: Optional[ConfidenceEngineConfig] = None
) -> DecisionAssessment:
    """
    Evaluates evidence quality, classifier confidence, and convergence to compute calibrated confidence
    and determine the explicit decision state (INSUFFICIENT_OBSERVATION, UNKNOWN, NEEDS_VERIFICATION, KNOWN).
    """
    if config is None:
        config = ConfidenceEngineConfig()

    if calibrator is None:
        calibrator = ConfidenceCalibrator(method=CALIBRATION_METHOD_IDENTITY)

    # 1. Calibration
    calibrated_conf, cal_status, cal_method = calibrator.calibrate(raw_model_confidence)

    # 2. Extract inspection dimensions
    data_quality_confidence = float(evidence_ledger.data_quality_score)
    if canon is not None and hasattr(canon, 'observation_quality'):
        data_quality_confidence = float(canon.observation_quality)

    evidence_completeness = float(evidence_ledger.global_evidence_completeness)

    # Temporal sufficiency computation
    if canon is not None:
        obs_count = canon.observation_count_so_far
        duration = getattr(canon, 'event_age', getattr(canon, 'persistence', 0.0))
        if obs_count >= 3 and duration >= 12.0:
            temporal_sufficiency = 1.0
        elif obs_count >= 2:
            temporal_sufficiency = 0.6
        elif obs_count == 1:
            temporal_sufficiency = 0.2
        else:
            temporal_sufficiency = 0.0
    else:
        # Fallback inspection of evidence ledger
        temp_items = [e for e in evidence_ledger.evidence_items if e.evidence_family == "TEMPORAL" and e.direction == "SUPPORTING"]
        temporal_sufficiency = 1.0 if temp_items else 0.2

    # Historical sufficiency computation
    if abnormality_result is not None:
        if abnormality_result.abnormality_state in ["NORMAL", "UNUSUAL", "HIGHLY_ABNORMAL"]:
            historical_sufficiency = 1.0
        else:
            historical_sufficiency = 0.2
    elif canon is not None and getattr(canon, 'missing_history_indicator', 0) == 1:
        historical_sufficiency = 0.2
    else:
        hist_items = [e for e in evidence_ledger.evidence_items if e.evidence_family in ["HISTORICAL", "ANOMALY"] and e.status in ["OBSERVED", "DERIVED"]]
        historical_sufficiency = 1.0 if hist_items else 0.2

    # Family-aware evidence convergence & conflict grouping
    supporting_families = sorted(list(set(
        item.evidence_family for item in evidence_ledger.evidence_items if item.direction == "SUPPORTING"
    )))
    conflicting_families = sorted(list(set(
        item.evidence_family for item in evidence_ledger.evidence_items if item.direction == "CONFLICTING"
    )))
    missing_critical_families = sorted(list(set(
        item.evidence_family for item in evidence_ledger.evidence_items 
        if item.direction == "MISSING" and item.evidence_family in CRITICAL_FAMILIES
    )))

    # Compute family convergence score (0.0 to 1.0)
    net_supporting_count = max(0, len(supporting_families) - len(conflicting_families))
    if net_supporting_count >= 4 and len(conflicting_families) == 0:
        evidence_convergence_score = 1.0
    elif net_supporting_count >= 3:
        evidence_convergence_score = 0.8
    elif net_supporting_count >= 2:
        evidence_convergence_score = 0.6
    elif net_supporting_count == 1:
        evidence_convergence_score = 0.35
    else:
        evidence_convergence_score = 0.1

    # Contradiction penalty score
    # Note: Missing evidence is not conflicting evidence!
    if conflicting_families:
        contradiction_penalty = min(1.0, len(conflicting_families) * 0.35)
    else:
        contradiction_penalty = 0.0

    # Overall decision confidence
    # Auditable score composition (not blind multiplication)
    weighted_score = (
        0.35 * calibrated_conf +
        0.25 * evidence_completeness +
        0.25 * evidence_convergence_score +
        0.15 * data_quality_confidence
    )
    overall_decision_confidence = max(0.0, min(1.0, weighted_score - 0.3 * contradiction_penalty))
    confidence_level = _compute_confidence_level(overall_decision_confidence)

    # 3. Decision Hierarchy & Abstention Engine
    # Evaluated in strict order:
    # 1. INSUFFICIENT_OBSERVATION
    # 2. UNKNOWN
    # 3. NEEDS_VERIFICATION
    # 4. KNOWN

    abstention_codes: List[str] = []
    limiting_factors: List[str] = []
    decision_state = DECISION_KNOWN
    operational_action = ACTION_AUTO_CLASSIFY

    # --- GATE 1: INSUFFICIENT_OBSERVATION ---
    is_insufficient_obs = False
    if data_quality_confidence < config.min_data_quality:
        is_insufficient_obs = True
        abstention_codes.append(REASON_LOW_DATA_QUALITY)
        limiting_factors.append(f"Low observation quality (score={data_quality_confidence:.2f})")

    if temporal_sufficiency < config.min_temporal_sufficiency:
        is_insufficient_obs = True
        abstention_codes.append(REASON_INSUFFICIENT_TEMPORAL_HISTORY)
        limiting_factors.append(f"Insufficient temporal observation count/history (score={temporal_sufficiency:.2f})")

    if historical_sufficiency < config.min_historical_sufficiency and (abnormality_result is not None and abnormality_result.abnormality_state == "UNKNOWN"):
        abstention_codes.append(REASON_INSUFFICIENT_HISTORICAL_BASELINE)
        limiting_factors.append("Missing historical baseline for change analysis")

    if is_insufficient_obs:
        decision_state = DECISION_INSUFFICIENT_OBSERVATION
        operational_action = ACTION_INSUFFICIENT_DATA

    # --- GATE 2: UNKNOWN ---
    elif (
        evidence_completeness < config.min_evidence_completeness or
        evidence_convergence_score < config.min_evidence_convergence or
        len(supporting_families) == 0 or
        calibrated_conf < 0.35
    ):
        decision_state = DECISION_UNKNOWN
        operational_action = ACTION_REVIEW_RECOMMENDED
        if evidence_completeness < config.min_evidence_completeness:
            abstention_codes.append(REASON_LOW_EVIDENCE_COMPLETENESS)
            limiting_factors.append(f"Low evidence completeness ({evidence_completeness:.2f})")
        if evidence_convergence_score < config.min_evidence_convergence:
            abstention_codes.append(REASON_LOW_INDEPENDENT_CONVERGENCE)
            limiting_factors.append("Weak independent evidence convergence across families")
        if len(supporting_families) == 0:
            abstention_codes.append(REASON_SOURCE_AMBIGUITY)
            limiting_factors.append("No independent evidence families support the predicted class")
        if calibrated_conf < 0.35:
            abstention_codes.append(REASON_MODEL_UNCERTAINTY)
            limiting_factors.append(f"High model classifier uncertainty (score={calibrated_conf:.2f})")
        if missing_critical_families:
            abstention_codes.append(REASON_CRITICAL_EVIDENCE_MISSING)
            limiting_factors.append(f"Missing critical evidence families: {missing_critical_families}")

    # --- GATE 3: NEEDS_VERIFICATION ---
    elif (
        contradiction_penalty >= config.max_contradiction_penalty_known or
        len(conflicting_families) >= 1 or
        calibrated_conf < config.min_model_confidence_known or
        overall_decision_confidence < config.min_decision_confidence_known
    ):
        decision_state = DECISION_NEEDS_VERIFICATION
        operational_action = ACTION_VERIFY_REQUIRED
        if len(conflicting_families) >= 1 or contradiction_penalty >= config.max_contradiction_penalty_known:
            abstention_codes.append(REASON_STRONG_EVIDENCE_CONFLICT)
            limiting_factors.append(f"Evidence contradiction detected in families: {conflicting_families}")
        if calibrated_conf < config.min_model_confidence_known:
            abstention_codes.append(REASON_MODEL_UNCERTAINTY)
            limiting_factors.append(f"Model confidence ({calibrated_conf:.2f}) below auto-classification threshold ({config.min_model_confidence_known:.2f})")
        if overall_decision_confidence < config.min_decision_confidence_known:
            abstention_codes.append(REASON_SOURCE_AMBIGUITY)
            limiting_factors.append(f"Overall decision confidence ({overall_decision_confidence:.2f}) requires human verification")

    # --- GATE 4: KNOWN ---
    else:
        decision_state = DECISION_KNOWN
        operational_action = ACTION_AUTO_CLASSIFY

    # Deduplicate reason codes
    abstention_codes = sorted(list(set(abstention_codes)))

    # Structure Confidence Assessment
    confidence_obj = ConfidenceAssessment(
        classification_confidence=calibrated_conf,
        evidence_completeness=evidence_completeness,
        evidence_convergence=evidence_convergence_score,
        data_quality_confidence=data_quality_confidence,
        temporal_sufficiency=temporal_sufficiency,
        historical_sufficiency=historical_sufficiency,
        contradiction_penalty=contradiction_penalty,
        overall_decision_confidence=overall_decision_confidence,
        confidence_level=confidence_level,
        decision_state=decision_state,
        abstention_reason=abstention_codes,
        limiting_factors=limiting_factors,
        evidence_family_summary={
            "supporting_families": supporting_families,
            "conflicting_families": conflicting_families,
            "missing_critical_families": missing_critical_families,
            "net_supporting_count": len(supporting_families) - len(conflicting_families)
        }
    )

    is_abstained = (decision_state != DECISION_KNOWN)

    return DecisionAssessment(
        event_id=event_id,
        predicted_source_class=predicted_source_class,
        decision_state=decision_state,
        confidence=confidence_obj,
        calibration={
            "calibration_status": cal_status,
            "calibration_method": cal_method,
            "raw_model_confidence": str(raw_model_confidence),
            "calibrated_confidence": str(calibrated_conf)
        },
        evidence_summary={
            "supporting_families": supporting_families,
            "conflicting_families": conflicting_families,
            "missing_critical_families": missing_critical_families,
            "convergence_summary": f"{len(supporting_families)} supporting, {len(conflicting_families)} conflicting"
        },
        abstention={
            "is_abstained": is_abstained,
            "abstention_reason_codes": abstention_codes,
            "limiting_factors": limiting_factors
        },
        operational_action=operational_action
    )
