# Agni-Netra Observation Quality, Saturation & Sun-Glint Defense Layer (Phase 20A)

## 1. Executive Summary & Core Principles

The **Observation Quality, Saturation & Sun-Glint Defense Layer** acts as a defensive pre-processing filter placed immediately after raw observation ingestion and before expensive downstream intelligence (canonical feature generation, Low-T persistence, historical abnormality, model inference, evidence aggregation, risk/priority, and explanations).

$$\text{OBSERVATION QUALITY} \neq \text{EVENT CLASSIFICATION}$$
$$\text{SATURATION} \neq \text{FIRE}$$
$$\text{GLINT RISK} \neq \text{FALSE POSITIVE}$$
$$\text{MISSING EVIDENCE} \neq \text{NEGATIVE EVIDENCE}$$

### Key Scientific Rules
1. **Preserve Raw Observations**: Original raw observation values are never mutated or overwritten (`raw_observation_ref`).
2. **Defensive Filtering, Not Deletion**: Questionable observations are characterized with explicit reason codes (`ACCEPT`, `FLAG`, `DOWNWEIGHT`, `EXCLUDE`) rather than being silently deleted.
3. **Saturation Is Not Fire**: Thermal saturation downweights evidence reliability; it never automatically classifies an event as a fire/flare or inflates confidence.
4. **Sun-Glint Is Not False Positive**: Sun-glint risk indicates reflective surface contamination; it downweights optical evidence without deleting the event.

---

## 2. Architecture & Pipeline Sequence

```
+-----------------------------------------------------------------------------------+
|                            RAW OBSERVATION INGESTION                              |
|  (Satellite / FIRMS / Sensor Detection Metadata: lat, lon, FRP, BT, Day/Night)     |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|               1. OBSERVATION QUALITY DEFENSE LAYER (Phase 20A)                    |
|  - Hard Validation (Non-repairing coordinate & non-finite FRP check)              |
|  - Thermal Saturation Defense (VIIRS I4 367K, MODIS B20/B21/B31)                  |
|  - Pixel-Folding / Non-Linearity Detection                                        |
|  - Sun-Glint & Specular Reflection Risk Detection                                 |
|  - Action Assignment: ACCEPT, FLAG, DOWNWEIGHT, EXCLUDE                           |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                       2. EVENT PIPELINE ORCHESTRATION                             |
|  Canonical Features -> Low-T -> Abnormality -> Model -> Evidence ->               |
|  Confidence -> Risk / Priority -> Explanation                                     |
+-----------------------------------------------------------------------------------+
```

---

## 3. Defensive Dimensions

### A. Hard Validation
Non-repairing validation enforced before downstream scoring:
- **Latitude & Longitude Bounds**: Valid range $[-90^\circ, 90^\circ]$ for latitude and $[-180^\circ, 180^\circ]$ for longitude. Non-finite (NaN / inf) or out-of-bound coordinates result in `action = EXCLUDE`, `usable_for_evidence = False`.
- **Thermal Value Finiteness**: Non-finite (NaN / negative / inf) FRP values result in `action = EXCLUDE`, flag `NON_FINITE_FRP_VALUE`.

### B. Thermal Saturation & Sensor Non-Linearity Defense
Inspects sensor/product context:
- **VIIRS I4 Band Saturation**: $T_{b4} \ge 367.0\text{ K}$ flags `THERMAL_SATURATION_LIKELY` and state `LIKELY_SATURATION`.
- **MODIS / General Saturation**: Brightness temperature $\ge 500\text{ K}$ or extreme FRP $\ge 1000\text{ MW}$ flags `THERMAL_SATURATION_POSSIBLE`.
- **Pixel-Folding Anomaly**: Unusually low reported FRP ($< 1.0\text{ MW}$) despite extreme brightness temperature ($> 360\text{ K}$) flags `POSSIBLE_PIXEL_FOLDING_ANOMALY`.
- **Downweighting**: Saturation downweights `recommended_weight` ($0.50 \dots 0.85$) and quality score, but NEVER inflates classifier confidence or physical hazard.

