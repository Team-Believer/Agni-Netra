# Agni-Netra: AI Domain Context & Core Hypotheses

## 1. Domain Problem Statement
Satellite sensors detect thermal radiation signatures across the earth's surface. However, raw sensors output only numbers (Fire Radiative Power, Brightness Temperature) without semantic comprehension. A pixel flashing 350K could be:
* An illegal chemical waste fire
* A steel plant blast furnace or flare stack operating normally
* Stubble burning in agricultural fields
* A forest wildfire spreading toward critical infrastructure

Agni-Netra bridges raw orbital data and operational emergency dispatch.

```mermaid
flowchart TD
    RAW[Raw Satellite Pixels\nVIIRS / MODIS / INSAT-3DS] --> AN[Agni-Netra AI Engine]
    
    subgraph Reasoning Pillars
        AN --> H1[Thermal Physics & Planck Inversion]
        AN --> H2[Temporal Persistence & Re-visit Clustering]
        AN --> H3[Geospatial Ground Truth & Industrial Anchors]
        AN --> H4[Weather & Wind Plume Modeling]
    end
    
    H1 & H2 & H3 & H4 --> DEC[Operational Intelligence & Dispatch Priority]
```

---

## 2. Scientific Hypotheses

### Hypothesis 1: High-T vs Low-T Thermal Profiles
* **Industrial Flaring:** Extremely localized, high temperature ($T > 1000\text{ K}$), low spatial footprint ($< 100\text{ m}^2$).
* **Biomass / Forest Fires:** Large spatial footprint ($> 1\text{ km}^2$), lower combustion temperature ($600\text{ K} - 800\text{ K}$).

### Hypothesis 2: Temporal Recurrence Signatures
* Controlled industrial sources exhibit consistent day/night persistence over 30-day windows.
* Uncontrolled fires exhibit explosive onset, radial growth, and subsequent dissipation.

```mermaid
sequenceDiagram
    participant S as Orbiting Satellite
    participant P as Feature Pipeline
    participant M as Multitask Classifier
    participant D as Verification Queue
    
    S->>P: Ingest Hotspot Observation (FRP, Lat, Lon, Temp)
    P->>P: Correlate Historical Buffer & OSM Land Cover
    P->>M: 32-Dimension Feature Vector
    M->>M: Predict Class + Anomaly Score + Uncertainty
    alt High Risk / Novel Anomaly
        M->>D: Route to Emergency Verification Queue
    else Routine Operation
        M->>D: Log into Background Monitoring Ledger
    end
```
