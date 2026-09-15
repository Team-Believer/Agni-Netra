"""
Agni-Netra Real-Data AI Behavioral Demonstration Scenarios (Phase 20H)

Creates a deterministic, REAL-DATA demonstration suite showing how the complete
Agni-Netra AI/ML intelligence stack (analyze_event()) differentiates behavioral scenarios
on real FIRMS/VIIRS thermal observations.

Core Principles:
1. REAL OBSERVATION != REAL GROUND TRUTH
2. SCENARIO LABEL != SOURCE CLASS (Scenario label describes observed system behavior)
3. Deterministic selection with fitness scoring & tie-breaking by (fitness, event_id)
4. Explicit handling of unavailable scenarios (available = False, NO_REAL_EVENT_MEETS_SCENARIO_CRITERIA)
5. Strict adherence to AI Output Contract AGN-EVENT-INTELLIGENCE-1.0
"""

import os
import json
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple

from src.intelligence.analyze_event import analyze_event, EventIntelligenceResult
from src.intelligence.output_contract import build_canonical_contract, SCHEMA_VERSION, PIPELINE_VERSION
from src.intelligence.real_event_replay import load_real_event_fixtures, RealEventFixture


# ==============================================================================
# 1. SCENARIO RECORD DATACLASS
# ==============================================================================

@dataclass
class AgninetraDemoScenario:
    scenario_id: str
    scenario_name: str
    description: str
    available: bool
    unavailable_reason: Optional[str]
    real_event_id: str
    observation_ids: List[str]
    observation_count: int
    event_time: Dict[str, str]
    location: Dict[str, float]
    ai_result: Dict[str, Any]
    evidence_summary: Dict[str, Any]
    behavior_summary: str
    why: Dict[str, Any]
    why_not: Dict[str, Any]
    what_changed: Dict[str, Any]
    uncertainty: Dict[str, Any]
    verification_state: str
    limitations: List[str]
    provenance: Dict[str, Any]
    ground_truth_status: str = "NOT_ESTABLISHED"
    observation_type: str = "REAL_OBSERVATION"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ==============================================================================
# 2. SCENARIO FITNESS EVALUATORS
# ==============================================================================

def score_persistent_fitness(fixture: RealEventFixture, result: EventIntelligenceResult) -> float:
    """Scores fitness for Scenario 1: Persistent / Routine Thermal Source."""
    res_dict = result.to_dict()
    beh = res_dict.get("behavior_assessment", {})
    obs_cnt = fixture.observation_count
    state = beh.get("event_state", "UNKNOWN")
    low_t_state = beh.get("low_t_state", "")

    if obs_cnt < 2:
        return 0.0

    score = 0.0
    if state == "PERSISTING":
        score += 50.0
    elif state == "STABLE":
        score += 30.0

    if low_t_state == "LOW_T_PERSISTENT":
        score += 30.0

    score += min(20.0, obs_cnt * 1.5)
    return score


def score_escalating_fitness(fixture: RealEventFixture, result: EventIntelligenceResult) -> float:
    """Scores fitness for Scenario 2: Escalating / Abnormal Event."""
    res_dict = result.to_dict()
    beh = res_dict.get("behavior_assessment", {})
    abn = res_dict.get("abnormality_assessment", {})
    state = beh.get("event_state", "UNKNOWN")
    abn_level = abn.get("abnormality_level", "NORMAL")

    score = 0.0
    if state in ["ESCALATING", "ABNORMAL"]:
        score += 50.0

    if abn_level in ["UNUSUAL", "HIGHLY_ABNORMAL"] or abn.get("change_detected", False):
        score += 30.0

    if fixture.max_frp > 15.0:
        score += 20.0

    return score


