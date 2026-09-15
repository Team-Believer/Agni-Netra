# Agni-Netra Phase 20D: Event State Machine & Behavioral State Intelligence

## 1. Core Principles & Mandates

```
STATE != SOURCE CLASSIFICATION
STATE != ABNORMALITY
STATE != RISK
STATE != PRIORITY
OBSERVATION GAP != PHYSICAL INACTIVITY
DORMANT != CONFIRMED EXTINCTION
```

The Agni-Netra Event State Machine tracks an event as an evolving physical process across temporal observations rather than treating each observation in isolation. State transitions describe **event evolution** and lifecycle behavior independently of source classification.

---

## 2. Controlled State Taxonomy

| State | Description | Typical Trigger / Entry Condition |
| :--- | :--- | :--- |
| `NEW` | Newly emerged event | $\le 1$ observation; insufficient temporal history |
| `PERSISTING` | Continued thermal activity | $\ge 3$ repeated compatible observations over time |
| `STABLE` | Consistent thermal/behavioral envelope | Persistent observations with low thermal variability ($STD_{frp} < 15.0$) or Low-T persistence |
| `INTERMITTENT` | Temporal gaps between observations | Observations repeatedly appear/disappear across windows ($\Delta t > 12\text{ h}$) |
| `ESCALATING` | Increasing thermal intensity / footprint | Multi-signal increase: FRP spike, High-T signal, or footprint expansion |
| `ABNORMAL` | Historical baseline deviation | Abnormality engine reports `UNUSUAL` or `HIGHLY_ABNORMAL` state |
| `RESOLVING` | Declining activity / cooling trend | Decreasing thermal intensity or footprint contraction |
| `DORMANT` | Inactive within preservation window | No observations within `dormancy_window_hours` ($\ge 24\text{ h}$) |
| `REACTIVATED` | Dormant event resumes activity | Compatible new observation received for previously `DORMANT` event identity |
| `UNKNOWN` | Contradictory or insufficient evidence | Sparse, unparseable, or contradictory temporal signals |

---

## 3. Transition Model Graph

```
                   ┌──────────┐
                   │   NEW    │
                   └────┬─────┘
                        │
                        ▼
               ┌────────────────┐
               │   PERSISTING   │◄─────────────────┐
               └──────┬──┬──────┘                  │
        ┌─────────────┘  └──────────────┐          │
        ▼                               ▼          │
  ┌──────────┐                    ┌──────────┐     │
  │  STABLE  │◄──────────────────►│ESCALATING│     │
  └─────┬────┘                    └────┬─────┘     │
        │                              │           │
        ▼                              ▼           │
  ┌───────────┐                  ┌──────────┐      │
  │ INTERMIT. │                  │ ABNORMAL │      │
  └─────┬─────┘                  └────┬─────┘      │
        │                              │           │
        └──────────────┬───────────────┘           │
                       │                           │
                       ▼                           │
                 ┌───────────┐                     │
                 │ RESOLVING │                     │
                 └─────┬─────┘                     │
                       │                           │
                       ▼                           │
                 ┌───────────┐                     │
                 │  DORMANT  │                     │
                 └─────┬─────┘                     │
                       │                           │
                       ▼                           │
                 ┌───────────┐                     │
                 │REACTIVATED├─────────────────────┘
                 └───────────┘
```

---

## 4. Key Behavioral Disambiguations

### A. Observation Gap vs. Physical Inactivity
Missing observations due to cloud cover, daytime solar glint, or sensor pass geometry are explicitly tagged as `OBSERVATION_GAP` or `SENSOR_UNAVAILABLE`. The state machine does **not** interpret sensor gaps as physical event resolution or extinction.

### B. Dormancy vs. Extinction
`DORMANT` means no observations have been logged within the configured event-preservation window ($24.0\text{ hours}$). It does **not** mean the thermal source is permanently extinguished. When a dormant event receives new compatible observations, it transitions to `REACTIVATED` while retaining its original persistent event ID.

---

## 5. System & Downstream Integration

1. **Evidence Ledger (Phase 17D)**: Emits evidence items under family `BEHAVIOR_STATE` (`SUPPORTING`, `CONFLICTING`, `NEUTRAL`).
2. **Confidence Engine (Phase 17E)**: `state_confidence` is computed independently of classification confidence.
3. **Risk & Operational Priority (Phase 17F)**: `ESCALATING` increases operational urgency; `RESOLVING` reduces urgency without modifying physical hazard.
4. **Explanation Engine (Phase 17G)**: Produces controlled explanations (*"Event is currently ESCALATING due to increasing thermal intensity..."*).
5. **Orchestration (`analyze_event()`)**: Executes as Stage 6: `event_state_machine`.
