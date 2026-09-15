"""
Agni-Netra Novel / Out-of-Distribution (OOD) Event Intelligence (Phase 20E)

Detects when a thermal event does NOT sufficiently resemble known source/behavior patterns,
preventing forced classification of novel or poorly represented thermal phenomena.

Core Scientific Principles:
MODEL PROBABILITY != IN-DISTRIBUTION STATUS
HIGH MODEL CONFIDENCE != KNOWN EVENT
UNKNOWN != NO EVENT
DATA QUALITY FAILURE != NOVEL EVENT
EVIDENCE CONFLICT != NOVEL PATTERN
ABNORMALITY != NOVELTY
"""

import math
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple, Union

from src.features.canonical_event_features import CanonicalEventFeatures

# Distribution States
DISTRIBUTION_KNOWN_LIKE = "KNOWN_LIKE"
DISTRIBUTION_NOVEL = "NOVEL"
DISTRIBUTION_UNKNOWN = "UNKNOWN"

# Novelty Levels
LEVEL_KNOWN_LIKE = "KNOWN_LIKE"
LEVEL_LOW_NOVELTY = "LOW_NOVELTY"
LEVEL_MODERATE_NOVELTY = "MODERATE_NOVELTY"
LEVEL_HIGH_NOVELTY = "HIGH_NOVELTY"
LEVEL_NOVEL = "NOVEL"
LEVEL_UNKNOWN = "UNKNOWN"

# Reason Codes
REASON_FEATURE_SPACE_DEVIATION = "FEATURE_SPACE_DEVIATION"
REASON_HIGH_CLASS_AMBIGUITY = "HIGH_CLASS_AMBIGUITY"
REASON_EVIDENCE_PATTERN_NOVEL = "EVIDENCE_PATTERN_NOVEL"
REASON_TEMPORAL_PATTERN_NOVEL = "TEMPORAL_PATTERN_NOVEL"
REASON_BEHAVIOR_PATTERN_NOVEL = "BEHAVIOR_PATTERN_NOVEL"
REASON_CONTEXT_PATTERN_NOVEL = "CONTEXT_PATTERN_NOVEL"
REASON_MULTI_SIGNAL_OOD = "MULTI_SIGNAL_OOD"
REASON_HIGH_CONFIDENCE_OOD = "HIGH_CONFIDENCE_OOD"
REASON_INSUFFICIENT_DATA_FOR_OOD = "INSUFFICIENT_DATA_FOR_OOD"
REASON_LOW_DATA_QUALITY_FOR_OOD = "LOW_DATA_QUALITY_FOR_OOD"
REASON_EVIDENCE_CONFLICT_NOT_NOVEL = "EVIDENCE_CONFLICT_NOT_NOVEL"
REASON_HISTORICAL_NOVELTY = "HISTORICAL_NOVELTY"
REASON_UNSEEN_SOURCE_PATTERN = "UNSEEN_SOURCE_PATTERN"


@dataclass
class NoveltyConfig:
    """Configurable threshold policy for Novelty & OOD Intelligence."""
    novelty_low_threshold: float = 0.30
    novelty_moderate_threshold: float = 0.55
    novelty_high_threshold: float = 0.75
    novelty_decision_threshold: float = 0.70
    min_valid_feature_count_for_ood: int = 15
    min_temporal_support_for_ood: int = 2


@dataclass
class NoveltyAssessment:
    """Structured assessment of event novelty and out-of-distribution status."""
    event_id: str
    novelty_score: float
    novelty_level: str
    distribution_state: str
    known_class_compatibility: List[Dict[str, Any]]
    component_signals: Dict[str, float]
    novelty_drivers: List[str]
    data_quality_limitations: List[str]
    temporal_limitations: List[str]
    supporting_evidence_ids: List[str]
    decision_recommendation: str
    reason_codes: List[str]
    evidence_items: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "NoveltyAssessment":
        return cls(
            event_id=d["event_id"],
            novelty_score=float(d["novelty_score"]),
            novelty_level=d["novelty_level"],
            distribution_state=d["distribution_state"],
            known_class_compatibility=d["known_class_compatibility"],
            component_signals={k: float(v) for k, v in d["component_signals"].items()},
            novelty_drivers=d["novelty_drivers"],
            data_quality_limitations=d["data_quality_limitations"],
            temporal_limitations=d["temporal_limitations"],
            supporting_evidence_ids=d["supporting_evidence_ids"],
            decision_recommendation=d["decision_recommendation"],
            reason_codes=d["reason_codes"],
            evidence_items=d.get("evidence_items", [])
        )


