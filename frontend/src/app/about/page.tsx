'use client';

import React, { useState } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import {
  Globe, Shield, Cpu, Zap, Activity, Info, Search, Eye, Target, Users,
  Satellite, Radio, Layers, Wind, MapPin, BarChart3, Brain, CheckCircle2,
  AlertTriangle, ArrowRight, Flame, TrendingUp, ShieldCheck, FileSearch,
  Gauge, Bell, HelpCircle, Lock, Lightbulb, CircleDot, ArrowDown,
  ChevronDown, ChevronUp, Database, Sparkles, Scale, BookOpen, Clock,
  FileText, ShieldAlert, CheckCircle, XCircle, AlertOctagon, CornerDownRight,
  Filter, Crosshair, Thermometer, Binary, RefreshCw
} from 'lucide-react';

/* ─────────────────────────────────────────────────────────────
   TECHNICAL PROVENANCE BADGES
   Product-Oriented Scientific Categories (Zero Academic Jargon)
───────────────────────────────────────────────────────────── */

type ProvenanceType =
  | 'PUBLISHED_RESULT'
  | 'AGNI_NETRA_DEMO'
  | 'SENSOR_SPEC'
  | 'ADVANCED_CAPABILITY'
  | 'VALIDATION_NEEDED';

function ProvenanceBadge({ type, label }: { type: ProvenanceType; label?: string }) {
  const styles: Record<ProvenanceType, { text: string; bg: string; border: string; defaultLabel: string }> = {
    PUBLISHED_RESULT: {
      text: 'text-purple-700',
      bg: 'bg-purple-50',
      border: 'border-purple-200',
      defaultLabel: 'PUBLISHED RESULT',
    },
    AGNI_NETRA_DEMO: {
      text: 'text-blue-700',
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      defaultLabel: 'AGNI-NETRA DEMO',
    },
    SENSOR_SPEC: {
      text: 'text-cyan-700',
      bg: 'bg-cyan-50',
      border: 'border-cyan-200',
      defaultLabel: 'SENSOR SPECIFICATION',
    },
    ADVANCED_CAPABILITY: {
      text: 'text-amber-700',
      bg: 'bg-amber-50',
      border: 'border-amber-200',
      defaultLabel: 'ADVANCED CAPABILITY',
    },
    VALIDATION_NEEDED: {
      text: 'text-rose-700',
      bg: 'bg-rose-50',
      border: 'border-rose-200',
      defaultLabel: 'VALIDATION NEEDED',
    },
  };

  const item = styles[type];
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase border ${item.bg} ${item.text} ${item.border}`}
    >
      [{label || item.defaultLabel}]
    </span>
  );
}

/* ─────────────────────────────────────────────────────────────
   ORIGINAL PRESERVED DATA
───────────────────────────────────────────────────────────── */

const pillars = [
  { icon: Satellite, label: 'Detect', desc: 'Multi-source thermal observations' },
  { icon: Search, label: 'Understand', desc: 'AI + contextual analysis' },
  { icon: Target, label: 'Prioritize', desc: 'Risk & impact assessment' },
  { icon: Users, label: 'Enable Action', desc: 'Human verification & alerts' },
];

const technicalEnablers = [
  { name: 'VIIRS Nightfire', desc: 'High-T thermal physics → Multispectral Planck fitting for hot persistent sources and flare characterization.' },
  { name: 'INSAT-3DS', desc: 'High-cadence GEO monitoring → 4 km / 15–30 min Indian thermal observations (ISRO/SAC validation).' },
  { name: 'Sentinel-2 SWIR', desc: 'Fine spatial refinement → 20 m optical/SWIR context for facility-level thermal segmentation and corroboration.' },
  { name: 'TROPOMI', desc: 'Atmospheric corroboration → NO₂/SO₂/CO evidence to support or challenge thermal-event hypotheses.' },
  { name: 'NiSAR / Sentinel-1', desc: 'Structural context → SAR-based infrastructure/surface-change evidence (context layer).' },
  { name: 'AlphaEarth', desc: 'Facility fingerprint + novelty → 10 m, 64-dimensional contextual embeddings for structural/change and OOD signals.' },
  { name: 'CAAQMS', desc: 'Ground air-quality context → 15–60 minute cross-checks from ~300 sites (proposed/pilot, not standalone proof).' },
];

const workflowSteps = [
  'Satellite / Sensor Data',
  'Thermal Observation',
  'Event Reconstruction',
  'Source Attribution',
  'Historical Behavior',
  'Abnormality Detection',
  'Multi-Sensor Evidence Fusion',
  'Uncertainty / OOD',
  'Risk Assessment',
  'Priority',
  'Human Verification',
  'Action & Monitoring',
];

const whyDifferent = [
  { capability: 'Persistent Event Intelligence', matter: 'Converts fragmented observations into one evolving event.' },
  { capability: 'Dual Thermal Intelligence', matter: 'Detects both high-T flares and lower-T persistent industrial heat.' },
  { capability: 'Evidence Fusion + Conflict Handling', matter: 'Combines independent sensors without forcing conflicting evidence into one answer.' },
  { capability: 'Historical Fingerprint + Change Detection', matter: 'Determines whether current behavior is normal or abnormal for that location.' },
  { capability: 'Uncertainty + OOD + Abstention', matter: 'Can return Unknown / Insufficient Evidence instead of forcing a wrong class.' },
  { capability: 'Risk → Priority → Verification', matter: 'Converts detection into an actionable, human-verifiable operational decision.' },
];

const existingGaps = [
  { title: 'Thermal anomaly ≠ source', desc: 'Same thermal signature can represent fire, flare, biomass or other heat.' },
  { title: 'Observations ≠ physical event', desc: 'Multiple detections may belong to one evolving incident.' },
  { title: 'Coarse spatial resolution', desc: 'Thermal pixels may not identify the exact facility/unit involved.' },
  { title: 'Revisit & verification latency', desc: 'Different sensors have different revisit times and data latency.' },
  { title: 'High-T bias', desc: 'Flare-focused methods can miss lower-temperature industrial heat.' },
  { title: 'No adaptive normality / uncertainty', desc: 'Static detection cannot reliably handle abnormal, conflicting or unknown events.' },
  { title: 'Limited Indian ground truth', desc: 'Models need India-/facility-specific validation and transfer testing.' },
];

const solutions = [
  { title: 'Persistent Event Reconstruction', desc: 'Multi-sensor observations → physical event ID → lifecycle tracking.' },
  { title: 'Multi-Sensor Evidence Fusion', desc: 'FIRMS/VIIRS + INSAT-3DS + Sentinel + NiSAR/SAR + TROPOMI + weather + geospatial context.' },
  { title: 'Dual Thermal Intelligence', desc: 'High-T VNF/Planck physics + low-T Temporal/DBSCAN facility-source detection.' },
  { title: 'Historical & Behavioral Intelligence', desc: 'Facility thermal fingerprint + change-point detection → normal vs abnormal behavior.' },
  { title: 'Risk Assessment', desc: 'Comprehensive risk & exposure assessment with priority-based response.' },
  { title: 'Uncertainty-Aware Decision Intelligence', desc: 'Evidence conflict + OOD/abstention + conformal uncertainty → Risk → Priority → Verification.' },
];

const benefits = [
  { title: 'Faster Incident Awareness', desc: 'Earlier identification of emerging thermal events.' },
  { title: 'Reduced False Alerts', desc: 'Multi-sensor evidence helps distinguish routine heat from abnormal events.' },
  { title: 'Facility-Level Situational Awareness', desc: 'Clearer picture of what is happening and where.' },
  { title: 'Abnormal Event Detection', desc: 'Identifies behavior that deviates from normal.' },
  { title: 'Risk & Exposure Assessment', desc: 'Assesses event severity and potential impact.' },
  { title: 'Priority-Based Response', desc: 'Focuses attention where it matters most.' },
  { title: 'Explainable & Auditable Decisions', desc: 'WHY / WHY NOT / WHAT CHANGED with evidence.' },
  { title: 'Uncertainty-Aware Intelligence', desc: 'Handles unknown or conflicting evidence safely.' },
];

const aiModels = [
  { icon: Flame, name: 'Industrial Source Classifier', desc: 'Predicts likely source (flare, fire, etc.)' },
  { icon: Activity, name: 'Behavior & Abnormality Model', desc: 'Detects persistence, recurrence, unusual behavior' },
  { icon: Gauge, name: 'Risk & Priority Model', desc: 'Estimates risk and operational priority' },
  { icon: MapPin, name: 'Context / Embedding Model', desc: 'Facility fingerprint + novelty (AlphaEarth)' },
  { icon: HelpCircle, name: 'Uncertainty & OOD Layer', desc: 'Handles unknown / conflicting cases' },
];

const techStack = [
  'Python', 'FastAPI', 'SQLite', 'Next.js', 'React',
  'MapLibre GL', 'GeoPandas', 'Shapely', 'Scikit-learn', 'XGBoost',
];

/* ─────────────────────────────────────────────────────────────
   13-STAGE COMPACT PRODUCT PIPELINE
───────────────────────────────────────────────────────────── */

interface PipelineStage {
  id: number;
  name: string;
  shortDesc: string;
  details: string;
  inputs: string[];
  outputs: string[];
  keyPrinciple: string;
  badge: { type: ProvenanceType; text: string };
}

const pipelineStages: PipelineStage[] = [
  {
    id: 1,
    name: 'Observation',
    shortDesc: 'Multi-sensor ingestion across orbital & in-situ streams.',
    details: 'Raw radiometric observations captured by NASA FIRMS (VIIRS 375m), INSAT-3DS (4km GEO), Sentinel-2 MSI, Sentinel-1/NISAR SAR, TROPOMI atmospheric chemistry, CAAQMS ground monitors, and OpenWeather.',
    inputs: ['Raw satellite radiance', 'Thermal infrared channels', 'Ground telemetry'],
    outputs: ['Raw hotspot records with coordinates, timestamp, sensor metadata'],
    keyPrinciple: 'A thermal anomaly is an observation of thermal activity. It is NOT automatically an industrial fire, flare, or confirmed emergency.',
    badge: { type: 'SENSOR_SPEC', text: 'SENSOR SPECIFICATION' },
  },
  {
    id: 2,
    name: 'Quality Check',
    shortDesc: 'Schema unification, coordinate sanity, and saturation defense.',
    details: 'Standardizes disparate sensor streams into the NormalizedObservation contract. Implements finite-bounds validation, spatial truncation defense, and flags optical/detector saturation risks before downstream ingestion.',
    inputs: ['Raw sensor records'],
    outputs: ['NormalizedObservation schema', 'Quality flags (DEGRADED, EXCLUDED, USABLE)'],
    keyPrinciple: 'Detector saturation indicates sensor non-linearity, never higher fire confidence or physical temperature.',
    badge: { type: 'AGNI_NETRA_DEMO', text: 'CURRENT IMPLEMENTATION' },
  },
  {
    id: 3,
    name: 'Event Reconstruction',
    shortDesc: 'Associating isolated detections into persistent physical entities.',
    details: 'Associates disjoint satellite passes across time using Haversine distance clustering and temporal windowing into persistent event entities (e.g. AGN-E-000421), generating bounding GeoJSON footprints.',
    inputs: ['NormalizedObservations over rolling time window'],
    outputs: ['Persistent Event ID', 'Event Centroid', 'Footprint GeoJSON', 'Observation Count'],
    keyPrinciple: 'Individual satellite hotspot pixels are transformed into single evolving physical events with unified lifecycles.',
    badge: { type: 'AGNI_NETRA_DEMO', text: 'AGNI-NETRA DEMO' },
  },
  {
    id: 4,
    name: 'Measurement',
    shortDesc: 'Extraction of physical intensity, expansion, and duration metrics.',
    details: 'Calculates Fire Radiative Power (FRP in MW), brightness temperature extrema (T4/T11 in Kelvin), footprint expansion ratios, and observation timeline duration without inventing unmeasured physical constants.',
    inputs: ['Event observation clusters'],
    outputs: ['Max FRP (MW)', 'Brightness Temp (K)', 'Footprint Ratio (e.g. 5.5×)', 'Duration (Hours)'],
    keyPrinciple: 'FRP is a satellite-derived radiative metric, not a direct thermometer measurement of ground facility temperature.',
    badge: { type: 'AGNI_NETRA_DEMO', text: 'AGNI-NETRA DEMO' },
  },
  {
    id: 5,
    name: 'Historical Baseline',
    shortDesc: 'Multi-year facility thermal fingerprint and recurrence profile comparison.',
    details: 'Compares current event characteristics against long-term historical behavior for the specific spatial coordinate/facility, establishing expected baseline FRP, duration patterns, and recurrence intervals.',
    inputs: ['Facility coordinates', 'Historical observation records', 'OSM/GIDC registry'],
    outputs: ['Historical Baseline FRP (e.g. 87.3 MW)', 'Baseline Footprint', 'History Tier'],
    keyPrinciple: 'Historical normality provides the baseline reference against which deviations are quantified.',
    badge: { type: 'AGNI_NETRA_DEMO', text: 'AGNI-NETRA DEMO' },
  },
  {
    id: 6,
    name: 'Source Attribution',
    shortDesc: 'Multi-evidence classification across 8 supported source taxonomies.',
    details: 'Predicts source class: Industrial Fire, Routine Flare, Emergency Flare, Wildfire, Agricultural Burn, Mining Heat, Landfill/Other, or Unknown. Incorporates contextual proximity without allowing facility type alone to dictate classification.',
    inputs: ['Canonical feature vector (AGN-FEATURES-1.1)', 'Proximity buffers'],
    outputs: ['Predicted Source Class', 'Model Class Probabilities', 'Decision State'],
    keyPrinciple: 'Proximity to an industrial facility is supporting context; it does not alone prove that the facility generated the fire.',
    badge: { type: 'AGNI_NETRA_DEMO', text: 'AGNI-NETRA DEMO' },
  },
  {
    id: 7,
    name: 'Behavior',
    shortDesc: 'Event state machine modeling lifecycle and thermal trends.',
    details: 'Tracks transition states: NEW → PERSISTING → STABLE → ESCALATING → ABNORMAL → RESOLVING. Evaluates Low-T persistent heat signatures and High-T flare-like radiative stability.',
    inputs: ['Temporal observation sequence', 'FRP trajectory', 'Spatial growth'],
    outputs: ['Event State', 'State Confidence', 'Behavioral Driver Codes'],
    keyPrinciple: 'Behavior ("How is it behaving?") is strictly decoupled from Source Identity ("What is it?") and Abnormality.',
    badge: { type: 'AGNI_NETRA_DEMO', text: 'AGNI-NETRA DEMO' },
  },
  {
    id: 8,
    name: 'Abnormality',
    shortDesc: 'Mathematical deviation quantification against historical baselines.',
    details: 'Quantifies deviation score [0.0, 1.0] and categorizes levels (NORMAL, UNUSUAL, HIGHLY_ABNORMAL). Emits auditable change statements when sudden spikes or footprint blowouts occur.',
    inputs: ['Current FRP & footprint', 'Historical baseline distribution'],
    outputs: ['Abnormality Score', 'Abnormality Level', 'Change Summary'],
    keyPrinciple: 'Persistence does not equal abnormality. A routine flare may be 100% persistent yet 0% abnormal.',
    badge: { type: 'AGNI_NETRA_DEMO', text: 'AGNI-NETRA DEMO' },
  },
  {
    id: 9,
    name: 'Evidence Fusion',
    shortDesc: 'Synthesizes multi-sensor evidence graph with explicit directionality.',
    details: 'Aggregates independent evidence families (Thermal Physics, GEO Continuity, Optical SWIR, SAR Surface, Atmospheric, Weather, Context) attributing SUPPORTING, CONFLICTING, NEUTRAL, or MISSING directions.',
    inputs: ['All active sensor adapter results'],
    outputs: ['Evidence Graph / Ledger', 'Evidence Completeness Score', 'Evidence Convergence'],
    keyPrinciple: 'Independent sensor evidence must never be forced into artificial consensus; conflicting signals are explicitly preserved.',
    badge: { type: 'AGNI_NETRA_DEMO', text: 'AGNI-NETRA DEMO' },
  },
  {
    id: 10,
    name: 'Uncertainty',
    shortDesc: 'Confidence calibration, novelty detection, and safe abstention.',
    details: 'Evaluates feature space bounds for novelty. Applies contradiction penalties when evidence conflicts. Emits safe UNKNOWN or INSUFFICIENT_OBSERVATION decision states when data is inadequate.',
    inputs: ['Model confidence', 'Novelty score', 'Evidence contradiction vector'],
    outputs: ['Calibrated Decision Confidence', 'Prediction Set', 'Abstention Reason Codes'],
    keyPrinciple: 'UNKNOWN is a safe, valid operational answer. The system never forces an arbitrary class when evidence is lacking.',
    badge: { type: 'AGNI_NETRA_DEMO', text: 'AGNI-NETRA DEMO' },
  },
  {
    id: 11,
    name: 'Risk',
    shortDesc: 'Physical hazard modeling combined with consequence/exposure impact.',
    details: 'Computes Base Risk = sqrt(Hazard × Impact) on a transparent 0–100 scale. Combines thermal extremeness, growth rate, and critical infrastructure proximity without hiding unexposed formulas.',
    inputs: ['Inherent source hazard', 'FRP intensity modifier', 'Facility impact & exposure'],
    outputs: ['Hazard Score [0-1]', 'Impact Score [0-1]', 'Risk Index [0-100]', 'Risk Level'],
    keyPrinciple: 'Risk Index is a transparent decision-support score, not a certified physical hazard guarantee.',
    badge: { type: 'AGNI_NETRA_DEMO', text: 'AGNI-NETRA DEMO' },
  },
  {
    id: 12,
    name: 'Priority',
    shortDesc: 'Operational triage score decoupling physical hazard from response urgency.',
    details: 'Calculates operational priority (P0 Critical, P1 Urgent, P2 Evaluate, P3 Monitor, P4 Informational) by weighting Base Risk (45%), Urgency (30%), Impact (15%), and Verification Need (10%).',
    inputs: ['Base Risk Score', 'Urgency Drivers', 'Impact Context', 'Verification Flag'],
    outputs: ['Priority Level (P0-P4)', 'Operational Action Recommendation', 'Priority Drivers'],
    keyPrinciple: 'Risk asks "How concerning is this event?" Priority asks "Which event should the analyst investigate first?"',
    badge: { type: 'AGNI_NETRA_DEMO', text: 'AGNI-NETRA DEMO' },
  },
  {
    id: 13,
    name: 'Human Verification',
    shortDesc: 'Closing the operational loop with analyst review, audit, and feedback.',
    details: 'Presents explainable AI summaries (WHY, WHY NOT, WHAT CHANGED) alongside raw evidence to human analysts. Enables one-click verification: CONFIRM, REJECT, or REQUEST MORE EVIDENCE.',
    inputs: ['AI Intelligence Package', 'Evidence Ledger', 'XAI Triad Explanations'],
    outputs: ['Verification State (HUMAN_VERIFIED / DISPUTED)', 'Audit Trail Timestamp'],
    keyPrinciple: 'Agni-Netra is AI decision support. Human verification remains an essential operational checkpoint.',
    badge: { type: 'AGNI_NETRA_DEMO', text: 'AGNI-NETRA DEMO' },
  },
];

/* ─────────────────────────────────────────────────────────────
   SENSOR CONTRIBUTION TABLE DATA
───────────────────────────────────────────────────────────── */

interface SensorContribution {
  source: string;
  whatItObserves: string;
  agniNetraUse: string;
  whatItDoesNotProve: string;
  validationStatus: {
    statusText: string;
    type: ProvenanceType;
  };
}

const sensorContributions: SensorContribution[] = [
  {
    source: 'NASA FIRMS / VIIRS',
    whatItObserves: 'Thermal anomaly, FRP (MW), Brightness Temp (K), timestamp and detection coordinates.',
    agniNetraUse: 'Primary thermal observation backbone for hotspot discovery and baseline FRP tracking.',
    whatItDoesNotProve: 'Does NOT prove industrial causation or whether heat is a routine flare vs industrial fire.',
    validationStatus: {
      statusText: 'Operational global LEO product. Validated thermal physics (Planck law).',
      type: 'SENSOR_SPEC',
    },
  },
  {
    source: 'INSAT-3DS',
    whatItObserves: 'High-cadence geostationary thermal context (4 km resolution at 15–30 min intervals).',
    agniNetraUse: 'Temporal evolution, rapid-scan continuity, and diurnal thermal persistence tracking.',
    whatItDoesNotProve: 'Does NOT provide facility-level localization (4km pixel) and is not gold-standard ground truth.',
    validationStatus: {
      statusText: 'Published ISRO validation: POD = 45.31%, Precision = 73.34%, FAR = 26.66% (vs MODIS).',
      type: 'PUBLISHED_RESULT',
    },
  },
  {
    source: 'Sentinel-2 SWIR',
    whatItObserves: 'Fine spatial optical/SWIR context (20m resolution B11/B12 reflectance).',
    agniNetraUse: 'Spatial refinement, facility boundary alignment, and plume/burned-area corroboration.',
    whatItDoesNotProve: 'Does NOT provide continuous real-time monitoring due to 5-day revisit latency.',
    validationStatus: {
      statusText: 'Published performance: 92.8% daytime classification accuracy (11,000 scenes).',
      type: 'PUBLISHED_RESULT',
    },
  },
  {
    source: 'Sentinel-1 / NISAR',
    whatItObserves: 'Structural and surface-change context (SAR backscatter, coherence, ground deformation).',
    agniNetraUse: 'Complementary structural evidence and retrospective post-incident confirmation.',
    whatItDoesNotProve: 'Does NOT measure active fire temperature and is NOT a real-time trigger (~48h latency).',
    validationStatus: {
      statusText: 'NISAR S-band operational via Bhoonidhi (48h latency); L-band calibrated provisional products.',
      type: 'SENSOR_SPEC',
    },
  },
  {
    source: 'TROPOMI (Sentinel-5P)',
    whatItObserves: 'Atmospheric gas information (column concentrations of NO₂, SO₂, and CO).',
    agniNetraUse: 'Atmospheric corroboration layer verifying combustion plumes downwind of active events.',
    whatItDoesNotProve: 'Does NOT prove which specific industrial stack or facility caused the event.',
    validationStatus: {
      statusText: 'Operational atmospheric chemistry telemetry (7 × 3.5 km resolution).',
      type: 'SENSOR_SPEC',
    },
  },
  {
    source: 'Weather (ECMWF/OpenWeather)',
    whatItObserves: 'Wind speed, wind direction, humidity, ambient temperature, and dispersion conditions.',
    agniNetraUse: 'Plume dispersion trajectory modeling and smoke exposure risk evaluation.',
    whatItDoesNotProve: 'Does NOT indicate whether a fire exists; strictly models physical dispersion environment.',
    validationStatus: {
      statusText: 'Standard operational meteorological feeds.',
      type: 'SENSOR_SPEC',
    },
  },
  {
    source: 'OSM / GIDC Facility Data',
    whatItObserves: 'Facility boundaries, chemical estate polygons (GIDC), critical infrastructure, and land use.',
    agniNetraUse: 'Spatial attribution support, contextual exposure scoring, and facility profile binding.',
    whatItDoesNotProve: 'Proximity to an industrial facility does NOT automatically make an event an industrial accident.',
    validationStatus: {
      statusText: 'Integrated OpenStreetMap + Gujarat GIDC database layers in current implementation.',
      type: 'AGNI_NETRA_DEMO',
    },
  },
  {
    source: 'CAAQMS (CPCB Ground)',
    whatItObserves: 'Ground air-quality context (in-situ PM2.5, PM10, SO₂, NOx at 15–60 min intervals).',
    agniNetraUse: 'Environmental corroboration pilot layer cross-checking downwind particulate spikes.',
    whatItDoesNotProve: 'Does NOT provide dense localized ground truth across non-monitored rural corridors.',
    validationStatus: {
      statusText: 'Pilot validation layer (~300 stations nationwide); not certified ground truth.',
      type: 'VALIDATION_NEEDED',
    },
  },
  {
    source: 'AlphaEarth Foundations',
    whatItObserves: 'Contextual embeddings (10m resolution, 64-dimensional multi-temporal representations).',
    agniNetraUse: 'Facility fingerprinting, contextual similarity, change detection, and novelty/OOD support.',
    whatItDoesNotProve: 'Pretrained capability does NOT guarantee zero-shot Indian industrial accuracy without local calibration.',
    validationStatus: {
      statusText: 'Published capability (2017–2025 archive); Agni-Netra transfer in pilot stage.',
      type: 'ADVANCED_CAPABILITY',
    },
  },
];

/* ─────────────────────────────────────────────────────────────
   SCORECARD: AGNI-NETRA VS PUBLISHED TECHNICAL PERFORMANCE
───────────────────────────────────────────────────────────── */

interface ScorecardItem {
  capability: string;
  publishedResult: string;
  publishedBadge: ProvenanceType;
  agniNetraUse: string;
  agniNetraBadge: ProvenanceType;
}

const capabilityScorecard: ScorecardItem[] = [
  {
    capability: 'VIIRS Nightfire / Planck Thermal Physics',
    publishedResult: 'Published thermal characterization; Planck curve fitting; NIR/SWIR doubled detections.',
    publishedBadge: 'PUBLISHED_RESULT',
    agniNetraUse: 'Primary thermal intelligence (Reduced Thermal Physics Mode active in pipeline).',
    agniNetraBadge: 'AGNI_NETRA_DEMO',
  },
  {
    capability: 'INSAT-3DS High-Cadence GEO Detection',
    publishedResult: '45.31% POD / 73.34% precision / 26.66% FAR (ISRO published study vs MODIS).',
    publishedBadge: 'PUBLISHED_RESULT',
    agniNetraUse: 'Temporal thermal corroboration and 15-minute continuous event evolution tracking.',
    agniNetraBadge: 'AGNI_NETRA_DEMO',
  },
  {
    capability: 'Sentinel-2 / SWIR Classification',
    publishedResult: '92.8% published daytime classification result; ~79.3% nighttime (11,000 scenes).',
    publishedBadge: 'PUBLISHED_RESULT',
    agniNetraUse: 'Spatial & SWIR corroboration layer for facility-level thermal footprint refinement.',
    agniNetraBadge: 'AGNI_NETRA_DEMO',
  },
  {
    capability: 'SAR / NISAR Structural Confirmation',
    publishedResult: '~48 h operational data latency through Bhoonidhi; provisional L-band available.',
    publishedBadge: 'SENSOR_SPEC',
    agniNetraUse: 'Structural confirmation layer and post-incident surface deformation audit.',
    agniNetraBadge: 'AGNI_NETRA_DEMO',
  },
  {
    capability: 'AlphaEarth Foundation Embeddings',
    publishedResult: '10 m / 64-dimensional multi-temporal embeddings (2017–2025 archive).',
    publishedBadge: 'PUBLISHED_RESULT',
    agniNetraUse: 'Facility context, landscape similarity, and Out-of-Distribution (OOD) novelty support.',
    agniNetraBadge: 'ADVANCED_CAPABILITY',
  },
  {
    capability: 'Conformal Prediction Uncertainty Sets',
    publishedResult: 'Distribution-free finite-sample coverage guarantees (e.g. 90% confidence sets).',
    publishedBadge: 'PUBLISHED_RESULT',
    agniNetraUse: 'Prediction set generation & OOD bounds checking active in ML inference engine.',
    agniNetraBadge: 'AGNI_NETRA_DEMO',
  },
  {
    capability: 'Indian Industrial Source Classification',
    publishedResult: 'Published literature reports ~77% accuracy on global VIIRS time-series datasets.',
    publishedBadge: 'PUBLISHED_RESULT',
    agniNetraUse: 'Demonstrated on curated/synthetic Indian industrial scenarios; field pilot underway.',
    agniNetraBadge: 'VALIDATION_NEEDED',
  },
];

/* ─────────────────────────────────────────────────────────────
   TECHNICAL MEASUREMENT DICTIONARY (14 Terms)
───────────────────────────────────────────────────────────── */

interface DictionaryItem {
  term: string;
  category: string;
  whatItMeans: string;
  input: string;
  howDerived: string;
  unit: string;
  limitation: string;
  badge: ProvenanceType;
}

const measurementDictionary: DictionaryItem[] = [
  {
    term: 'FRP (Fire Radiative Power)',
    category: 'Thermal Physics',
    whatItMeans: 'A satellite-derived measure associated with radiative energy release of a detected thermal source in megawatts.',
    input: 'Mid-Infrared (MWIR ~3.9 µm) and Long-Wave Infrared (LWIR ~11 µm) spectral radiances.',
    howDerived: 'Derived by satellite product algorithm based on radiance deficit relative to background.',
    unit: 'Megawatts (MW)',
    limitation: 'FRP is a satellite-derived product value. It is not a direct ground measurement of facility temperature.',
    badge: 'SENSOR_SPEC',
  },
  {
    term: 'Footprint',
    category: 'Spatial Geometry',
    whatItMeans: 'The spatial extent multiplier associated with clustered thermal observations over time.',
    input: 'Coordinates of associated satellite observation centroids over the event clustering window.',
    howDerived: 'Calculated via convex hull GeoJSON geometry or spatial bounding relative to baseline.',
    unit: 'Multiplier (e.g. 5.5×) or Bounding Envelope',
    limitation: 'Reflects satellite pixel cluster extent; does not invent sub-pixel physical area if unexposed.',
    badge: 'AGNI_NETRA_DEMO',
  },
  {
    term: 'Observation Count',
    category: 'Event History',
    whatItMeans: 'Total number of valid satellite and sensor detections correlated to a single persistent event.',
    input: 'Count of associated observations in the event record.',
    howDerived: 'Direct tally of NormalizedObservation records linked to the persistent event ID.',
    unit: 'Count (integer)',
    limitation: 'Dependent on orbital pass schedules and cloud cover over the scene.',
    badge: 'AGNI_NETRA_DEMO',
  },
  {
    term: 'Persistence',
    category: 'Temporal Dynamics',
    whatItMeans: 'Repeated thermal detection across multiple consecutive satellite passes or sensor overflights.',
    input: 'Time-series observation frequency and temporal gap intervals.',
    howDerived: 'Temporal clustering continuity over rolling observation windows.',
    unit: 'Score [0.0, 1.0] or State Flag',
    limitation: 'Persistence alone does NOT mean abnormality. Routine flares are naturally persistent.',
    badge: 'AGNI_NETRA_DEMO',
  },
  {
    term: 'Duration',
    category: 'Temporal Dynamics',
    whatItMeans: 'The elapsed time between earliest and latest recorded satellite observations for an active event.',
    input: 'First observation timestamp (t_first) and latest observation timestamp (t_last).',
    howDerived: 'Duration = t_last − t_first (expressed in hours or days).',
    unit: 'Hours / Days',
    limitation: 'Underestimates true duration if initial satellite pass occurred after physical ignition.',
    badge: 'AGNI_NETRA_DEMO',
  },
  {
    term: 'Historical Baseline',
    category: 'Historical Profile',
    whatItMeans: 'The expected reference thermal behavior (FRP, footprint, duration) for a specific facility or coordinate.',
    input: 'Multi-year historical observations filtered by spatial polygon / facility buffer.',
    howDerived: 'Statistical mean, median, and variance calculated across pre-event historical periods.',
    unit: 'MW / Footprint Multiplier',
    limitation: 'Sparse or newly constructed facilities may have limited historical baseline data.',
    badge: 'AGNI_NETRA_DEMO',
  },
  {
    term: 'Baseline Deviation',
    category: 'Abnormality',
    whatItMeans: 'Percentage deviation of current event measurements relative to historical baseline.',
    input: 'Current FRP (F_current) and Historical Baseline FRP (F_baseline).',
    howDerived: 'Formula: ((Current FRP − Baseline FRP) / Baseline FRP) × 100',
    unit: 'Percentage (%)',
    limitation: 'Valid only when historical baseline is statistically sufficient (History Tier: LONG_TERM_BASELINE).',
    badge: 'AGNI_NETRA_DEMO',
  },
  {
    term: 'Behavior',
    category: 'State Machine',
    whatItMeans: 'The kinetic trajectory and thermodynamic state of the event over time.',
    input: 'FRP rate of change, spatial expansion velocity, and observation cadence.',
    howDerived: 'State machine evaluation: NEW, PERSISTING, STABLE, INTERMITTENT, ESCALATING, ABNORMAL, RESOLVING.',
    unit: 'Categorical State',
    limitation: 'Discrete states approximate continuous real-world industrial and environmental processes.',
    badge: 'AGNI_NETRA_DEMO',
  },
  {
    term: 'Abnormality',
    category: 'Abnormality',
    whatItMeans: 'Degree to which current event behavior violates expected historical facility patterns.',
    input: 'Baseline deviation, sudden expansion flags, and unusual operational timing.',
    howDerived: 'Deviation scoring algorithm [0.0, 1.0] categorized into NORMAL, UNUSUAL, HIGHLY_ABNORMAL.',
    unit: 'Score [0.0, 1.0] / Level',
    limitation: 'Assumes facility operational parameters have remained constant over baseline window.',
    badge: 'AGNI_NETRA_DEMO',
  },
  {
    term: 'Classification Confidence',
    category: 'Decision Quality',
    whatItMeans: 'Model probability assigned to the top predicted source class by the ML inference engine.',
    input: 'Extracted canonical feature vector (AGN-FEATURES-1.1).',
    howDerived: 'Softmax / gradient-boosted class probability output from inference model.',
    unit: 'Percentage (%) or [0.0, 1.0]',
    limitation: 'High classification confidence does NOT imply certainty if evidence completeness is low.',
    badge: 'AGNI_NETRA_DEMO',
  },
  {
    term: 'Evidence Completeness',
    category: 'Evidence Fusion',
    whatItMeans: 'The proportion of expected multi-sensor evidence channels successfully retrieved for the event.',
    input: 'Availability vector across active evidence families (Thermal, GEO, SWIR, SAR, Weather, Context).',
    howDerived: 'Weighted completeness score based on active vs missing sensor adapters.',
    unit: 'Percentage (%) or [0.0, 1.0]',
    limitation: 'Reflects data channel availability, not whether the independent evidence sources agree.',
    badge: 'AGNI_NETRA_DEMO',
  },
  {
    term: 'Data Quality',
    category: 'Observation Quality',
    whatItMeans: 'Measurement integrity reflecting sensor saturation risk, coordinate validity, and cloud flags.',
    input: 'Quality flags, optical saturation indicators, and finite-bounds check.',
    howDerived: 'Ratio of usable vs degraded/excluded observations in the event cluster.',
    unit: 'Categorical (HIGH, MODERATE, DEGRADED)',
    limitation: 'Detector saturation flags potential non-linearity rather than total observation invalidity.',
    badge: 'AGNI_NETRA_DEMO',
  },
  {
    term: 'Risk Index',
    category: 'Risk Intelligence',
    whatItMeans: 'Overall physical hazard and contextual exposure score for operational decision support.',
    input: 'Physical Hazard (FRP, growth, abnormality) and Consequence Impact (facility proximity, context).',
    howDerived: 'Formula: Base Risk = sqrt(Hazard × Impact) scaled to 0–100.',
    unit: 'Index [0–100]',
    limitation: 'Risk Index is a decision-support score, not a certified physical hazard measurement.',
    badge: 'AGNI_NETRA_DEMO',
  },
  {
    term: 'Priority',
    category: 'Operational Triage',
    whatItMeans: 'Triage rank indicating how urgently an analyst must review or dispatch an event.',
    input: 'Base Risk, Urgency Drivers (spikes/escalation), Impact Context, and Verification Need.',
    howDerived: 'Formula: Priority = 0.45×Risk + 0.30×Urgency + 0.15×Impact + 0.10×Verification.',
    unit: 'Tier (P0 Critical to P4 Informational)',
    limitation: 'Triage recommendation designed for human-in-the-loop workflow; does not execute autonomous dispatch.',
    badge: 'AGNI_NETRA_DEMO',
  },
];

/* ─────────────────────────────────────────────────────────────
   PUBLISHED TECHNICAL REFERENCES (NO "RESEARCH" TERMINOLOGY)
───────────────────────────────────────────────────────────── */

interface ReferenceItem {
  id: string;
  sourceTitle: string;
  authors: string;
  year: string;
  technicalTask: string;
  dataset: string;
  publishedMetric: string;
  publishedResult: string;
  limitation: string;
  badge: ProvenanceType;
}

const technicalReferences: ReferenceItem[] = [
  {
    id: 'vnf-physics',
    sourceTitle: 'VIIRS Nightfire: Multispectral Pyrometry for Hot Persistent Sources',
    authors: 'Elvidge, C. D., Zhizhin, M., Hsu, F. C., et al.',
    year: '2013 / 2015',
    technicalTask: 'Multispectral detection and characterization of combustion sources using Planck curve fitting.',
    dataset: 'Global Suomi-NPP VIIRS Nighttime Radiance Collection.',
    publishedMetric: 'Detection sensitivity & dual-band temperature inversion.',
    publishedResult: 'Adding NIR/SWIR roughly doubled detections vs MWIR-only under documented conditions; reports detection down to ~0.001 m² at ~1800 K.',
    limitation: 'Published finding. Requires raw multispectral radiances; standard FIRMS feeds operate in reduced mode without Planck curve fitting.',
    badge: 'PUBLISHED_RESULT',
  },
  {
    id: 'insat3ds-isro',
    sourceTitle: 'Evaluation of High-Cadence Geostationary Fire Detection over India (INSAT-3DS)',
    authors: 'ISRO / Space Applications Centre (SAC)',
    year: '2024',
    technicalTask: 'Validation of 4km / 15-min cadence geostationary thermal anomaly detection over the Indian subcontinent.',
    dataset: 'INSAT-3DS Imager payload compared against MODIS/VIIRS reference passes.',
    publishedMetric: 'Probability of Detection (POD), Precision, and False Alarm Rate (FAR).',
    publishedResult: 'POD = 45.31%, Precision = 73.34%, False Alarm Rate = 26.66% in published validation study.',
    limitation: 'Published sensor-method result evaluated primarily on agricultural fire domains, not Agni-Netra end-to-end industrial accuracy.',
    badge: 'PUBLISHED_RESULT',
  },
  {
    id: 'sentinel2-swir',
    sourceTitle: 'High-Resolution Thermal Anomaly Classification via Sentinel-2 SWIR',
    authors: 'Remote Sensing Multi-Source Technical Group',
    year: '2021',
    technicalTask: 'Machine learning classification of industrial and landscape thermal sources using 20m SWIR bands.',
    dataset: '~11,000 multi-regional labeled thermal scenes.',
    publishedMetric: 'Overall classification accuracy (Daytime vs Nighttime).',
    publishedResult: '92.8% daytime classification accuracy; ~79.3% nighttime accuracy in cited literature.',
    limitation: 'Published result. 5-day revisit latency restricts Sentinel-2 to spatial confirmation rather than real-time alerting.',
    badge: 'PUBLISHED_RESULT',
  },
  {
    id: 'vnf-timeseries',
    sourceTitle: 'Time-Series Characterization of Industrial Gas Flares and Hotspots',
    authors: 'Global Thermal Anomaly Analysis Consortium',
    year: '2019',
    technicalTask: 'Differentiating routine industrial flaring from abnormal thermal incidents using time-series persistence.',
    dataset: 'Global VIIRS Nightfire time-series archive.',
    publishedMetric: 'Classification accuracy & industrial misclassification rate.',
    publishedResult: '~77% overall accuracy; ~1.4% industrial-source misclassification in cited study.',
    limitation: 'Published result evaluated on global oil/gas flares; local Indian industrial transfer testing required.',
    badge: 'PUBLISHED_RESULT',
  },
  {
    id: 'alphaearth',
    sourceTitle: 'AlphaEarth Foundations: Pretrained Satellite Representations at Scale',
    authors: 'Google / DeepMind Earth AI',
    year: '2024',
    technicalTask: 'Self-supervised 64-dimensional temporal embeddings for global landscape and facility representation.',
    dataset: 'Global 10m multispectral satellite archive (2017–2025).',
    publishedMetric: 'Contextual representation fidelity & zero-shot transfer capability.',
    publishedResult: 'Pretrained 64-dim embeddings capture facility structure and change without task-specific fine-tuning.',
    limitation: 'Demonstrated capability in published literature. Agni-Netra industrial transfer is in pilot implementation.',
    badge: 'ADVANCED_CAPABILITY',
  },
  {
    id: 'conformal-prediction',
    sourceTitle: 'A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty',
    authors: 'Angelopoulos, A. N., & Bates, S.',
    year: '2021 / 2023',
    technicalTask: 'Distribution-free finite-sample prediction sets with guaranteed user-defined marginal coverage.',
    dataset: 'Theoretical statistical methodology applicable across ML classifiers.',
    publishedMetric: 'Marginal coverage guarantee 1 − α (e.g. 90% confidence set).',
    publishedResult: 'Guarantees prediction set contains true class with probability ≥ 1 − α under exchangeability.',
    limitation: 'Validated statistical method; guarantees prediction set coverage under assumptions, not single-class certainty.',
    badge: 'ADVANCED_CAPABILITY',
  },
];

/* ─────────────────────────────────────────────────────────────
   MAIN COMPONENT
───────────────────────────────────────────────────────────── */

export default function AboutPage() {
  const [currentTab, setCurrentTab] = useState('about');
  const [searchQuery, setSearchQuery] = useState('');

  // Interactive UI state
  const [expandedStage, setExpandedStage] = useState<number | null>(1);
  const [dictionarySearch, setDictionarySearch] = useState<string>('');
  const [expandedDictionaryTerm, setExpandedDictionaryTerm] = useState<string | null>('FRP (Fire Radiative Power)');
  const [expandedRef, setExpandedRef] = useState<string | null>('vnf-physics');

  // Filter dictionary
  const filteredDictionary = measurementDictionary.filter((item) => {
    const q = dictionarySearch.toLowerCase();
    return item.term.toLowerCase().includes(q) || item.whatItMeans.toLowerCase().includes(q) || item.category.toLowerCase().includes(q);
  });

  return (
    <div className="min-h-screen bg-[#F4F6F9] flex flex-col">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-[1400px] mx-auto px-6 py-8 space-y-12">

            {/* ═══════════ STICKY QUICK NAVIGATION BAR ═══════════ */}
            <div className="bg-white/90 backdrop-blur-md border border-slate-200 rounded-xl px-4 py-3 shadow-sm flex flex-wrap items-center justify-between gap-2 sticky top-0 z-30">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                  <BookOpen className="w-4 h-4 text-blue-600" />
                  Inside Agni-Netra:
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-1.5 text-xs">
                <a href="#pipeline-section" className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-blue-50 hover:text-blue-700 font-medium text-slate-600 transition-colors">
                  How It Works
                </a>
                <a href="#sensors-section" className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-blue-50 hover:text-blue-700 font-medium text-slate-600 transition-colors">
                  Sensor Roles
                </a>
                <a href="#measurements-section" className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-blue-50 hover:text-blue-700 font-medium text-slate-600 transition-colors">
                  Calculations & Math
                </a>
                <a href="#questions-section" className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-blue-50 hover:text-blue-700 font-medium text-slate-600 transition-colors">
                  Source / Behavior / State
                </a>
                <a href="#evidence-section" className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 font-medium text-slate-600 transition-colors">
                  Evidence & Uncertainty
                </a>
                <a href="#risk-priority-section" className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-amber-50 hover:text-amber-700 font-medium text-slate-600 transition-colors">
                  Risk ≠ Priority
                </a>
                <a href="#published-performance-section" className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-purple-50 hover:text-purple-700 font-medium text-slate-600 transition-colors">
                  Published Performance
                </a>
                <a href="#walkthrough-section" className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 font-medium text-slate-600 transition-colors">
                  Demo Walkthrough
                </a>
                <a href="#dictionary-section" className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-blue-50 hover:text-blue-700 font-medium text-slate-600 transition-colors">
                  Dictionary
                </a>
                <a href="#limitations-section" className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-red-50 hover:text-red-700 font-medium text-slate-600 transition-colors">
                  Limitations
                </a>
              </div>
            </div>

            {/* ═══════════ HERO SECTION (Preserved) ═══════════ */}
            <section className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="grid grid-cols-1 lg:grid-cols-5 gap-0">
                {/* Left text */}
                <div className="lg:col-span-3 p-8 lg:p-10 flex flex-col justify-center">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-800 border border-blue-200">
                      SIH PS162 Geospatial Intelligence
                    </span>
                    <ProvenanceBadge type="AGNI_NETRA_DEMO" label="AGNI-NETRA CORE ARCHITECTURE" />
                  </div>
                  <h1 className="text-3xl lg:text-4xl font-extrabold text-slate-900 tracking-tight">About Agni-Netra</h1>
                  <p className="mt-2 text-lg text-blue-700 font-semibold italic">
                    The satellite sees heat. Agni-Netra understands the event.
                  </p>
                  <p className="mt-4 text-sm text-slate-600 leading-relaxed max-w-xl">
                    Agni-Netra is an AI-enabled geospatial intelligence system that turns satellite thermal observations and multi-source evidence into
                    persistent events, risk-aware analysis, and human-verifiable decisions to support industrial safety, environmental monitoring, and disaster response.
                  </p>
                  <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
                    {pillars.map((p) => (
                      <div key={p.label} className="flex flex-col items-center text-center bg-slate-50 border border-slate-100 rounded-xl p-4 hover:shadow-md transition-shadow">
                        <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center mb-2">
                          <p.icon className="w-5 h-5" />
                        </div>
                        <span className="text-xs font-bold text-slate-900">{p.label}</span>
                        <span className="text-[10px] text-slate-500 mt-0.5 leading-tight">{p.desc}</span>
                      </div>
                    ))}
                  </div>
                </div>
                {/* Right visual card */}
                <div className="lg:col-span-2 relative min-h-[300px] bg-gradient-to-br from-slate-900 via-blue-950 to-indigo-950 p-6 flex flex-col justify-between text-white">
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <div className="bg-blue-600 text-white text-[10px] font-bold px-3 py-1.5 rounded-lg shadow-lg">
                        From Space to Safety
                      </div>
                      <div className="bg-white/10 backdrop-blur-md text-white/90 text-[10px] font-semibold px-2.5 py-1 rounded-md border border-white/20">
                        PS162 Evidence Engine
                      </div>
                    </div>
                    <h3 className="text-lg font-bold tracking-tight">Multi-Sensor Evidence Graph</h3>
                    <p className="text-xs text-slate-300 mt-1">
                      Synthesizing VIIRS, INSAT-3DS, Sentinel-2, SAR, TROPOMI & ground telemetry into auditable decision intelligence.
                    </p>
                  </div>

                  <div className="space-y-2 my-4">
                    <div className="bg-white/10 backdrop-blur-md border border-white/15 rounded-lg p-2.5 flex items-center justify-between text-xs">
                      <span className="text-slate-200">Orbital Cadence</span>
                      <span className="font-mono font-bold text-sky-300">15-min GEO / 12-hr LEO</span>
                    </div>
                    <div className="bg-white/10 backdrop-blur-md border border-white/15 rounded-lg p-2.5 flex items-center justify-between text-xs">
                      <span className="text-slate-200">Evidence Modalities</span>
                      <span className="font-mono font-bold text-emerald-300">7 Independent Lanes</span>
                    </div>
                    <div className="bg-white/10 backdrop-blur-md border border-white/15 rounded-lg p-2.5 flex items-center justify-between text-xs">
                      <span className="text-slate-200">Decision Safety</span>
                      <span className="font-mono font-bold text-amber-300">OOD & Safe Abstention</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5 text-[11px] text-slate-300">
                    <CheckCircle2 className="w-4 h-4 text-green-400 shrink-0" />
                    <span>Observations → Understanding → Actionable Triage</span>
                  </div>
                </div>
              </div>
            </section>

            {/* ═══════════ PRODUCT EXPLANATION BANNER ═══════════ */}
            <section className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-white rounded-2xl p-6 border border-blue-800 shadow-md">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="w-5 h-5 text-blue-300" />
                    <h2 className="text-sm font-bold uppercase tracking-wider text-blue-200">
                      Technical Integrity & Provenance Standard
                    </h2>
                  </div>
                  <p className="text-base font-bold text-white">
                    Published reference performance is explicitly separated from Agni-Netra demonstration data.
                  </p>
                  <p className="text-xs text-blue-200 leading-relaxed max-w-3xl">
                    Every quantitative value on this page carries an auditable technical label. Published sensor results (e.g. Sentinel-2 92.8% or INSAT-3DS 45.31% POD) represent published technical references on underlying methods and are <span className="font-bold underline text-white">never presented as Agni-Netra end-to-end system accuracy</span>.
                  </p>
                </div>
                <div className="flex flex-wrap md:flex-col gap-2 shrink-0">
                  <div className="flex items-center gap-1.5 bg-purple-950/80 border border-purple-500/40 px-2.5 py-1 rounded text-[10px] font-mono text-purple-200">
                    <span className="w-2 h-2 rounded-full bg-purple-400"></span> [PUBLISHED RESULT]
                  </div>
                  <div className="flex items-center gap-1.5 bg-blue-950/80 border border-blue-500/40 px-2.5 py-1 rounded text-[10px] font-mono text-blue-200">
                    <span className="w-2 h-2 rounded-full bg-blue-400"></span> [AGNI-NETRA DEMO]
                  </div>
                  <div className="flex items-center gap-1.5 bg-rose-950/80 border border-rose-500/40 px-2.5 py-1 rounded text-[10px] font-mono text-rose-200">
                    <span className="w-2 h-2 rounded-full bg-rose-400"></span> [VALIDATION NEEDED]
                  </div>
                </div>
              </div>
            </section>

            {/* ═══════════ SECTION 1: 13-STAGE COMPACT PRODUCT PIPELINE ═══════════ */}
            <section id="pipeline-section" className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8 space-y-6">
              <div className="border-b border-slate-100 pb-4">
                <div className="flex items-center gap-2">
                  <ProvenanceBadge type="AGNI_NETRA_DEMO" label="END-TO-END PIPELINE" />
                  <span className="text-xs font-semibold text-slate-500">System Architecture</span>
                </div>
                <h2 className="text-2xl font-extrabold text-slate-900 mt-1">
                  How Agni-Netra Measures & Understands an Event
                </h2>
                <p className="text-sm text-blue-700 font-semibold mt-0.5">
                  From satellite observations to measurable, explainable and human-verifiable intelligence.
                </p>
                <p className="text-xs text-slate-500 mt-2">
                  Click any stage in the pipeline below to inspect its data inputs, outputs, mathematical formulation, and operational guarantees.
                </p>
              </div>

              {/* Visual Pipeline Grid / Steps */}
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-2.5">
                {pipelineStages.map((stage) => {
                  const isSelected = expandedStage === stage.id;
                  return (
                    <button
                      key={stage.id}
                      onClick={() => setExpandedStage(stage.id)}
                      className={`text-left p-3 rounded-xl border transition-all flex flex-col justify-between ${
                        isSelected
                          ? 'bg-blue-600 text-white border-blue-700 shadow-md ring-2 ring-blue-300'
                          : 'bg-slate-50 hover:bg-slate-100 text-slate-800 border-slate-200'
                      }`}
                    >
                      <div className="flex items-center justify-between w-full mb-1.5">
                        <span
                          className={`text-[10px] font-mono font-extrabold px-1.5 py-0.5 rounded ${
                            isSelected ? 'bg-white/20 text-white' : 'bg-blue-100 text-blue-700'
                          }`}
                        >
                          {String(stage.id).padStart(2, '0')}
                        </span>
                        {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-white" />}
                      </div>
                      <div className="text-xs font-bold leading-tight line-clamp-2">{stage.name}</div>
                    </button>
                  );
                })}
              </div>

              {/* Active Stage Detail Panel */}
              {expandedStage && (
                <div className="bg-gradient-to-br from-slate-50 to-blue-50/40 border border-blue-200 rounded-xl p-6 transition-all">
                  {(() => {
                    const stage = pipelineStages.find((s) => s.id === expandedStage)!;
                    return (
                      <div className="space-y-4">
                        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-blue-100 pb-3">
                          <div className="flex items-center gap-3">
                            <span className="w-8 h-8 rounded-lg bg-blue-600 text-white font-bold text-sm flex items-center justify-center shadow">
                              {String(stage.id).padStart(2, '0')}
                            </span>
                            <div>
                              <h3 className="text-base font-extrabold text-slate-900">Stage {stage.id}: {stage.name}</h3>
                              <p className="text-xs text-slate-600 font-medium">{stage.shortDesc}</p>
                            </div>
                          </div>
                          <ProvenanceBadge type={stage.badge.type} label={stage.badge.text} />
                        </div>

                        <p className="text-sm text-slate-700 leading-relaxed">{stage.details}</p>

                        {/* Crucial Principle */}
                        <div className="bg-white border-l-4 border-blue-600 rounded-r-lg p-3.5 shadow-sm">
                          <div className="text-[11px] font-bold text-blue-900 uppercase tracking-wide flex items-center gap-1.5">
                            <Lightbulb className="w-3.5 h-3.5 text-blue-600" />
                            Core Technical Principle
                          </div>
                          <div className="text-xs text-slate-800 font-semibold mt-1">
                            {stage.keyPrinciple}
                          </div>
                        </div>

                        {/* Inputs and Outputs */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-1">
                          <div className="bg-white rounded-lg border border-slate-200 p-3.5">
                            <div className="font-bold text-slate-700 uppercase tracking-wider text-[10px] mb-2 flex items-center gap-1">
                              <CornerDownRight className="w-3 h-3 text-slate-500" /> Inputs
                            </div>
                            <ul className="space-y-1 text-slate-600">
                              {stage.inputs.map((inp, idx) => (
                                <li key={idx} className="flex items-center gap-1.5">
                                  <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                                  {inp}
                                </li>
                              ))}
                            </ul>
                          </div>

                          <div className="bg-white rounded-lg border border-slate-200 p-3.5">
                            <div className="font-bold text-slate-700 uppercase tracking-wider text-[10px] mb-2 flex items-center gap-1">
                              <ArrowRight className="w-3 h-3 text-emerald-600" /> Outputs & Contracts
                            </div>
                            <ul className="space-y-1 text-slate-600">
                              {stage.outputs.map((out, idx) => (
                                <li key={idx} className="flex items-center gap-1.5">
                                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                                  {out}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    );
                  })()}
                </div>
              )}
            </section>

            {/* ═══════════ SECTION 2: WHAT AGNI-NETRA OBSERVES ═══════════ */}
            <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8 space-y-6">
              <div className="border-b border-slate-100 pb-4">
                <div className="flex items-center gap-2">
                  <ProvenanceBadge type="SENSOR_SPEC" label="RAW DATA CHANNELS" />
                  <span className="text-xs font-semibold text-slate-500">Observation Capabilities</span>
                </div>
                <h2 className="text-2xl font-extrabold text-slate-900 mt-1">
                  What Agni-Netra Observes
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Supported satellite and ground data sources provide continuous observations across multiple physical dimensions.
                </p>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 text-xs">
                {[
                  { label: 'Location & Centroid', desc: 'Precision coordinates in decimal degrees (WGS-84).' },
                  { label: 'Timestamp & Cadence', desc: 'Observation timestamps with 15-min GEO / 12-hr LEO schedules.' },
                  { label: 'Thermal Anomaly (MWIR/LWIR)', desc: 'Radiance and brightness temperature measurements (T4 / T11).' },
                  { label: 'FRP (Fire Radiative Power)', desc: 'Instantaneous radiative energy output measured in megawatts (MW).' },
                  { label: 'Spatial Footprint & Extent', desc: 'Clustered convex hull bounding geometries and growth multipliers.' },
                  { label: 'Optical / SWIR Context', desc: '20m shortwave infrared reflectance (Sentinel-2 MSI B11/B12).' },
                  { label: 'SAR Structural Context', desc: 'All-weather backscatter, coherence, and surface texture (S1 / NISAR).' },
                  { label: 'Atmospheric Gas Plumes', desc: 'Combustion column concentrations of NO₂, SO₂, and CO (TROPOMI).' },
                  { label: 'Meteorological Conditions', desc: 'Wind speed, wind direction, humidity, and plume dispersion (NWP).' },
                  { label: 'Facility & Land-Use Context', desc: 'Industrial park boundaries (GIDC), critical assets, and OSM polygons.' },
                  { label: 'Ground Air Quality (In-Situ)', desc: 'Continuous particulate (PM2.5/PM10) and gas readings from CPCB stations.' },
                  { label: 'Embeddings & Novelty', desc: 'Multi-temporal 64-dimensional foundational representations (AlphaEarth).' },
                ].map((item, idx) => (
                  <div key={idx} className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 space-y-1">
                    <div className="font-bold text-slate-900 flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-600"></span>
                      {item.label}
                    </div>
                    <div className="text-[11px] text-slate-600 leading-snug">{item.desc}</div>
                  </div>
                ))}
              </div>

              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3.5 text-xs text-amber-900 flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <div>
                  <strong>Important Technical Distinction:</strong> Thermal Anomaly ≠ Confirmed Fire. A single observation is evidence, not a final conclusion.
                </div>
              </div>
            </section>

            {/* ═══════════ SECTION 3: SENSOR ROLES TABLE ═══════════ */}
            <section id="sensors-section" className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8 space-y-6">
              <div className="border-b border-slate-100 pb-4">
                <div className="flex items-center gap-2">
                  <ProvenanceBadge type="SENSOR_SPEC" label="SENSOR CONTRIBUTION MATRIX" />
                  <span className="text-xs font-semibold text-slate-500">Multi-Sensor Roles</span>
                </div>
                <h2 className="text-2xl font-extrabold text-slate-900 mt-1">
                  What Each Data Source Contributes
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Clear technical roles and boundaries for each integrated orbital and ground data source.
                </p>
              </div>

              <div className="border border-slate-200 rounded-xl overflow-hidden shadow-sm">
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="bg-slate-100 border-b border-slate-200 text-slate-700 font-bold uppercase tracking-wider text-[10px]">
                        <th className="p-3.5 w-1/5">Data Source</th>
                        <th className="p-3.5 w-1/4">What It Contributes</th>
                        <th className="p-3.5 w-1/4">How Agni-Netra Uses It</th>
                        <th className="p-3.5 w-1/3">Technical Limitation</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {sensorContributions.map((s, idx) => (
                        <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                          <td className="p-3.5 align-top">
                            <div className="font-bold text-slate-900 text-xs">{s.source}</div>
                            <div className="mt-1">
                              <ProvenanceBadge type={s.validationStatus.type} />
                            </div>
                          </td>
                          <td className="p-3.5 align-top text-slate-700 leading-snug">{s.whatItObserves}</td>
                          <td className="p-3.5 align-top text-slate-700 leading-snug">{s.agniNetraUse}</td>
                          <td className="p-3.5 align-top text-rose-700 font-medium leading-snug bg-rose-50/30">
                            {s.whatItDoesNotProve}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs text-slate-600 flex items-center gap-2">
                <Info className="w-4 h-4 text-blue-600 shrink-0" />
                <span>
                  <strong>Data Availability Notice:</strong> Not every source is available for every event. Unavailable sensors cleanly return <code>MISSING</code> in the evidence ledger without breaking downstream processing.
                </span>
              </div>
            </section>

            {/* ═══════════ SECTIONS 4 to 8: CALCULATIONS & DERIVATIONS (FRP, FOOTPRINT, PERSISTENCE, EVENT RECONSTRUCTION, BASELINE) ═══════════ */}
            <section id="measurements-section" className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8 space-y-6">
              <div className="border-b border-slate-100 pb-4">
                <div className="flex items-center gap-2">
                  <ProvenanceBadge type="AGNI_NETRA_DEMO" label="FORMULAS & DERIVATIONS" />
                  <span className="text-xs font-semibold text-slate-500">Mathematical Formulations</span>
                </div>
                <h2 className="text-2xl font-extrabold text-slate-900 mt-1">
                  How Values Are Calculated
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Implemented formulas and technical rules for thermal intensity, spatial growth, temporal persistence, event reconstruction, and baseline normality.
                </p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Section 4: How Agni-Netra Uses FRP */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-extrabold text-slate-900">How Agni-Netra Uses FRP</h3>
                    <ProvenanceBadge type="AGNI_NETRA_DEMO" label="FRP FORMULA" />
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    <strong>FRP (Fire Radiative Power)</strong> is a satellite-derived measure associated with radiative energy release of a detected thermal source in megawatts (MW).
                  </p>

                  {/* Formula Callout */}
                  <div className="bg-white border border-blue-200 rounded-lg p-3 text-center shadow-sm">
                    <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Implemented Baseline Deviation Formula</div>
                    <div className="font-mono text-xs font-bold text-blue-800 bg-blue-50 py-1.5 px-3 rounded border border-blue-100 inline-block">
                      Change (%) = ((Current FRP − Baseline FRP) / Baseline FRP) × 100
                    </div>
                  </div>

                  {/* Example Cards */}
                  <div className="grid grid-cols-3 gap-2 text-center text-xs">
                    <div className="bg-white border border-slate-200 rounded-lg p-2">
                      <div className="text-[10px] text-slate-500 font-semibold">CURRENT FRP</div>
                      <div className="font-bold text-slate-900 mt-0.5">480 MW</div>
                      <span className="text-[9px] text-blue-600">[DEMO DATA]</span>
                    </div>
                    <div className="bg-white border border-slate-200 rounded-lg p-2">
                      <div className="text-[10px] text-slate-500 font-semibold">HISTORICAL BASELINE</div>
                      <div className="font-bold text-slate-900 mt-0.5">87.3 MW</div>
                      <span className="text-[9px] text-blue-600">[MULTI-YEAR]</span>
                    </div>
                    <div className="bg-white border border-slate-200 rounded-lg p-2">
                      <div className="text-[10px] text-slate-500 font-semibold">CHANGE</div>
                      <div className="font-bold text-rose-600 mt-0.5">+450%</div>
                      <span className="text-[9px] text-rose-600">[ABNORMAL SPIKE]</span>
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-500 italic">
                    FRP is a satellite-derived observation/product value. It is not a direct ground measurement of facility temperature.
                  </p>
                </div>

                {/* Section 5: How Event Footprint Is Measured */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-extrabold text-slate-900">How Event Footprint Is Measured</h3>
                    <ProvenanceBadge type="AGNI_NETRA_DEMO" label="SPATIAL EXTENT" />
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    The system tracks the spatial extent associated with the event&apos;s thermal observations relative to its reference baseline.
                  </p>

                  <div className="grid grid-cols-3 gap-2 text-center text-xs">
                    <div className="bg-white border border-slate-200 rounded-lg p-2">
                      <div className="text-[10px] text-slate-500 font-semibold">REFERENCE</div>
                      <div className="font-bold text-slate-900 mt-0.5">1.0×</div>
                      <span className="text-[9px] text-slate-500">[BASELINE]</span>
                    </div>
                    <div className="bg-white border border-slate-200 rounded-lg p-2">
                      <div className="text-[10px] text-slate-500 font-semibold">CURRENT</div>
                      <div className="font-bold text-slate-900 mt-0.5">5.5×</div>
                      <span className="text-[9px] text-rose-600">[OBSERVED]</span>
                    </div>
                    <div className="bg-white border border-slate-200 rounded-lg p-2">
                      <div className="text-[10px] text-slate-500 font-semibold">GROWTH</div>
                      <div className="font-bold text-rose-600 mt-0.5">5.5×</div>
                      <span className="text-[9px] text-rose-600">[EXPANSION]</span>
                    </div>
                  </div>

                  <div className="text-xs text-slate-600 bg-white border border-slate-200 rounded-lg p-3">
                    <strong>Convex Hull Bounding Geometry:</strong> Footprint tracks bounding spatial expansion multipliers. Agni-Netra avoids inventing uncalibrated physical sub-pixel area values beyond sensor resolution.
                  </div>
                </div>

                {/* Section 6: How Persistence Is Measured */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-extrabold text-slate-900">How Persistence Is Measured</h3>
                    <ProvenanceBadge type="AGNI_NETRA_DEMO" label="TEMPORAL DYNAMICS" />
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Repeated observations across time are linked to the same event entity, allowing Agni-Netra to distinguish an isolated detection from a persistent event.
                  </p>

                  {/* Timeline Sequence */}
                  <div className="bg-white border border-slate-200 rounded-lg p-3 text-xs space-y-2">
                    <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Observation Sequence</div>
                    <div className="flex items-center justify-between gap-1 overflow-x-auto py-1">
                      {['O1', 'O2', 'O3', 'O4', 'O5'].map((obs, idx, arr) => (
                        <React.Fragment key={idx}>
                          <span className="px-2.5 py-1 rounded bg-blue-50 border border-blue-200 text-blue-800 text-[11px] font-mono font-bold">
                            {obs}
                          </span>
                          {idx < arr.length - 1 && <ArrowRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>

                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-2.5 text-xs text-amber-900">
                    <strong>Crucial Rule:</strong> Persistence alone does NOT mean abnormality. A routine flare can also be persistent and normal.
                  </div>
                </div>

                {/* Section 7: Event Reconstruction */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-extrabold text-slate-900">From Multiple Observations to One Event</h3>
                    <ProvenanceBadge type="AGNI_NETRA_DEMO" label="SPATIOTEMPORAL CLUSTERING" />
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    The event-reconstruction logic associates multiple satellite detections across time and space into a single persistent physical entity:
                  </p>

                  <div className="bg-white border border-slate-200 rounded-lg p-3 text-xs space-y-1.5">
                    <div className="font-mono text-center text-slate-800 font-bold bg-slate-50 py-1 rounded border border-slate-200">
                      Observation 1 + Observation 2 + Observation 3 + Observation 4 → EVENT-042
                    </div>
                    <div className="grid grid-cols-2 gap-1 text-[11px] text-slate-600 pt-1">
                      <div>• Spatial proximity (Haversine ≤ 10km)</div>
                      <div>• Temporal windowing (Δt ≤ 3.0h)</div>
                      <div>• Footprint centroid tracking</div>
                      <div>• Facility / GIDC relationships</div>
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-500">
                    <em>Implementation detail:</em> Uses Haversine spatiotemporal clustering and PostGIS / ST-ClusterDBSCAN.
                  </p>
                </div>

              </div>

              {/* Section 8: How Agni-Netra Defines Normal */}
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-extrabold text-slate-900">How Agni-Netra Defines &ldquo;Normal&rdquo; (Historical Baseline)</h3>
                  <ProvenanceBadge type="AGNI_NETRA_DEMO" label="BASELINE FINGERPRINT" />
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Agni-Netra compares current event behavior against historical behavior across supported dimensions: FRP intensity, footprint extent, duration, recurrence, temporal duty cycle, and facility context.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div className="bg-white border border-green-200 rounded-lg p-3.5 space-y-1">
                    <div className="text-[10px] font-bold text-green-800 uppercase flex items-center gap-1">
                      <CheckCircle className="w-3.5 h-3.5 text-green-600" /> NORMAL
                    </div>
                    <div className="text-slate-700 font-medium">Current ≈ Historical Pattern</div>
                    <div className="text-[11px] text-slate-500">FRP and spatial extent remain within expected multi-year baseline bounds.</div>
                  </div>

                  <div className="bg-white border border-rose-200 rounded-lg p-3.5 space-y-1">
                    <div className="text-[10px] font-bold text-rose-800 uppercase flex items-center gap-1">
                      <AlertOctagon className="w-3.5 h-3.5 text-rose-600" /> ABNORMALITY CANDIDATE
                    </div>
                    <div className="text-slate-700 font-medium">Current significantly differs from expected behavior</div>
                    <div className="text-[11px] text-slate-500">Sudden spike (+450% FRP) and blowout expansion (5.5× footprint).</div>
                  </div>
                </div>

                <p className="text-[11px] text-slate-600 italic">
                  Important: A detected change or baseline abnormality is not automatically a confirmed fire.
                </p>
              </div>
            </section>

            {/* ═══════════ SECTION 9: THREE DIFFERENT QUESTIONS (SOURCE VS BEHAVIOR VS STATE) ═══════════ */}
            <section id="questions-section" className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8 space-y-6">
              <div className="border-b border-slate-100 pb-4">
                <div className="flex items-center gap-2">
                  <ProvenanceBadge type="AGNI_NETRA_DEMO" label="CONCEPTUAL SEPARATION" />
                  <span className="text-xs font-semibold text-slate-500">Core Decision Intelligence</span>
                </div>
                <h2 className="text-2xl font-extrabold text-slate-900 mt-1">
                  Three Different Questions (Source vs Behavior vs State)
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  This conceptual separation is one of the foundational capabilities of Agni-Netra.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                {/* Card 1: SOURCE */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-1 rounded bg-blue-100 text-blue-800 font-mono font-bold text-xs">
                      SOURCE
                    </span>
                    <ProvenanceBadge type="AGNI_NETRA_DEMO" />
                  </div>
                  <div className="text-sm font-extrabold text-blue-950 italic">&ldquo;What is it likely to be?&rdquo;</div>
                  <div className="bg-white border border-slate-200 rounded-lg p-3 text-xs text-slate-800">
                    <strong>Example:</strong> Industrial Fire, Routine Flare, Wildfire
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Identifies the physical process producing the thermal signature.
                  </p>
                </div>

                {/* Card 2: BEHAVIOR */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-1 rounded bg-indigo-100 text-indigo-800 font-mono font-bold text-xs">
                      BEHAVIOR
                    </span>
                    <ProvenanceBadge type="AGNI_NETRA_DEMO" />
                  </div>
                  <div className="text-sm font-extrabold text-indigo-950 italic">&ldquo;How is it behaving?&rdquo;</div>
                  <div className="bg-white border border-slate-200 rounded-lg p-3 text-xs text-slate-800">
                    <strong>Example:</strong> Sudden Spike, Stable Baseline, Intermittent
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Captures kinetic dynamics and energy trends over time.
                  </p>
                </div>

                {/* Card 3: STATE */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-1 rounded bg-emerald-100 text-emerald-800 font-mono font-bold text-xs">
                      STATE
                    </span>
                    <ProvenanceBadge type="AGNI_NETRA_DEMO" />
                  </div>
                  <div className="text-sm font-extrabold text-emerald-950 italic">&ldquo;Where is it in the event lifecycle?&rdquo;</div>
                  <div className="bg-white border border-slate-200 rounded-lg p-3 text-xs text-slate-800">
                    <strong>Example:</strong> Escalating, Persisting, Resolving
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Tracks operational lifecycle for triage and verification timing.
                  </p>
                </div>

              </div>

              {/* Follow-up: Abnormality */}
              <div className="bg-purple-50/60 border border-purple-200 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
                <div>
                  <span className="font-mono font-bold text-purple-900 uppercase">ABNORMALITY: </span>
                  <span className="text-purple-950 font-medium italic">&ldquo;Is this behavior unusual for this location?&rdquo;</span>
                </div>
                <span className="px-3 py-1 rounded-md bg-purple-100 text-purple-800 font-bold border border-purple-200">
                  Example: Highly Abnormal (+450% FRP vs Baseline)
                </span>
              </div>
            </section>

            {/* ═══════════ SECTION 10: SOURCE ATTRIBUTION ═══════════ */}
            <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8 space-y-6">
              <div className="border-b border-slate-100 pb-4">
                <div className="flex items-center gap-2">
                  <ProvenanceBadge type="AGNI_NETRA_DEMO" label="SOURCE CLASSIFICATION" />
                  <span className="text-xs font-semibold text-slate-500">Attribution Engine</span>
                </div>
                <h2 className="text-2xl font-extrabold text-slate-900 mt-1">
                  How Agni-Netra Identifies the Likely Source
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Source attribution combines thermal information, spatial context, temporal behavior, facility context, historical behavior, and supporting sensor evidence.
                </p>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                {[
                  { name: 'INDUSTRIAL_FIRE', label: 'Industrial Fire', color: 'border-red-300 bg-red-50 text-red-900' },
                  { name: 'ROUTINE_FLARE', label: 'Routine Flare', color: 'border-green-300 bg-green-50 text-green-900' },
                  { name: 'WILDFIRE', label: 'Forest Fire / Wildfire', color: 'border-orange-300 bg-orange-50 text-orange-900' },
                  { name: 'AGRICULTURAL_BURN', label: 'Agricultural Burn', color: 'border-yellow-300 bg-yellow-50 text-yellow-900' },
                  { name: 'MINING_INDUSTRIAL_HEAT', label: 'Coal Mine Fire', color: 'border-slate-300 bg-slate-100 text-slate-900' },
                  { name: 'UNKNOWN', label: 'Unknown / Abstain', color: 'border-blue-300 bg-blue-50 text-blue-900' },
                ].map((item) => (
                  <div key={item.name} className={`border rounded-xl p-3 text-center ${item.color}`}>
                    <div className="text-xs font-extrabold">{item.label}</div>
                    <div className="text-[10px] font-mono mt-0.5 opacity-80">{item.name}</div>
                  </div>
                ))}
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs text-slate-700">
                <strong>Attribution Rule:</strong> Agni-Netra does not force a classification when evidence is inadequate. Proximity to a facility is supporting context, not definitive proof of source class.
              </div>
            </section>

            {/* ═══════════ SECTIONS 11 to 17: PUBLISHED TECHNICAL PERFORMANCE ═══════════ */}
            <section id="published-performance-section" className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8 space-y-6">
              <div className="border-b border-slate-100 pb-4">
                <div className="flex items-center gap-2">
                  <ProvenanceBadge type="PUBLISHED_RESULT" label="PUBLISHED TECHNICAL REFERENCES" />
                  <span className="text-xs font-semibold text-slate-500">Sensor & Method Validation</span>
                </div>
                <h2 className="text-2xl font-extrabold text-slate-900 mt-1">
                  Published Technical Performance
                </h2>
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 text-xs text-purple-900 font-bold mt-2">
                  ⚠️ NOTICE: These numbers describe published methods used as technical references. They are NOT Agni-Netra&apos;s own end-to-end accuracy unless independently validated by Agni-Netra.
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

                {/* Section 13: VIIRS Nightfire Technical Basis */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 flex flex-col justify-between space-y-3">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-extrabold text-slate-900">High-Temperature Thermal Basis</span>
                      <ProvenanceBadge type="PUBLISHED_RESULT" label="PUBLISHED FINDING" />
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      VIIRS Nightfire utilizes MWIR, SWIR, NIR channels and Planck-law curve fitting for high-temperature persistent source characterization.
                    </p>
                    <div className="space-y-1.5 text-xs text-slate-800 bg-white border border-slate-200 rounded-lg p-3">
                      <div className="font-semibold text-purple-900 text-[11px]">Published Technical Finding:</div>
                      <div>• Adding NIR/SWIR <strong>roughly doubled detections</strong> vs MWIR-only under documented conditions.</div>
                      <div>• Detection capability down to <strong>~0.001 m² at ~1800 K</strong> under suitable conditions.</div>
                    </div>
                  </div>
                  <div className="text-[10px] text-slate-500 border-t border-slate-200 pt-2">
                    Source: Elvidge et al. (VIIRS Nightfire published technical basis)
                  </div>
                </div>

                {/* Section 12: INSAT-3DS */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 flex flex-col justify-between space-y-3">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-extrabold text-slate-900">India-Ready Geostationary Context</span>
                      <ProvenanceBadge type="PUBLISHED_RESULT" label="PUBLISHED SENSOR-METHOD RESULT" />
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      INSAT-3DS provides 4 km spatial resolution, ~15–30 minute cadence, and rapid-scan capability across MWIR/TIR channels.
                    </p>
                    <div className="space-y-1 text-xs text-slate-800 bg-white border border-slate-200 rounded-lg p-3">
                      <div className="font-semibold text-purple-900 text-[11px]">Published ISRO Validation:</div>
                      <div className="flex justify-between font-mono">
                        <span>POD:</span>
                        <span className="font-bold text-purple-700">45.31% [PUBLISHED RESULT]</span>
                      </div>
                      <div className="flex justify-between font-mono">
                        <span>Precision:</span>
                        <span className="font-bold text-purple-700">73.34% [PUBLISHED RESULT]</span>
                      </div>
                      <div className="flex justify-between font-mono">
                        <span>False Alarm Rate:</span>
                        <span className="font-bold text-purple-700">26.66% [PUBLISHED RESULT]</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-[10px] text-slate-500 border-t border-slate-200 pt-2">
                    These figures describe the published INSAT-3DS detection method, not Agni-Netra&apos;s end-to-end accuracy.
                  </div>
                </div>

                {/* Section 14: Sentinel-2 SWIR */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 flex flex-col justify-between space-y-3">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-extrabold text-slate-900">Fine Spatial Context (Sentinel-2)</span>
                      <ProvenanceBadge type="PUBLISHED_RESULT" label="PUBLISHED RESULT" />
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      Sentinel-2 SWIR provides 20m spatial refinement for facility-level surroundings, burned-area context, and plume interpretation.
                    </p>
                    <div className="space-y-1.5 text-xs text-slate-800 bg-white border border-slate-200 rounded-lg p-3">
                      <div className="font-semibold text-purple-900 text-[11px]">Published Classification Performance:</div>
                      <div className="flex justify-between font-mono font-bold text-slate-900">
                        <span>Daytime Accuracy:</span>
                        <span className="text-purple-700">92.8% [PUBLISHED RESULT]</span>
                      </div>
                      <div className="flex justify-between font-mono font-bold text-slate-900">
                        <span>Nighttime Result:</span>
                        <span className="text-purple-700">~79.3% [PUBLISHED RESULT]</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-[10px] text-slate-500 border-t border-slate-200 pt-2">
                    Sentinel-2 revisit timing means it is not a continuous real-time thermal trigger.
                  </div>
                </div>

                {/* Section 15: NISAR */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 flex flex-col justify-between space-y-3">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-extrabold text-slate-900">Structural Confirmation Layer</span>
                      <ProvenanceBadge type="SENSOR_SPEC" label="SENSOR SPECIFICATION" />
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      NISAR / Sentinel-1 provides complementary SAR-based structural, coherence, and surface-change context.
                    </p>
                    <div className="space-y-1 text-xs text-slate-800 bg-white border border-slate-200 rounded-lg p-3">
                      <div className="font-semibold text-blue-900 text-[11px]">Technical Status & Latency:</div>
                      <div>• NISAR S-band: <strong>~48-hour data latency</strong> through Bhoonidhi.</div>
                      <div>• L-band: calibrated provisional products available.</div>
                      <div className="text-amber-800 font-semibold mt-1">Used for retrospective confirmation, not real-time emergency trigger.</div>
                    </div>
                  </div>
                  <div className="text-[10px] text-slate-500 border-t border-slate-200 pt-2">
                    SAR backscatter does not measure direct active fire temperature.
                  </div>
                </div>

                {/* Section 16: AlphaEarth */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 flex flex-col justify-between space-y-3">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-extrabold text-slate-900">Facility Fingerprinting & Context</span>
                      <ProvenanceBadge type="ADVANCED_CAPABILITY" label="ADVANCED CAPABILITY" />
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      Published characteristics: 10m resolution, 64-dimensional temporal embeddings across global annual coverage (2017–2025).
                    </p>
                    <div className="space-y-1 text-xs text-slate-800 bg-white border border-slate-200 rounded-lg p-3">
                      <div className="font-semibold text-indigo-900 text-[11px]">Supported Use Cases:</div>
                      <div>• Facility fingerprinting & contextual similarity</div>
                      <div>• Landscape change detection & novelty / OOD support</div>
                    </div>
                  </div>
                  <div className="text-[10px] text-slate-500 border-t border-slate-200 pt-2">
                    Published dataset capability; industrial transfer tested in pilot.
                  </div>
                </div>

                {/* Section 17: TROPOMI Atmospheric Corroboration */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 flex flex-col justify-between space-y-3">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-extrabold text-slate-900">Atmospheric Corroboration</span>
                      <ProvenanceBadge type="SENSOR_SPEC" label="SENSOR SPECIFICATION" />
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      TROPOMI contributes atmospheric composition data (NO₂, SO₂, CO) to support or challenge thermal hypotheses.
                    </p>
                    <div className="space-y-1 text-xs text-slate-800 bg-white border border-slate-200 rounded-lg p-3">
                      <div className="font-semibold text-slate-900 text-[11px]">Operational Fusion:</div>
                      <div className="font-mono text-[11px] text-blue-900">Thermal Hypothesis + Atmospheric Evidence</div>
                    </div>
                  </div>
                  <div className="text-[10px] text-slate-500 border-t border-slate-200 pt-2">
                    Atmospheric evidence does NOT automatically prove a specific facility caused the event.
                  </div>
                </div>

              </div>
            </section>

            {/* ═══════════ SECTION 18: EVIDENCE FUSION GRAPH ═══════════ */}
            <section id="evidence-section" className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8 space-y-6">
              <div className="border-b border-slate-100 pb-4">
                <div className="flex items-center gap-2">
                  <ProvenanceBadge type="AGNI_NETRA_DEMO" label="EVIDENCE SYNTHESIS" />
                  <span className="text-xs font-semibold text-slate-500">Multi-Source Graph</span>
                </div>
                <h2 className="text-2xl font-extrabold text-slate-900 mt-1">
                  How Multiple Sources Become One Decision
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Agni-Netra aggregates multi-sensor evidence while preserving conflicts instead of forcing all sensors to agree.
                </p>
              </div>

              {/* Visual Fusion Flow */}
              <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-blue-950 text-white rounded-xl p-6 shadow-inner space-y-6">
                <div className="text-center text-xs font-bold uppercase tracking-wider text-slate-300">
                  Agni-Netra Multi-Sensor Evidence Graph Architecture
                </div>

                {/* 7 Modality Inputs */}
                <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 text-center text-xs">
                  {[
                    { label: 'Thermal', sub: 'VIIRS / VNF' },
                    { label: 'Temporal', sub: 'INSAT-3DS' },
                    { label: 'Spatial', sub: 'Sentinel-2 SWIR' },
                    { label: 'Facility', sub: 'OSM / GIDC' },
                    { label: 'Historical', sub: 'Multi-Year Profile' },
                    { label: 'Atmospheric', sub: 'TROPOMI' },
                    { label: 'Weather', sub: 'Wind & Humidity' },
                  ].map((item, idx) => (
                    <div key={idx} className="bg-white/10 border border-white/20 rounded-lg p-2.5 backdrop-blur-sm">
                      <div className="font-bold text-sky-300 text-[11px]">{item.label}</div>
                      <div className="text-[10px] text-slate-300 mt-0.5">{item.sub}</div>
                    </div>
                  ))}
                </div>

                <div className="flex justify-center text-slate-400">
                  <ArrowDown className="w-5 h-5 animate-bounce" />
                </div>

                {/* Evidence Graph Layer */}
                <div className="bg-white/10 border border-white/20 rounded-xl p-4 backdrop-blur-md text-center max-w-xl mx-auto space-y-2">
                  <div className="text-xs font-extrabold text-white">EVIDENCE GRAPH / LEDGER</div>
                  <div className="grid grid-cols-4 gap-2 text-xs">
                    <span className="px-2 py-1 rounded bg-emerald-500/30 border border-emerald-400 text-emerald-200 font-bold text-[10px]">
                      SUPPORTING
                    </span>
                    <span className="px-2 py-1 rounded bg-rose-500/30 border border-rose-400 text-rose-200 font-bold text-[10px]">
                      CONFLICTING
                    </span>
                    <span className="px-2 py-1 rounded bg-slate-500/30 border border-slate-400 text-slate-200 font-bold text-[10px]">
                      NEUTRAL
                    </span>
                    <span className="px-2 py-1 rounded bg-amber-500/30 border border-amber-400 text-amber-200 font-bold text-[10px]">
                      MISSING
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-300 mt-2">
                    Directional flags attribute independent support without overriding conflicting signals.
                  </p>
                </div>

                <div className="flex justify-center text-slate-400">
                  <ArrowDown className="w-5 h-5" />
                </div>

                {/* Hypothesis Result */}
                <div className="bg-blue-600/40 border border-blue-400 rounded-lg p-3 text-center max-w-md mx-auto">
                  <div className="text-xs font-bold text-sky-200 uppercase">Calibrated Hypothesis Package</div>
                  <div className="text-sm font-extrabold text-white mt-0.5">Decision State + Prediction Set + XAI Ledger</div>
                </div>
              </div>
            </section>

            {/* ═══════════ SECTIONS 19 & 20: CONFIDENCE & UNCERTAINTY / ABSTENTION ═══════════ */}
            <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8 space-y-6">
              <div className="border-b border-slate-100 pb-4">
                <div className="flex items-center gap-2">
                  <ProvenanceBadge type="AGNI_NETRA_DEMO" label="CONFIDENCE & SAFETY" />
                  <span className="text-xs font-semibold text-slate-500">Uncertainty Governance</span>
                </div>
                <h2 className="text-2xl font-extrabold text-slate-900 mt-1">
                  Confidence Is Not Certainty
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Agni-Netra explicitly separates model confidence from evidence completeness and data quality.
                </p>
              </div>

              {/* 3 Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800">CLASSIFICATION CONFIDENCE</span>
                    <ProvenanceBadge type="AGNI_NETRA_DEMO" />
                  </div>
                  <div className="text-2xl font-black text-blue-700 font-mono">94%</div>
                  <p className="text-xs text-slate-600">
                    How strongly the model supports the selected class based on available features.
                  </p>
                </div>

                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800">EVIDENCE COMPLETENESS</span>
                    <ProvenanceBadge type="AGNI_NETRA_DEMO" />
                  </div>
                  <div className="text-2xl font-black text-amber-600 font-mono">52%</div>
                  <p className="text-xs text-slate-600">
                    How much expected multi-sensor evidence is currently available.
                  </p>
                </div>

                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800">DATA QUALITY</span>
                    <ProvenanceBadge type="AGNI_NETRA_DEMO" />
                  </div>
                  <div className="text-2xl font-black text-emerald-600 font-mono">HIGH</div>
                  <p className="text-xs text-slate-600">
                    How reliable the available observations are (free from fatal detector saturation).
                  </p>
                </div>

              </div>

              {/* Section 20: When Agni-Netra Says I Don't Know */}
              <div className="bg-blue-50/60 border border-blue-200 rounded-xl p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <HelpCircle className="w-5 h-5 text-blue-600" />
                    <h3 className="text-sm font-extrabold text-blue-950">When Agni-Netra Says &ldquo;I Don&apos;t Know&rdquo;</h3>
                  </div>
                  <ProvenanceBadge type="AGNI_NETRA_DEMO" label="SAFE ABSTENTION" />
                </div>
                <p className="text-xs text-slate-700 leading-relaxed">
                  When evidence is insufficient or conflicting, Agni-Netra avoids forcing an inaccurate classification:
                </p>
                <div className="bg-white rounded-lg border border-blue-200 p-3 text-xs space-y-1 font-mono">
                  <div className="text-slate-800">Strong evidence → Classification</div>
                  <div className="text-rose-700 font-bold">Insufficient/conflicting evidence → Unknown / Insufficient Observation → Needs Verification</div>
                </div>
                <p className="text-[11px] text-blue-900 font-semibold">
                  This safe abstention is an intentional safety feature, not a system failure.
                </p>
              </div>
            </section>

            {/* ═══════════ SECTIONS 21 & 22: RISK & PRIORITY (RISK ≠ PRIORITY) ═══════════ */}
            <section id="risk-priority-section" className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8 space-y-6">
              <div className="border-b border-slate-100 pb-4">
                <div className="flex items-center gap-2">
                  <ProvenanceBadge type="AGNI_NETRA_DEMO" label="OPERATIONAL DECISION LOGIC" />
                  <span className="text-xs font-semibold text-slate-500">Hazard & Triage Decoupling</span>
                </div>
                <h2 className="text-2xl font-extrabold text-slate-900 mt-1">
                  How Risk and Priority Are Assessed (Risk ≠ Priority)
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Risk models physical danger and consequence; Priority models operational triage urgency.
                </p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Section 21: How Risk Is Assessed */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Gauge className="w-5 h-5 text-rose-600" />
                      <h3 className="text-sm font-extrabold text-slate-900">How Risk Is Assessed</h3>
                    </div>
                    <ProvenanceBadge type="AGNI_NETRA_DEMO" label="0–100 RISK INDEX" />
                  </div>

                  <p className="text-xs text-slate-600">
                    Risk asks: <em>&ldquo;How concerning is this event?&rdquo;</em>
                  </p>

                  <div className="bg-white border border-slate-200 rounded-lg p-3 text-center">
                    <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Risk Factors Flow</div>
                    <div className="font-mono text-xs font-bold text-rose-800 bg-rose-50 py-1.5 px-3 rounded border border-rose-100 inline-block">
                      Thermal Intensity + Growth + Footprint + Persistence + Abnormality + Exposure → RISK INDEX (0–100)
                    </div>
                  </div>

                  <div className="text-xs text-slate-600">
                    Risk Index is generated by the Agni-Netra decision layer. Detailed internal weighting is not exposed in the current application.
                  </div>

                  <p className="text-[11px] text-slate-500 italic">
                    Risk Index is a decision-support score, not a certified physical hazard measurement.
                  </p>
                </div>

                {/* Section 22: Priority Formulation */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Target className="w-5 h-5 text-blue-600" />
                      <h3 className="text-sm font-extrabold text-slate-900">Risk ≠ Priority</h3>
                    </div>
                    <ProvenanceBadge type="AGNI_NETRA_DEMO" label="OPERATIONAL TRIAGE" />
                  </div>

                  <p className="text-xs text-slate-600">
                    Priority asks: <em>&ldquo;Which event should the analyst investigate first?&rdquo;</em>
                  </p>

                  <div className="bg-white border border-slate-200 rounded-lg p-3 text-center">
                    <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Priority Flow</div>
                    <div className="font-mono text-xs font-bold text-blue-800 bg-blue-50 py-1.5 px-3 rounded border border-blue-100 inline-block">
                      Risk + Abnormality + Exposure + Growth + Uncertainty + Operational Context → PRIORITY
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-white border border-slate-200 rounded-lg p-2.5">
                      <div className="font-bold text-slate-900 text-[11px]">P0 — Critical</div>
                      <div className="text-[10px] text-slate-600">Action: <code>IMMEDIATE_REVIEW</code></div>
                    </div>
                    <div className="bg-white border border-slate-200 rounded-lg p-2.5">
                      <div className="font-bold text-slate-900 text-[11px]">P1 — Urgent</div>
                      <div className="text-[10px] text-slate-600">Action: <code>PRIORITY_REVIEW</code></div>
                    </div>
                    <div className="bg-white border border-slate-200 rounded-lg p-2.5">
                      <div className="font-bold text-slate-900 text-[11px]">P2 — Evaluate</div>
                      <div className="text-[10px] text-slate-600">Action: <code>VERIFY</code></div>
                    </div>
                    <div className="bg-white border border-slate-200 rounded-lg p-2.5">
                      <div className="font-bold text-slate-900 text-[11px]">P3/P4 — Monitor</div>
                      <div className="text-[10px] text-slate-600">Action: <code>MONITOR / INFO</code></div>
                    </div>
                  </div>
                </div>

              </div>
            </section>

            {/* ═══════════ SECTION 23: WHY / WHY NOT / WHAT CHANGED (XAI) ═══════════ */}
            <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8 space-y-6">
              <div className="border-b border-slate-100 pb-4">
                <div className="flex items-center gap-2">
                  <ProvenanceBadge type="AGNI_NETRA_DEMO" label="XAI EXPLAINABILITY" />
                  <span className="text-xs font-semibold text-slate-500">Auditable Decision Ledger</span>
                </div>
                <h2 className="text-2xl font-extrabold text-slate-900 mt-1">
                  How Agni-Netra Explains Its Decision
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Connects directly with the Event Detail forensics page with structured reasoning vectors.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                {/* WHY */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                    <h3 className="text-sm font-extrabold text-slate-900">WHY?</h3>
                  </div>
                  <p className="text-xs text-slate-600">
                    Evidence supporting the current hypothesis:
                  </p>
                  <ul className="space-y-1.5 text-xs text-slate-700 bg-white border border-slate-200 rounded-lg p-3">
                    <li className="flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                      FRP increased 5.5× (+450%) above baseline
                    </li>
                    <li className="flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                      Spatial footprint blowout from 1.0× to 5.5×
                    </li>
                    <li className="flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                      Facility boundary matched (GIDC Estate)
                    </li>
                  </ul>
                </div>

                {/* WHY NOT */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
                  <div className="flex items-center gap-2">
                    <XCircle className="w-5 h-5 text-rose-600" />
                    <h3 className="text-sm font-extrabold text-slate-900">WHY NOT?</h3>
                  </div>
                  <p className="text-xs text-slate-600">
                    Evidence against plausible alternatives:
                  </p>
                  <ul className="space-y-1.5 text-xs text-slate-700 bg-white border border-slate-200 rounded-lg p-3">
                    <li className="flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
                      Footprint expansion violates routine flare envelope
                    </li>
                    <li className="flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
                      FRP spike (480 MW) exceeds historical 87 MW limit
                    </li>
                  </ul>
                </div>

                {/* WHAT CHANGED */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-blue-600" />
                    <h3 className="text-sm font-extrabold text-slate-900">WHAT CHANGED?</h3>
                  </div>
                  <p className="text-xs text-slate-600">
                    Difference between current behavior and historical behavior:
                  </p>
                  <ul className="space-y-1.5 text-xs text-slate-700 bg-white border border-slate-200 rounded-lg p-3">
                    <li className="flex items-center justify-between">
                      <span className="text-slate-600">FRP:</span>
                      <span className="font-mono font-bold text-rose-700">87.3 MW → 480 MW</span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span className="text-slate-600">Footprint:</span>
                      <span className="font-mono font-bold text-rose-700">1.0× → 5.5×</span>
                    </li>
                  </ul>
                </div>

              </div>
            </section>

            {/* ═══════════ SECTION 24: HUMAN VERIFICATION LOOP ═══════════ */}
            <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8 space-y-6">
              <div className="border-b border-slate-100 pb-4">
                <div className="flex items-center gap-2">
                  <ProvenanceBadge type="AGNI_NETRA_DEMO" label="OPERATIONAL WORKFLOW" />
                  <span className="text-xs font-semibold text-slate-500">Expert-in-the-Loop</span>
                </div>
                <h2 className="text-2xl font-extrabold text-slate-900 mt-1">
                  Human Verification Completes the Loop
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Agni-Netra supports analyst decision-making rather than silently turning an uncertain observation into ground truth.
                </p>
              </div>

              <div className="flex flex-col md:flex-row items-center justify-between gap-4 bg-slate-50 border border-slate-200 rounded-xl p-6">
                <div className="flex items-center gap-3 text-center md:text-left">
                  <div className="w-12 h-12 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center shrink-0 font-bold text-base">
                    AI
                  </div>
                  <div>
                    <div className="text-xs font-bold text-slate-800">AI Assessment</div>
                    <div className="text-[11px] text-slate-500">Intelligence Result + XAI Ledger</div>
                  </div>
                </div>

                <ArrowRight className="w-5 h-5 text-slate-400 hidden md:block" />
                <ArrowDown className="w-5 h-5 text-slate-400 md:hidden" />

                <div className="flex items-center gap-3 text-center md:text-left">
                  <div className="w-12 h-12 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center shrink-0 font-bold text-base">
                    <FileSearch className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-slate-800">Evidence Review</div>
                    <div className="text-[11px] text-slate-500">Multi-Sensor Graph Audit</div>
                  </div>
                </div>

                <ArrowRight className="w-5 h-5 text-slate-400 hidden md:block" />
                <ArrowDown className="w-5 h-5 text-slate-400 md:hidden" />

                <div className="flex items-center gap-2">
                  <span className="px-3 py-2 rounded-lg bg-green-600 text-white font-bold text-xs shadow-sm">
                    Confirm
                  </span>
                  <span className="px-3 py-2 rounded-lg bg-rose-600 text-white font-bold text-xs shadow-sm">
                    Reject
                  </span>
                  <span className="px-3 py-2 rounded-lg bg-amber-500 text-white font-bold text-xs shadow-sm">
                    Request More Evidence
                  </span>
                </div>
              </div>
            </section>

            {/* ═══════════ SECTIONS 25 & 26: HOW ACCURATE IS AGNI-NETRA? & SCORECARD ═══════════ */}
            <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8 space-y-8">

              {/* Section 25: How Accurate Is Agni-Netra? */}
              <div className="space-y-4">
                <div className="border-b border-slate-100 pb-4">
                  <div className="flex items-center gap-2">
                    <ShieldAlert className="w-5 h-5 text-blue-600" />
                    <h2 className="text-2xl font-extrabold text-slate-900">
                      How Accurate Is Agni-Netra?
                    </h2>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    Published performance provides technical reference points; Agni-Netra&apos;s end-to-end performance must be established through its own validation dataset.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                  <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-2">
                    <div className="text-[10px] font-bold text-purple-700 uppercase">PUBLISHED TECHNICAL RESULTS</div>
                    <div className="font-bold text-slate-900 text-sm">Reference Performance</div>
                    <p className="text-slate-600 leading-snug">
                      Underlying sensors and methods (e.g. Sentinel-2 92.8% or INSAT-3DS 45.31% POD) provide baseline technical feasibility.
                    </p>
                  </div>

                  <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-2">
                    <div className="text-[10px] font-bold text-blue-700 uppercase">CURRENT AGNI-NETRA VALIDATION</div>
                    <div className="font-bold text-slate-900 text-sm">Demonstrated Scenarios</div>
                    <p className="text-slate-600 leading-snug">
                      Demonstrated on curated/synthetic industrial scenarios within the current MVP release.
                    </p>
                  </div>

                  <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-2">
                    <div className="text-[10px] font-bold text-rose-700 uppercase">VALIDATION LIMITATION</div>
                    <div className="font-bold text-slate-900 text-sm">Indian Ground Truth</div>
                    <p className="text-slate-600 leading-snug">
                      Indian industrial ground truth remains limited; full empirical accuracy requires local industrial field pilots.
                    </p>
                  </div>
                </div>
              </div>

              {/* Section 26: Agni-Netra vs Published Results */}
              <div className="space-y-4">
                <div className="border-b border-slate-100 pb-4">
                  <div className="flex items-center gap-2">
                    <ProvenanceBadge type="AGNI_NETRA_DEMO" label="CAPABILITY SCORECARD" />
                    <span className="text-xs font-semibold text-slate-500">Transparent Comparison</span>
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 mt-1">
                    Agni-Netra vs Published Technical Results
                  </h3>
                </div>

                <div className="border border-slate-200 rounded-xl overflow-hidden shadow-sm">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="bg-slate-100 border-b border-slate-200 text-slate-700 font-bold uppercase tracking-wider text-[10px]">
                          <th className="p-3.5 w-1/4">Capability</th>
                          <th className="p-3.5 w-1/3">Published Result / Specification</th>
                          <th className="p-3.5 w-1/3">Agni-Netra Use</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {capabilityScorecard.map((item, idx) => (
                          <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                            <td className="p-3.5 align-top font-bold text-slate-900 text-xs">
                              {item.capability}
                            </td>
                            <td className="p-3.5 align-top space-y-1">
                              <div className="text-slate-800 leading-snug">{item.publishedResult}</div>
                              <ProvenanceBadge type={item.publishedBadge} />
                            </td>
                            <td className="p-3.5 align-top space-y-1">
                              <div className="text-slate-800 leading-snug">{item.agniNetraUse}</div>
                              <ProvenanceBadge type={item.agniNetraBadge} />
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              {/* Section 29: Technical Confidence Labels */}
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
                <h4 className="text-sm font-extrabold text-slate-900">Technical Confidence Framework</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                  <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200">
                    <div className="font-bold text-emerald-950">🟢 ESTABLISHED</div>
                    <div className="text-emerald-800 text-[11px] mt-0.5">Published / operational / directly supported in pipeline.</div>
                  </div>
                  <div className="p-3 rounded-lg bg-amber-50 border border-amber-200">
                    <div className="font-bold text-amber-950">🟡 VALIDATION NEEDED</div>
                    <div className="text-amber-800 text-[11px] mt-0.5">Technically sound but requires local Agni-Netra validation.</div>
                  </div>
                  <div className="p-3 rounded-lg bg-blue-50 border border-blue-200">
                    <div className="font-bold text-blue-950">🔵 ADVANCED / FUTURE</div>
                    <div className="text-blue-800 text-[11px] mt-0.5">Planned or advanced capability in project roadmap.</div>
                  </div>
                </div>
              </div>

            </section>

            {/* ═══════════ SECTION 27: END-TO-END DEMO EXAMPLE ═══════════ */}
            <section id="walkthrough-section" className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8 space-y-6">
              <div className="border-b border-slate-100 pb-4">
                <div className="flex items-center gap-2">
                  <ProvenanceBadge type="AGNI_NETRA_DEMO" label="AGNI-NETRA MVP DEMONSTRATION DATA" />
                  <span className="text-xs font-semibold text-slate-500">Product Forensics Trace</span>
                </div>
                <h2 className="text-2xl font-extrabold text-slate-900 mt-1">
                  From Observation to Decision
                </h2>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-2.5 text-xs text-blue-900 font-semibold mt-2">
                  ℹ️ AGNI-NETRA MVP DEMONSTRATION DATA — Illustrates the step-by-step decision production flow on synthetic test data.
                </div>
              </div>

              {/* Step Sequence */}
              <div className="relative border-l-2 border-blue-400 pl-6 ml-4 space-y-5 text-xs">

                <div className="relative">
                  <span className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-blue-600 ring-4 ring-white"></span>
                  <div className="font-bold text-slate-900 text-sm">Thermal Observation Progression</div>
                  <div className="font-mono text-blue-800 font-bold mt-1 bg-slate-50 py-1.5 px-3 rounded border border-slate-200 inline-block">
                    42 MW → 120 MW → 280 MW → 480 MW
                  </div>
                </div>

                <div className="relative">
                  <span className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-blue-600 ring-4 ring-white"></span>
                  <div className="font-bold text-slate-900 text-sm">Event Reconstruction & Extent</div>
                  <p className="text-slate-600 mt-0.5">
                    <strong>12 observations</strong> linked → <strong>4.2× footprint expansion</strong> observed.
                  </p>
                </div>

                <div className="relative">
                  <span className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-blue-600 ring-4 ring-white"></span>
                  <div className="font-bold text-slate-900 text-sm">Historical Baseline Comparison</div>
                  <p className="text-slate-600 mt-0.5">
                    <strong>87.3 MW</strong> historical baseline → <strong>+450% baseline deviation</strong>.
                  </p>
                </div>

                <div className="relative">
                  <span className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-blue-600 ring-4 ring-white"></span>
                  <div className="font-bold text-slate-900 text-sm">Multi-Source Evidence Synthesis</div>
                  <p className="text-slate-600 mt-0.5">
                    VIIRS + INSAT-3DS + Sentinel-2 SWIR + Weather + GIDC context aggregated into Evidence Graph.
                  </p>
                </div>

                <div className="relative">
                  <span className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-blue-600 ring-4 ring-white"></span>
                  <div className="font-bold text-slate-900 text-sm">Intelligence Output</div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 font-mono">
                    <div className="bg-slate-100 p-2 rounded">Source: <strong>Industrial Fire</strong></div>
                    <div className="bg-slate-100 p-2 rounded">Behavior: <strong>Sudden Spike</strong></div>
                    <div className="bg-slate-100 p-2 rounded">Abnormality: <strong>Highly Abnormal</strong></div>
                    <div className="bg-slate-100 p-2 rounded">Risk: <strong>95 / 100</strong></div>
                  </div>
                </div>

                <div className="relative">
                  <span className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-emerald-600 ring-4 ring-white"></span>
                  <div className="font-bold text-emerald-900 text-sm">Operational Triage</div>
                  <p className="text-slate-600 mt-0.5">
                    Priority: <strong>Critical (P0)</strong> → Dispatched to Analyst as <strong>Needs Verification</strong>.
                  </p>
                </div>

              </div>
            </section>

            {/* ═══════════ SECTION 28: WHAT AGNI-NETRA DOES NOT CLAIM (SIMPLIFIED) ═══════════ */}
            <section id="limitations-section" className="bg-white rounded-2xl border border-rose-200/80 shadow-sm p-6 space-y-4">
              <h2 className="text-xl lg:text-2xl font-bold text-slate-900">
                What Agni-Netra Does Not Claim
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                <div className="flex items-start gap-2.5 bg-rose-50/40 border border-rose-100/80 rounded-xl p-3.5 text-[13px] text-slate-800 leading-snug">
                  <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                  <span><strong>Thermal anomaly</strong> ≠ confirmed fire.</span>
                </div>

                <div className="flex items-start gap-2.5 bg-rose-50/40 border border-rose-100/80 rounded-xl p-3.5 text-[13px] text-slate-800 leading-snug">
                  <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                  <span><strong>Facility proximity</strong> ≠ proof of causation.</span>
                </div>

                <div className="flex items-start gap-2.5 bg-rose-50/40 border border-rose-100/80 rounded-xl p-3.5 text-[13px] text-slate-800 leading-snug">
                  <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                  <span><strong>SAR</strong> provides structural/context evidence, not direct fire-temperature measurement.</span>
                </div>

                <div className="flex items-start gap-2.5 bg-rose-50/40 border border-rose-100/80 rounded-xl p-3.5 text-[13px] text-slate-800 leading-snug">
                  <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                  <span><strong>Weather and atmospheric data</strong> provide contextual/corroborating evidence, not automatic source attribution.</span>
                </div>

                <div className="flex items-start gap-2.5 bg-rose-50/40 border border-rose-100/80 rounded-xl p-3.5 text-[13px] text-slate-800 leading-snug">
                  <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                  <span><strong>Risk Index</strong> is a decision-support score, not a certified physical hazard measurement.</span>
                </div>

                <div className="flex items-start gap-2.5 bg-rose-50/40 border border-rose-100/80 rounded-xl p-3.5 text-[13px] text-slate-800 leading-snug">
                  <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                  <span><strong>Sensor gaps</strong>, cloud cover and limited local ground truth can create <strong>uncertainty</strong>.</span>
                </div>
              </div>
            </section>

            {/* ═══════════ SECTION 30: TECHNICAL MEASUREMENT DICTIONARY ═══════════ */}
            <section id="dictionary-section" className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8 space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <ProvenanceBadge type="AGNI_NETRA_DEMO" label="14 TECHNICAL TERMS" />
                    <span className="text-xs font-semibold text-slate-500">Glossary of Derivations</span>
                  </div>
                  <h2 className="text-2xl font-extrabold text-slate-900 mt-1">
                    Measurement Dictionary
                  </h2>
                  <p className="text-xs text-slate-500 mt-1">
                    Complete technical definitions, inputs, derivations, units, and limitations for each metric.
                  </p>
                </div>

                {/* Search input */}
                <div className="relative w-full sm:w-64">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    value={dictionarySearch}
                    onChange={(e) => setDictionarySearch(e.target.value)}
                    placeholder="Search dictionary..."
                    className="w-full pl-9 pr-3 py-1.5 rounded-lg border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* Accordion Dictionary */}
              <div className="space-y-2.5">
                {filteredDictionary.map((item) => {
                  const isExpanded = expandedDictionaryTerm === item.term;
                  return (
                    <div
                      key={item.term}
                      className={`border rounded-xl transition-all overflow-hidden ${
                        isExpanded ? 'border-blue-300 bg-blue-50/20 shadow-sm' : 'border-slate-200 bg-slate-50/50'
                      }`}
                    >
                      <button
                        onClick={() => setExpandedDictionaryTerm(isExpanded ? null : item.term)}
                        className="w-full text-left p-4 flex items-center justify-between gap-4 hover:bg-slate-100/60 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <span className="font-extrabold text-slate-900 text-sm font-mono">{item.term}</span>
                          <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-200 text-slate-700">
                            {item.category}
                          </span>
                        </div>
                        <div className="flex items-center gap-3">
                          <ProvenanceBadge type={item.badge} />
                          {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
                        </div>
                      </button>

                      {isExpanded && (
                        <div className="px-5 pb-5 pt-1 space-y-3 text-xs border-t border-slate-200/60 bg-white">
                          <div>
                            <span className="font-bold text-slate-700 uppercase tracking-wider text-[10px]">What It Means: </span>
                            <span className="text-slate-800">{item.whatItMeans}</span>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                            <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                              <div className="font-bold text-slate-600 text-[10px] uppercase">Input Data:</div>
                              <div className="text-slate-800 mt-0.5">{item.input}</div>
                            </div>
                            <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                              <div className="font-bold text-slate-600 text-[10px] uppercase">How It Is Derived:</div>
                              <div className="text-blue-900 font-medium mt-0.5">{item.howDerived}</div>
                            </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                              <div className="font-bold text-slate-600 text-[10px] uppercase">Standard Unit:</div>
                              <div className="text-slate-800 mt-0.5 font-mono font-bold">{item.unit}</div>
                            </div>
                            <div className="bg-rose-50 border border-rose-200 rounded-lg p-3">
                              <div className="font-bold text-rose-800 text-[10px] uppercase">Technical Limitation:</div>
                              <div className="text-rose-900 mt-0.5">{item.limitation}</div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </section>

            {/* ═══════════ SECTION: TECHNICAL REFERENCES (EXPANDABLE CITATIONS) ═══════════ */}
            <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 lg:p-8 space-y-6">
              <div className="border-b border-slate-100 pb-4">
                <div className="flex items-center gap-2">
                  <ProvenanceBadge type="PUBLISHED_RESULT" label="TECHNICAL REFERENCES" />
                  <span className="text-xs font-semibold text-slate-500">Underlying Scientific Basis</span>
                </div>
                <h2 className="text-2xl font-extrabold text-slate-900 mt-1">
                  Published Technical References
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Expandable citations detailing underlying published papers, methods, datasets, metrics, and limitations.
                </p>
              </div>

              <div className="space-y-3">
                {technicalReferences.map((ref) => {
                  const isExpanded = expandedRef === ref.id;
                  return (
                    <div
                      key={ref.id}
                      className={`border rounded-xl transition-all overflow-hidden ${
                        isExpanded ? 'border-purple-300 bg-purple-50/20 shadow-sm' : 'border-slate-200 bg-slate-50/50'
                      }`}
                    >
                      <button
                        onClick={() => setExpandedRef(isExpanded ? null : ref.id)}
                        className="w-full text-left p-4 flex items-center justify-between gap-4 hover:bg-slate-100/60 transition-colors"
                      >
                        <div>
                          <div className="font-extrabold text-slate-900 text-sm">{ref.sourceTitle}</div>
                          <div className="text-xs text-slate-500 mt-0.5 font-medium">{ref.authors} ({ref.year})</div>
                        </div>
                        <div className="flex items-center gap-3">
                          <ProvenanceBadge type={ref.badge} />
                          {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
                        </div>
                      </button>

                      {isExpanded && (
                        <div className="px-5 pb-5 pt-1 space-y-3 text-xs border-t border-slate-200/60 bg-white">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                              <div className="font-bold text-slate-600 text-[10px] uppercase">Technical Task:</div>
                              <div className="text-slate-800 mt-0.5">{ref.technicalTask}</div>
                            </div>
                            <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                              <div className="font-bold text-slate-600 text-[10px] uppercase">Dataset / Population:</div>
                              <div className="text-slate-800 mt-0.5">{ref.dataset}</div>
                            </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                              <div className="font-bold text-purple-900 text-[10px] uppercase">Published Metric & Result:</div>
                              <div className="text-purple-950 font-semibold mt-0.5">{ref.publishedMetric} → {ref.publishedResult}</div>
                            </div>
                            <div className="bg-rose-50 border border-rose-200 rounded-lg p-3">
                              <div className="font-bold text-rose-800 text-[10px] uppercase">Technical Limitation:</div>
                              <div className="text-rose-900 mt-0.5">{ref.limitation}</div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </section>

            {/* ═══════════ ORIGINAL SECTIONS PRESERVED: ENABLERS + WORKFLOW + WHY DIFFERENT ═══════════ */}
            <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Col 1 — Technical Enablers */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-lg font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <Radio className="w-5 h-5 text-blue-600" />
                  Key Technical Enablers
                </h2>
                <div className="space-y-4">
                  {technicalEnablers.map((t) => (
                    <div key={t.name} className="border-l-3 border-blue-500 pl-3">
                      <div className="text-xs font-bold text-blue-700">{t.name}</div>
                      <div className="text-[11px] text-slate-600 leading-snug mt-0.5">{t.desc}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Col 2 — System Workflow */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-lg font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <Layers className="w-5 h-5 text-indigo-600" />
                  System Workflow
                </h2>
                <div className="flex flex-col items-center gap-0">
                  {workflowSteps.map((step, i) => {
                    const isLast = i === workflowSteps.length - 1;
                    const colors = i < 2 ? 'bg-sky-100 text-sky-800 border-sky-200'
                      : i < 5 ? 'bg-blue-100 text-blue-800 border-blue-200'
                      : i < 7 ? 'bg-indigo-100 text-indigo-800 border-indigo-200'
                      : i < 9 ? 'bg-amber-100 text-amber-800 border-amber-200'
                      : i < 11 ? 'bg-emerald-100 text-emerald-800 border-emerald-200'
                      : 'bg-green-100 text-green-800 border-green-200';
                    return (
                      <React.Fragment key={step}>
                        <div className={`w-full text-center text-[11px] font-bold py-2 px-4 rounded-lg border ${colors}`}>
                          {step}
                        </div>
                        {!isLast && (
                          <ArrowDown className="w-3.5 h-3.5 text-slate-400 my-0.5 shrink-0" />
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>
              </div>

              {/* Col 3 — Why Different */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-lg font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-amber-500" />
                  Why Agni-Netra is Different
                </h2>
                <div className="space-y-0 border border-slate-200 rounded-lg overflow-hidden">
                  <div className="grid grid-cols-2 bg-slate-100 border-b border-slate-200">
                    <div className="text-[10px] font-bold text-slate-600 uppercase tracking-wider px-3 py-2">Technical Capability</div>
                    <div className="text-[10px] font-bold text-slate-600 uppercase tracking-wider px-3 py-2">Why It Matters</div>
                  </div>
                  {whyDifferent.map((w, i) => (
                    <div key={i} className={`grid grid-cols-2 ${i < whyDifferent.length - 1 ? 'border-b border-slate-100' : ''}`}>
                      <div className="text-[11px] font-semibold text-slate-800 px-3 py-2.5">{w.capability}</div>
                      <div className="text-[11px] text-slate-600 px-3 py-2.5">{w.matter}</div>
                    </div>
                  ))}
                </div>

                {/* Same Thermal Signal comparison */}
                <div className="mt-6">
                  <h3 className="text-xs font-bold text-slate-800 mb-3">Same Thermal Signal → Different Intelligence</h3>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <div className="text-[10px] font-bold text-green-800 mb-2 flex items-center gap-1">
                        <CircleDot className="w-3 h-3" /> Routine Flare
                      </div>
                      <ul className="text-[10px] text-green-700 space-y-1">
                        <li>High thermal signal</li>
                        <li>Persistent / fixed footprint</li>
                        <li>Historical behavior = normal</li>
                        <li>Evidence supports routine flare</li>
                        <li className="font-bold">Normal → Monitor</li>
                      </ul>
                    </div>
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <div className="text-[10px] font-bold text-red-800 mb-2 flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" /> Abnormal Industrial Event
                      </div>
                      <ul className="text-[10px] text-red-700 space-y-1">
                        <li>High thermal signal</li>
                        <li>FRP ↑ + expanding footprint</li>
                        <li>Historical behavior = abnormal</li>
                        <li>Evidence supports abnormal event</li>
                        <li className="font-bold">Highly Abnormal → Verify / Escalate</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* ═══════════ ORIGINAL SECTIONS PRESERVED: GAPS → SOLUTIONS → BENEFITS ═══════════ */}
            <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Existing Gaps */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-lg font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-red-500" />
                  Existing Gaps
                </h2>
                <div className="space-y-3">
                  {existingGaps.map((g, i) => (
                    <div key={i} className="flex gap-3">
                      <div className="w-6 h-6 rounded-full bg-red-100 text-red-700 flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                        {i + 1}
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-800">{g.title}</div>
                        <div className="text-[11px] text-slate-500 leading-snug">{g.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Agni-Netra Solution */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-lg font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-blue-600" />
                  Agni-Netra Solution
                </h2>
                <div className="space-y-3">
                  {solutions.map((s, i) => (
                    <div key={i} className="flex gap-3">
                      <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                        {i + 1}
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-800">{s.title}</div>
                        <div className="text-[11px] text-slate-500 leading-snug">{s.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Key Benefits */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-lg font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                  Key Benefits
                </h2>
                <div className="space-y-3">
                  {benefits.map((b, i) => (
                    <div key={i} className="flex gap-3">
                      <div className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-[9px] font-bold shrink-0 mt-0.5">
                        {String(i + 1).padStart(2, '0')}
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-800">{b.title}</div>
                        <div className="text-[11px] text-slate-500 leading-snug">{b.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            {/* ═══════════ ORIGINAL SECTIONS PRESERVED: AI/ML MODELS + TECH STACK ═══════════ */}
            <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* AI/ML Models */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-lg font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <Brain className="w-5 h-5 text-purple-600" />
                  Our AI/ML Models
                </h2>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                  {aiModels.map((m) => (
                    <div key={m.name} className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 text-center hover:shadow-md transition-shadow flex flex-col items-center">
                      <div className="w-10 h-10 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center mb-2">
                        <m.icon className="w-5 h-5" />
                      </div>
                      <div className="text-[10px] font-bold text-slate-800 leading-tight">{m.name}</div>
                      <div className="text-[9px] text-slate-500 mt-1 leading-tight">{m.desc}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Technology Stack */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-lg font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-indigo-600" />
                  Technology Stack
                </h2>
                <div className="flex flex-wrap gap-2.5">
                  {techStack.map((t) => (
                    <span key={t} className="px-4 py-2 bg-gradient-to-b from-blue-50 to-blue-100 border border-blue-200 rounded-lg text-xs font-bold text-blue-800 shadow-sm hover:shadow-md transition-shadow cursor-default">
                      {t}
                    </span>
                  ))}
                </div>
                <p className="text-[11px] text-slate-500 mt-4 italic">Simple. Modular. Scalable.</p>
              </div>
            </section>

            {/* ═══════════ FOOTER BANNER (Preserved) ═══════════ */}
            <section className="bg-gradient-to-r from-blue-700 via-blue-600 to-indigo-700 rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-4 shadow-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5 text-white" />
                </div>
                <span className="text-white text-lg font-bold tracking-tight">Towards a Safer, Cleaner and More Resilient India</span>
              </div>
              <div className="text-white/80 text-sm italic text-right">
                <span>&ldquo;Observations to Understanding.</span><br />
                <span>Understanding to Action.&rdquo;</span><br />
                <span className="text-white font-semibold not-italic">— Agni-Netra</span>
              </div>
            </section>

          </div>
        </main>
      </div>
    </div>
  );
}