def score_sparse_fitness(fixture: RealEventFixture, result: EventIntelligenceResult) -> float:
    """Scores fitness for Scenario 3: Sparse / Insufficient Observation."""
    res_dict = result.to_dict()
    src = res_dict.get("source_assessment", {})
    obs_cnt = fixture.observation_count
    dec_state = src.get("decision_state", "UNKNOWN")

    if obs_cnt > 2:
        return 0.0

    score = 0.0
    if obs_cnt == 1:
        score += 50.0
    if dec_state == "INSUFFICIENT_OBSERVATION":
        score += 40.0
    elif dec_state == "UNKNOWN":
        score += 20.0

    return score


def score_conflicting_fitness(fixture: RealEventFixture, result: EventIntelligenceResult) -> float:
    """Scores fitness for Scenario 4: Conflicting Evidence Event."""
    res_dict = result.to_dict()
    ev = res_dict.get("evidence_assessment", {})
    items = ev.get("evidence_items", [])

    conflicting_items = [i for i in items if i.get("direction") == "CONFLICTING"]
    if len(conflicting_items) == 0:
        return 0.0

    return 50.0 + len(conflicting_items) * 10.0


def score_novelty_fitness(fixture: RealEventFixture, result: EventIntelligenceResult) -> float:
    """Scores fitness for Scenario 5: Novel / OOD-like Event."""
    res_dict = result.to_dict()
    src = res_dict.get("source_assessment", {})
    dist_state = src.get("distribution_state", "KNOWN_LIKE")
    nov_score = src.get("novelty_score", 0.0)

    score = 0.0
    if dist_state == "NOVEL":
        score += 60.0
    elif dist_state == "UNKNOWN":
        score += 20.0

    score += nov_score * 40.0
    return score


def score_priority_fitness(fixture: RealEventFixture, result: EventIntelligenceResult) -> float:
    """Scores fitness for Scenario 6: High-Priority Event."""
    res_dict = result.to_dict()
    prio = res_dict.get("priority_assessment", {})
    risk = res_dict.get("risk_assessment", {})
    prio_lvl = prio.get("priority_level", "P4")

    score = 0.0
    if prio_lvl in ["P0", "P1", "P0_CRITICAL", "P1_URGENT"]:
        score += 60.0
    elif prio_lvl in ["P2", "P2_EVALUATE"]:
        score += 30.0

    score += prio.get("priority_score", 0.0) * 40.0
    return score


# ==============================================================================
# 3. DEMO SCENARIO SELECTOR & PACKAGE BUILDER
# ==============================================================================

