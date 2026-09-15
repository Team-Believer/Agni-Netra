# Agni-Netra Phase 20B: INSAT-3DS High-Cadence Thermal Evidence Lane

## 1. Core Scientific Principles & Mandate

```
INSAT-3DS != GROUND TRUTH
INSAT-3DS != FIRE CONFIRMATION
INSAT-3DS != FACILITY-LEVEL LOCALIZATION
INSAT-3DS = HIGH-CADENCE THERMAL EVIDENCE / CORROBORATION
```

FIRMS / VIIRS (and MODIS) remains the primary event observation backbone within Agni-Netra. INSAT-3DS is integrated as a modular Indian Geostationary (GEO) observation and evidence source. Its primary value lies in its **high-cadence temporal awareness (~15-minute imaging interval)** and **thermal persistence cross-checking**, not high spatial resolution or definitive fire classification.

---

## 2. Ingestion & Normalization Architecture

```
INSAT-3DS (GEO Payload / Local Product / Direct Feed)
                        ↓
                 Raw Ingestion
                        ↓
            Shared Normalization Layer
         (NormalizedObservation Schema)
                        ↓
            Phase 20A Observation Quality
         (Coordinates, Finiteness, Saturation)
                        ↓
             Cross-Sensor Event Alignment
          (Spatial Radius & Temporal Window)
                        ↓
              Sensor Corroboration Engine
            (SensorCorroborationAssessment)
                        ↓
           Phase 17D Event Evidence Ledger
               (GEO_THERMAL Family)
                        ↓
      Downstream Intelligence & Orchestration
     (Confidence, Risk/Priority, Explanation, analyze_event)
```

---

## 3. Common Observation Contract (`NormalizedObservation`)

All incoming INSAT-3DS data is normalized into the shared `NormalizedObservation` schema:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `observation_id` | `str` | Unique observation identifier |
| `source_sensor` | `str` | `"INSAT-3DS"` (explicit, never generic `"satellite"`) |
| `product` | `str` | Product identifier (e.g. `"INSAT3DS_HEM_L2B"`) |
| `timestamp` | `str` | ISO 8601 UTC timestamp |
| `latitude` | `float` | Latitude in decimal degrees |
| `longitude` | `float` | Longitude in decimal degrees |
| `brightness_temperature` | `Optional[float]` | Mid-Infrared (MIR / T31) Brightness Temperature in Kelvin |
| `thermal_band` | `Optional[str]` | Thermal channel (e.g. `"MIR"`) |
| `radiance` | `Optional[float]` | Radiance value if available |
| `frp` | `Optional[float]` | Fire Radiative Power (MW) — **Only set if explicitly provided** by source product |
| `quality` | `Optional[float]` | Source quality flag (0.0 to 1.0) |
| `cloud_status` | `Optional[str]` | Cloud status metadata (`"CLEAR"`, `"CLOUDY"`, `"UNKNOWN"`) |
| `sensor_metadata` | `Dict[str, Any]` | Raw metadata preservation dictionary |

> **Scientific Rule**: FRP is never fabricated or converted from generic brightness temperature if not natively produced by the source product.

---

## 4. Source Identity & Registry (`SensorSourceRegistry`)

Every observation clearly identifies its originating sensor. Sensor specifications are registered centrally in `SENSOR_REGISTRY`:

- **Sensor Name**: `INSAT-3DS`
- **Sensor Type**: `GEO` (Geostationary Earth Orbit)
- **Cadence Class**: `HIGH_CADENCE_15MIN`
- **Spatial Resolution Class**: `COARSE_GEO_4KM` (4 km thermal infrared pixel resolution)
- **Latency Class**: `RAPID_REALTIME`
- **Evidence Types**: `["THERMAL_CONTINUITY", "BRIGHTNESS_TEMP", "TEMPORAL_ESCALATION"]`

---

## 5. Cross-Sensor Event Alignment & Spatial Resolution Limitations

INSAT-3DS operates at a coarse spatial resolution (~4 km pixel footprint). Therefore:
- Facility-level localization is **never claimed** from INSAT-3DS alone.
- Observations map onto existing persistent event centroids using Haversine great-circle distance ($d \le 10.0\text{ km}$) and temporal windowing ($\Delta t \le 3.0\text{ hours}$).
- Alignment States:
  - `ALIGNED`: Observation falls within spatial radius and temporal window.
  - `AMBIGUOUS_EVENT_ASSOCIATION`: Ambiguous spatial or temporal boundary match.
  - `UNALIGNED`: Disjoint spatial/temporal footprint.

---

## 6. Freshness & Latency Semantics

Observation freshness is categorized dynamically relative to event baseline time:
- `FRESH`: Age $\le 1.0\text{ hour}$
- `RECENT`: Age $\le 6.0\text{ hours}$
- `STALE`: Age $\le 24.0\text{ hours}$
- `UNKNOWN`: Unparseable timestamp or missing baseline.

---

## 7. Cross-Sensor Corroboration Engine (`SensorCorroborationAssessment`)

Corroboration combines FIRMS detections with INSAT-3DS temporal observations:

- **States**:
  - `CORROBORATING`: $\ge 2$ aligned INSAT observations supporting FIRMS detections.
  - `PARTIALLY_CORROBORATING`: $1$ aligned INSAT observation supporting FIRMS detections.
  - `CONFLICTING`: FIRMS shows activity but aligned INSAT observations show no thermal support (subject to coverage/cloud limitations).
  - `INSUFFICIENT`: Insufficient observations to perform cross-sensor comparison.
  - `NOT_AVAILABLE`: INSAT-3DS product unavailable for the given time/region.

> **Important**: Absence of INSAT-3DS detection is categorized as `MISSING` or `UNAVAILABLE`, **not** automatically negative evidence for fire presence.

---

## 8. Integration into `analyze_event()` & Production Pipeline

INSAT-3DS is an **optional observation source**. When unavailable:
1. Pipeline sets `insat3ds_summary = {"availability": "UNAVAILABLE", "corroboration_state": "NOT_AVAILABLE"}`.
2. Sensor is recorded in `limitations["unavailable_sensors"]`.
3. Pipeline continues execution through all downstream stages normally.

Controlled explanation phrasing (Phase 17G) strictly enforces:
- *"High-cadence GEO observations (INSAT-3DS) support continued thermal activity."*
- *"INSAT-3DS evidence is unavailable for the relevant period."*
- *"Thermal observations from FIRMS and INSAT-3DS are not fully aligned; verification is recommended."*
- **Never say**: *"INSAT-3DS confirms fire."*
