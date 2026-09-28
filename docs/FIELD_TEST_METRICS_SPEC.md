# Agni-Netra: Field Test Metrics & Verification Specification

## 1. Metric Hierarchy & Definitions
Field testing assesses operational reliability across three dimensions: **Detection Fidelity**, **Computational Latency**, and **Human-in-the-Loop Efficiency**.

```mermaid
graph TD
    M[Field Test Metric Evaluation] --> M1[Fidelity Metrics]
    M --> M2[Performance & Latency]
    M --> M3[Human Decision Speed]
    
    M1 --> M1A[Precision & Recall]
    M1 --> M1B[False Discovery Rate]
    
    M2 --> M2A[Ingestion Pipeline Latency]
    M2 --> M2B[Map Tile & UI Load Times]
    
    M3 --> M3A[Time-to-Verification]
    M3 --> M3B[Analyst Workload Reduction]
```

---

## 2. Formal Metric Formulas

### 1. Industrial Anomaly Precision ($P_{\text{ind}}$)
$$P_{\text{ind}} = \frac{\text{True Industrial Emergencies Detected}}{\text{Total Industrial Emergency Alerts Dispatched}}$$

### 2. False Alarm Ratio ($FAR$)
$$FAR = \frac{\text{Benign Fires Flagged as Critical}}{\text{Total Critical Dispatches}}$$

### 3. Mean Time to Comprehension ($MTTC$)
The elapsed time from when an event appears on the Live Event Map until the analyst confirms an emergency dispatch or dismisses the incident.

```mermaid
sequenceDiagram
    participant O as Orbit (INSAT / VIIRS)
    participant E as Agni-Netra Engine
    participant A as Analyst Dashboard
    
    Note over O,E: Data Transfer & Cluster (T_ingest < 5s)
    O->>E: Transmit Hotspot Telemetry
    Note over E,A: ML Inference & Risk Scoring (T_infer < 1s)
    E->>A: Push Event to Live Map & Queue
    Note over A: Analyst Reviews Evidence Ledger (T_analyst < 45s)
    A->>E: Submit Verification Decision
```

---

## 3. SLA Pass/Fail Thresholds

| Metric | Target Threshold | Critical Failure Threshold |
|---|---|---|
| Precision (High/Critical Priority) | $\ge 92.0\%$ | $< 80.0\%$ |
| False Positive Alarm Rate | $\le 5.0\%$ | $> 15.0\%$ |
| Time-to-Verification | $\le 60\text{ s}$ | $> 180\text{ s}$ |
| Tile Request Failure Rate | $0.0\%$ | $> 0.1\%$ |