def build_scenario_record(
    scenario_id: str,
    scenario_name: str,
    description: str,
    fixture: Optional[RealEventFixture],
    result: Optional[EventIntelligenceResult],
    unavailable_reason: Optional[str] = None
) -> AgninetraDemoScenario:
    """
    Builds a structured AgninetraDemoScenario from an event fixture and analyze_event() result.
    If fixture or result is None, builds an explicit unavailable scenario record.
    """
    if fixture is None or result is None:
        return AgninetraDemoScenario(
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            description=description,
            available=False,
            unavailable_reason=unavailable_reason or "NO_REAL_EVENT_MEETS_SCENARIO_CRITERIA",
            real_event_id="NONE",
            observation_ids=[],
            observation_count=0,
            event_time={"first_observation": "N/A", "last_observation": "N/A", "duration": "N/A"},
            location={"latitude": 0.0, "longitude": 0.0},
            ai_result={},
            evidence_summary={},
            behavior_summary="Scenario unavailable in real corpus fixture set",
            why={},
            why_not={},
            what_changed={},
            uncertainty={},
            verification_state="UNAVAILABLE",
            limitations=["NO_REAL_DATA_MEETS_FITNESS_CRITERIA"],
            provenance={}
        )

    res_dict = result.to_dict()
    contract = build_canonical_contract(res_dict)

    src = contract["source"]
    beh = contract["behavior"]
    abn = contract["abnormality"]
    nov = contract["novelty"]
    conf = contract["confidence"]
    risk = contract["risk"]
    prio = contract["priority"]
    expl = contract["explanation"]
    ver = contract["verification"]
    lim = contract["limitations"]
    prov = contract["provenance"]
    ev = contract["evidence"]

    ai_result_summary = {
        "source_class": src["predicted_source_class"],
        "decision_state": src["decision_state"],
        "distribution_state": nov["distribution_state"],
        "event_state": beh["event_state"],
        "abnormality_level": abn["abnormality_level"],
        "novelty_level": nov["novelty_level"],
        "confidence_level": conf["confidence_level"],
        "risk_level": risk["risk_level"],
        "priority_level": prio["priority_level"],
        "urgency": prio["urgency"],
        "operational_action": prio["operational_action"]
    }

    evidence_summary = {
        "supporting_families": ev["supporting_families"],
        "conflicting_families": ev["conflicting_families"],
        "missing_families": ev["missing_families"],
        "evidence_completeness": ev["evidence_completeness"],
        "evidence_convergence": ev["evidence_convergence"]
    }

    return AgninetraDemoScenario(
        scenario_id=scenario_id,
        scenario_name=scenario_name,
        description=description,
        available=True,
        unavailable_reason=None,
        real_event_id=fixture.event_id,
        observation_ids=fixture.observation_ids,
        observation_count=fixture.observation_count,
        event_time={
            "first_observation": fixture.first_observation,
            "last_observation": fixture.last_observation,
            "duration": f"{fixture.raw_event_dict.get('current_duration', 0.0):.2f} hours"
        },
        location={
            "latitude": fixture.lat,
            "longitude": fixture.lon
        },
        ai_result=ai_result_summary,
        evidence_summary=evidence_summary,
        behavior_summary=f"Observed event state: {beh['event_state']}. Low-T status: {beh['low_t_behavior']}.",
        why=expl.get("why", {}),
        why_not=expl.get("why_not", {}),
        what_changed=expl.get("what_changed", {}),
        uncertainty=expl.get("uncertainty", {}),
        verification_state=ver["verification_state"],
        limitations=lim.get("unavailable_sensors", []) + lim.get("missing_data", []),
        provenance=prov,
        ground_truth_status="NOT_ESTABLISHED",
        observation_type="REAL_OBSERVATION"
    )


def select_demo_scenarios(
    fixtures: Optional[List[RealEventFixture]] = None,
    max_candidates: int = 50
) -> Dict[str, AgninetraDemoScenario]:
    """
    Deterministically selects the best matching real event for each of the 6 demonstration scenarios.
    Returns a dictionary mapping scenario_id (SCENARIO_1 to SCENARIO_6) to AgninetraDemoScenario records.
    """
    if fixtures is None:
        fixtures = load_real_event_fixtures(max_fixtures=max_candidates)

    # Evaluate analyze_event() for all fixtures deterministically
    evaluations: List[Tuple[RealEventFixture, EventIntelligenceResult]] = []
    for fix in fixtures:
        res = analyze_event(fix.raw_event_dict)
        evaluations.append((fix, res))

    scenario_specs = [
        ("SCENARIO_1", "PERSISTENT_ROUTINE_SOURCE", "Persistent / Routine Thermal Source", score_persistent_fitness),
        ("SCENARIO_2", "ESCALATING_ABNORMAL_EVENT", "Escalating / Abnormal Event", score_escalating_fitness),
        ("SCENARIO_3", "SPARSE_INSUFFICIENT_OBSERVATION", "Sparse / Insufficient Observation", score_sparse_fitness),
        ("SCENARIO_4", "CONFLICTING_EVIDENCE_EVENT", "Conflicting Evidence Event", score_conflicting_fitness),
        ("SCENARIO_5", "NOVEL_OOD_LIKE_EVENT", "Novel / OOD-like Event", score_novelty_fitness),
        ("SCENARIO_6", "HIGH_PRIORITY_EVENT", "High-Priority Event", score_priority_fitness)
    ]

    selected_scenarios: Dict[str, AgninetraDemoScenario] = {}
    used_event_ids: Set[str] = set()

    for s_id, s_code, s_name, score_fn in scenario_specs:
        candidates = []
        for fix, res in evaluations:
            # Prefer unique events per scenario where possible
            fit_score = score_fn(fix, res)
            if fit_score > 0.0:
                # Deterministic tie-breaking by (score, event_id)
                candidates.append((fit_score, fix.event_id, fix, res))

        # Sort candidates descending by fitness score, ascending by event_id for deterministic tie-breaking
        candidates.sort(key=lambda x: (-x[0], x[1]))

        if len(candidates) > 0:
            # Pick highest scoring unused event if possible
            best_tuple = candidates[0]
            for cand in candidates:
                if cand[1] not in used_event_ids:
                    best_tuple = cand
                    break

            best_score, best_e_id, best_fix, best_res = best_tuple
            used_event_ids.add(best_e_id)

            rec = build_scenario_record(s_id, s_code, s_name, best_fix, best_res)
            selected_scenarios[s_id] = rec
        else:
            # Mark unavailable explicitly
            rec = build_scenario_record(s_id, s_code, s_name, None, None, unavailable_reason="NO_REAL_EVENT_MEETS_SCENARIO_CRITERIA")
            selected_scenarios[s_id] = rec

    return selected_scenarios


