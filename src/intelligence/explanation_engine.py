"""
Agni-Netra WHY / WHY NOT / WHAT CHANGED Explanation Engine (Phase 17G)

Production explanation layer that converts outputs from:
- Canonical features
- Low-T persistent heat intelligence
- Historical abnormality & change intelligence
- Evidence aggregation + Event Evidence Ledger
- Confidence / Calibration / UNKNOWN decision engine
- Risk / Priority intelligence engine

into an auditable, evidence-grounded structured explanation.

Answers:
1. WHY?
2. WHY NOT?
3. WHAT CHANGED?
4. UNKNOWN / LIMITATIONS?
5. WHAT SHOULD HAPPEN NEXT?

Controlled Language Rule:
Never invent evidence. Never say "confirmed fire" or "certainly safe".
Use calibrated phrasing ("classified as", "evidence supports", "verification recommended").
"""

import numpy as np
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple

from src.features.canonical_event_features import CanonicalEventFeatures
from src.features.low_t_persistent_heat import LowTResult
from src.intelligence.historical_abnormality import AbnormalityResult
from src.intelligence.evidence_aggregation import EventEvidenceLedger, EvidenceItem
from src.intelligence.confidence_decision import (
    DecisionAssessment, ConfidenceAssessment,
    DECISION_KNOWN, DECISION_UNKNOWN, DECISION_NEEDS_VERIFICATION,
    DECISION_INSUFFICIENT_OBSERVATION
)
from src.intelligence.risk_priority import RiskPriorityAssessment


@dataclass
class EventExplanation:
    event_id: str
    summary: str
    classification: Dict[str, Any]
    why: Dict[str, Any]
    why_not: Dict[str, Any]
    what_changed: Dict[str, Any]
    uncertainty: Dict[str, Any]
    risk_priority: Dict[str, Any]
    next_action: Dict[str, Any]
    provenance: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EventExplanation":
        return cls(
            event_id=d["event_id"],
            summary=d["summary"],
            classification=d["classification"],
            why=d["why"],
            why_not=d["why_not"],
            what_changed=d["what_changed"],
            uncertainty=d["uncertainty"],
            risk_priority=d["risk_priority"],
            next_action=d["next_action"],
            provenance=d["provenance"]
        )


def _build_why_section(
    decision_assessment: DecisionAssessment,
    evidence_ledger: EventEvidenceLedger,
    low_t_result: Optional[LowTResult] = None
) -> Tuple[str, List[str], List[str]]:
    """
    Builds the WHY section using independent evidence family signals.
    Returns: (headline, supporting_families, supporting_reasons)
    """
    predicted_class = decision_assessment.predicted_source_class
    conf_level = decision_assessment.confidence.confidence_level

    supporting_items = [e for e in evidence_ledger.evidence_items if e.direction == "SUPPORTING"]
    supporting_families = sorted(list(set(e.evidence_family for e in supporting_items)))

    supporting_reasons = []

    # 1. Thermal & Temporal
    thermal_items = [e for e in supporting_items if e.evidence_family == "THERMAL"]
    if thermal_items:
        supporting_reasons.append("Thermal intensity is elevated above detection baseline")

    temp_items = [e for e in supporting_items if e.evidence_family == "TEMPORAL"]
    if temp_items:
        supporting_reasons.append("Event exhibits repeated detections and temporal persistence")

    # 2. GEO Thermal (INSAT-3DS High-Cadence)
    geo_items = [e for e in supporting_items if e.evidence_family == "GEO_THERMAL"]
    if geo_items:
        for gi in geo_items:
            supporting_reasons.append(gi.description)

    # 3. Sentinel Optical / SAR
    sentinel_items = [e for e in supporting_items if e.evidence_family == "SENTINEL"]
    if sentinel_items:
        supporting_reasons.append("Sentinel optical imagery corroboration is present")

    # 4. Facility Context (Controlled phrasing)
    facility_items = [e for e in supporting_items if e.evidence_family in ["CONTEXT", "FACILITY"]]
    if facility_items:
        supporting_reasons.append("Nearby industrial facility context supports an anthropogenic heat interpretation")

    # 5. Low-T Persistent Heat (Controlled phrasing)
    if low_t_result is not None and low_t_result.low_t_state == "LOW_T_PERSISTENT":
        supporting_reasons.append("Persistent moderate-intensity thermal behavior supports sustained thermal activity")

    # 5. Historical Abnormality
    anomaly_items = [e for e in supporting_items if e.evidence_family == "ANOMALY"]
    if anomaly_items:
        supporting_reasons.append("Current thermal pattern deviates significantly from normal historical baseline")

    # 6. Model Output (Explicitly labeled as model-derived)
    raw_conf_str = decision_assessment.calibration.get("raw_model_confidence", "0.0")
    supporting_reasons.append(f"Model-derived probability score ({float(raw_conf_str):.2f}) favors {predicted_class}")

    headline = f"Event is classified as {predicted_class} with {conf_level} decision confidence supported by {', '.join(supporting_families) if supporting_families else 'model'} evidence."

    return headline, supporting_families, supporting_reasons


