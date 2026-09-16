# Agni-Netra System Architecture

**Tagline:** "The satellite sees heat. Agni-Netra understands the event."

## 1. System Overview
Agni-Netra is a real-time, event-centric geospatial thermal intelligence platform. It ingests satellite thermal anomaly data, fuses it with meteorological and infrastructure GIS data, and uses AI/ML to classify events, assess risk, and alert analysts.

## 2. Technical Stack
- **Frontend:** Next.js, React, TailwindCSS, MapLibre GL JS, Recharts
- **Backend:** FastAPI, Python, SQLAlchemy, Uvicorn
- **Database:** SQLite (Strict compliance - No Docker, No Postgres, No Redis)
- **AI/ML:** XGBoost for classification, scikit-learn for calibration and SHAP for explainability

## 3. Core Modules

### 3.1 Data Ingestion Pipeline
Ingests active fire data from LEO satellites (VIIRS) and GEO satellites (INSAT-3DS).
- Formats data into `Observation` records.
- Standardizes spatial (Lat/Lon) and temporal (Timestamp) fields.

### 3.2 Event Reconstruction Engine
Groups raw thermal pixels (Observations) into cohesive `Event` entities.
- Spatial grouping based on proximity.
- Temporal persistence tracking.
- Tracks footprint expansion and FRP escalation.

### 3.3 ML Classification & Inference
Applies the pre-trained `b0_source_classifier` (XGBoost).
- Generates probabilities for 5 hypotheses: Industrial Fire, Routine Flare, Agricultural Burn, Wildfire, Unknown.
- Calibrates confidence scores.

### 3.4 Multi-Sensor Evidence Fusion
Gathers supporting or conflicting evidence for each hypothesis.
- Example: High wind + expanding footprint + proximity to refinery = Industrial Fire evidence.
- Records data into an immutable Evidence Ledger.

### 3.5 Risk & Priority Engine
Calculates the Risk Index (0-100) based on hazard intensity, exposure, and vulnerability.
- Flags Critical/High priority events for immediate analyst review.

### 3.6 Explainability Engine
Generates human-readable explanations:
- *Why is this classification chosen?*
- *Why not a routine flare?*
- *What changed from historical baselines?*

### 3.7 Human-in-the-Loop Verification
Allows analysts to review evidence, mark as Confirmed / Rejected / Needs Data.
- Creates an audit trail of decisions (`VerificationRecord`).

### 3.8 Dashboard & Real-time Map
- Live updating map powered by MapLibre GL.
- Color-coded severity indicators.

### 3.9 Analytics & Reporting
- Visualizes event trends over time using Recharts.
- Tracks classification distribution and priority levels.

### 3.10 Facilities Directory
- Maintains a registry of monitored critical infrastructure.
- Links events directly to nearby facilities.

## 4. Development Guidelines
- Always use **NO DATA over FAKE DATA**.
- The system must function entirely on `localhost` without external services (Docker, Redis, PostGIS).
- Aesthetics must remain clean, minimal, and engineering-oriented.
