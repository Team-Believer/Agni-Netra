# Agni-Netra Phase 20C: High-Temperature Thermal Physics Lane

## 1. Core Scientific Principles & Mandates

```
HIGH-T SIGNAL != SOURCE CLASS
FRP != TEMPERATURE
REDUCED MODE != FULL VNF
SATURATION != HIGHER CONFIDENCE
```

Agni-Netra organizes thermal observation intelligence into two complementary regimes:

```
THERMAL INTELLIGENCE
├── HIGH-TEMP PHYSICS  (Regime 1: FRP intensity, Brightness Temp, Radiative extremeness)
└── LOW-TEMP PERSISTENCE (Regime 2: Temporal persistence, DBSCAN clustering, Industrial fingerprint)
```

The High-T Thermal Physics lane extracts physically interpretable thermal indicators from available FIRMS/VIIRS data. It acts as an **evidence-producing physics layer**, not a standalone fire classifier.

---

## 2. Reduced Mode vs. Full Multispectral VNF Mode

| Operating Mode | Trigger Condition | Capabilities | Limitations |
| :--- | :--- | :--- | :--- |
| `REDUCED_THERMAL_PHYSICS_MODE` | Standard FIRMS / VIIRS input | FRP intensity scoring, Brightness Temperature summaries, thermal extremeness, thermal concentration | No fake Planck curve fitting; no fake spectral source area calculations |
| `FULL_MODE` | Future multispectral feeds (band radiances, emissivity, source area) | Planck curve fitting, multispectral temperature inversion, emitter area estimation | Requires multispectral band radiances |
| `UNAVAILABLE` | Missing valid FRP & BT measurements | Emits `available=False` and reason codes | Pipeline continues gracefully |

---

## 3. High-Temperature Signal & Physics Contract (`HighTThermalAssessment`)

The bounded signal `high_temperature_signal` takes one of five explicit states:
- `STRONG`: Elevated thermal intensity ($\text{FRP} \ge 200\text{ MW}$ or $T_{b} \ge 360\text{ K}$)
- `MODERATE`: Moderate thermal intensity ($\text{FRP} \ge 50\text{ MW}$ or $T_{b} \ge 330\text{ K}$)
- `WEAK`: Low-intensity thermal signatures
- `NOT_DETECTABLE`: Minimal/zero thermal intensity
- `UNKNOWN`: Missing thermal measurements

> **Note**: `high_temperature_signal` indicates physical high-temperature characteristics, **not** fire probability or source class.

---

## 4. FRP Semantics vs. Temperature

- **FRP (Fire Radiative Power, MW)**: Represents radiative energy output over the pixel area.
- **Brightness Temperature ($T_b$, Kelvin)**: Represents radiometric temperature in the MIR/T31 channel.
- **Data Discipline Rule**: FRP and Brightness Temperature are evaluated separately (`frp_summary` vs. `brightness_temperature_summary`). High FRP alone does not imply high source temperature, and Brightness Temperature is never mathematically converted from FRP using invented formulas.

---

## 5. Saturation Defense Integration (Phase 20A Interaction)

When Phase 20A flags thermal saturation (`SATURATION_LIKELY` or `SATURATION_POSSIBLE`):
- `thermal_measurement_reliability` is downweighted (e.g. to $0.50$ or $0.75$).
- Saturation indicates sensor non-linearity / pixel-folding risk, **not** higher heat or higher risk.
- Downstream evidence ledger receives a `CONFLICTING` evidence item noting measurement degradation.

---

## 6. Downstream Integrations

1. **Evidence Ledger (Phase 17D)**: Emits items under family `THERMAL_PHYSICS` (`SUPPORTING`, `NEUTRAL`, `CONFLICTING`, `MISSING`).
2. **Confidence Engine (Phase 17E)**: Influences evidence completeness and convergence without forcing class confidence.
3. **Risk & Priority (Phase 17F)**: Contributes to hazard rating without forcing high risk automatically.
4. **Explanation Engine (Phase 17G)**: Generates controlled explanation phrasing (*"Thermal observations indicate a strong high-temperature signal"*, never *"proves industrial fire"*).
5. **Orchestrator (`analyze_event()`)**: Executes as Stage 5: `high_t_physics` after Stage 4 (`low_t_heat`).