def _build_why_not_section(
    decision_assessment: DecisionAssessment,
    evidence_ledger: EventEvidenceLedger
) -> Tuple[List[str], List[str], List[str]]:
    """
    Builds the WHY NOT section explaining competing hypotheses, conflicts, and limitations.
    Returns: (competing_hypotheses, conflicting_families, limiting_reasons)
    """
    conflicting_items = [e for e in evidence_ledger.evidence_items if e.direction == "CONFLICTING"]
    conflicting_families = sorted(list(set(e.evidence_family for e in conflicting_items)))

    missing_items = [e for e in evidence_ledger.evidence_items if e.direction == "MISSING"]

    competing_hypotheses = []
    for cls, hyp_supp in evidence_ledger.hypothesis_support_matrix.items():
        if cls != decision_assessment.predicted_source_class and hyp_supp.model_score is not None and hyp_supp.model_score > 0.15:
            competing_hypotheses.append(f"{cls} (competing model score = {hyp_supp.model_score:.2f})")

    limiting_reasons = []

    if conflicting_items:
        for item in conflicting_items:
            limiting_reasons.append(f"Conflicting evidence: {item.description}")

    if missing_items:
        for item in missing_items:
            limiting_reasons.append(f"Missing evidence: {item.description}")

    if decision_assessment.confidence.evidence_completeness < 0.5:
        limiting_reasons.append(f"Low overall evidence completeness ({decision_assessment.confidence.evidence_completeness:.2f})")

    if decision_assessment.confidence.contradiction_penalty > 0.2:
        limiting_reasons.append(f"Evidence contradiction penalty ({decision_assessment.confidence.contradiction_penalty:.2f}) detected across families")

    return competing_hypotheses, conflicting_families, limiting_reasons


def _build_what_changed_section(
    abnormality_result: Optional[AbnormalityResult],
    canon: Optional[CanonicalEventFeatures]
) -> Tuple[bool, List[str], str]:
    """
    Builds WHAT CHANGED section using historical abnormality and change indicators.
    Returns: (change_detected, change_reasons, historical_comparison)
    """
    if abnormality_result is None or abnormality_result.abnormality_state == "UNKNOWN":
        return (
            False,
            ["Historical baseline is insufficient to establish change or abnormality."],
            "Historical baseline unavailable or insufficient."
        )

    change_reasons = []

    if abnormality_result.change_indicators.frp_spike == 1:
        change_reasons.append("Sudden FRP thermal intensity spike detected")

    if abnormality_result.change_indicators.footprint_expansion == 1:
        change_reasons.append("Spatial footprint expanded rapidly relative to historical observations")

    if abnormality_result.change_indicators.activity_shift == 1:
        change_reasons.append("Sharp shift in recent detection activity frequency")

    if abnormality_result.change_indicators.regime_change == 1:
        change_reasons.append("Significant regime transition in thermal anomaly behavior")

    if abnormality_result.abnormality_state in ["UNUSUAL", "HIGHLY_ABNORMAL"]:
        hist_comp = f"Current thermal behavior is {abnormality_result.abnormality_state.lower().replace('_', ' ')} relative to historical baseline (Abnormality Score = {abnormality_result.abnormality_score:.2f})."
        if not change_reasons:
            change_reasons.append(f"Thermal intensity deviates from historical mean")
        return True, change_reasons, hist_comp
    else:
        return (
            False,
            ["Current thermal activity remains within expected historical baseline limits."],
            "Normal historical baseline activity."
        )


