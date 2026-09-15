import uuid
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from src.features.canonical_event_features import CanonicalEventFeatures
from src.features.low_t_persistent_heat import LowTResult
from src.intelligence.historical_abnormality import AbnormalityResult

EVIDENCE_FAMILIES = [
    "THERMAL", "TEMPORAL", "SPATIAL", "CONTEXT", "HISTORICAL",
    "BEHAVIOR", "ANOMALY", "SENTINEL", "SAR", "WEATHER",
    "FACILITY", "DATA_QUALITY", "MODEL", "VERIFICATION"
]

@dataclass
class EvidenceItem:
    evidence_id: str
    evidence_type: str
    evidence_family: str
    source: str
    status: str # OBSERVED, DERIVED, UNAVAILABLE, NOT_APPLICABLE
    direction: str # SUPPORTING, CONFLICTING, MISSING, NEUTRAL
    strength: str # VERY_WEAK, WEAK, MODERATE, STRONG, VERY_STRONG
    description: str
    value: Any = None
    unit: Optional[str] = None
    observation_time: Optional[str] = None
    availability: bool = True
    provenance: str = ""

@dataclass
class HypothesisSupport:
    hypothesis: str
    supporting_evidence: List[EvidenceItem] = field(default_factory=list)
    conflicting_evidence: List[EvidenceItem] = field(default_factory=list)
    missing_evidence: List[EvidenceItem] = field(default_factory=list)
    model_score: Optional[float] = None
    evidence_completeness: float = 0.0
    evidence_convergence: str = "UNKNOWN"

@dataclass
class EventEvidenceLedger:
    event_id: str
    evidence_items: List[EvidenceItem]
    hypothesis_support_matrix: Dict[str, HypothesisSupport]
    global_evidence_completeness: float
    data_quality_score: float
    
    # Hooks for downstream pipelines
    why_supporting: List[str] = field(default_factory=list)
    why_conflicting: List[str] = field(default_factory=list)
    why_missing: List[str] = field(default_factory=list)
    what_changed: List[str] = field(default_factory=list)

def _create_evidence_item(family: str, status: str, direction: str, strength: str, desc: str, source: str = "Agni-Netra Pipeline") -> EvidenceItem:
    return EvidenceItem(
        evidence_id=str(uuid.uuid4()),
        evidence_type="system_extracted",
        evidence_family=family,
        source=source,
        status=status,
        direction=direction,
        strength=strength,
        description=desc,
        availability=(status in ["OBSERVED", "DERIVED"])
    )