### C. Sun-Glint & Specular Reflection Risk Defense
Evaluates daytime solar illumination context:
- **Period Handling**:
  - `NIGHT` (Day/Night indicator == `N` or Solar Zenith $\ge 85^\circ$): Glint risk is automatically set to `NO_GLINT_RISK`.
  - `DAY` (Solar Zenith $< 85^\circ$): Glint geometry is evaluated.
- **Specular Geometry**:
  - Glint Angle $\le 10.0^\circ$ or High Surface Reflectance ($> 0.4$ over water context): `HIGH_GLINT_RISK`, flags `SUN_GLINT_RISK_HIGH` and `POTENTIAL_REFLECTIVE_CONTAMINATION`.
  - Glint Angle $\le 20.0^\circ$: `MODERATE_GLINT_RISK`.
  - Missing Geometry Metadata: Set to `UNKNOWN_GLINT_RISK` without fabricating glint evidence!

---

## 4. Quality Level & Action Mappings

| Quality Score | Quality Level | Action | Usable Detection | Usable Classification | Recommended Weight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| $\ge 0.85$ | `GOOD` | `ACCEPT` | True | True | 1.00 |
| $0.60 \dots 0.84$ | `ACCEPTABLE` | `FLAG` | True | True | 0.85 |
| $0.35 \dots 0.59$ | `DEGRADED` | `DOWNWEIGHT` | True | False | 0.50 |
| $< 0.35$ | `POOR` | `DOWNWEIGHT` / `EXCLUDE` | True / False | False | $0.00 \dots 0.20$ |

---

## 5. Multi-Observation Event Aggregation

For events containing multiple observations, `evaluate_event_observation_quality()` computes an event-level aggregate:
- `total_observation_count`: Total observations ingested.
- `usable_observation_count`: Count of non-excluded observations.
- `degraded_observation_count`: Count of observations flagged with degraded/poor quality.
- `excluded_observation_count`: Count of hard-rejected observations.
- `overall_observation_quality`: Mean quality score across usable observations.
- Aggregated saturation, glint risk, and critical quality flag summaries.

---

## 6. Downstream Integrations

1. **Evidence Aggregation (Phase 17D)**: Quality issues inject `DATA_QUALITY` evidence items with `direction = CONFLICTING` or `NEUTRAL` into the evidence ledger.
2. **Confidence Engine (Phase 17E)**: `overall_observation_quality` populates `data_quality_confidence`. Degraded quality adds `limiting_factors` and triggers human verification gates when below policy thresholds.
3. **Risk & Priority Engine (Phase 17F)**: Degraded observation quality lowers `risk_confidence` and increases verification urgency, without suppressing or inflating physical hazard.
4. **Explanation Engine (Phase 17G)**: Exposes quality limitations in `why_not` and `uncertainty` explanations (e.g. *"Thermal interpretation is limited by possible saturation"*).
5. **Orchestrator (`analyze_event()`)**: Positioned as Stage #2 (`observation_quality`), running immediately after input validation.

---

## 7. Output Contract (`ObservationQualityAssessment`)

```json
{
  "observation_id": "obs_viirs_001",
  "quality_score": 0.65,
  "quality_level": "ACCEPTABLE",
  "action": "FLAG",
  "usable_for_event_detection": true,
  "usable_for_classification": true,
  "usable_for_evidence": true,
  "recommended_weight": 0.85,
  "quality_flags": [
    "VIIRS_I4_SATURATION_TEMPERATURE_EXCEEDED"
  ],
  "reason_codes": [
    "THERMAL_RESPONSE_DEGRADED",
    "THERMAL_SATURATION_LIKELY"
  ],
  "limitations": [
    "Thermal saturation likely: thermal intensity accuracy degraded"
  ],
  "saturation_state": "LIKELY_SATURATION",
  "glint_risk_state": "NO_GLINT_RISK",
  "observation_period": "DAY",
  "raw_observation_ref": {
    "observation_id": "obs_viirs_001",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "frp": 120.0,
    "sensor": "VIIRS",
    "bright_ti4": 372.0,
    "daynight": "D"
  }
}
```