# ==============================================================================
# 4. PACKAGE & MATRIX BUILDER
# ==============================================================================

def generate_scenario_matrix_md(scenarios: Dict[str, AgninetraDemoScenario]) -> str:
    """Generates Markdown comparison matrix table for documentation and UI handoff."""
    lines = [
        "# AI Behavioral Scenario Comparison Matrix",
        "",
        "> [!IMPORTANT]",
        "> **Operational Disclaimer**: `REAL OBSERVATION != REAL GROUND TRUTH`. Scenario labels describe observed AI system behavior based on available evidence, not verified ground truth.",
        "",
        "| Scenario ID | Scenario Name | Event ID | Obs Count | Event State | Decision State | Distribution | Risk Level | Priority | Action | Available |",
        "| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: |"
    ]

    for s_id in ["SCENARIO_1", "SCENARIO_2", "SCENARIO_3", "SCENARIO_4", "SCENARIO_5", "SCENARIO_6"]:
        sc = scenarios.get(s_id)
        if sc is None or not sc.available:
            lines.append(f"| {s_id} | {sc.scenario_name if sc else s_id} | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | FALSE |")
        else:
            ai = sc.ai_result
            lines.append(
                f"| {sc.scenario_id} | {sc.scenario_name} | `{sc.real_event_id}` | {sc.observation_count} | "
                f"`{ai.get('event_state')}` | `{ai.get('decision_state')}` | `{ai.get('distribution_state')}` | "
                f"`{ai.get('risk_level')}` | `{ai.get('priority_level')}` | `{ai.get('operational_action')}` | **TRUE** |"
            )

    lines.append("")
    return "\n".join(lines)


def build_and_export_demo_package(out_dir: str = "docs/demo") -> Dict[str, Any]:
    """
    Builds and exports demo scenario artifacts:
    - docs/demo/ai_behavior_scenario_matrix.json
    - docs/demo/ai_behavior_scenario_matrix.md
    """
    os.makedirs(out_dir, exist_ok=True)
    scenarios = select_demo_scenarios()

    package_dict = {
        "title": "AI_DEMO_SCENARIO_PACKAGE",
        "schema_version": SCHEMA_VERSION,
        "pipeline_version": PIPELINE_VERSION,
        "ground_truth_disclaimer": "REAL_OBSERVATION (GROUND_TRUTH_STATUS = NOT_ESTABLISHED)",
        "scenarios": {s_id: sc.to_dict() for s_id, sc in scenarios.items()}
    }

    # Export JSON
    json_path = os.path.join(out_dir, "ai_behavior_scenario_matrix.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(package_dict, f, indent=2)

    # Export Markdown
    md_content = generate_scenario_matrix_md(scenarios)
    md_path = os.path.join(out_dir, "ai_behavior_scenario_matrix.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return package_dict