def aggregate_event_evidence(
    event_id: str,
    canon: CanonicalEventFeatures,
    low_t_result: Optional[LowTResult] = None,
    abnormality_result: Optional[AbnormalityResult] = None,
    model_probs: Optional[np.ndarray] = None,
    source_classes: Optional[List[str]] = None,
    insat_corroboration: Optional[Any] = None,
    high_t_result: Optional[Any] = None,
    state_assessment: Optional[Any] = None,
    novelty_assessment: Optional[Any] = None
) -> EventEvidenceLedger:
    
    ledger_items = []

    # 0A. OOD Novelty Evidence
    if novelty_assessment is not None:
        d_state = getattr(novelty_assessment, "distribution_state", "UNKNOWN")
        n_score = getattr(novelty_assessment, "novelty_score", 0.0)
        n_level = getattr(novelty_assessment, "novelty_level", "UNKNOWN")
        if d_state == "NOVEL":
            ledger_items.append(_create_evidence_item(
                "OOD_NOVELTY", "OBSERVED", "SUPPORTING",
                "STRONG" if n_score >= 0.75 else "MODERATE",
                f"Event exhibits out-of-distribution characteristics (Novelty Score: {n_score:.2f}, Level: {n_level}).",
                source="NovelEventDetection"
            ))
        elif d_state == "KNOWN_LIKE":
            ledger_items.append(_create_evidence_item(
                "OOD_NOVELTY", "OBSERVED", "NEUTRAL", "WEAK",
                f"Event pattern is consistent with known training distributions (Novelty Score: {n_score:.2f}).",
                source="NovelEventDetection"
            ))
        else:
            ledger_items.append(_create_evidence_item(
                "OOD_NOVELTY", "UNAVAILABLE", "MISSING", "WEAK",
                "MISSING: Novelty could not be assessed reliably due to data quality or sparse observations.",
                source="NovelEventDetection"
            ))

    # 0B. Event State Machine / Behavioral State Evidence
    if state_assessment is not None:
        c_state = getattr(state_assessment, "current_state", "UNKNOWN")
        c_conf = getattr(state_assessment, "current_state_confidence", 0.5)
        l_trans = getattr(state_assessment, "last_transition", "")
        if c_state in ["PERSISTING", "STABLE", "ESCALATING", "ABNORMAL", "REACTIVATED"]:
            ledger_items.append(_create_evidence_item(
                "BEHAVIOR_STATE", "OBSERVED", "SUPPORTING",
                "STRONG" if c_conf >= 0.80 else "MODERATE",
                f"Event state evaluates to {c_state} ({l_trans}).",
                source="EventStateMachine"
            ))
        elif c_state == "INTERMITTENT":
            ledger_items.append(_create_evidence_item(
                "BEHAVIOR_STATE", "OBSERVED", "CONFLICTING", "MODERATE",
                f"Event exhibits intermittent temporal activity ({l_trans}).",
                source="EventStateMachine"
            ))
        else:
            ledger_items.append(_create_evidence_item(
                "BEHAVIOR_STATE", "OBSERVED", "NEUTRAL", "WEAK",
                f"Event state evaluates to {c_state} ({l_trans}).",
                source="EventStateMachine"
            ))
    
    # 0A. High-T Thermal Physics Evidence
    if high_t_result is not None and getattr(high_t_result, "available", False):
        sig = getattr(high_t_result, "high_temperature_signal", "UNKNOWN")
        phys_mode = getattr(high_t_result, "physics_mode", "REDUCED_THERMAL_PHYSICS_MODE")
        frp_max = getattr(high_t_result, "frp_summary", {}).get("max", 0.0)
        
        if sig in ["STRONG", "MODERATE"]:
            ledger_items.append(_create_evidence_item(
                "THERMAL_PHYSICS", "OBSERVED", "SUPPORTING",
                "STRONG" if sig == "STRONG" else "MODERATE",
                f"Thermal physics exhibit {sig.lower()} high-temperature signal ({phys_mode}, FRP max: {frp_max} MW).",
                source="HighTThermalPhysics"
            ))
        elif sig == "WEAK":
            ledger_items.append(_create_evidence_item(
                "THERMAL_PHYSICS", "OBSERVED", "NEUTRAL", "WEAK",
                f"Thermal physics exhibit low-intensity characteristics ({phys_mode}).",
                source="HighTThermalPhysics"
            ))
        
        rel = getattr(high_t_result, "thermal_measurement_reliability", 1.0)
        if rel < 1.0:
            ledger_items.append(_create_evidence_item(
                "THERMAL_PHYSICS", "DERIVED", "CONFLICTING", "MODERATE",
                f"Possible sensor saturation reduces thermal measurement reliability ({rel:.2f}).",
                source="HighTThermalPhysics"
            ))
    else:
        ledger_items.append(_create_evidence_item(
            "THERMAL_PHYSICS", "UNAVAILABLE", "MISSING", "WEAK",
            "MISSING: High-temperature thermal physics evidence unavailable.", source="HighTThermalPhysics"
        ))

    # 0B. INSAT-3DS High-Cadence GEO Thermal Evidence
    if insat_corroboration is not None:
        c_state = getattr(insat_corroboration, 'corroboration_state', 'NOT_AVAILABLE')
        summary_text = getattr(insat_corroboration, 'summary', 'INSAT-3DS evidence unavailable.')
        if c_state in ["CORROBORATING", "PARTIALLY_CORROBORATING"]:
            ledger_items.append(_create_evidence_item(
                "GEO_THERMAL", "OBSERVED", "SUPPORTING", "MODERATE",
                summary_text, source="INSAT-3DS"
            ))
        elif c_state == "CONFLICTING":
            ledger_items.append(_create_evidence_item(
                "GEO_THERMAL", "OBSERVED", "CONFLICTING", "MODERATE",
                summary_text, source="INSAT-3DS"
            ))
        else:
            ledger_items.append(_create_evidence_item(
                "GEO_THERMAL", "UNAVAILABLE", "MISSING", "WEAK",
                "MISSING: INSAT-3DS GEO thermal evidence is unavailable for period.", source="INSAT-3DS"
            ))
    else:
        ledger_items.append(_create_evidence_item(
            "GEO_THERMAL", "UNAVAILABLE", "MISSING", "WEAK",
            "MISSING: INSAT-3DS GEO thermal evidence is unavailable for period.", source="INSAT-3DS"
        ))
    
    # 1. Thermal & Temporal
    if canon.current_mean_frp > 0:
        ledger_items.append(_create_evidence_item(
            "THERMAL", "OBSERVED", "SUPPORTING", "MODERATE",
            f"Thermal detection with mean FRP {canon.current_mean_frp:.1f}"
        ))
        
    if canon.observation_count_so_far >= 3:
        ledger_items.append(_create_evidence_item(
            "TEMPORAL", "OBSERVED", "SUPPORTING", "MODERATE",
            f"Repeated detections observed ({canon.observation_count_so_far} times)."
        ))
        
    # 2. Sentinel Evidence
    if canon.sentinel_available == 1:
        ledger_items.append(_create_evidence_item(
            "SENTINEL", "OBSERVED", "SUPPORTING", "STRONG",
            "Sentinel optical confirmation present."
        ))
    else:
        ledger_items.append(_create_evidence_item(
            "SENTINEL", "UNAVAILABLE", "MISSING", "MODERATE",
            "MISSING: Sentinel optical confirmation."
        ))

    # 3. Context & Facility
    if canon.missing_context_indicator == 0:
        if canon.nearby_industrial_flag == 1 or canon.land_context == 1:
            ledger_items.append(_create_evidence_item(
                "CONTEXT", "OBSERVED", "SUPPORTING", "MODERATE",
                "Industrial facility context is present nearby."
            ))
            ledger_items.append(_create_evidence_item(
                "FACILITY", "OBSERVED", "SUPPORTING", "MODERATE",
                "Facility detected in vicinity."
            ))
        else:
            ledger_items.append(_create_evidence_item(
                "CONTEXT", "OBSERVED", "CONFLICTING", "WEAK",
                "Forest/Vegetation context provides competing interpretation."
            ))
    else:
        ledger_items.append(_create_evidence_item(
            "CONTEXT", "UNAVAILABLE", "MISSING", "WEAK",
            "MISSING: Facility/Context operating state."
        ))

    # 4. Low-T Lane
    if low_t_result:
        if low_t_result.low_t_state == "LOW_T_PERSISTENT":
            ledger_items.append(_create_evidence_item(
                "BEHAVIOR", "DERIVED", "SUPPORTING", "STRONG",
                "Persistent moderate-intensity thermal activity detected."
            ))
        elif low_t_result.low_t_state == "LOW_T_INSUFFICIENT_EVIDENCE":
            ledger_items.append(_create_evidence_item(
                "BEHAVIOR", "UNAVAILABLE", "MISSING", "MODERATE",
                "MISSING: Insufficient data to determine persistence behavior."
            ))

    # 5. Historical Abnormality Lane
    if abnormality_result:
        if abnormality_result.abnormality_state in ["UNUSUAL", "HIGHLY_ABNORMAL"]:
            ledger_items.append(_create_evidence_item(
                "ANOMALY", "DERIVED", "SUPPORTING", "STRONG",
                f"Current activity is {abnormality_result.abnormality_state.lower().replace('_', ' ')} relative to history."
            ))
        elif abnormality_result.abnormality_state == "NORMAL":
            ledger_items.append(_create_evidence_item(
                "ANOMALY", "DERIVED", "CONFLICTING", "STRONG",
                "Current activity remains within historical baseline limits."
            ))
        elif abnormality_result.abnormality_state == "UNKNOWN":
            ledger_items.append(_create_evidence_item(
                "HISTORICAL", "UNAVAILABLE", "MISSING", "STRONG",
                "MISSING: Sufficient historical baseline for abnormality detection."
            ))

    # 6. Model Probabilities
    # Model derived goes to model family explicitly
    if model_probs is not None and source_classes is not None:
        best_idx = np.argmax(model_probs)
        best_class = source_classes[best_idx]
        best_score = float(model_probs[best_idx])
        ledger_items.append(_create_evidence_item(
            "MODEL", "DERIVED", "NEUTRAL", "MODERATE",
            f"MODEL-DERIVED: {best_class} score = {best_score:.2f}"
        ))

    # 7. Data Quality
    dq_score = canon.observation_quality
    if dq_score < 0.5:
        ledger_items.append(_create_evidence_item(
            "DATA_QUALITY", "OBSERVED", "CONFLICTING", "STRONG",
            "Poor observation quality reduces overall evidence reliability."
        ))

    # Aggregate families & calculate completeness
    global_completeness = calculate_evidence_completeness(ledger_items)

    # Build Hypothesis Matrix
    matrix = {}
    if source_classes:
        for idx, cls in enumerate(source_classes):
            support = build_hypothesis_evidence(cls, ledger_items, global_completeness, float(model_probs[idx]) if model_probs is not None else None)
            matrix[cls] = support

    # Hooks for explanation
    why_supp = [e.description for e in ledger_items if e.direction == "SUPPORTING"]
    why_conf = [e.description for e in ledger_items if e.direction == "CONFLICTING"]
    why_miss = [e.description for e in ledger_items if e.direction == "MISSING"]
    what_changed = []
    if abnormality_result and abnormality_result.change_indicators.frp_spike:
        what_changed.append("Sudden FRP spike.")
    if abnormality_result and abnormality_result.change_indicators.footprint_expansion:
        what_changed.append("Footprint expanded rapidly.")

    return EventEvidenceLedger(
        event_id=event_id,
        evidence_items=ledger_items,
        hypothesis_support_matrix=matrix,
        global_evidence_completeness=global_completeness,
        data_quality_score=dq_score,
        why_supporting=why_supp,
        why_conflicting=why_conf,
        why_missing=why_miss,
        what_changed=what_changed
    )