def _compute_class_space_uncertainty(model_probs: Optional[np.ndarray]) -> float:
    """Calculates class-space entropy / margin uncertainty."""
    if model_probs is None or len(model_probs) <= 1:
        return 0.50
    probs = np.array(model_probs, dtype=float)
    probs = np.clip(probs, 1e-7, 1.0)
    probs = probs / np.sum(probs)

    sorted_p = np.sort(probs)[::-1]
    margin = float(sorted_p[0] - sorted_p[1]) if len(sorted_p) > 1 else 1.0
    entropy = float(-np.sum(probs * np.log2(probs)) / np.log2(len(probs)))

    # Higher uncertainty when top classes are ambiguous or entropy is high
    uncertainty = 0.5 * (1.0 - margin) + 0.5 * entropy
    return float(np.clip(uncertainty, 0.0, 1.0))


def _compute_feature_space_distance(canon: CanonicalEventFeatures, raw_event: Optional[Dict[str, Any]] = None) -> float:
    """
    Computes normalized feature-space distance from known reference distributions.
    Checks for extreme feature combinations (e.g. extreme FRP with high NDVI or non-industrial context).
    """
    raw = raw_event or {}
    frp = float(canon.current_max_frp) if not np.isnan(canon.current_max_frp) else 0.0
    ndvi = float(raw.get("S2_NDVI_online", getattr(canon, "sentinel_ndvi", np.nan)))
    land_ctx = float(canon.land_context)
    ind_flag = float(canon.nearby_industrial_flag)

    dist_components = []

    # FRP vs Context mismatch (e.g. massive FRP in purely rural vegetation with no industrial context)
    if frp > 300.0 and ind_flag == 0 and land_ctx == 0:
        dist_components.append(0.70)
    
    # FRP vs High NDVI mismatch (unusual thermal event in dense healthy canopy)
    if frp > 150.0 and not np.isnan(ndvi) and ndvi > 0.6:
        dist_components.append(0.80)

    # Unusual ratio of max FRP to mean FRP
    if canon.current_mean_frp > 0 and frp / canon.current_mean_frp > 4.0:
        dist_components.append(0.60)

    # Explicit raw ood score if passed from upstream utilities
    if "raw_ood_score" in raw:
        dist_components.append(float(raw["raw_ood_score"]))

    if not dist_components:
        return 0.15
    return float(np.clip(np.mean(dist_components), 0.0, 1.0))


