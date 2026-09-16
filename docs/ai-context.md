# Agni-Netra: AI & ML Context

This document captures the state of the Artificial Intelligence and Machine Learning implementation within the Agni-Netra platform as of the current phase.

## Overview
Agni-Netra utilizes a **pre-trained XGBoost model** to classify thermal events. As per the strict development constraints, **no new models are trained**, and the ML pipeline focuses purely on *inference and feature extraction* to support the decision engine.

## Model Details
- **Location**: `models/b0/`
- **Algorithm**: XGBoost
- **Classes**: 4 behavior classes (e.g., Industrial Fire, Routine Flare, Agricultural Burn, Unknown/Transient)
- **Input Schema**: The model expects a **24-feature canonical extraction** representing the spatiotemporal footprint and thermal history of an event.
- **Output Schema**: Probabilities across the 4 classes and a dominant label hypothesis.

## Integration Architecture
The AI integration follows this flow:
1. **Raw Ingestion**: Multi-sensor data (FIRMS, INSAT-3DS) is ingested.
2. **Canonical Extraction**: The `backend/app/pipeline` extracts the required 24 features for a given thermal event cluster.
3. **Inference**: The model artifacts (`xgboost_b0.json`, `label_mapping.json`, `model_config.json`) are loaded natively into the FastAPI backend (formerly via `src/model/inference_b0.py`).
4. **Decision Engine**: 
   - Uses the XGBoost outputs to calculate **Abnormality** (divergence from baseline) and **Risk Index** (0-100).
   - Generates an **Operational Priority** (Critical, High, Medium, Low/Monitor).
   - Formulates evidence-grounded **Explanations** (WHY / WHY NOT / WHAT CHANGED).

## Current Development State
- The XGBoost artifacts are successfully integrated into the backend.
- The `seed_demo_data.py` script effectively simulates inference results to populate the SQLite database, mimicking the expected outputs (e.g., EVENT-042: Industrial Fire).
- The Next.js frontend is actively consuming these predictions and priority scores for the dashboard visualization.
