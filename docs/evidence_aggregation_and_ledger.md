# Evidence Aggregation & Event Evidence Ledger

## 1. Purpose
The Evidence Aggregation and Event Evidence Ledger module formalizes the crucial distinction between **Model Prediction** and **Evidence** in Agni-Netra. A classification score is a model's *hypothesis*; this module provides the transparent, auditable ledger of facts that either support, conflict with, or are missing regarding that hypothesis.

## 2. Core Concepts

### Evidence Item
Every piece of evidence is represented explicitly via `EvidenceItem`:
- **Direction**: `SUPPORTING`, `CONFLICTING`, `MISSING`, or `NEUTRAL`.
- **Status**: `OBSERVED`, `DERIVED`, `UNAVAILABLE`, `NOT_APPLICABLE`.
- **Strength**: Contextual strength indicator (e.g., `STRONG`, `WEAK`).
- **Family**: Grouping of related signals to prevent highly correlated features from inflating evidence counts (e.g., `THERMAL`, `TEMPORAL`, `CONTEXT`, `SENTINEL`, `MODEL`, `ANOMALY`, `BEHAVIOR`).

### Evidence Completeness
Answers: *"How much of the expected evidence is actually available?"*
It explicitly does **NOT** equal model confidence. An event can have 99% model confidence but 40% evidence completeness if key sensors were missing.

### Evidence Convergence
Answers: *"How many independent evidence families agree with the same interpretation?"*
Multiple raw thermal variables (`current_mean_frp`, `frp_std`) only count as a single `THERMAL` family vector, ensuring independent convergence (e.g., `THERMAL` + `SENTINEL` + `CONTEXT`) isn't faked by correlated parameters.

## 3. Key Decoupling Principles

### Missing Evidence ≠ Negative Evidence
If a Sentinel pass was obstructed by clouds, the evidence is `MISSING`. It is NOT recorded as `CONFLICTING` evidence against a fire hypothesis. Missing evidence lowers *completeness*, not *confidence* automatically.

### Model Score = MODEL-DERIVED Evidence
The output of the Phase 16E-R2 frozen classifier is captured in the ledger as explicitly `MODEL-DERIVED`. A high probability score is not converted into a statement like "Industrial Fire Confirmed". It remains an independent piece of algorithmic evidence alongside physical observations.

### Low-T and Abnormality Integration
- The **Low-T Intelligence Lane (Phase 17B)** feeds behavioral evidence (e.g., "Persistent moderate-intensity thermal activity detected"). It does NOT feed source classifications.
- The **Historical Abnormality Engine (Phase 17C)** feeds anomaly evidence (e.g., "Current activity is highly abnormal relative to history"). It does NOT rule out natural events.

## 4. Hypothesis Support Matrix
The `EventEvidenceLedger` contains a `hypothesis_support_matrix`. For each possible source hypothesis (e.g., `INDUSTRIAL_FIRE`, `WILDFIRE`), the ledger dynamically aligns available evidence into `SUPPORTING`, `CONFLICTING`, and `MISSING` bins. 

This directly powers downstream confidence calibration, risk scoring, and human-readable explanation interfaces (WHY / WHY NOT / WHAT CHANGED).