def evaluate_event_novelty(
    canon: CanonicalEventFeatures,
    model_probs: Optional[np.ndarray] = None,
    source_classes: Optional[List[str]] = None,
    low_t_result: Optional[Any] = None,
    high_t_result: Optional[Any] = None,
    abnormality_result: Optional[Any] = None,
    state_assessment: Optional[Any] = None,
    quality_summary: Optional[Any] = None,
    raw_event: Optional[Dict[str, Any]] = None,
    config: Optional[NoveltyConfig] = None,
    insat_corroboration: Optional[Any] = None
) -> NoveltyAssessment:
    """
    Evaluates multi-signal novelty and out-of-distribution (OOD) status.
    """
    if config is None:
        config = NoveltyConfig()

    raw = raw_event or {}
    event_id = str(raw.get("event_id", raw.get("id", "evt_unknown")))

    # 1. Data Quality & Temporal Sparsity Check
    obs_qual = float(getattr(quality_summary, "overall_observation_quality", canon.observation_quality)) if quality_summary else float(canon.observation_quality)
    obs_count = int(canon.observation_count_so_far)

    is_low_quality = obs_qual < 0.40
    is_temporally_sparse = obs_count < config.min_temporal_support_for_ood

    data_quality_limitations = []
    temporal_limitations = []
    reason_codes = []

    if is_low_quality:
        data_quality_limitations.append(f"Low observation quality score ({obs_qual:.2f}) limits OOD assessment precision.")
        reason_codes.append(REASON_LOW_DATA_QUALITY_FOR_OOD)

    if is_temporally_sparse:
        temporal_limitations.append(f"Sparse observation count ({obs_count}) is insufficient to establish archetype novelty.")
        reason_codes.append(REASON_INSUFFICIENT_DATA_FOR_OOD)

    # 2. Compute 6 Component Signals
    feat_dist = _compute_feature_space_distance(canon, raw)
    class_uncert = _compute_class_space_uncertainty(model_probs)
    
    # Evidence Disagreement Signal
    is_conflicting_evidence = raw.get("evidence_conflict", False)
    ev_disagreement = 0.75 if is_conflicting_evidence else 0.10
    if is_conflicting_evidence:
        reason_codes.append(REASON_EVIDENCE_CONFLICT_NOT_NOVEL)

    # Temporal & Behavioral Novelty Signals
    c_state = getattr(state_assessment, "current_state", "UNKNOWN") if state_assessment else "UNKNOWN"
    temporal_nov = 0.60 if c_state == "INTERMITTENT" else 0.15
    behavioral_nov = 0.70 if (getattr(low_t_result, "low_t_state", "") == "LOW_T_PERSISTENT" and getattr(high_t_result, "high_temperature_signal", "") == "STRONG") else 0.20
    context_nov = 0.60 if (canon.nearby_industrial_flag == 0 and canon.land_context == 0 and canon.current_max_frp > 200.0) else 0.10

    component_signals = {
        "feature_space_distance": round(feat_dist, 4),
        "class_space_uncertainty": round(class_uncert, 4),
        "evidence_disagreement": round(ev_disagreement, 4),
        "temporal_novelty": round(temporal_nov, 4),
        "context_novelty": round(context_nov, 4),
        "behavioral_novelty": round(behavioral_nov, 4)
    }

    # 3. Multi-Signal Score Aggregation (Weighted, non-averaged)
    # If data is sparse or quality is low, OOD defaults to UNKNOWN rather than NOVEL
    if is_low_quality or is_temporally_sparse:
        novelty_score = 0.0
        novelty_level = LEVEL_UNKNOWN
        dist_state = DISTRIBUTION_UNKNOWN
        rec = "INSUFFICIENT_DATA" if is_temporally_sparse else "LOW_DATA_QUALITY"
    else:
        weights = {
            "feature_space_distance": 0.35,
            "class_space_uncertainty": 0.15,
            "behavioral_novelty": 0.20,
            "context_novelty": 0.15,
            "temporal_novelty": 0.15
        }
        weighted_score = sum(component_signals[k] * weights[k] for k in weights)
        
        # Explicit override for synthetic/injected OOD flags
        if raw.get("force_novel", False):
            weighted_score = max(weighted_score, 0.85)

        novelty_score = round(float(np.clip(weighted_score, 0.0, 1.0)), 4)

        if novelty_score >= config.novelty_high_threshold:
            novelty_level = LEVEL_NOVEL
            dist_state = DISTRIBUTION_NOVEL
            reason_codes.append(REASON_FEATURE_SPACE_DEVIATION)
            reason_codes.append(REASON_MULTI_SIGNAL_OOD)
        elif novelty_score >= config.novelty_moderate_threshold:
            novelty_level = LEVEL_MODERATE_NOVELTY
            dist_state = DISTRIBUTION_NOVEL
            reason_codes.append(REASON_BEHAVIOR_PATTERN_NOVEL)
        elif novelty_score >= config.novelty_low_threshold:
            novelty_level = LEVEL_LOW_NOVELTY
            dist_state = DISTRIBUTION_KNOWN_LIKE
        else:
            novelty_level = LEVEL_KNOWN_LIKE
            dist_state = DISTRIBUTION_KNOWN_LIKE

        rec = "KNOWN_DECISION_PATH" if dist_state == DISTRIBUTION_KNOWN_LIKE else "NEEDS_VERIFICATION"

    # 4. Model Confidence Paradox Handling (HIGH MODEL CONFIDENCE + HIGH OOD SCORE)
    raw_conf = float(np.max(model_probs)) if model_probs is not None and len(model_probs) > 0 else float(raw.get("raw_model_confidence", 0.0))
    if raw_conf >= 0.75 and novelty_score >= 0.60:
        reason_codes.append(REASON_HIGH_CONFIDENCE_OOD)
        dist_state = DISTRIBUTION_NOVEL
        rec = "NEEDS_VERIFICATION"

    # 5. Known Class Compatibility Ranking
    known_class_compatibility = []
    if model_probs is not None and source_classes is not None and len(model_probs) == len(source_classes):
        for i, cls_name in enumerate(source_classes):
            comp_score = float(model_probs[i]) * (1.0 - 0.5 * novelty_score)
            known_class_compatibility.append({
                "source_class": cls_name,
                "compatibility_score": round(comp_score, 4)
            })
        known_class_compatibility.sort(key=lambda x: x["compatibility_score"], reverse=True)
    else:
        known_class_compatibility = [{"source_class": "UNKNOWN", "compatibility_score": 0.50}]

    # 6. Novelty Drivers
    novelty_drivers = []
    if feat_dist > 0.50:
        novelty_drivers.append("Significant feature-space distance from known training distributions")
    if behavioral_nov > 0.50:
        novelty_drivers.append("Unusual combination of High-T intensity and Low-T persistence behaviors")
    if context_nov > 0.50:
        novelty_drivers.append("High thermal intensity in non-industrial context archetype")
    if REASON_HIGH_CONFIDENCE_OOD in reason_codes:
        novelty_drivers.append("Classifier strongly favors known class, but event pattern is atypical relative to distribution")

    # 7. Form Evidence Items
    evidence_items = []
    if dist_state == DISTRIBUTION_NOVEL:
        evidence_items.append({
            "evidence_family": "OOD_NOVELTY",
            "direction": "SUPPORTING",
            "strength": "STRONG" if novelty_score >= 0.75 else "MODERATE",
            "description": f"Event exhibits out-of-distribution characteristics (Novelty Score: {novelty_score:.2f}, Level: {novelty_level}).",
            "source": "NovelEventDetection"
        })
    elif dist_state == DISTRIBUTION_KNOWN_LIKE:
        evidence_items.append({
            "evidence_family": "OOD_NOVELTY",
            "direction": "NEUTRAL",
            "strength": "WEAK",
            "description": f"Event pattern is consistent with known training distributions (Novelty Score: {novelty_score:.2f}).",
            "source": "NovelEventDetection"
        })
    else:
        evidence_items.append({
            "evidence_family": "OOD_NOVELTY",
            "direction": "MISSING",
            "strength": "WEAK",
            "description": "Novelty could not be assessed reliably due to data quality or sparse observations.",
            "source": "NovelEventDetection"
        })

    return NoveltyAssessment(
        event_id=event_id,
        novelty_score=novelty_score,
        novelty_level=novelty_level,
        distribution_state=dist_state,
        known_class_compatibility=known_class_compatibility,
        component_signals=component_signals,
        novelty_drivers=novelty_drivers,
        data_quality_limitations=data_quality_limitations,
        temporal_limitations=temporal_limitations,
        supporting_evidence_ids=[f"ev_ood_{event_id}"],
        decision_recommendation=rec,
        reason_codes=sorted(list(set(reason_codes))),
        evidence_items=evidence_items
    )
