# Agni-Netra: Frontend API Checkpoints & UI Integration Tests

## 1. Overview
This specification details the validation checkpoints for frontend network communication, reactive state management, and MapLibre GL tile rendering.

```mermaid
graph TD
    A[Start Frontend Checkpoints] --> B[CP-FE-01: No Double Slashes in Requests]
    B --> C[CP-FE-02: Live Event Map & Satellite Tiles]
    C --> D[CP-FE-03: Dashboard KPI Auto-Sync]
    D --> E[CP-FE-04: Event Selection & Verification]
    E --> F[CP-FE-05: PDF/CSV Binary Downloads]
    F --> G[All Frontend Checkpoints PASSED]
```

---

## 2. Checkpoint Validation Table

| Checkpoint | Target Feature | Validation Criteria | Status |
|---|---|---|---|
| **CP-FE-01** | API Normalization | Requests use `${baseUrl}/${endpoint}` without double slashes `//` | PASSED |
| **CP-FE-02** | Live Event Map | Esri satellite & boundary labels render without "API KEY REQUIRED" watermarks | PASSED |
| **CP-FE-03** | Dashboard Sync | `loadData()` retrieves summary KPIs and event array on mount | PASSED |
| **CP-FE-04** | Event Selection | Clicking map marker / table row updates active detail panel and URL `?eventId=` | PASSED |
| **CP-FE-05** | Verification Action | Submitting review triggers `verifyEvent()` and updates event status indicator | PASSED |
| **CP-FE-06** | Reports Export | Clicking CSV / PDF creates local download blob with correct MIME types | PASSED |
| **CP-FE-07** | Analytics Graphs | Recharts components render time-series, classification, and priority charts | PASSED |
| **CP-FE-08** | Production Build | `npm run build` exits with code 0 and generates all static/dynamic routes | PASSED |

---

## 3. UI State Transition Diagram

```mermaid
stateDiagram-v2
    [*] --> IdleDashboard
    IdleDashboard --> EventSelected: User clicks Map Marker / Table Row
    EventSelected --> VerificationModal: User clicks 'Verify Event'
    VerificationModal --> Submitting: Analyst inputs decision & note
    Submitting --> EventSelected: Optimistic UI update & status refresh
    EventSelected --> IdleDashboard: User clears selection
```