def calculate_evidence_completeness(items: List[EvidenceItem]) -> float:
    # Expected families to have non-missing status
    expected_families = {"THERMAL", "TEMPORAL", "SPATIAL", "CONTEXT", "HISTORICAL", "SENTINEL"}
    present_families = set([i.evidence_family for i in items if i.direction != "MISSING"])
    if not expected_families: return 1.0
    return len(present_families.intersection(expected_families)) / len(expected_families)

def calculate_evidence_convergence(items: List[EvidenceItem]) -> str:
    # How many independent evidence families agree with the same interpretation
    # We measure this by the number of independent families that are SUPPORTING without CONFLICTING
    supporting_families = set([i.evidence_family for i in items if i.direction == "SUPPORTING"])
    conflicting_families = set([i.evidence_family for i in items if i.direction == "CONFLICTING"])
    
    net_supporting = supporting_families - conflicting_families
    
    if len(net_supporting) >= 4 and len(conflicting_families) == 0:
        return "HIGH"
    elif len(net_supporting) >= 2 and len(conflicting_families) <= 1:
        return "MODERATE"
    elif len(conflicting_families) >= 2:
        return "CONFLICTING"
    else:
        return "LOW"

def build_hypothesis_evidence(hypothesis: str, items: List[EvidenceItem], completeness: float, model_score: Optional[float]) -> HypothesisSupport:
    # In reality, this would map specific evidence items to specific hypotheses.
    # For now, we group based on generalized rules for the MVP.
    
    supp = []
    conf = []
    miss = []
    
    for i in items:
        if i.direction == "MISSING":
            miss.append(i)
        elif i.direction == "SUPPORTING":
            # Just as an MVP example, context supports Industrial if hypothesis is Industrial.
            if hypothesis in ["INDUSTRIAL_FIRE", "ROUTINE_FLARE"] and i.evidence_family in ["CONTEXT", "FACILITY"]:
                supp.append(i)
            elif hypothesis == "WILDFIRE" and i.evidence_family in ["CONTEXT", "FACILITY"] and "Forest" in i.description:
                supp.append(i)
            else:
                supp.append(i)
        elif i.direction == "CONFLICTING":
            conf.append(i)
            
    # Modify convergence per hypothesis
    convergence = calculate_evidence_convergence(supp + conf)
    
    return HypothesisSupport(
        hypothesis=hypothesis,
        supporting_evidence=supp,
        conflicting_evidence=conf,
        missing_evidence=miss,
        model_score=model_score,
        evidence_completeness=completeness,
        evidence_convergence=convergence
    )
