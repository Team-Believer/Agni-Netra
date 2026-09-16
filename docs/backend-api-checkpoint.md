# Agni-Netra: Backend API Checkpoint

This document outlines the current state of the frontend-backend API contracts to ensure integration stability.

## Base URL
All API requests are prefixed with `/api`.
Currently, the backend runs at `http://localhost:8000`.

## Implemented Endpoints

### Health & System
- `GET /api/health`: Returns system operational state.

### Dashboard
- `GET /api/dashboard/summary`: Returns KPI metrics (active, high priority, under verification, resolved).
- `GET /api/dashboard/hotspots`: Returns GeoJSON feature collection for the MapLibre layer.

### Events
- `GET /api/events`: Lists events with optional filtering (status, priority).
- `GET /api/events/{id}`: Returns complete event details, AI explanations, and evidence ledger.
- `GET /api/events/{id}/timeline`: Returns chronological sensor observation timeline for an event.
- `POST /api/events/{id}/verify`: Submits analyst human verification decisions.

### Observations
- `GET /api/observations`: Lists raw thermal observations from sensors.

### Sources
- `GET /api/sources`: Returns the status and latency of ingestion sensor adapters (FIRMS, INSAT-3DS).

### Reports & Alerts
- `GET /api/reports/{id}`: Exports structured event reports.
- `GET /api/alerts`: Returns active priority alerts.

### Models
- `GET /api/models/status`: Returns status and configuration of the pre-trained XGBoost model.

## Current State & Notes
- The Next.js frontend is actively consuming these endpoints.
- The `seed_demo_data.py` script populates the SQLite database to fulfill these contracts realistically, ensuring the frontend can be developed without a live data feed dependency.
- Swagger UI interactive documentation is available locally at `http://localhost:8000/docs`.