def generate_explanation(
    event_id: str,
    decision_assessment: DecisionAssessment,
    risk_priority_assessment: RiskPriorityAssessment,
    evidence_ledger: EventEvidenceLedger,
    canon: Optional[CanonicalEventFeatures] = None,
    low_t_result: Optional[LowTResult] = None,
    abnormality_result: Optional[AbnormalityResult] = None
) -> EventExplanation:
    """
    Generates a structured, evidence-grounded explanation for an analyzed thermal event.
    """
    predicted_class = decision_assessment.predicted_source_class
    decision_state = decision_assessment.decision_state

    # 1. WHY Section
    why_headline, supporting_families, supporting_reasons = _build_why_section(
        decision_assessment=decision_assessment,
        evidence_ledger=evidence_ledger,
        low_t_result=low_t_result
    )

    # 2. WHY NOT Section
    competing_hypotheses, conflicting_families, limiting_reasons = _build_why_not_section(
        decision_assessment=decision_assessment,
        evidence_ledger=evidence_ledger
    )

    # 3. WHAT CHANGED Section
    change_detected, change_reasons, historical_comparison = _build_what_changed_section(
        abnormality_result=abnormality_result,
        canon=canon
    )

    # 4. UNCERTAINTY / LIMITATIONS Section
    uncertainty_reasons = decision_assessment.abstention.get("abstention_reason_codes", [])
    missing_info = [
        item.description for item in evidence_ledger.evidence_items if item.direction == "MISSING"
    ]

    # 5. RISK & PRIORITY Section
    rp_risk = risk_priority_assessment.risk
    rp_priority = risk_priority_assessment.priority
    rp_drivers = risk_priority_assessment.drivers

    # 6. NEXT ACTION Section
    verification_req = (decision_state in [DECISION_NEEDS_VERIFICATION, DECISION_UNKNOWN, DECISION_INSUFFICIENT_OBSERVATION])
    next_action = {
        "recommendation": rp_priority["operational_action"],
        "verification_required": verification_req
    }

    # 7. PROVENANCE Section
    evidence_source_ids = [e.evidence_id for e in evidence_ledger.evidence_items]
    evidence_family_ids = sorted(list(set(e.evidence_family for e in evidence_ledger.evidence_items)))
    reason_codes = sorted(list(set(uncertainty_reasons + rp_drivers.get("priority_drivers", []))))

    provenance = {
        "evidence_source_ids": evidence_source_ids,
        "evidence_family_ids": evidence_family_ids,
        "reason_codes": reason_codes
    }

    # 8. HUMAN-READABLE OPERATOR SUMMARY TEMPLATE
    summary_lines = [
        f"Event {event_id} is classified as {predicted_class} with {decision_assessment.confidence.confidence_level} decision confidence ({decision_state}).",
        "",
        "Why:",
        "\n".join(f"- {r}" for r in supporting_reasons) if supporting_reasons else "- Model prediction baseline",
        "",
        "Why not:",
        "\n".join(f"- {r}" for r in limiting_reasons) if limiting_reasons else "- No major evidence conflicts observed",
        "",
        "What changed:",
        f"- {historical_comparison}",
        "\n".join(f"  * {r}" for r in change_reasons) if change_reasons else "",
        "",
        "Risk & Priority:",
        f"- Physical Risk Level: {rp_risk['risk_level']} (Base Score: {rp_risk['base_risk_score']:.2f}, Risk Confidence: {rp_risk['risk_confidence']:.2f})",
        f"- Priority Level: {rp_priority['priority_level']} (Urgency: {rp_priority['urgency']})",
        "",
        "Action:",
        f"- Recommended Action: {rp_priority['operational_action']}",
        f"- Verification Required: {'YES' if verification_req else 'NO'}",
        "",
        "Uncertainty & Limitations:",
        f"- Evidence Completeness: {decision_assessment.confidence.evidence_completeness:.2f}",
        f"- Decision State: {decision_state}"
    ]
    summary_text = "\n".join(summary_lines)

    return EventExplanation(
        event_id=event_id,
        summary=summary_text,
        classification={
            "predicted_source_class": predicted_class,
            "decision_state": decision_state
        },
        why={
            "headline": why_headline,
            "supporting_families": supporting_families,
            "supporting_reasons": supporting_reasons
        },
        why_not={
            "competing_hypotheses": competing_hypotheses,
            "conflicting_families": conflicting_families,
            "limiting_reasons": limiting_reasons
        },
        what_changed={
            "change_detected": change_detected,
            "change_reasons": change_reasons,
            "historical_comparison": historical_comparison
        },
        uncertainty={
            "confidence_level": decision_assessment.confidence.confidence_level,
            "evidence_completeness": decision_assessment.confidence.evidence_completeness,
            "evidence_convergence": decision_assessment.confidence.evidence_convergence,
            "uncertainty_reasons": uncertainty_reasons,
            "missing_information": missing_info
        },
        risk_priority={
            "risk_level": rp_risk["risk_level"],
            "risk_confidence": rp_risk["risk_confidence"],
            "priority_level": rp_priority["priority_level"],
            "urgency": rp_priority["urgency"],
            "operational_action": rp_priority["operational_action"],
            "priority_drivers": rp_drivers.get("priority_drivers", [])
        },
        next_action=next_action,
        provenance=provenance
    )
