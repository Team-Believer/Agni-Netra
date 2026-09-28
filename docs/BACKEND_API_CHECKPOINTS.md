# Agni-Netra: Backend API Checkpoints & Testing Specification

## 1. Overview
This specification defines the validation criteria for all backend micro-services, ensuring data integrity, correct serialization, and sub-100ms response times.

```mermaid
graph LR
    UNIT[Unit Tests: Services & Models] --> INTG[Integration Tests: FastAPI TestClient]
    INTG --> LOAD[Load & Concurrency Tests]
    LOAD --> PROD[Production Health Monitoring]
```

---

## 2. Checkpoint Validation Matrix

```mermaid
flowchart TD
    A[Start Backend Tests] --> B{Health Check OK?}
    B -- No --> FAIL1[Fail: Check Uvicorn Binding]
    B -- Yes --> C{Database Seeded?}
    C -- No --> FAIL2[Fail: Run seed_demo.py]
    C -- Yes --> D{Auth Token Valid?}
    D -- Yes --> E[Validate Event Query Endpoints]
    E --> F[Validate Verification Mutation]
    F --> G[Validate PDF / CSV Generation]
    G --> PASS[All 8 Backend Checkpoints Passed]
```

| Checkpoint | Target Endpoint | Validation Criteria | Status |
|---|---|---|---|
| **CP-BE-01** | `GET /health` | Status 200, JSON payload with `status: ok` | PASSED |
| **CP-BE-02** | `HEAD /` | Status 200, zero body content (Render probe) | PASSED |
| **CP-BE-03** | `GET /api/dashboard/summary` | Contains `total_active`, `high_priority`, `under_verification` | PASSED |
| **CP-BE-04** | `GET /api/events` | Returns list of serialized events matching schema | PASSED |
| **CP-BE-05** | `GET /api/events/{id}` | Returns event detail with explanations, evidence, and history | PASSED |
| **CP-BE-06** | `POST /api/events/{id}/verify` | Updates state to confirmed/dismissed and records reviewer | PASSED |
| **CP-BE-07** | `GET /api/analytics/events-over-time` | Returns date-indexed array of event counts | PASSED |
| **CP-BE-08** | `GET /api/reports/export/csv` | Content-Type `text/csv`, valid CSV header and rows | PASSED |
