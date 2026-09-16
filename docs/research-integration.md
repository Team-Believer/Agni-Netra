# Agni-Netra: Research Integration Map

This document maps the core research capabilities of Agni-Netra (SIH PS162) to the actual system modules and architecture implemented in the application.

## 1. System-Wide Philosophy
**Event-Centric Evidence Intelligence**
Most thermal detection systems are "point-in-time anomaly mappers" (plotting FIRMS hotspots on a map). Agni-Netra is an **Event-Centric Evidence Graph**. We ingest point anomalies, reconstruct them into physical events (spatiotemporal clustering), and then synthesize an Evidence Graph by aggregating corroborated multi-sensor intelligence.

## 2. Research Capabilities to Module Mapping

### A. Modular Data Ingestion & Dual Thermal Lanes
**Concept:** Handling different satellite orbital paths, resolutions, and revisit times without generating fake data.
**Module:** `backend/app/ingestion/`
- **`firms.py`**: Extracts high-thermal FRP characteristics. (VIIRS)
- **`insat.py`**: Adapter for high-cadence 15-minute Geostationary temporal tracking.
- **`sentinel.py`**: High-resolution optical/SWIR anomaly extraction.
- **`weather.py`**: Ground-truth atmospheric dispersion conditions.
- **`osm.py`**: Offline industrial infrastructure and proximity mapping.
- **`alphaearth.py` & `nisar.py`**: Stubs for SAR and contextual embeddings.
*(Note: Per the strict NO-FAKE-DATA policy, unavailable sensors cleanly return `MISSING` rather than hallucinated responses).*

### B. Event Reconstruction & Clustering
**Concept:** Grouping disparate satellite passes into a single persistent physical entity.
**Module:** `backend/app/pipeline/event_reconstruction.py`
- Implements spatiotemporal Haversine clustering.
- Bounding GeoJSON generation to track footprint expansion.

### C. Multi-Sensor Evidence Fusion
**Concept:** Synthesizing thermal, spatial, temporal, optical, weather, and facility contexts.
**Module:** `backend/app/pipeline/evidence_fusion.py`
- Aggregates the inputs from `ingestion/` into an array of `EventEvidence` objects.
- Attributes `direction` flags: `SUPPORTING`, `CONFLICTING`, `NEUTRAL`, or `MISSING`.
- Exposed via `/api/v1/events/{id}/evidence`.

### D. Conformal Prediction & OOD (Out-of-Distribution)
**Concept:** Allowing the model to say "I'm not sure" (Prediction Sets) or "I've never seen this before" (OOD) rather than forcing a misclassification.
**Module:** `backend/app/ml/inference.py`
- Wraps the XGBoost predictions.
- Generates a `prediction_set` array (e.g. `["Wildfire", "Routine Flare"]` if confidence is low).
- Flags `ood_status` if the inputs (like Max FRP) drastically violate training bounds.
- Displayed natively in the frontend Event Details (`frontend/src/app/events/[id]/page.tsx`).

### E. Priority vs. Risk Decoupling
**Concept:** Risk = Physical Danger. Priority = Human Attention Need.
**Module:** `backend/app/pipeline/risk.py` & `backend/app/pipeline/priority.py`
- **Risk Index (0-100)**: Evaluates FRP intensity, footprint growth, and proximity to critical infrastructure.
- **Operational Priority**: Determines triage based on Abnormality. A massive flare might have High Risk but Low Priority (if routine). A small unexplained fire near a sensitive asset has High Priority.

### F. Explainable AI (XAI)
**Concept:** Translating black-box scores into human-readable rationale.
**Module:** `backend/app/ml/explainability.py`
- Provides `Why`, `Why Not`, and `What Changed` reasoning vectors.
- Displayed directly to the analyst for rapid validation.

## 3. UI/UX Mapping

- **Live Map (`/live-map`)**: Real-time rendering of active events with Mapbox / MapLibre.
- **Event Detail (`/events/[id]`)**: Deep-dive forensics page displaying the full Evidence Graph, Conformal Prediction sets, and XAI reasoning.
- **Source Health (`/sources`)**: A transparency dashboard showing exactly which orbital sensors and APIs are online, offline, or not configured.
- **Analytics (`/analytics`)**: System-wide trends, hypothesis distributions, and multi-sensor contribution charts.
- **Product Explainer (`/about`)**: Directly communicates the SIH problem statement (PS162) and core differentiators.

## 4. Execution Flow
1. Cron/trigger invokes `IngestionPipeline.run_cycle()`.
2. Raw observations fetched.
3. EventReconstructor clusters into `Event`.
4. Inference Engine predicts classification and conformal uncertainty.
5. Risk and Priority models calculate scores.
6. EvidenceFusion synthesizes adapter responses.
7. Explanations generated.
8. Persisted to SQLite -> Rendered to Next.js Frontend.
