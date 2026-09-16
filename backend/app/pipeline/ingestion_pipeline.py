from typing import List, Dict, Any
from sqlalchemy.orm import Session
import datetime

from backend.app.core.logging import logger
from backend.app.database.models import Event, Observation, EventObservation, EventEvidence, EventPrediction, RiskScore, PriorityScore, Alert
from backend.app.ingestion.firms import FirmsAdapter
from backend.app.ingestion.insat import InsatAdapter
from backend.app.ingestion.sentinel import SentinelAdapter
from backend.app.ingestion.weather import WeatherAdapter
from backend.app.ingestion.osm import OsmFacilityAdapter
from backend.app.pipeline.event_reconstruction import EventReconstructor
from backend.app.pipeline.feature_extraction import extract_canonical_features
from backend.app.pipeline.risk import calculate_risk_index
from backend.app.pipeline.priority import evaluate_operational_priority
from backend.app.pipeline.evidence_fusion import fuse_event_evidence
from backend.app.ml.inference import inference_service
from backend.app.ml.explainability import format_event_explanations

class IngestionPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.firms_adapter = FirmsAdapter()
        self.insat_adapter = InsatAdapter()
        self.sentinel_adapter = SentinelAdapter()
        self.weather_adapter = WeatherAdapter()
        self.osm_adapter = OsmFacilityAdapter()
        self.reconstructor = EventReconstructor()

    def run_cycle(self) -> Dict[str, Any]:
        logger.info("Starting ingestion and event intelligence cycle...")
        
        # 1. Fetch raw observations
        raw_obs = self.firms_adapter.fetch_recent_observations()
        logger.info(f"Ingested {len(raw_obs)} raw thermal observations.")

        # 2. Persist observations
        db_obs_list = []
        for o in raw_obs:
            db_obs = Observation(**o)
            self.db.add(db_obs)
            db_obs_list.append(db_obs)
        self.db.commit()

        # 3. Cluster observations into Events
        clusters = self.reconstructor.cluster_observations(raw_obs)
        logger.info(f"Clustered observations into {len(clusters)} physical events.")

        processed_events = []
        for idx, cluster in enumerate(clusters, start=1):
            event_id = f"EVENT-AUTO-{int(datetime.datetime.utcnow().timestamp()) % 100000:05d}-{idx:02d}"
            cent_lat = sum(o["latitude"] for o in cluster) / len(cluster)
            cent_lon = sum(o["longitude"] for o in cluster) / len(cluster)
            
            # Match nearest facility
            facility = self.osm_adapter.find_nearest_facility(cent_lat, cent_lon)
            facility_name = facility["name"] if facility else "Open Terrain"
            district = facility["district"] if facility else "Unknown District"
            state = facility["state"] if facility else "India"

            # Features & ML Inference
            features = extract_canonical_features(cluster)
            features["event_id"] = event_id
            pred_res = inference_service.predict_features(features)

            pred_class = pred_res["classification"]["label"]
            conf = pred_res["classification"]["confidence"]

            # Context & Environmental data
            weather = self.weather_adapter.get_conditions(cent_lat, cent_lon, cluster[-1]["timestamp"])
            sentinel = self.sentinel_adapter.get_corroboration(cent_lat, cent_lon, cluster[-1]["timestamp"])

            # Risk & Priority
            duration = features.get("duration_hours", 1.0)
            max_frp = features.get("max_frp", 20.0)
            dist_km = facility.get("distance_km", 10.0) if facility else 10.0
            footprint_factor = 2.5 if features.get("expanding_indicator") else 1.1

            risk_idx, risk_level, risk_factors = calculate_risk_index(
                frp_max=max_frp,
                footprint_factor=footprint_factor,
                duration_hours=duration,
                facility_distance_km=dist_km,
                is_critical_facility=dist_km < 3.0
            )

            abnormality = "Highly Abnormal" if (max_frp > 100 or risk_idx > 70) else "Normal"
            behavior = "Escalating" if features.get("sudden_frp_increase") else ("Persistent" if duration > 5 else "Transient")

            priority_level, justification = evaluate_operational_priority(
                risk_index=risk_idx,
                abnormality=abnormality,
                source_hypothesis=pred_class,
                verification_status="Needs Verification",
                confidence=conf
            )

            # Evidence fusion
            evidence_items, completeness = fuse_event_evidence(
                event_id=event_id,
                observations=cluster,
                facility_info=facility or {},
                weather_info=weather,
                sentinel_info=sentinel,
                source_class=pred_class
            )

            # Explanations
            explanations = format_event_explanations(
                source_class=pred_class,
                confidence=conf,
                behavior=behavior,
                abnormality=abnormality,
                frp_change_pct=features.get("frp_change", 0.0),
                footprint_factor=footprint_factor,
                duration_hours=duration
            )

            # Persist Event
            event_obj = Event(
                event_id=event_id,
                title=f"{pred_class} (Hypothesis)",
                location_name=f"{facility_name}, {district}",
                district=district,
                state=state,
                nearby_facility=facility_name,
                facility_type=facility.get("type") if facility else "Natural",
                first_detected=cluster[0]["timestamp"],
                last_observed=cluster[-1]["timestamp"],
                centroid_lat=cent_lat,
                centroid_lon=cent_lon,
                bounding_geojson=self.reconstructor.create_bounding_geojson(cluster),
                observation_count=len(cluster),
                current_state="Active",
                source_hypothesis=pred_class,
                behavior=behavior,
                abnormality=abnormality,
                risk_level=risk_level,
                risk_index=risk_idx,
                priority_level=priority_level,
                confidence=conf,
                evidence_completeness=completeness,
                verification_status="Needs Verification" if priority_level in ["Critical", "High"] else "Monitoring",
                frp_change_pct=features.get("frp_change", 0.0),
                footprint_expansion_factor=footprint_factor,
                current_assessment=f"Automated pipeline assessment: {pred_class} detected with {conf*100:.0f}% confidence.",
                why_explanation=explanations["why"],
                why_not_explanation=explanations["why_not"],
                what_changed_explanation=explanations["what_changed"]
            )
            self.db.add(event_obj)
            self.db.commit()
            self.db.refresh(event_obj)

            # Save Evidence
            for ev in evidence_items:
                ev_obj = EventEvidence(event_id=event_id, **ev)
                self.db.add(ev_obj)

            # Save Alert if Critical or High
            if priority_level in ["Critical", "High"]:
                alert = Alert(
                    event_id=event_id,
                    alert_type="Automated Priority Escalation",
                    severity=priority_level,
                    title=f"{priority_level} Event: {pred_class} at {facility_name}",
                    message=f"Event {event_id} exhibits {abnormality} behavior with Risk Index {risk_idx}/100."
                )
                self.db.add(alert)

            self.db.commit()
            processed_events.append(event_id)

        logger.info(f"Pipeline cycle completed. Processed {len(processed_events)} events.")
        return {
            "status": "SUCCESS",
            "observations_ingested": len(raw_obs),
            "events_reconstructed": len(processed_events),
            "event_ids": processed_events
        }
