export interface EventItem {
  id: number;
  event_id: string;
  title: string;
  location: string;
  district: string;
  state: string;
  nearby_facility: string;
  latitude: number;
  longitude: number;
  classification: string;
  confidence: number;
  evidence_completeness: number;
  risk_index: number;
  risk_level: string;
  priority: string;
  status: string;
  behavior: string;
  abnormality: string;
  first_seen: string;
  last_seen: string;
  observations_count: number;
  frp_change_pct: number;
  footprint_expansion_factor: number;
  current_assessment: string;
  satellite_image_url?: string;
}

export interface EvidenceItem {
  id: number;
  source: string;
  sensor?: string;
  availability?: boolean;
  evidence_type: string;
  direction: 'SUPPORTING' | 'CONFLICTING' | 'NEUTRAL' | 'MISSING';
  quality: number;
  relevance: number;
  value: string;
  explanation: string;
}

export interface VerificationHistory {
  reviewer: string;
  decision: string;
  comment?: string;
  new_status: string;
  timestamp: string;
}

export interface EventPrediction {
  model_name: string;
  predicted_class: string;
  confidence: number;
  prediction_set: string[];
  uncertainty: number;
  ood_status: boolean;
}

export interface EventDetail extends EventItem {
  facility_type?: string;
  bounding_geojson?: string;
  explanations: {
    why: string[];
    why_not: string[];
    what_changed: string[];
  };
  evidence: EvidenceItem[];
  verifications: VerificationHistory[];
  predictions?: EventPrediction[];
}

export interface TimelinePoint {
  timestamp: string;
  satellite: string;
  frp: number;
  brightness_temperature: number;
  confidence: number;
  quality: string;
}

export interface DashboardSummary {
  total_active: number;
  high_priority: number;
  under_verification: number;
  resolved_24h: number;
  total_events: number;
  active_change_vs_yesterday: number;
  high_priority_change: number;
  under_verification_change: number;
  resolved_change: number;
  system_status: string;
  last_synced: string;
}

export interface DataSourceItem {
  name: string;
  source_type: string;
  status: string;
  configured: boolean;
  available: boolean;
  coverage: string;
  latency_ms: number;
  freshness: string;
  errors: number;
  record_count: number;
  last_fetch: string | null;
  last_observation: string | null;
}
