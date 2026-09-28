# Agni-Netra: Frontend API Client & State Management

## 1. Client Architecture
The frontend client uses a centralized API access layer in [`frontend/src/lib/api.ts`](file:///d:/Buildlaunchs/Agni-Netra/frontend/src/lib/api.ts). It enforces URL normalization, header injection, authentication token lifecycle, and error isolation across all UI pages.

```mermaid
graph TD
    subgraph UI Page Components
        DASH[dashboard/page.tsx]
        MAP[live-map/page.tsx]
        RPT[reports/page.tsx]
        SET[settings/page.tsx]
        ALT[alerts/page.tsx]
    end

    subgraph Central API Layer
        API_TS[frontend/src/lib/api.ts]
        NORM[URL Normalizer: buildApiUrl]
        AUTH[Auth Token & Header Interceptor]
        FETCH[fetchAPI Runner]
    end

    subgraph Backend Target
        SERVER[FastAPI Backend Server]
    end

    DASH & MAP & RPT & SET & ALT --> API_TS
    API_TS --> NORM --> AUTH --> FETCH
    FETCH -->|HTTP Requests| SERVER
```

---

## 2. API Method Reference

```typescript
// Core Data Fetchers
fetchDashboardSummary(): Promise<DashboardSummary>
fetchEvents(params?: FilterParams): Promise<EventItem[]>
fetchEventDetail(eventId: string): Promise<EventDetail | null>
fetchEventTimeline(eventId: string): Promise<TimelinePoint[]>
fetchSources(): Promise<DataSourceItem[]>
fetchAlerts(): Promise<AlertItem[]>
fetchModelStatus(): Promise<ModelStatus | null>

// Analyst Mutations
verifyEvent(eventId: string, payload: VerificationPayload): Promise<VerificationResult>

// Report & Document Generators
fetchReportData(eventId: string): Promise<any>
exportReportCsvBlob(): Promise<Blob>
exportReportPdfBlob(eventId: string): Promise<Blob>
```

---

## 3. URL Normalization Engine
To prevent double slashes (e.g., `https://domain.com//events`) in diverse deployment environments (Vercel, Render, Localhost), all requests pass through `buildApiUrl()`:

```mermaid
flowchart LR
    RAW["NEXT_PUBLIC_API_URL\n('https://domain.com/')"] --> CLEAN["getApiBaseUrl()\n('https://domain.com')"]
    EP["Endpoint\n('/events')"] --> NORM["cleanEndpoint\n('/events')"]
    CLEAN & NORM --> FINAL["buildApiUrl()\n'https://domain.com/events'"]
```
